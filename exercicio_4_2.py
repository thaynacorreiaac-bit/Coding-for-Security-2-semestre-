# Exercício 4.2 - Detecção de acessos anômalos (Isolation Forest)
import numpy as np
from sklearn.ensemble import IsolationForest

# [hora_do_dia, tentativas_login, bytes_baixados]
acessos = np.array([
    [9, 1, 200], [10, 1, 500], [14, 2, 300], [11, 1, 250], [16, 1, 400],
    [3, 40, 900000],   # madrugada, muitas tentativas, download enorme
    [10, 1, 350], [15, 2, 280],
    [2, 55, 800000],   # outra anomalia
])

# contamination = proporção estimada de anomalias
detector = IsolationForest(contamination=0.25, random_state=42)
resultados = detector.fit_predict(acessos)   # 1 = normal, -1 = anomalia

for i in range(len(acessos)):
    amostra = "[" + str(acessos[i][0]) + ", " + str(acessos[i][1]) + ", " + str(acessos[i][2]) + "]"
    if resultados[i] == -1:
        print("Amostra", i, ":", amostra, "-> ANOMALIA")
    else:
        print("Amostra", i, ":", amostra, "-> Normal")
