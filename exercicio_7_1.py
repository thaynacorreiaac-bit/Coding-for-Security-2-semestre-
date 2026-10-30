# Exercício 7.1 - API de incidentes com MongoDB (CRUD completo)
from datetime import datetime
from flask import Flask, jsonify, request
from pymongo import MongoClient
from bson import ObjectId
from bson.errors import InvalidId

app = Flask(__name__)
db = MongoClient("mongodb://localhost:27017/").seguranca
colecao = db.incidentes

SEVERIDADES = ("baixa", "media", "alta", "critica")
STATUS_VALIDOS = ("aberto", "em_andamento", "resolvido")


def serializar(doc):
    # ObjectId não vira JSON sozinho, então converte o _id em texto
    doc["_id"] = str(doc["_id"])
    return doc


def converter_id(id):
    # Retorna o ObjectId, ou None se o id for malformado
    try:
        return ObjectId(id)
    except InvalidId:
        return None


@app.route("/api/incidentes", methods=["GET"])
def listar():
    lista = []
    for doc in colecao.find():
        lista.append(serializar(doc))
    return jsonify(lista), 200


@app.route("/api/incidentes", methods=["POST"])
def criar():
    dados = request.get_json(silent=True)

    if not dados or "titulo" not in dados or "severidade" not in dados or "ip_origem" not in dados:
        return jsonify({"erro": "Campos 'titulo', 'severidade' e 'ip_origem' são obrigatórios"}), 400

    if dados["severidade"] not in SEVERIDADES:
        return jsonify({"erro": "severidade inválida"}), 400

    # status é opcional: se não vier, o incidente nasce "aberto"
    status = dados.get("status", "aberto")
    if status not in STATUS_VALIDOS:
        return jsonify({"erro": "status inválido"}), 400

    incidente = {
        "titulo": dados["titulo"],
        "severidade": dados["severidade"],
        "status": status,
        "ip_origem": dados["ip_origem"],
        "criado_em": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    resultado = colecao.insert_one(incidente)
    return jsonify({"id": str(resultado.inserted_id)}), 201


@app.route("/api/incidentes/<id>", methods=["GET"])
def obter(id):
    oid = converter_id(id)
    if oid is None:
        return jsonify({"erro": "id inválido"}), 400

    doc = colecao.find_one({"_id": oid})
    if doc is None:
        return jsonify({"erro": "não encontrado"}), 404

    return jsonify(serializar(doc)), 200


@app.route("/api/incidentes/<id>", methods=["PUT"])
def atualizar(id):
    oid = converter_id(id)
    if oid is None:
        return jsonify({"erro": "id inválido"}), 400

    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({"erro": "Corpo JSON ausente ou inválido"}), 400

    # Só aceita os campos permitidos (ignora o resto)
    novos = {}
    for campo in ("titulo", "severidade", "status", "ip_origem"):
        if campo in dados:
            novos[campo] = dados[campo]

    if len(novos) == 0:
        return jsonify({"erro": "Nenhum campo válido para atualizar"}), 400

    if "severidade" in novos and novos["severidade"] not in SEVERIDADES:
        return jsonify({"erro": "severidade inválida"}), 400

    if "status" in novos and novos["status"] not in STATUS_VALIDOS:
        return jsonify({"erro": "status inválido"}), 400

    resultado = colecao.update_one({"_id": oid}, {"$set": novos})
    if resultado.matched_count == 0:
        return jsonify({"erro": "não encontrado"}), 404

    doc = colecao.find_one({"_id": oid})
    return jsonify(serializar(doc)), 200


@app.route("/api/incidentes/<id>", methods=["DELETE"])
def deletar(id):
    oid = converter_id(id)
    if oid is None:
        return jsonify({"erro": "id inválido"}), 400

    resultado = colecao.delete_one({"_id": oid})
    if resultado.deleted_count == 0:
        return jsonify({"erro": "não encontrado"}), 404

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
