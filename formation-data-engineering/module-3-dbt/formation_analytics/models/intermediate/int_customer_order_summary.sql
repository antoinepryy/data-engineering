{{
    config(
        materialized='view',
        tags=['intermediate', 'daily']
    )
}}

-- ============================================================================
-- INTERMEDIATE: CUSTOMER ORDER SUMMARY
-- Agrégation des commandes par client avec métriques RFM
-- ============================================================================

WITH customers AS (
    SELECT * FROM {{ ref('stg_customers') }}
),

orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
    WHERE is_completed = TRUE  -- On ne compte que les commandes complétées
),

order_items AS (
    SELECT * FROM {{ ref('int_order_items_enriched') }}
    WHERE is_completed = TRUE
),

customer_orders AS (
    SELECT
        c.customer_id,
        c.customer_full_name,
        c.customer_email,
        c.customer_location,
        c.country_code,
        c.customer_tenure_segment,
        c.days_since_registration,
        
        -- Métriques de commandes
        COUNT(DISTINCT o.order_id) AS total_orders,
        COUNT(DISTINCT CASE WHEN o.is_cancelled THEN o.order_id END) AS cancelled_orders,
        COUNT(DISTINCT CASE WHEN o.is_refunded THEN o.order_id END) AS refunded_orders,
        
        -- Montants
        COALESCE(SUM(o.order_total_amount), 0) AS lifetime_value,
        COALESCE(AVG(o.order_total_amount), 0) AS average_order_value,
        COALESCE(MIN(o.order_total_amount), 0) AS min_order_value,
        COALESCE(MAX(o.order_total_amount), 0) AS max_order_value,
        
        -- Dates
        MIN(o.order_date) AS first_order_date,
        MAX(o.order_date) AS last_order_date,
        
        -- RFM Metrics
        DATE_PART('day', CURRENT_DATE - MAX(o.order_date)::date) AS days_since_last_order,
        
        -- Fréquence d'achat
        CASE 
            WHEN COUNT(DISTINCT o.order_id) > 1 
            THEN DATE_PART('day', MAX(o.order_date)::date - MIN(o.order_date)::date) / NULLIF(COUNT(DISTINCT o.order_id) - 1, 0)
            ELSE NULL
        END AS avg_days_between_orders
        
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY 
        c.customer_id,
        c.customer_full_name,
        c.customer_email,
        c.customer_location,
        c.country_code,
        c.customer_tenure_segment,
        c.days_since_registration
),

customer_products AS (
    SELECT
        customer_id,
        
        -- Produits préférés
        COUNT(DISTINCT product_id) AS unique_products_purchased,
        COUNT(DISTINCT product_category) AS unique_categories_purchased,
        COUNT(DISTINCT brand) AS unique_brands_purchased,
        
        -- Comportement d'achat
        AVG(quantity) AS avg_items_per_order,
        SUM(quantity) AS total_items_purchased,
        
        -- Utilisation des promotions
        AVG(discount_percentage) AS avg_discount_percentage,
        SUM(CASE WHEN has_discount THEN 1 ELSE 0 END)::FLOAT / NULLIF(COUNT(*), 0) * 100 AS discount_usage_rate
        
    FROM order_items
    GROUP BY customer_id
),

rfm_scores AS (
    SELECT
        co.*,
        cp.unique_products_purchased,
        cp.unique_categories_purchased,
        cp.unique_brands_purchased,
        cp.avg_items_per_order,
        cp.total_items_purchased,
        cp.avg_discount_percentage,
        cp.discount_usage_rate,
        
        -- Score de Récence (R)
        CASE
            WHEN days_since_last_order <= 30 THEN 5
            WHEN days_since_last_order <= 60 THEN 4
            WHEN days_since_last_order <= 90 THEN 3
            WHEN days_since_last_order <= 180 THEN 2
            ELSE 1
        END AS recency_score,
        
        -- Score de Fréquence (F)
        CASE
            WHEN total_orders >= 10 THEN 5
            WHEN total_orders >= 5 THEN 4
            WHEN total_orders >= 3 THEN 3
            WHEN total_orders >= 2 THEN 2
            ELSE 1
        END AS frequency_score,
        
        -- Score Monétaire (M)
        CASE
            WHEN lifetime_value >= 5000 THEN 5
            WHEN lifetime_value >= 2000 THEN 4
            WHEN lifetime_value >= 1000 THEN 3
            WHEN lifetime_value >= 500 THEN 2
            ELSE 1
        END AS monetary_score
        
    FROM customer_orders co
    LEFT JOIN customer_products cp ON co.customer_id = cp.customer_id
),

customer_segments AS (
    SELECT
        *,
        
        -- Score RFM combiné
        CONCAT(recency_score, frequency_score, monetary_score) AS rfm_score,
        
        -- Segmentation client
        CASE
            WHEN recency_score >= 4 AND frequency_score >= 4 AND monetary_score >= 4 THEN 'Champions'
            WHEN recency_score >= 3 AND frequency_score >= 3 AND monetary_score >= 4 THEN 'Loyal Customers'
            WHEN recency_score >= 3 AND frequency_score <= 2 AND monetary_score >= 3 THEN 'Potential Loyalists'
            WHEN recency_score >= 4 AND frequency_score <= 2 THEN 'New Customers'
            WHEN recency_score >= 3 AND frequency_score >= 3 AND monetary_score <= 3 THEN 'Promising'
            WHEN recency_score <= 2 AND frequency_score >= 3 THEN 'Need Attention'
            WHEN recency_score <= 2 AND frequency_score <= 2 AND monetary_score >= 3 THEN 'About to Sleep'
            WHEN recency_score <= 2 AND frequency_score >= 4 THEN 'At Risk'
            WHEN recency_score <= 1 AND frequency_score >= 3 AND monetary_score >= 3 THEN 'Cant Lose Them'
            WHEN recency_score <= 2 AND frequency_score <= 2 AND monetary_score <= 2 THEN 'Hibernating'
            ELSE 'Lost'
        END AS customer_segment,
        
        -- Indicateurs de risque
        CASE 
            WHEN days_since_last_order > COALESCE(avg_days_between_orders * 2, 90) THEN TRUE
            ELSE FALSE
        END AS is_at_risk,
        
        CASE
            WHEN total_orders = 1 THEN 'One-time'
            WHEN total_orders = 2 THEN 'Returning'
            WHEN total_orders >= 3 THEN 'Frequent'
            ELSE 'No Purchase'
        END AS purchase_frequency_tier
        
    FROM rfm_scores
)

SELECT * FROM customer_segments