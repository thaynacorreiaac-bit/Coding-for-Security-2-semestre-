# Exercício 3.2 - Prova de conceito de SQL Injection (DEFENSIVO)
# Roda só no banco local de laboratório.
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

# Garante a tabela e os 3 usuários (INSERT IGNORE pula o que já existe, o email é único)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nome VARCHAR(100) NOT NULL,
        email VARCHAR(100) NOT NULL UNIQUE,
        nivel_acesso INT NOT NULL
    )
""")
usuarios = [
    ("Carlos Silva", "carlos@empresa.com", 3),
    ("Ana Costa", "ana@empresa.com", 5),
    ("Bruno Lima", "bruno@empresa.com", 1),
]
cursor.executemany(
    "INSERT IGNORE INTO usuarios (nome, email, nivel_acesso) VALUES (%s, %s, %s)",
    usuarios
)
conexao.commit()


def buscar_inseguro(nome):
    # VULNERÁVEL: concatena a entrada direto na query
    query = "SELECT * FROM usuarios WHERE nome = '" + nome + "'"
    print("   Query executada:", query)
    cursor.execute(query)
    return cursor.fetchall()


def buscar_seguro(nome):
    # SEGURO: query parametrizada, a entrada é tratada como dado
    query = "SELECT * FROM usuarios WHERE nome = %s"
    print("   Query executada:", query, "com parâmetro", (nome,))
    cursor.execute(query, (nome,))
    return cursor.fetchall()


entrada_maliciosa = "' OR '1'='1"

print("[INSEGURO] entrada:", entrada_maliciosa)
resultado = buscar_inseguro(entrada_maliciosa)
print("[INSEGURO] entrada:", entrada_maliciosa, "->", len(resultado), "usuários retornados (VAZAMENTO!)")

print("")

print("[SEGURO]   entrada:", entrada_maliciosa)
resultado = buscar_seguro(entrada_maliciosa)
print("[SEGURO]   entrada:", entrada_maliciosa, "->", len(resultado), "usuários retornados (defesa OK)")

print("")
print("Conclusão: a query parametrizada tratou a entrada como texto literal.")

cursor.close()
conexao.close()
