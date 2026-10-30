# Exercício 7.3 - API de usuários com MySQL e tratamento de erros
# Todas as queries são parametrizadas. Erros de banco NÃO vazam pro cliente
# (o detalhe real só aparece no terminal do servidor).
import mysql.connector
from mysql.connector import Error
from flask import Flask, jsonify, request

app = Flask(__name__)

# Porta do MySQL: 3307 (container mysql-lab). Se for o MySQL da faculdade, troque pra 3306
PORTA = 3307


def get_db():
    return mysql.connector.connect(
        host="localhost", port=PORTA, user="root",
        password="senha", database="seguranca",
        connection_timeout=3
    )


def criar_tabela():
    # Roda uma vez quando o servidor sobe. Se o banco estiver fora, só avisa no terminal
    conexao = None
    try:
        conexao = get_db()
        cursor = conexao.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                nivel_acesso INT NOT NULL DEFAULT 1
            )
        """)
        conexao.commit()
    except Error as e:
        print("Aviso: não foi possível criar a tabela agora:", e)
    finally:
        if conexao is not None and conexao.is_connected():
            conexao.close()


def erro_banco(e):
    # Detalhe real só no log do servidor; o cliente recebe uma mensagem genérica
    print("Erro de banco:", e)
    return jsonify({"erro": "serviço indisponível"}), 500


def nivel_valido(nivel):
    if type(nivel) != int:
        return False
    return nivel >= 1 and nivel <= 5


@app.route("/api/usuarios", methods=["GET"])
def listar():
    conexao = None
    try:
        conexao = get_db()
        cursor = conexao.cursor(dictionary=True)
        cursor.execute("SELECT id, nome, email, nivel_acesso FROM usuarios")
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        return erro_banco(e)
    finally:
        if conexao is not None and conexao.is_connected():
            conexao.close()


@app.route("/api/usuarios/<int:id>", methods=["GET"])
def obter(id):
    conexao = None
    try:
        conexao = get_db()
        cursor = conexao.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, nome, email, nivel_acesso FROM usuarios WHERE id = %s",
            (id,)
        )
        usuario = cursor.fetchone()

        if usuario is None:
            return jsonify({"erro": "usuário não encontrado"}), 404
        return jsonify(usuario), 200
    except Error as e:
        return erro_banco(e)
    finally:
        if conexao is not None and conexao.is_connected():
            conexao.close()


@app.route("/api/usuarios", methods=["POST"])
def criar():
    dados = request.get_json(silent=True)

    if type(dados) != dict or "nome" not in dados or "email" not in dados:
        return jsonify({"erro": "Campos 'nome' e 'email' são obrigatórios"}), 400

    if type(dados["nome"]) != str or type(dados["email"]) != str:
        return jsonify({"erro": "'nome' e 'email' devem ser texto"}), 400

    nivel = dados.get("nivel_acesso", 1)
    if not nivel_valido(nivel):
        return jsonify({"erro": "nivel_acesso inválido (use de 1 a 5)"}), 400

    conexao = None
    try:
        conexao = get_db()
        cursor = conexao.cursor()
        cursor.execute(
            "INSERT INTO usuarios (nome, email, nivel_acesso) VALUES (%s, %s, %s)",
            (dados["nome"], dados["email"], nivel)
        )
        conexao.commit()
        return jsonify({"id": cursor.lastrowid}), 201
    except mysql.connector.IntegrityError:
        return jsonify({"erro": "email já cadastrado"}), 409
    except Error as e:
        return erro_banco(e)
    finally:
        if conexao is not None and conexao.is_connected():
            conexao.close()


@app.route("/api/usuarios/<int:id>", methods=["PUT"])
def atualizar(id):
    dados = request.get_json(silent=True)

    if type(dados) != dict or len(dados) == 0:
        return jsonify({"erro": "Corpo JSON ausente ou inválido"}), 400

    # Monta o UPDATE só com os campos enviados.
    # O texto do SQL vem só de strings fixas daqui; os valores vão separados, em %s
    campos = []
    valores = []

    if "nome" in dados:
        if type(dados["nome"]) != str:
            return jsonify({"erro": "'nome' deve ser texto"}), 400
        campos.append("nome = %s")
        valores.append(dados["nome"])

    if "email" in dados:
        if type(dados["email"]) != str:
            return jsonify({"erro": "'email' deve ser texto"}), 400
        campos.append("email = %s")
        valores.append(dados["email"])

    if "nivel_acesso" in dados:
        if not nivel_valido(dados["nivel_acesso"]):
            return jsonify({"erro": "nivel_acesso inválido (use de 1 a 5)"}), 400
        campos.append("nivel_acesso = %s")
        valores.append(dados["nivel_acesso"])

    if len(campos) == 0:
        return jsonify({"erro": "Nenhum campo válido para atualizar"}), 400

    conexao = None
    try:
        conexao = get_db()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("SELECT id FROM usuarios WHERE id = %s", (id,))
        if cursor.fetchone() is None:
            return jsonify({"erro": "usuário não encontrado"}), 404

        valores.append(id)
        cursor.execute(
            "UPDATE usuarios SET " + ", ".join(campos) + " WHERE id = %s",
            tuple(valores)
        )
        conexao.commit()

        cursor.execute(
            "SELECT id, nome, email, nivel_acesso FROM usuarios WHERE id = %s",
            (id,)
        )
        return jsonify(cursor.fetchone()), 200
    except mysql.connector.IntegrityError:
        return jsonify({"erro": "email já cadastrado"}), 409
    except Error as e:
        return erro_banco(e)
    finally:
        if conexao is not None and conexao.is_connected():
            conexao.close()


@app.route("/api/usuarios/<int:id>", methods=["DELETE"])
def deletar(id):
    conexao = None
    try:
        conexao = get_db()
        cursor = conexao.cursor()

        cursor.execute("SELECT id FROM usuarios WHERE id = %s", (id,))
        if cursor.fetchone() is None:
            return jsonify({"erro": "usuário não encontrado"}), 404

        cursor.execute("DELETE FROM usuarios WHERE id = %s", (id,))
        conexao.commit()
        return jsonify({"mensagem": "Removido"}), 200
    except Error as e:
        return erro_banco(e)
    finally:
        if conexao is not None and conexao.is_connected():
            conexao.close()


@app.errorhandler(404)
def nao_encontrado(e):
    return jsonify({"erro": "Rota não existe"}), 404


@app.errorhandler(405)
def metodo_nao_permitido(e):
    return jsonify({"erro": "Método não permitido"}), 405


@app.errorhandler(500)
def erro_interno(e):
    return jsonify({"erro": "Erro interno do servidor"}), 500


criar_tabela()

if __name__ == "__main__":
    # debug=True só pra laboratório! Nunca em produção
    app.run(debug=True, port=5000)
