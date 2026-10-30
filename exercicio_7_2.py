# Exercício 7.2 - Paginação e filtros na API de incidentes
# (é a API do 7.1 completa, com a listagem melhorada)
#
# GET /api/incidentes aceita estes parâmetros (todos opcionais, podem ser combinados):
#   pagina     -> número da página, começa em 1 (padrão: 1)
#   tamanho    -> itens por página, de 1 a 100 (padrão: 10)
#   severidade -> filtra por baixa | media | alta | critica
#   status     -> filtra por aberto | em_andamento | resolvido
# Ordenação: sempre do mais recente pro mais antigo (criado_em decrescente).
# Parâmetro inválido -> 400.
#
# Exemplos:
#   GET /api/incidentes?tamanho=5&pagina=1
#   GET /api/incidentes?severidade=critica
#   GET /api/incidentes?status=aberto&tamanho=3
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


def ler_inteiro(nome, padrao):
    # Lê um parâmetro da URL como inteiro. Retorna None se não for número
    valor = request.args.get(nome, padrao)
    try:
        return int(valor)
    except ValueError:
        return None


@app.route("/api/incidentes", methods=["GET"])
def listar():
    pagina = ler_inteiro("pagina", 1)
    tamanho = ler_inteiro("tamanho", 10)

    if pagina is None or pagina < 1:
        return jsonify({"erro": "pagina inválida (use um número a partir de 1)"}), 400

    if tamanho is None or tamanho < 1 or tamanho > 100:
        return jsonify({"erro": "tamanho inválido (use de 1 a 100)"}), 400

    # Monta o filtro só com o que foi informado
    filtro = {}

    severidade = request.args.get("severidade")
    if severidade is not None:
        if severidade not in SEVERIDADES:
            return jsonify({"erro": "severidade inválida"}), 400
        filtro["severidade"] = severidade

    status = request.args.get("status")
    if status is not None:
        if status not in STATUS_VALIDOS:
            return jsonify({"erro": "status inválido"}), 400
        filtro["status"] = status

    # Mais recentes primeiro (o _id desempata incidentes criados no mesmo segundo)
    cursor = colecao.find(filtro).sort([("criado_em", -1), ("_id", -1)])
    cursor = cursor.skip((pagina - 1) * tamanho).limit(tamanho)

    lista = []
    for doc in cursor:
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
