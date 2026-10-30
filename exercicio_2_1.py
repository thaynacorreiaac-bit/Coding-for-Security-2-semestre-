# Exercício 2.1 - CRUD de inventário de ativos (MongoDB)
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

cliente = MongoClient("mongodb://localhost:27017/")
banco = cliente["seguranca"]
colecao = banco["ativos"]

# Índice único no IP: o próprio MongoDB barra IP duplicado
colecao.create_index("ip", unique=True)

# Dados iniciais (só insere se a coleção estiver vazia)
ativos = [
    {"nome": "SRV-WEB01", "tipo": "servidor", "ip": "192.168.1.10", "status": "ativo"},
    {"nome": "PC-RH03", "tipo": "estacao", "ip": "192.168.1.45", "status": "ativo"},
    {"nome": "SW-CORE01", "tipo": "switch", "ip": "192.168.1.1", "status": "inativo"},
]

if colecao.count_documents({}) == 0:
    colecao.insert_many(ativos)


def cadastrar():
    nome = input("Nome: ")
    tipo = input("Tipo: ")
    ip = input("IP: ")
    status = input("Status: ")

    ativo = {"nome": nome, "tipo": tipo, "ip": ip, "status": status}

    try:
        colecao.insert_one(ativo)
        print("Ativo cadastrado!")
    except DuplicateKeyError:
        print("Erro: IP já cadastrado!")


def listar():
    print("NOME".ljust(12) + "TIPO".ljust(12) + "IP".ljust(16) + "STATUS")
    print("-" * 50)
    for ativo in colecao.find():
        print(ativo["nome"].ljust(12) + ativo["tipo"].ljust(12) + ativo["ip"].ljust(16) + ativo["status"])


def buscar():
    ip = input("IP para buscar: ")
    ativo = colecao.find_one({"ip": ip})

    if ativo is None:
        print("Ativo não encontrado!")
    else:
        print("Nome:", ativo["nome"])
        print("Tipo:", ativo["tipo"])
        print("IP:", ativo["ip"])
        print("Status:", ativo["status"])


def atualizar():
    ip = input("IP do ativo: ")
    novo_status = input("Novo status: ")

    resultado = colecao.update_one({"ip": ip}, {"$set": {"status": novo_status}})

    if resultado.matched_count == 0:
        print("Ativo não encontrado!")
    else:
        print("Status atualizado!")


def remover():
    ip = input("IP do ativo para remover: ")

    resultado = colecao.delete_one({"ip": ip})

    if resultado.deleted_count == 0:
        print("Ativo não encontrado!")
    else:
        print("Ativo removido!")


while True:
    print("")
    print("===== INVENTÁRIO DE ATIVOS =====")
    print("[1] Cadastrar")
    print("[2] Listar")
    print("[3] Buscar por IP")
    print("[4] Atualizar status")
    print("[5] Remover")
    print("[6] Sair")
    opcao = input("Escolha: ")

    if opcao == "1":
        cadastrar()
    elif opcao == "2":
        listar()
    elif opcao == "3":
        buscar()
    elif opcao == "4":
        atualizar()
    elif opcao == "5":
        remover()
    elif opcao == "6":
        print("Saindo...")
        break
    else:
        print("Opção inválida!")
