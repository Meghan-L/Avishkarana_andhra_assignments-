-- Sample SQL queries for bank fraud detection

-- 1. Fraud rate by merchant category
SELECT merchant_category,
       COUNT(*) AS tx_count,
       SUM(is_fraud) AS fraud_count,
       ROUND(100.0 * SUM(is_fraud)/COUNT(*), 2) AS fraud_rate
FROM fact_transactions
GROUP BY merchant_category
ORDER BY fraud_rate DESC;

-- 2. High amount transactions flagged as fraud
SELECT type,
       COUNT(*) AS tx_count,
       SUM(is_fraud) AS fraud_count
FROM fact_transactions
WHERE high_amount = 1
GROUP BY type
ORDER BY fraud_count DESC;

-- 3. Customer risk segmentation
SELECT customer_risk,
       COUNT(DISTINCT customer_id) AS customers,
       SUM(is_fraud) AS fraud_tx
FROM fact_transactions
JOIN dim_customers USING (customer_id)
GROUP BY customer_risk;
