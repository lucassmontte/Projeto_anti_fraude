-- Gera a view `refined_users` no BigQuery, usada como base do pipeline em Python
-- Inclui: limpeza cadastral, agregação de comportamento de compra e criação da flag is_bad_payer

WITH user_demographics AS (
  -- Etapa 1: Limpeza e padronização dos dados cadastrais dos clientes
  SELECT 
    id AS user_id,
    age,
    gender,
    state,
    country,
    created_at AS account_created_at
  FROM `bigquery-public-data.thelook_ecommerce.users`
  WHERE country = 'United States'
),

user_order_aggregates AS (
  -- Agregação do comportamento de compra e histórico financeiro
  SELECT 
    user_id,
    COUNT(order_id) AS total_orders,
    -- Quantidade de pedidos que não foram pagos ou foram cancelados (sinalizador de risco)
    COUNT(CASE WHEN status = 'Cancelled' THEN 1 END) AS total_cancelled_orders,
    COUNT(CASE WHEN status = 'Returned' THEN 1 END) AS total_returned_orders,
    -- Cálculo de ticket médio e volumetria financeira
    ROUND(SUM(num_of_item), 2) AS total_items_purchased,
    -- há quanto tempo o cliente não compra
    MAX(created_at) AS last_order_date
  FROM `bigquery-public-data.thelook_ecommerce.orders`
  GROUP BY user_id
)

-- Etapa 3: Consolidação final e criação das flags de Risco (Feature Engineering inicial)
SELECT 
  u.user_id,
  u.age,
  u.gender,
  u.state,
  u.account_created_at,
  COALESCE(o.total_orders, 0) AS total_orders,
  COALESCE(o.total_cancelled_orders, 0) AS total_cancelled_orders,
  COALESCE(o.total_returned_orders, 0) AS total_returned_orders,
  COALESCE(o.total_items_purchased, 0) AS total_items_purchased,
  o.last_order_date,
  
  -- Definição da variável alvo (Rótulo de Risco/Inadimplência)
  -- Regra: Se o cliente tem mais de 50% dos pedidos cancelados/devolvidos tendo feito pelo menos 2 pedidos
  CASE 
    WHEN o.total_orders >= 2 AND ((o.total_cancelled_orders + o.total_returned_orders) / o.total_orders) >= 0.5 THEN 1
    ELSE 0
  END AS is_bad_payer

FROM user_demographics u
LEFT JOIN user_order_aggregates o ON u.user_id = o.user_id;