# Exercício 4.1 - Classificador de phishing (Random Forest)
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report

# Features: [qtd_links, tem_anexo(0/1), urgencia_no_assunto(0/1), dominio_suspeito(0/1), erros_gramaticais]
X = np.array([
    [1, 0, 0, 0, 0], [0, 0, 0, 0, 1], [2, 1, 0, 0, 0], [1, 0, 0, 0, 0],
    [8, 1, 1, 1, 5], [12, 0, 1, 1, 8], [6, 1, 1, 1, 3], [10, 1, 1, 1, 6],
    [0, 0, 0, 0, 0], [15, 1, 1, 1, 9],
])
y = np.array([0, 0, 0, 0, 1, 1, 1, 1, 0, 1])   # 0 = legítimo, 1 = phishing

# Divisão treino/teste
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42)

# Treino do Random Forest
modelo = RandomForestClassifier(n_estimators=100, random_state=42)
modelo.fit(X_train, y_train)

# Avaliação no conjunto de teste
previsoes = modelo.predict(X_test)

print("Amostras de treino:", len(X_train), "| Amostras de teste:", len(X_test))
print("Acurácia:", round(accuracy_score(y_test, previsoes), 2))
print("Precisão:", round(precision_score(y_test, previsoes, zero_division=0), 2))
print("Recall:", round(recall_score(y_test, previsoes, zero_division=0), 2))
print("F1:", round(f1_score(y_test, previsoes, zero_division=0), 2))
print("")
print(classification_report(y_test, previsoes, zero_division=0))

# Teste com um caso novo
novo = [[11, 1, 1, 1, 7]]
if modelo.predict(novo)[0] == 1:
    print("Caso novo [11,1,1,1,7] -> Phishing")
else:
    print("Caso novo [11,1,1,1,7] -> Legítimo")
