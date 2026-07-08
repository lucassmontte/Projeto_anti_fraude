# 🛡️ Detecção de Risco e Inadimplência em E-commerce

Pipeline de dados + modelo preditivo para identificar padrões comportamentais de maus pagadores (`is_bad_payer`) em transações de e-commerce, com análise de comportamento de risco por turno (noite/madrugada vs. manhã/tarde).

**Stack:** Python · Pandas · Numpy · GCP (BigQuery / Cloud Storage) · Power Query M

## 📌 Contexto do Problema

Times de antifraude precisam identificar, em tempo real, quais pedidos apresentam maior risco de inadimplência ou fraude — antes da aprovação final da compra. Este projeto simula essa jornada: da origem dos dados em nuvem até um modelo capaz de pontuar o risco de cada transação.

## 🏗️ Arquitetura

GCP (BigQuery/Storage) → Extração (.csv) → Tratamento & Feature Engineering → Modelo de ML

- **Origem:** [`bigquery-public-data.thelook_ecommerce`](https://console.cloud.google.com/marketplace/product/bigquery-public-data/thelook-ecommerce) — dataset público do Google BigQuery com dados sintéticos de e-commerce (tabelas `users`, `orders`, `order_items`, `products`, entre outras), consultado via SQL e extraído para tratamento local.
- **Volume:** 28,12 mil pedidos, 22,47 mil clientes únicos e receita total de R$ 18,61 milhões no período analisado.
- **Evolução planejada:** persistir os dados tratados de volta na nuvem (Parquet no Cloud Storage ou Cloud SQL) para um pipeline produtivo.
* **Neste Projeto foi utilizado a extração em CSV, devido o parquet no Cloud ser umserviço pago.**

## 🔧 Principais Decisões Técnicas

**1. Regra cronológica de turno comercial (a decisão central do projeto)**

A ordenação padrão quebra o contexto às 00h. Para tratar o turno noite/madrugada (18h–05h) como um bloco contínuo, foi criada uma regra de reindexação:

se order_hour ≥ 18 → order_hour - 18
senão              → order_hour + 6

Isso evita que o modelo interprete a virada da meia-noite como dois períodos distintos, preservando o padrão real de comportamento de risco.

**2. Feature engineering**
Variáveis comportamentais selecionadas: cancelamento (`is_cancelled`), devolução (`is_returned`), horário do pedido, turno (`turno_pedido`), entre outras relacionadas ao comportamento de entrega.

**3. Modelagem**
Classificador supervisionado treinado para estimar a probabilidade de inadimplência/fraude por pedido, servindo de insumo para motores de decisão em tempo real (ex: acionar autenticação em duas etapas para pedidos de alto risco).

**4. Análise comparativa entre turnos**
Para testar a hipótese inicial de concentração de risco, o mesmo tratamento foi aplicado ao turno manhã/tarde (05h–18h) e os resultados foram comparados: **2.840 detratores no turno noite/madrugada** contra **2.789 no turno manhã/tarde** — uma diferença de menos de 2%. Ou seja, os dados não sustentam a hipótese de que o período noturno concentra desproporcionalmente mais risco; o comportamento de maus pagadores se mostrou praticamente equivalente entre os dois turnos. Esse resultado reforça a importância de validar hipóteses com dados antes de aplicar regras de negócio assimétricas — nem sempre a intuição inicial se confirma, e identificar isso também é parte do valor da análise.

**5. Segmentação por perfil de cliente**
Além da análise por turno, o projeto testou outras hipóteses de risco cruzando `is_bad_payer` com variáveis de perfil (idade, gênero, tempo de conta). Cada hipótese foi validada checando também o volume de amostra por grupo, para evitar interpretar ruído estatístico como padrão de negócio (ver Insights abaixo).

## 📈 Principais Insights

| Insight | Descrição |

| **Tempo de conta** | Taxa de inadimplência cai de forma consistente conforme a conta "amadurece": 22,55% (<30 dias) → 20,46% (30-90) → 18,96% (90-365) → 20,05% (+365 dias) — padrão compatível com risco elevado em contas recém-criadas |
| **Idade e gênero** | Nenhum padrão relevante identificado — variação de apenas ~1,3 p.p. entre faixas etárias, sem tendência consistente. Hipótese de risco elevado em clientes 60+ foi testada e descartada após cruzamento com tempo de conta (contas antigas nessa faixa, não novas, concentravam a leve elevação) |
| **Comparação entre turnos** | Detratores praticamente equivalentes entre noite/madrugada (2.840) e manhã/tarde (2.789) — diferença de menos de 2%, insuficiente para justificar priorização de um turno sobre o outro |
| **Picos de vulnerabilidade** | Picos cíclicos de risco acima da média, úteis para regras de step-up authentication independente do turno |
| **Conversão** | 20,02% das ordens geradas não são concluídas (79,98% concluídas) — sinal relevante para separar clientes legítimos de possíveis detratores |
| **Pico de inadimplência por valor** | O maior percentual de valor em risco por hora ocorre às 17h (23,60%) — no fim do turno manhã/tarde, não na madrugada, reforçando que o risco financeiro não está concentrado em um único turno |

## 📂 Estrutura do Repositório

```
├── sql/
│   ├── refined_users_orders.sql   # Consultas de tratamento no BigQuery
│    └── refined_orders.sql
├── src/
│   ├── eda_and_etl.py             # Pipeline com features de risco (turno, tempo de conta)
│   └── train_model.py             # Treinamento e avaliação do modelo
├── requirements.txt
└── README.md
```

## 🛠️ Tecnologias

- **Cloud:** GCP (BigQuery, Cloud Storage, SQL)
- **Linguagem:** Python, Power Query M (lógica condicional/indexação cronológica)
- **ML:** Pandas, Numpy

---

*Projeto de portfólio — Engenharia e Inteligência de Dados aplicadas a Segurança Digital, Prevenção a Fraude e Modelagem de Risco.*
