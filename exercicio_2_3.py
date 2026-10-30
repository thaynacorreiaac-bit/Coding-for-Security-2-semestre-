# Exercício 2.3 - Consulta com filtros avançados
# (usa a coleção "eventos" criada no exercício 2.2)
from pymongo import MongoClient

cliente = MongoClient("mongodb://localhost:27017/")
banco = cliente["seguranca"]
colecao = banco["eventos"]


def consultar(fonte=None, tipo=None, ip=None, desde=None):
    # Começa com filtro vazio e só adiciona o que foi informado
    filtro = {}

    if fonte is not None:
        filtro["fonte"] = fonte

    if tipo is not None:
        filtro["tipo"] = tipo

    if ip is not None:
        filtro["ip"] = ip

    if desde is not None:
        filtro["timestamp"] = {"$gte": desde}

    # sort por timestamp, do mais antigo pro mais novo
    resultados = colecao.find(filtro).sort("timestamp", 1)

    return list(resultados)


# Teste 1: só as falhas desse IP
print("--- tipo=FAIL, ip=185.220.101.1 ---")
lista = consultar(tipo="FAIL", ip="185.220.101.1")
for doc in lista:
    print(doc["timestamp"], doc["tipo"], doc["usuario"], doc["ip"])
print("Total:", len(lista))

# Teste 2: todos os eventos de auth
print("")
print("--- fonte=auth ---")
lista = consultar(fonte="auth")
for doc in lista:
    print(doc["timestamp"], doc["tipo"], doc["usuario"], doc["ip"])
print("Total:", len(lista))

# Teste 3: com filtro de data
print("")
print("--- fonte=auth, desde=2025-02-20 08:30:00 ---")
lista = consultar(fonte="auth", desde="2025-02-20 08:30:00")
for doc in lista:
    print(doc["timestamp"], doc["tipo"], doc["usuario"], doc["ip"])
print("Total:", len(lista))
