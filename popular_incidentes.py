# Popula 15 incidentes variados pra testar o exercício 7.2
# (apaga os incidentes que já existem antes de inserir)
from pymongo import MongoClient

colecao = MongoClient("mongodb://localhost:27017/").seguranca.incidentes
colecao.delete_many({})

# (titulo, severidade, status, ip_origem)
dados = [
    ("Brute force SSH", "critica", "aberto", "185.220.101.1"),
    ("Port scan na DMZ", "alta", "resolvido", "45.33.32.156"),
    ("XSS no portal", "media", "aberto", "91.240.118.172"),
    ("Malware em estação", "critica", "em_andamento", "10.0.0.45"),
    ("Tentativa de SQLi", "alta", "aberto", "103.21.244.5"),
    ("Varredura de vulnerabilidades", "baixa", "resolvido", "45.33.32.156"),
    ("Phishing para o RH", "alta", "em_andamento", "198.51.100.7"),
    ("DDoS no site", "critica", "aberto", "185.220.101.1"),
    ("Login fora do horário", "media", "resolvido", "192.168.1.77"),
    ("Exfiltração de dados", "critica", "em_andamento", "91.240.118.172"),
    ("Senha fraca em servidor", "media", "aberto", "10.0.0.12"),
    ("Brute force RDP", "alta", "aberto", "103.21.244.5"),
    ("Ransomware detectado", "critica", "resolvido", "198.51.100.7"),
    ("Scan de portas externo", "baixa", "aberto", "45.33.32.156"),
    ("Acesso indevido a pasta", "media", "em_andamento", "192.168.1.30"),
]

documentos = []
numero = 1
for item in dados:
    documentos.append({
        "titulo": item[0],
        "severidade": item[1],
        "status": item[2],
        "ip_origem": item[3],
        # um dia a mais por incidente, então o último da lista é o mais recente
        "criado_em": "2026-10-" + str(numero).zfill(2) + " 10:00:00",
    })
    numero = numero + 1

colecao.insert_many(documentos)
print("Incidentes inseridos:", len(documentos))
