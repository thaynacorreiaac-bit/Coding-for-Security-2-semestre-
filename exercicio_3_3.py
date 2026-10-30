# Exercício 3.3 - Relatório de alertas por tipo e severidade
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
    CREATE TABLE IF NOT EXISTS alertas (
        id INT AUTO_INCREMENT PRIMARY KEY,
        tipo VARCHAR(50), descricao TEXT,
        ip_origem VARCHAR(45),
        severidade ENUM('baixa','media','alta','critica'),
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# Limpa a tabela pra não duplicar os 10 registros se rodar de novo
cursor.execute("DELETE FROM alertas")

alertas = [
    ("BRUTE_FORCE", "10 falhas de login", "185.220.101.1", "critica"),
    ("BRUTE_FORCE", "25 falhas de login", "185.220.101.1", "critica"),
    ("BRUTE_FORCE", "40 falhas de login", "185.220.101.1", "critica"),
    ("BRUTE_FORCE", "5 falhas de login", "185.220.101.1", "alta"),
    ("PORT_SCAN", "Scan de portas detectado", "45.33.32.156", "alta"),
    ("PORT_SCAN", "Scan de portas detectado", "45.33.32.156", "alta"),
    ("PORT_SCAN", "Scan de portas detectado", "45.33.32.156", "alta"),
    ("XSS", "script na URL", "91.240.118.172", "media"),
    ("XSS", "script em formulário", "91.240.118.172", "media"),
    ("SQLI", "aspas simples em parâmetro", "103.21.244.5", "baixa"),
]

cursor.executemany(
    "INSERT INTO alertas (tipo, descricao, ip_origem, severidade) VALUES (%s, %s, %s, %s)",
    alertas
)
conexao.commit()

# (a) contagem por severidade
# ORDER BY severidade DESC: o ENUM ordena pela posição (critica > alta > media > baixa)
print("=== Por severidade ===")
cursor.execute("""
    SELECT severidade, COUNT(*) AS total
    FROM alertas
    GROUP BY severidade
    ORDER BY severidade DESC
""")
for linha in cursor.fetchall():
    print(linha[0] + ":", linha[1])

# (b) contagem por tipo
print("")
print("=== Por tipo ===")
cursor.execute("""
    SELECT tipo, COUNT(*) AS total
    FROM alertas
    GROUP BY tipo
    ORDER BY total DESC
""")
for linha in cursor.fetchall():
    print(linha[0] + ":", linha[1])

# (c) top 5 IPs de origem
print("")
print("=== Top IPs de origem ===")
cursor.execute("""
    SELECT ip_origem, COUNT(*) AS total
    FROM alertas
    GROUP BY ip_origem
    ORDER BY total DESC
    LIMIT 5
""")
for linha in cursor.fetchall():
    print(linha[0], "->", linha[1], "alertas")

cursor.close()
conexao.close()
