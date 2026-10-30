# Exercício 6.1 - API CRUD de usuários (Flask, dados em memória)
from flask import Flask, jsonify, request

app = Flask(__name__)

usuarios = []     # "banco" em memória
proximo_id = 1


def buscar_usuario(id):
    # Procura o usuário pelo id. Retorna None se não achar
    for usuario in usuarios:
        if usuario["id"] == id:
            return usuario
    return None


def email_existe(email, ignorar_id=None):
    # Confere se o email já está em uso (ignorar_id serve pro PUT não conflitar consigo mesmo)
    for usuario in usuarios:
        if usuario["email"] == email and usuario["id"] != ignorar_id:
            return True
    return False


def nivel_valido(nivel):
    # Precisa ser inteiro entre 1 e 5 (type() != int também barra True/False)
    if type(nivel) != int:
        return False
    return nivel >= 1 and nivel <= 5


@app.route("/api/usuarios", methods=["GET"])
def listar():
    return jsonify(usuarios), 200


@app.route("/api/usuarios/<int:id>", methods=["GET"])
def obter(id):
    usuario = buscar_usuario(id)
    if usuario is None:
        return jsonify({"erro": "Usuário não encontrado"}), 404
    return jsonify(usuario), 200


@app.route("/api/usuarios", methods=["POST"])
def criar():
    global proximo_id

    dados = request.get_json(silent=True)

    if not dados or "nome" not in dados or "email" not in dados or "nivel" not in dados:
        return jsonify({"erro": "Campos 'nome', 'email' e 'nivel' são obrigatórios"}), 400

    if email_existe(dados["email"]):
        return jsonify({"erro": "email já existe"}), 400

    if not nivel_valido(dados["nivel"]):
        return jsonify({"erro": "nível inválido"}), 400

    usuario = {
        "id": proximo_id,
        "nome": dados["nome"],
        "email": dados["email"],
        "nivel": dados["nivel"],
    }
    usuarios.append(usuario)
    proximo_id = proximo_id + 1

    return jsonify(usuario), 201


@app.route("/api/usuarios/<int:id>", methods=["PUT"])
def atualizar(id):
    usuario = buscar_usuario(id)
    if usuario is None:
        return jsonify({"erro": "Usuário não encontrado"}), 404

    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({"erro": "Corpo JSON ausente ou inválido"}), 400

    # Valida primeiro, só altera se estiver tudo certo
    if "email" in dados and email_existe(dados["email"], id):
        return jsonify({"erro": "email já existe"}), 400

    if "nivel" in dados and not nivel_valido(dados["nivel"]):
        return jsonify({"erro": "nível inválido"}), 400

    if "nome" in dados:
        usuario["nome"] = dados["nome"]
    if "email" in dados:
        usuario["email"] = dados["email"]
    if "nivel" in dados:
        usuario["nivel"] = dados["nivel"]

    return jsonify(usuario), 200


@app.route("/api/usuarios/<int:id>", methods=["DELETE"])
def deletar(id):
    usuario = buscar_usuario(id)
    if usuario is None:
        return jsonify({"erro": "Usuário não encontrado"}), 404

    usuarios.remove(usuario)
    return jsonify({"mensagem": "Removido"}), 200


@app.errorhandler(404)
def nao_encontrado(e):
    return jsonify({"erro": "Rota não existe"}), 404


@app.errorhandler(405)
def metodo_nao_permitido(e):
    return jsonify({"erro": "Método não permitido"}), 405


@app.errorhandler(500)
def erro_interno(e):
    return jsonify({"erro": "Erro interno do servidor"}), 500


if __name__ == "__main__":
    # debug=True só pra laboratório! Nunca em produção
    app.run(debug=True, port=5000)
