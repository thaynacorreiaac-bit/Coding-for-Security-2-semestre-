# Exercício 4.3 - Avaliação honesta com matriz de confusão
from sklearn.metrics import confusion_matrix, precision_score, recall_score, f1_score, accuracy_score

y_verdadeiro = [0, 0, 0, 0, 0, 0, 0, 0, 1, 1]   # 8 normais, 2 ataques
y_previsto   = [0, 0, 0, 0, 0, 0, 0, 0, 0, 1]   # o modelo perdeu 1 ataque

matriz = confusion_matrix(y_verdadeiro, y_previsto)
precisao = precision_score(y_verdadeiro, y_previsto)
recall = recall_score(y_verdadeiro, y_previsto)
f1 = f1_score(y_verdadeiro, y_previsto)
acuracia = accuracy_score(y_verdadeiro, y_previsto)

print("Matriz de confusão:")
print(matriz)
print("[[VN FP]")
print(" [FN VP]]")
print("")
print("Verdadeiros negativos (VN):", matriz[0][0])
print("Falsos positivos (FP):", matriz[0][1])
print("Falsos negativos (FN):", matriz[1][0])
print("Verdadeiros positivos (VP):", matriz[1][1])
print("")
print("Precisão:", round(precisao, 2), "| Recall:", round(recall, 2), "| F1:", round(f1, 2), "| Acurácia:", round(acuracia, 2))
print("")
print("Interpretação:")
print("1) A acurácia de 90% parece ótima, mas ela é puxada pelos 8 casos normais, que são fáceis de acertar.")
print("2) O recall de 0.50 mostra que o modelo deixou passar 1 dos 2 ataques reais (FN = 1): metade dos ataques passou despercebida.")
print("3) Em segurança, um ataque não detectado custa muito mais que um alarme falso, então o recall importa mais que a acurácia.")
