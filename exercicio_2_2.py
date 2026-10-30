# Exercício 2.2 - Ingestão de logs do 1º semestre no MongoDB
from pymongo import MongoClient

cliente = MongoClient("mongodb://localhost:27017/")
banco = cliente["seguranca"]
colecao = banco["eventos"]

# Limpa a coleção pra não duplicar eventos se rodar o script de novo
colecao.delete_many({})

eventos = []

arquivo = open("auth.log", "r")

for linha in arquivo:
    linha = linha.strip()

    # pula linhas vazias
    if linha == "":
        continue

    # Formato: 2025-02-20 08:15:01 FAIL usuario=admin ip=185.220.101.1
    partes = linha.split()

    data = partes[0]
    hora = partes[1]
    tipo = partes[2]
    usuario = partes[3].split("=")[1]
    ip = partes[4].split("=")[1]

    evento = {
        "fonte": "auth",
        "timestamp": data + " " + hora,
        "tipo": tipo,
        "usuario": usuario,
        "ip": ip,
    }

    eventos.append(evento)

arquivo.close()

colecao.insert_many(eventos)

# Pipeline: só FAIL -> agrupa por ip -> ordena do maior pro menor -> top 5
pipeline = [
    {"$match": {"tipo": "FAIL"}},
    {"$group": {"_id": "$ip", "total": {"$sum": 1}}},
    {"$sort": {"total": -1}},
    {"$limit": 5},
]

print("=== Top IPs por falhas de login ===")
for resultado in colecao.aggregate(pipeline):
    print(resultado["_id"], "->", resultado["total"], "falhas")

print("Total de eventos inseridos:", len(eventos))
