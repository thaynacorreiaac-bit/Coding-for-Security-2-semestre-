# Exercício 10.2 - Explorador da API do GitHub com menu
# API pública sem token: limite de 60 requisições por hora
import json
import requests

API = "https://api.github.com"
MAX_PAGINAS = 10      # trava de segurança: no máx. 10 páginas x 100 repos
MOSTRAR = 20          # quantos repos aparecem na tela

usuario_atual = ""
perfil = {}
repos = []
detalhes = []


def nome_seguro(texto, extras):
    # Só aceita letras, números e os caracteres extras (evita montar URL estranha)
    if texto == "":
        return False
    for letra in texto:
        if not letra.isalnum() and letra not in extras:
            return False
    return True


def pedir(url, params=None):
    # Faz o GET tratando os erros. Retorna o JSON, ou None se algo deu errado
    try:
        resposta = requests.get(
            url, params=params, timeout=15,
            headers={"Accept": "application/vnd.github+json"}
        )
    except requests.exceptions.Timeout:
        print("Erro: a API demorou demais pra responder (timeout)")
        return None
    except requests.exceptions.ConnectionError:
        print("Erro: não foi possível conectar ao GitHub. Confira sua internet")
        return None
    except requests.exceptions.RequestException:
        print("Erro inesperado na requisição")
        return None

    if resposta.status_code == 403 or resposta.status_code == 429:
        print("Limite de requisições da API atingido (são 60 por hora sem token). Tente mais tarde")
        return None

    if resposta.status_code == 404:
        print("Não encontrado")
        return None

    if resposta.status_code != 200:
        print("Erro da API. Status:", resposta.status_code)
        return None

    try:
        return resposta.json()
    except ValueError:
        print("Erro: resposta fora do formato JSON")
        return None


def buscar_usuario():
    global usuario_atual, perfil, repos, detalhes

    usuario = input("Usuário do GitHub: ").strip()
    if not nome_seguro(usuario, "-"):
        print("Nome de usuário inválido")
        return

    dados = pedir(API + "/users/" + usuario)
    if dados is None:
        return

    usuario_atual = dados["login"]
    perfil = {
        "login": dados["login"],
        "nome": dados.get("name"),
        "repos_publicos": dados["public_repos"],
        "seguidores": dados["followers"],
        "url": dados["html_url"],
    }
    repos = []        # zera os dados do usuário anterior
    detalhes = []

    nome = perfil["nome"]
    if nome is None:
        nome = "(sem nome)"

    print("=== Perfil:", usuario_atual, "===")
    print("Nome:", nome, "| Repos públicos:", perfil["repos_publicos"], "| Seguidores:", perfil["seguidores"])


def ordenar_por_estrelas(lista):
    # Ordenação simples (bubble sort): mais estrelas primeiro
    n = len(lista)
    for i in range(n):
        for j in range(n - i - 1):
            if lista[j]["estrelas"] < lista[j + 1]["estrelas"]:
                troca = lista[j]
                lista[j] = lista[j + 1]
                lista[j + 1] = troca
    return lista


def listar_repos():
    global repos

    if usuario_atual == "":
        print("Busque um usuário primeiro (opção 1)")
        return

    # Paginação: pede página por página até vir uma lista vazia
    todos = []
    pagina = 1
    while pagina <= MAX_PAGINAS:
        lote = pedir(API + "/users/" + usuario_atual + "/repos", {"page": pagina, "per_page": 100})
        if lote is None:
            if len(todos) == 0:
                return
            print("Aviso: a listagem foi interrompida, os resultados abaixo estão incompletos")
            break

        if len(lote) == 0:
            break

        for repo in lote:
            linguagem = repo["language"]
            if linguagem is None:
                linguagem = "-"
            todos.append({
                "nome": repo["name"],
                "estrelas": repo["stargazers_count"],
                "linguagem": linguagem,
                "url": repo["html_url"],
            })
        pagina = pagina + 1

    repos = ordenar_por_estrelas(todos)

    print("=== Repositórios ===")
    numero = 1
    for repo in repos:
        if numero > MOSTRAR:
            print("... e mais", len(repos) - MOSTRAR, "repositórios (todos vão pro JSON)")
            break
        print(str(numero) + ".", repo["nome"].ljust(20), "★", repo["estrelas"], " (" + repo["linguagem"] + ")")
        numero = numero + 1

    if len(repos) == 0:
        print("Esse usuário não tem repositórios públicos")


def detalhar_repo():
    if usuario_atual == "":
        print("Busque um usuário primeiro (opção 1)")
        return

    nome_repo = input("Nome do repositório: ").strip()
    if not nome_seguro(nome_repo, "-_."):
        print("Nome de repositório inválido")
        return

    dados = pedir(API + "/repos/" + usuario_atual + "/" + nome_repo)
    if dados is None:
        return

    licenca = "-"
    if dados["license"] is not None:
        licenca = dados["license"]["name"]

    descricao = dados["description"]
    if descricao is None:
        descricao = "(sem descrição)"

    linguagem = dados["language"]
    if linguagem is None:
        linguagem = "-"

    print("=== Repositório:", dados["full_name"], "===")
    print("Descrição:", descricao)
    print("Linguagem:", linguagem)
    print("Estrelas:", dados["stargazers_count"], "| Forks:", dados["forks_count"], "| Issues abertas:", dados["open_issues_count"])
    print("Licença:", licenca)
    print("Última atualização:", dados["updated_at"])
    print("URL:", dados["html_url"])

    detalhes.append({
        "nome": dados["full_name"],
        "descricao": dados["description"],
        "linguagem": dados["language"],
        "estrelas": dados["stargazers_count"],
        "forks": dados["forks_count"],
        "issues_abertas": dados["open_issues_count"],
        "licenca": licenca,
        "atualizado_em": dados["updated_at"],
        "url": dados["html_url"],
    })


def salvar_json():
    if usuario_atual == "":
        print("Busque um usuário primeiro (opção 1)")
        return

    dados = {"perfil": perfil, "repositorios": repos, "detalhes": detalhes}
    nome_arquivo = "github_" + usuario_atual + ".json"

    try:
        arquivo = open(nome_arquivo, "w", encoding="utf-8")
        json.dump(dados, arquivo, indent=4, ensure_ascii=False)
        arquivo.close()
        print("Resultados salvos em", nome_arquivo)
    except OSError:
        print("Erro: não foi possível salvar o arquivo")


while True:
    print("")
    print("===== EXPLORADOR GITHUB =====")
    print("[1] Buscar usuário")
    print("[2] Listar repositórios")
    print("[3] Detalhar um repositório")
    print("[4] Salvar resultados em JSON")
    print("[5] Sair")
    opcao = input("Escolha: ")

    if opcao == "1":
        buscar_usuario()
    elif opcao == "2":
        listar_repos()
    elif opcao == "3":
        detalhar_repo()
    elif opcao == "4":
        salvar_json()
    elif opcao == "5":
        print("Saindo...")
        break
    else:
        print("Opção inválida!")
