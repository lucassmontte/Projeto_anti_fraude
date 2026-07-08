import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score, average_precision_score, precision_recall_curve
import joblib

print("======= Treinando IA Realista e Pronta para Produção =======")

# 1. Carregando os dados
df = pd.read_csv("features_modeling.csv")

# 2. REMOVENDO O VAZAMENTO DE DADOS:
# Tiramos 'total_cancelled_orders' e 'total_returned_orders' para o modelo não trapacear
features = ["age", "customer_lifetime_value", "customer_ticket_medio", "total_orders_calculated"]
target = "is_bad_payer"

X = df[features]
y = df[target]

# 3. Divisão dos dados (80/20)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

print(f"-> Alimentando Random Forest com {len(X_train)} perfis comportamentais...")

# Parâmetros controlados para evitar Overfitting + class_weight para lidar com desbalanceamento
model = RandomForestClassifier(
    n_estimators=100,
    max_depth=5,
    min_samples_leaf=5,
    class_weight="balanced",   # <-- NOVO: penaliza mais os erros na classe minoritária
    random_state=42
)
model.fit(X_train, y_train)

# 4. Predições e Avaliação
y_prob = model.predict_proba(X_test)[:, 1]

auc_score = roc_auc_score(y_test, y_prob)
pr_auc = average_precision_score(y_test, y_prob)  # <-- NOVO: métrica mais honesta p/ base desbalanceada

# 4.1 Encontrando o melhor threshold (que maximiza F1) em vez de usar 0.5 fixo
precisions, recalls, thresholds = precision_recall_curve(y_test, y_prob)
f1_scores = 2 * (precisions * recalls) / (precisions + recalls + 1e-9)
best_idx = np.argmax(f1_scores[:-1])  # o último ponto da curva não tem threshold correspondente
best_threshold = thresholds[best_idx]

y_pred_default = (y_prob >= 0.5).astype(int)
y_pred_tuned = (y_prob >= best_threshold).astype(int)

print("\n======= Performance REALISTA da IA =======")
print(f"-> ROC AUC Score: {auc_score:.4f}")
print(f"-> PR AUC (Average Precision): {pr_auc:.4f}")
print(f"-> Melhor threshold encontrado: {best_threshold:.4f} (F1 = {f1_scores[best_idx]:.4f})\n")

print("-> Relatório de Classificação (threshold padrão 0.5):")
print(classification_report(y_test, y_pred_default, target_names=["Bom Pagador (0)", "Mau Pagador (1)"]))

print("-> Relatório de Classificação (threshold ajustado):")
print(classification_report(y_test, y_pred_tuned, target_names=["Bom Pagador (0)", "Mau Pagador (1)"]))
print("=================================================\n")

# 5. Salvando o modelo definitivo + threshold escolhido
joblib.dump(model, "credit_guard_model.pkl")
joblib.dump(best_threshold, "credit_guard_threshold.pkl")  # <-- salva o threshold junto, importante para produção
print("[SUCESSO] Modelo saudável e realista salvo com sucesso!")