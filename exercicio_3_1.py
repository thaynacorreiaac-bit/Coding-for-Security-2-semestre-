# Exercício 3.1 - CRUD de usuários e permissões (MySQL)
# Todas as queries são parametrizadas (%s + tupla)
import mysql.connector
from mysql.connector import Error

# Porta do MySQL: 3307 (container mysql-lab). Se for o MySQL da faculdade, troque pra 3306
PORTA = 3307

try:
    conexao = mysql.connector.connect(
        host="localhost", port=PORTA, user="root",
        password="senha", database="seguranca"
    )
except Error as e:
    print("Erro de conexão:", e)
    exit()

cursor = conexao.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nome VARCHAR(100) NOT NULL,
        email VARCHAR(100) NOT NULL UNIQUE,
        nivel_acesso INT NOT NULL
    )
""")

# Dados iniciais (só insere se a tabela estiver vazia)
usuarios = [
    ("Carlos Silva", "carlos@empresa.com", 3),
    ("Ana Costa", "ana@empresa.com", 5),
    ("Bruno Lima", "bruno@empresa.com", 1),
]

cursor.execute("SELECT COUNT(*) FROM usuarios")
total = cursor.fetchone()[0]
if total == 0:
    cursor.executemany(
        "INSERT INTO usuarios (nome, email, nivel_acesso) VALUES (%s, %s, %s)",
        usuarios
    )
    conexao.commit()


def ler_nivel():
    # Pede o nível e valida: precisa ser número entre 1 e 5. Retorna None se inválido
    texto = input("Nível de acesso (1-5): ")
    try:
        nivel = int(texto)
    except ValueError:
        print("Erro: o nível precisa ser um número!")
        return None

    if nivel < 1 or nivel > 5:
        print("Erro: o nível precisa estar entre 1 e 5!")
        return None

    return nivel


def cadastrar():
    nome = input("Nome: ")
    email = input("Email: ")
    nivel = ler_nivel()
    if nivel is None:
        return

    try:
        cursor.execute(
            "INSERT INTO usuarios (nome, email, nivel_acesso) VALUES (%s, %s, %s)",
            (nome, email, nivel)
        )
        conexao.commit()
        print("Usuário cadastrado!")
    except mysql.connector.IntegrityError:
        conexao.rollback()
        print("Erro: email já existe")


def listar():
    cursor.execute("SELECT nome, email, nivel_acesso FROM usuarios ORDER BY id")
    for linha in cursor.fetchall():
        print(linha[0].ljust(13) + "| " + linha[1].ljust(19) + "| nível " + str(linha[2]))


def buscar():
    email = input("Email para buscar: ")
    cursor.execute(
        "SELECT nome, email, nivel_acesso FROM usuarios WHERE email = %s",
        (email,)
    )
    linha = cursor.fetchone()

    if linha is None:
        print("Usuário não encontrado!")
    else:
        print("Nome:", linha[0])
        print("Email:", linha[1])
        print("Nível de acesso:", linha[2])


def alterar_nivel():
    email = input("Email do usuário: ")

    cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
    if cursor.fetchone() is None:
        print("Usuário não encontrado!")
        return

    nivel = ler_nivel()
    if nivel is None:
        return

    cursor.execute(
        "UPDATE usuarios SET nivel_acesso = %s WHERE email = %s",
        (nivel, email)
    )
    conexao.commit()
    print("Nível atualizado!")


def remover():
    email = input("Email do usuário para remover: ")

    cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
    if cursor.fetchone() is None:
        print("Usuário não encontrado!")
        return

    cursor.execute("DELETE FROM usuarios WHERE email = %s", (email,))
    conexao.commit()
    print("Usuário removido!")


while True:
    print("")
    print("===== USUÁRIOS E PERMISSÕES =====")
    print("[1] Cadastrar")
    print("[2] Listar")
    print("[3] Buscar por email")
    print("[4] Promover/rebaixar nível")
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
        alterar_nivel()
    elif opcao == "5":
        remover()
    elif opcao == "6":
        print("Saindo...")
        break
    else:
        print("Opção inválida!")

cursor.close()
conexao.close()
