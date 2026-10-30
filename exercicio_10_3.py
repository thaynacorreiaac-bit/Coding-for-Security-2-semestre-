# Exercício 10.3 - Enriquecedor de IPs com cache e rate limit
# - Cache em dicionário (não consulta o mesmo IP duas vezes)
# - Backoff exponencial quando a API responde 429
# - Classificação privado/público (IP privado nem é consultado)
import json
import time
import requests

ips = ["8.8.8.8", "1.1.1.1", "185.220.101.1", "192.168.1.10", "8.8.8.8"]   # repetido de propósito

blacklist = {"185.220.101.1", "45.33.32.156", "91.240.118.172"}

cache = {}


def ip_valido(ip):
    partes = ip.split(".")
    if len(partes) != 4:
        return False
    for parte in partes:
        if not parte.isdigit():
            return False
        if int(parte) > 255:
            return False
    return True


def eh_privado(ip):
    # Privados (RFC 1918): 10.x.x.x, 172.16-31.x.x, 192.168.x.x (+ 127.x.x.x loopback)
    partes = ip.split(".")
    primeiro = int(partes[0])
    segundo = int(partes[1])

    if primeiro == 10:
        return True
    if primeiro == 172 and segundo >= 16 and segundo <= 31:
        return True
    if primeiro == 192 and segundo == 168:
        return True
    if primeiro == 127:
        return True
    return False


def consultar_ipinfo(ip, tentativas=3):
    # Faz a consulta HTTP. Em caso de 429, espera 1s, 2s, 4s... (backoff exponencial)
    url = "https://ipinfo.io/" + ip + "/json"

    for i in range(tentativas):
        try:
            resposta = requests.get(url, timeout=10)
        except requests.exceptions.Timeout:
            print("   Erro: timeout ao consultar", ip)
            return None
        except requests.exceptions.ConnectionError:
            print("   Erro: sem conexão ao consultar", ip)
            return None
        except requests.exceptions.RequestException:
            print("   Erro inesperado ao consultar", ip)
            return None

        if resposta.status_code == 429:
            espera = 2 ** i
            print("   Rate limit; aguardando", espera, "s...")
            time.sleep(espera)
            continue

        if resposta.status_code == 200:
            try:
                return resposta.json()
            except ValueError:
                return None

        print("   Erro da API. Status:", resposta.status_code)
        return None

    print("   Desisti de", ip, "depois de", tentativas, "tentativas (rate limit)")
    return None


def descrever(dados):
    # Monta "Cidade / País / Organização"
    cidade = dados.get("city", "?")
    pais = dados.get("country", "?")
    org = dados.get("org", "?")

    # O ipinfo manda a org assim: "AS15169 Google LLC" -> tira o "AS15169"
    if org.startswith("AS") and " " in org:
        org = org.split(" ", 1)[1]

    return cidade + " / " + pais + " / " + org


consultas_http = 0
cache_hits = 0
internos = 0
falhas = 0
invalidos = 0
relatorio = []

for ip in ips:
    if not ip_valido(ip):
        print(ip.ljust(15), "-> IP inválido")
        invalidos = invalidos + 1
        relatorio.append({"ip": ip, "resultado": "invalido"})
        continue

    if eh_privado(ip):
        print(ip.ljust(15), "-> Rede Interna (não consultado)")
        internos = internos + 1
        relatorio.append({"ip": ip, "resultado": "interno"})
        continue

    # IP externo: vê o cache antes de chamar a API
    if ip in cache:
        descricao = cache[ip]
        print(ip.ljust(15), "-> [CACHE]", descricao, "- sem nova chamada HTTP")
        cache_hits = cache_hits + 1
        relatorio.append({"ip": ip, "resultado": "externo", "descricao": descricao, "origem": "cache"})
        continue

    consultas_http = consultas_http + 1
    dados = consultar_ipinfo(ip)

    if dados is None:
        print(ip.ljust(15), "-> falha na consulta")
        falhas = falhas + 1
        relatorio.append({"ip": ip, "resultado": "falha"})
        continue

    descricao = descrever(dados)
    cache[ip] = descricao      # só guarda no cache quando deu certo

    tipo = "EXTERNO"
    suspeito = False
    if ip in blacklist:
        tipo = "EXTERNO, suspeito"
        suspeito = True

    print(ip.ljust(15), "->", descricao, "(" + tipo + ")")
    relatorio.append({"ip": ip, "resultado": "externo", "descricao": descricao, "suspeito": suspeito, "origem": "http"})

print("")
print("=== Resumo === Consultas HTTP:", consultas_http, "| Cache hits:", cache_hits, "| Internos:", internos)
if falhas > 0 or invalidos > 0:
    print("Falhas:", falhas, "| Inválidos:", invalidos)

# Relatório consolidado em JSON
try:
    arquivo = open("relatorio_ips.json", "w", encoding="utf-8")
    json.dump(relatorio, arquivo, indent=4, ensure_ascii=False)
    arquivo.close()
    print("Relatório salvo em relatorio_ips.json")
except OSError:
    print("Erro: não foi possível salvar o relatório")
