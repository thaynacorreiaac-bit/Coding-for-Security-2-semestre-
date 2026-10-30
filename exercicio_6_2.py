# Exercício 6.2 - Endpoint de análise de senha
from flask import Flask, jsonify, request

app = Flask(__name__)


def verificar_senha(senha):
    # Confere cada critério e devolve a força + o checklist
    especiais = "!@#$%^&*()-_=+[]{};:,.<>?/|~"

    tem_maiuscula = False
    tem_minuscula = False
    tem_numero = False
    tem_especial = False

    for letra in senha:
        if letra.isupper():
            tem_maiuscula = True
        elif letra.islower():
            tem_minuscula = True
        elif letra.isdigit():
            tem_numero = True
        elif letra in especiais:
            tem_especial = True

    criterios = {
        "tamanho_min": len(senha) >= 8,
        "maiuscula": tem_maiuscula,
        "minuscula": tem_minuscula,
        "numero": tem_numero,
        "especial": tem_especial,
    }

    # Conta quantos critérios foram atendidos
    pontos = 0
    for criterio in criterios:
        if criterios[criterio]:
            pontos = pontos + 1

    if pontos == 5:
        forca = "Muito forte"
    elif pontos == 4:
        forca = "Forte"
    elif pontos == 3:
        forca = "Média"
    else:
        forca = "Fraca"

    return forca, criterios


@app.route("/api/analisar-senha", methods=["POST"])
def analisar_senha():
    dados = request.get_json(silent=True)

    if not dados or "senha" not in dados:
        return jsonify({"erro": "campo 'senha' obrigatório"}), 400

    if type(dados["senha"]) != str or dados["senha"] == "":
        return jsonify({"erro": "campo 'senha' deve ser um texto não vazio"}), 400

    forca, criterios = verificar_senha(dados["senha"])

    return jsonify({"forca": forca, "criterios": criterios}), 200


@app.errorhandler(404)
def nao_encontrado(e):
    return jsonify({"erro": "Rota não existe"}), 404


@app.errorhandler(405)
def metodo_nao_permitido(e):
    return jsonify({"erro": "Método não permitido"}), 405


if __name__ == "__main__":
    # debug=True só pra laboratório! Nunca em produção
    app.run(debug=True, port=5000)
