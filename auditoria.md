# Auditoria de código — Exercício 8.3

## Código analisado

```python
@app.route("/user/<nome>")
def user(nome):
    cur.execute("SELECT * FROM users WHERE nome='" + nome + "'")   # (1)
    dados = cur.fetchone()
    return f"<h1>Bem-vindo {nome}</h1>" + str(dados)               # (2)

app.run(debug=True, host="0.0.0.0")                                # (3)
SENHA_DB = "123456"                                                # (4)
# (5) nenhuma rota registra logs de acesso ou tentativa de erro
```

## Resumo

| # | Vulnerabilidade | OWASP Top 10 (2025) | Correção |
|---|---|---|---|
| 1 | SQL Injection | A05 — Injection | Query parametrizada |
| 2 | XSS refletido | A05 — Injection | Escapar a saída (`escape()` / Jinja2) |
| 3 | Debug ligado e exposto na rede | A02 — Security Misconfiguration | `debug=False` + `host="127.0.0.1"` + servidor WSGI |
| 4 | Senha do banco fixa no código | A04 / A02 | Variável de ambiente |
| 5 | Ausência de logs e alertas | A09 — Security Logging & Alerting Failures | Registrar acessos, erros e tentativas suspeitas |

## Detalhamento

### 1. SQL Injection (A05 — Injection)
**Onde:** `cur.execute("SELECT * FROM users WHERE nome='" + nome + "'")`

**Problema:** o valor de `nome` vem da URL e é concatenado direto na query. Quem acessa `/user/' OR '1'='1` faz a condição virar sempre verdadeira e a query devolve dados que não deveria. Dependendo do banco, dá pra ler outras tabelas ou alterar dados.

**Correção:** query parametrizada, com o valor enviado separado do comando SQL:
```python
cur.execute("SELECT nome, email FROM users WHERE nome = %s", (nome,))
```

### 2. XSS (A05 — Injection)
**Onde:** `return f"<h1>Bem-vindo {nome}</h1>" + str(dados)`

**Problema:** `nome` volta pro navegador sem escape. Se a vítima abrir um link como `/user/<script>...</script>`, o script roda no navegador dela, com acesso a cookies e sessão do site.

**Correção:** escapar tudo que vem do usuário (e do banco) antes de montar o HTML:
```python
from markupsafe import escape
return "<h1>Bem-vindo " + str(escape(nome)) + "</h1>"
```
Em templates Jinja2, o `{{ nome }}` já escapa por padrão.

### 3. Security Misconfiguration (A02)
**Onde:** `app.run(debug=True, host="0.0.0.0")`

**Problema:** `debug=True` expõe o console interativo do Werkzeug e páginas de erro com código-fonte. Com `host="0.0.0.0"`, isso fica acessível por qualquer máquina da rede, o que pode virar execução remota de código.

**Correção:** `debug=False`, escutar só em `127.0.0.1` (ou deixar um proxy na frente) e usar um servidor WSGI de verdade em produção (gunicorn):
```python
app.run(debug=False, host="127.0.0.1")
```

### 4. Segredo no código (A04 / A02)
**Onde:** `SENHA_DB = "123456"`

**Problema:** a senha está escrita no código-fonte, então vai parar no repositório e no histórico do Git, e quem lê o código tem acesso ao banco. Além disso, `123456` é uma senha fraca, das primeiras que um atacante testa.

**Correção:** ler o segredo de uma variável de ambiente (e trocar por uma senha forte):
```python
import os
SENHA_DB = os.environ.get("SENHA_DB")
```

### 5. Falta de logging e alertas (A09)
**Onde:** nenhuma rota registra acessos ou erros.

**Problema:** um ataque como o do item 1 não deixa rastro, e ninguém percebe a tentativa de invasão nem consegue investigar depois (sem trilha de auditoria).

**Correção:** registrar acessos, erros e comportamentos suspeitos (por exemplo, nomes com aspas ou `<script>`), e alertar quando o volume passar do normal:
```python
import logging
logging.basicConfig(filename="acessos.log", level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")
logging.info("Acesso a /user de " + request.remote_addr)
```

## Observações extras

- `str(dados)` devolve a linha inteira do banco (`SELECT *`), o que pode expor colunas sensíveis, como hash de senha. A correção é selecionar só as colunas necessárias, como no item 1.
- Não há tratamento de exceção: se o banco falhar, o erro estoura pro usuário (A10 — Mishandling of Exceptional Conditions). Um `try/except` devolvendo uma mensagem genérica resolve.
- Não existe verificação de quem pode ver os dados de cada usuário (A01 — Broken Access Control): qualquer pessoa consulta qualquer `nome`.

## Versão corrigida

```python
import os
import logging
from flask import Flask, request
from markupsafe import escape

app = Flask(__name__)

logging.basicConfig(filename="acessos.log", level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")

SENHA_DB = os.environ.get("SENHA_DB")          # (4) segredo fora do código


@app.route("/user/<nome>")
def user(nome):
    logging.info("Acesso a /user. IP: " + request.remote_addr)     # (5) log

    try:
        # (1) parametrizada + só as colunas necessárias
        cur.execute("SELECT nome, email FROM users WHERE nome = %s", (nome,))
        dados = cur.fetchone()
    except Exception as e:
        logging.error("Erro no banco: " + str(e))                  # detalhe só no log
        return "Erro interno do servidor", 500

    if dados is None:
        logging.warning("Usuário não encontrado. IP: " + request.remote_addr)
        return "Usuário não encontrado", 404

    # (2) escapa o que vai pro HTML
    return "<h1>Bem-vindo " + str(escape(nome)) + "</h1>" + str(escape(str(dados)))


if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1")                         # (3)
```
