-- Consulta de tratamento e engenharia de features para usuários

SELECT 
  order_id,
  user_id,
  status,
  created_at AS order_timestamp,
  EXTRACT(HOUR FROM created_at) AS order_hour,
  
  -- Formato de hora cheia para facilitar a análise de padrões de compra por hora
  FORMAT_TIMESTAMP('%Hhs', created_at) AS order_hour_formatted,
  
  -- Divisão neutra dos dois blocos de 12 horas
  CASE 
    WHEN EXTRACT(HOUR FROM created_at) >= 18 OR EXTRACT(HOUR FROM created_at) <= 5 THEN 'Noite/Madrugada (18h-5h)'
    ELSE 'Manhã/Tarde (5h-18h)'
  END AS turno_pedido,
  
  -- Engenharia de features: Mapeando os cancelamentos e devoluções do dia inteiro
  CASE WHEN status = 'Cancelled' THEN 1 ELSE 0 END AS is_cancelled,
  CASE WHEN status = 'Returned' THEN 1 ELSE 0 END AS is_returned,
  
  num_of_item AS total_items_purchased,
  (num_of_item * 45.5) AS total_order_value
FROM `bigquery-public-data.thelook_ecommerce.orders`
WHERE user_id IN (SELECT user_id FROM `my-new-project-461718.Projeto_anti_fraude.refined_users`)