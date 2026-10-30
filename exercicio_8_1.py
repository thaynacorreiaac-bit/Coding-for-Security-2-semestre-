# Exercício 8.1 - Dashboard de alertas com defesa contra XSS
# Regra de ouro: valida a entrada, escapa a saída.
# O Jinja2 escapa tudo que vai dentro de {{ }} automaticamente (não desative isso!)
from flask import Flask, request, redirect, url_for, render_template_string

app = Flask(__name__)

alertas = []    # "banco" em memória
SEVERIDADES = ("baixa", "media", "alta", "critica")

PAGINA = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="utf-8">
    <title>Dashboard de Alertas</title>
</head>
<body>
    <h1>Dashboard de Alertas</h1>

    {% if erro %}
        <p><strong>Erro: {{ erro }}</strong></p>
    {% endif %}

    <h2>Novo alerta</h2>
    <form method="POST" action="/alertas">
        <p>
            Descrição:
            <input type="text" name="descricao" size="60" maxlength="200">
        </p>
        <p>
            Severidade:
            <select name="severidade">
                <option value="baixa">baixa</option>
                <option value="media">media</option>
                <option value="alta">alta</option>
                <option value="critica">critica</option>
            </select>
        </p>
        <button type="submit">Cadastrar</button>
    </form>

    <h2>Alertas cadastrados ({{ alertas|length }})</h2>
    <table border="1" cellpadding="6">
        <tr>
            <th>ID</th>
            <th>Severidade</th>
            <th>Descrição</th>
        </tr>
        {% for alerta in alertas %}
        <tr>
            <td>{{ alerta.id }}</td>
            <td>{{ alerta.severidade }}</td>
            <td>{{ alerta.descricao }}</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""


@app.route("/", methods=["GET"])
def index():
    return render_template_string(PAGINA, alertas=alertas, erro=None)


@app.route("/alertas", methods=["POST"])
def cadastrar():
    descricao = request.form.get("descricao", "").strip()
    severidade = request.form.get("severidade", "")

    # Valida a entrada
    if descricao == "":
        return render_template_string(PAGINA, alertas=alertas, erro="a descrição é obrigatória"), 400

    if len(descricao) > 200:
        return render_template_string(PAGINA, alertas=alertas, erro="descrição grande demais (máx. 200)"), 400

    if severidade not in SEVERIDADES:
        return render_template_string(PAGINA, alertas=alertas, erro="severidade inválida"), 400

    alerta = {
        "id": len(alertas) + 1,
        "descricao": descricao,     # guarda como veio; o escape acontece na SAÍDA
        "severidade": severidade,
    }
    alertas.append(alerta)

    return redirect(url_for("index"))


@app.after_request
def headers_seguranca(resp):
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    # Camada extra: mesmo que um script escapasse, o CSP bloqueia script inline
    resp.headers["Content-Security-Policy"] = "default-src 'self'"
    return resp


if __name__ == "__main__":
    # debug=True só pra laboratório! Nunca em produção
    app.run(debug=True, port=5000)
