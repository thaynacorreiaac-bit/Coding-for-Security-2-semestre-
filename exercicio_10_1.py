# Exercício 10.1 - Cliente para a API do NVD (CVEs)
# Endpoint: https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=CVE-2021-44228
import requests

URL_NVD = "https://services.nvd.nist.gov/rest/json/cves/2.0"


def formato_valido(cve_id):
    # Formato esperado: CVE-ANO-NUMERO (ex: CVE-2021-44228)
    partes = cve_id.split("-")
    if len(partes) != 3:
        return False
    if partes[0] != "CVE":
        return False
    if not partes[1].isdigit() or len(partes[1]) != 4:
        return False
    if not partes[2].isdigit() or len(partes[2]) < 4:
        return False
    return True


def buscar_cve(cve_id):
    # Retorna os dados da CVE, ou None se der erro / não existir
    try:
        resposta = requests.get(URL_NVD, params={"cveId": cve_id}, timeout=15)
    except requests.exceptions.Timeout:
        print("Erro: o NVD demorou demais pra responder (timeout)")
        return None
    except requests.exceptions.ConnectionError:
        print("Erro: não foi possível conectar ao NVD")
        return None
    except requests.exceptions.RequestException:
        print("Erro inesperado na requisição")
        return None

    if resposta.status_code == 404:
        print("CVE não encontrada")
        return None

    if resposta.status_code == 403 or resposta.status_code == 429:
        print("Limite de requisições do NVD atingido. Espere um pouco e tente de novo")
        return None

    if resposta.status_code != 200:
        print("Erro do NVD. Status:", resposta.status_code)
        return None

    try:
        dados = resposta.json()
    except ValueError:
        print("Erro: resposta do NVD não está em JSON")
        return None

    # O NVD responde 200 com lista vazia quando a CVE não existe
    if len(dados["vulnerabilities"]) == 0:
        print("CVE não encontrada")
        return None

    return dados["vulnerabilities"][0]["cve"]


def pegar_descricao(cve):
    # Prefere a descrição em inglês
    for item in cve["descriptions"]:
        if item["lang"] == "en":
            return item["value"]
    return cve["descriptions"][0]["value"]


def pegar_cvss(cve):
    # Tenta CVSS v3.1, depois v3.0, depois v2. Retorna (score, severidade) ou None
    metricas = cve.get("metrics", {})

    for versao in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
        if versao in metricas and len(metricas[versao]) > 0:
            escolhida = metricas[versao][0]

            # Prefere a avaliação "Primary" (a do NVD), se existir
            for metrica in metricas[versao]:
                if metrica["type"] == "Primary":
                    escolhida = metrica
                    break

            score = escolhida["cvssData"]["baseScore"]
            # No CVSS v2 a severidade fica fora do cvssData
            severidade = escolhida["cvssData"].get("baseSeverity", escolhida.get("baseSeverity", "N/D"))
            return score, severidade

    return None


def mostrar_cve(cve_id):
    cve = buscar_cve(cve_id)
    if cve is None:
        return

    print(cve["id"])

    cvss = pegar_cvss(cve)
    if cvss is None:
        print("  CVSS: não disponível (CVE ainda sem análise)")
    else:
        print("  CVSS:", cvss[0], "(" + cvss[1] + ")")

    descricao = pegar_descricao(cve)
    if len(descricao) > 300:
        descricao = descricao[:300] + "..."
    print("  Descrição:", descricao)


while True:
    print("")
    entrada = input("ID da CVE (ex: CVE-2021-44228) ou 'sair': ").strip().upper()

    if entrada == "SAIR":
        print("Saindo...")
        break

    if not formato_valido(entrada):
        print("Formato inválido. Use CVE-ANO-NUMERO, por exemplo CVE-2021-44228")
        continue

    mostrar_cve(entrada)
