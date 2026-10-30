# Exercício 3.2 — Prova de conceito de SQL Injection (defensivo)

Ambiente: banco local de laboratório (MySQL), tabela `usuarios` com 3 registros.
Entrada maliciosa usada: `' OR '1'='1`

## Resultado

| Função | Query executada | Usuários retornados |
|---|---|---|
| `buscar_inseguro` | `SELECT * FROM usuarios WHERE nome = '' OR '1'='1'` | **3** (vazamento) |
| `buscar_seguro` | `SELECT * FROM usuarios WHERE nome = %s` com parâmetro `("' OR '1'='1",)` | **0** (defesa OK) |

## Explicação

- Na versão **insegura**, a entrada foi concatenada na string da query. As aspas da entrada fecharam o texto original e o `OR '1'='1'` virou código SQL. Como `'1'='1'` é sempre verdadeiro, o `WHERE` passou a valer pra todas as linhas e a query devolveu a tabela inteira.
- Na versão **segura**, a query e o valor são enviados separadamente. O driver trata a entrada inteira como um texto literal, então o banco procurou um usuário chamado exatamente `' OR '1'='1`, que não existe.

## Conclusão

Queries parametrizadas (`%s` + tupla) neutralizam a injeção, porque a entrada do usuário nunca é interpretada como código SQL. Concatenar entrada na query é a causa da vulnerabilidade (OWASP Top 10 — Injection).
