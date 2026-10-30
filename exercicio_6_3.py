# Exercício 6.3 - API de verificação de IP em blacklist
from flask import Flask, jsonify

app = Flask(__name__)

blacklist = {"185.220.101.1", "45.33.32.156", "91.240.118.172"}


def ip_valido(ip):
    # IPv4 válido: 4 partes numéricas, cada uma entre 0 e 255
    partes = ip.split(".")

    if len(partes) != 4:
        return False

    for parte in partes:
        if not parte.isdigit():
            return False
        if int(parte) < 0 or int(parte) > 255:
            return False

    return True


def classificar_ip(ip):
    # Privados (RFC 1918): 10.x.x.x, 172.16-31.x.x, 192.168.x.x (+ 127.x.x.x loopback)
    partes = ip.split(".")
    primeiro = int(partes[0])
    segundo = int(partes[1])

    if primeiro == 10:
        return "privado"
    if primeiro == 172 and segundo >= 16 and segundo <= 31:
        return "privado"
    if primeiro == 192 and segundo == 168:
        return "privado"
    if primeiro == 127:
        return "privado"

    return "publico"


@app.route("/api/checar-ip/<ip>", methods=["GET"])
def checar_ip(ip):
    if not ip_valido(ip):
        return jsonify({"erro": "IP inválido"}), 400

    resposta = {
        "ip": ip,
        "na_blacklist": ip in blacklist,
        "tipo": classificar_ip(ip),
    }
    return jsonify(resposta), 200


@app.errorhandler(404)
def nao_encontrado(e):
    return jsonify({"erro": "Rota não existe"}), 404


if __name__ == "__main__":
    # debug=True só pra laboratório! Nunca em produção
    app.run(debug=True, port=5000)
