# Exercício 8.2 - Formulário de login endurecido
# - Query parametrizada no MySQL
# - 400 para campos vazios, 401 GENÉRICO para credenciais erradas
# - Limite de tentativas por IP (429)
# - Senhas guardadas como hash (nunca em texto puro)
import time
import mysql.connector
from mysql.connector import Error
from flask import Flask, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Porta do MySQL: 3307 (container mysql-lab). Se for o MySQL da faculdade, troque pra 3306
PORTA = 3307

MAX_TENTATIVAS = 5      # falhas permitidas...
JANELA_SEGUNDOS = 60    # ...dentro desta janela de tempo

falhas = {}             # ip -> lista com os horários das falhas

# Hash "de mentira": usado quando o usuário não existe, pra demorar o mesmo tempo
HASH_FALSO = generate_password_hash("senha-qualquer")


def get_db():
    return mysql.connector.connect(
        host="localhost", port=PORTA, user="root",
        password="senha", database="seguranca",
        connection_timeout=3
    )


def preparar_banco():
    # Cria a tabela e os 2 usuários do exercício (com a senha já em hash)
    conexao = None
    try:
        conexao = get_db()
        cursor = conexao.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS credenciais (
                id INT AUTO_INCREMENT PRIMARY KEY,
                usuario VARCHAR(50) NOT NULL UNIQUE,
                senha_hash VARCHAR(255) NOT NULL
            )
        """)

        usuarios = {"admin": "Cyber@2024", "analista": "S3gur4nca!"}
        for nome in usuarios:
            cursor.execute("SELECT id FROM credenciais WHERE usuario = %s", (nome,))
            if cursor.fetchone() is None:
                cursor.execute(
                    "INSERT INTO credenciais (usuario, senha_hash) VALUES (%s, %s)",
                    (nome, generate_password_hash(usuarios[nome]))
                )
        conexao.commit()
    except Error as e:
        print("Aviso: não foi possível preparar o banco agora:", e)
    finally:
        if conexao is not None and conexao.is_connected():
            conexao.close()


def limpar_falhas_antigas(ip):
    # Mantém só as falhas que ainda estão dentro da janela de tempo
    agora = time.time()
    recentes = []
    for horario in falhas.get(ip, []):
        if agora - horario < JANELA_SEGUNDOS:
            recentes.append(horario)
    falhas[ip] = recentes


@app.route("/login", methods=["POST"])
def login():
    ip = request.remote_addr

    # 1) Bloqueio por excesso de tentativas
    limpar_falhas_antigas(ip)
    if len(falhas[ip]) >= MAX_TENTATIVAS:
        return jsonify({"erro": "Muitas tentativas. Tente novamente mais tarde"}), 429

    # 2) Validação do corpo
    dados = request.get_json(silent=True)
    if type(dados) != dict:
        return jsonify({"erro": "Corpo JSON ausente ou inválido"}), 400

    usuario = dados.get("usuario", "")
    senha = dados.get("senha", "")

    if type(usuario) != str or type(senha) != str or usuario == "" or senha == "":
        return jsonify({"erro": "Campos 'usuario' e 'senha' são obrigatórios"}), 400

    # 3) Confere no banco com query parametrizada
    conexao = None
    try:
        conexao = get_db()
        cursor = conexao.cursor()
        cursor.execute(
            "SELECT senha_hash FROM credenciais WHERE usuario = %s",
            (usuario,)
        )
        linha = cursor.fetchone()
    except Error as e:
        print("Erro de banco:", e)    # detalhe só no log do servidor
        return jsonify({"erro": "serviço indisponível"}), 500
    finally:
        if conexao is not None and conexao.is_connected():
            conexao.close()

    # Se o usuário não existe, compara com o hash falso (mesmo tempo de resposta)
    if linha is None:
        check_password_hash(HASH_FALSO, senha)
        credenciais_ok = False
    else:
        credenciais_ok = check_password_hash(linha[0], senha)

    # 4) Mesma resposta 401 para usuário inexistente E senha errada
    if not credenciais_ok:
        falhas[ip].append(time.time())
        print("Login falhou. IP:", ip)
        return jsonify({"erro": "Credenciais inválidas"}), 401

    falhas[ip] = []     # login certo zera o contador
    return jsonify({"mensagem": "Login OK"}), 200


@app.errorhandler(404)
def nao_encontrado(e):
    return jsonify({"erro": "Rota não existe"}), 404


@app.errorhandler(405)
def metodo_nao_permitido(e):
    return jsonify({"erro": "Método não permitido"}), 405


preparar_banco()

if __name__ == "__main__":
    # debug=True só pra laboratório! Nunca em produção
    app.run(debug=True, port=5000)
