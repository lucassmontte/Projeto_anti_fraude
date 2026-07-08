import os
import pandas as pd
from google.cloud import bigquery


# CONFIGURAÇÃO DE CREDENCIAIS E AMBIENTE GCP

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"

PROJECT_ID = "my-new-project-461718"
DATASET_ID = "Projeto_anti_fraude"

client = bigquery.Client(project=PROJECT_ID)

print(" Inicializando Pipeline de Dados Imparcial (GCP)")

try:
    
    # 1. EXTRAÇÃO DAS COLUNAS DO BIGQUERY
    
    print(" Carregando tabelas refinadas com flags de cancelamento e devolucao...")
    query_users = f"SELECT user_id, age, gender, state, account_created_at, is_bad_payer FROM `{PROJECT_ID}.{DATASET_ID}.refined_users`"
    df_users = client.query(query_users).to_dataframe()

    query_orders = f"SELECT order_id, user_id, order_timestamp, order_hour, order_hour_formatted, turno_pedido, is_cancelled, is_returned, total_order_value FROM `{PROJECT_ID}.{DATASET_ID}.refined_orders`"
    df_orders = client.query(query_orders).to_dataframe()

    
    # 2. FEATURE ENGINEERING - AGRUPADO POR USUÁRIO
   
    print(" Calculando metricas de comportamento financeiro e friccao transacional...")

    df_behavior_features = df_orders.groupby("user_id").agg(
        customer_lifetime_value=("total_order_value", "sum"),
        customer_ticket_medio=("total_order_value", "mean"),
        total_cancelled_orders=("is_cancelled", "sum"),
        total_returned_orders=("is_returned", "sum"),
        total_orders_calculated=("order_id", "count")
    ).reset_index()

    df_final_ml = pd.merge(df_users, df_behavior_features, on="user_id", how="left")

    # Tratamento de nulos para garantir a matemática dos modelos
    colunas_comportamentais = [
        "customer_lifetime_value", "customer_ticket_medio",
        "total_cancelled_orders", "total_returned_orders", "total_orders_calculated"
    ]
    df_final_ml[colunas_comportamentais] = df_final_ml[colunas_comportamentais].fillna(0)

    df_final_ml["customer_lifetime_value"] = df_final_ml["customer_lifetime_value"].round(2)
    df_final_ml["customer_ticket_medio"] = df_final_ml["customer_ticket_medio"].round(2)

    # 3. BASE COMPLEMENTAR ABERTA POR PEDIDO (PARA GRÁFICOS DO POWER BI)

    print(" Sincronizando tabelas transacionais para visoes de turno...")
    df_orders_bi = pd.merge(
        df_orders,
        df_users[["user_id", "is_bad_payer", "account_created_at"]],
        on="user_id",
        how="left"
    )
    df_orders_bi["is_bad_payer"] = df_orders_bi["is_bad_payer"].fillna(0).astype(int)

    # NOVO: tempo de conta até a compra (em dias)
    # .dt.tz_localize(None) remove timezone (UTC) para evitar erro de subtração
    # entre datas "aware" e "naive"
    df_orders_bi["order_timestamp"] = pd.to_datetime(df_orders_bi["order_timestamp"]).dt.tz_localize(None)
    df_orders_bi["account_created_at"] = pd.to_datetime(df_orders_bi["account_created_at"]).dt.tz_localize(None)

    df_orders_bi["dias_conta_ate_compra"] = (
        df_orders_bi["order_timestamp"] - df_orders_bi["account_created_at"]
    ).dt.days

    # agrupamento em faixas, já ordenado para o gráfico
    def faixa_tempo_conta(dias):
        if dias < 0:
            return "0. Inconsistente"  # compra antes da criação da conta
        elif dias <= 30:
            return "1. < 30 dias"
        elif dias <= 90:
            return "2. 30-90 dias"
        elif dias <= 365:
            return "3. 90-365 dias"
        else:
            return "4. +365 dias"

    df_orders_bi["faixa_tempo_conta"] = df_orders_bi["dias_conta_ate_compra"].apply(faixa_tempo_conta)

  
    # 4. EXPORTAÇÃO DOS DATASETS

    df_final_ml.to_csv("features_modeling.csv", index=False)
    df_orders_bi.to_csv("orders_modeling.csv", index=False)

    print("\n[SUCESSO] Pipeline concluido! Bases geradas com foco em Cancelamentos e Devolucoes.")

except Exception as e:
    print(f"\n[ERRO NO PIPELINE]: {e}")