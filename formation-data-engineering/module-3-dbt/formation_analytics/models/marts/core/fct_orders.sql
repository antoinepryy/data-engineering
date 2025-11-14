{{
    config(
        materialized='incremental',
        unique_key='order_id',
        on_schema_change='fail',
        tags=['marts', 'core', 'incremental']
    )
}}

-- ============================================================================
-- FACT TABLE: ORDERS
-- Table de faits centrale pour l'analyse des commandes
-- Mode incrémental pour optimiser les performances
-- ============================================================================

WITH orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
    
    {% if is_incremental() %}
        -- En mode incrémental, on ne traite que les nouvelles commandes
        WHERE order_date > (SELECT MAX(order_date) FROM {{ this }})
    {% endif %}
),

order_items AS (
    SELECT 
        order_id,
        COUNT(DISTINCT product_id) AS unique_products,
        SUM(quantity) AS total_items,
        SUM(line_subtotal) AS subtotal_amount,
        SUM(discount_amount) AS total_discount,
        SUM(tax_amount) AS total_tax,
        SUM(line_total_with_tax) AS total_amount_with_tax,
        SUM(line_cost) AS total_cost,
        SUM(line_margin) AS total_margin,
        AVG(line_margin_percentage) AS avg_margin_percentage,
        MAX(line_total_with_tax) AS max_line_amount,
        STRING_AGG(DISTINCT product_category, ', ') AS product_categories
    FROM {{ ref('int_order_items_enriched') }}
    
    {% if is_incremental() %}
        WHERE order_id IN (SELECT order_id FROM orders)
    {% endif %}
    
    GROUP BY order_id
),

payments AS (
    SELECT 
        order_id,
        COUNT(*) AS payment_count,
        MAX(payment_date) AS last_payment_date,
        STRING_AGG(DISTINCT payment_method, ', ') AS payment_methods,
        MAX(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS has_successful_payment,
        MAX(CASE WHEN status = 'refunded' THEN 1 ELSE 0 END) AS has_refund
    FROM {{ source('raw', 'payments') }}
    
    {% if is_incremental() %}
        WHERE order_id IN (SELECT order_id FROM orders)
    {% endif %}
    
    GROUP BY order_id
),

final AS (
    SELECT
        -- Dimensions
        o.order_id,
        o.customer_id,
        o.order_date,
        o.order_date_only,
        o.order_year,
        o.order_quarter,
        o.order_month,
        o.order_week,
        o.order_day_of_week,
        o.order_day_name,
        o.is_weekend_order,
        
        -- Statut et type
        o.order_status,
        o.is_completed,
        o.is_cancelled,
        o.is_refunded,
        o.is_in_progress,
        o.order_size_category,
        o.shipping_type,
        
        -- Métriques de la commande
        COALESCE(oi.unique_products, 0) AS unique_products,
        COALESCE(oi.total_items, 0) AS total_items,
        COALESCE(oi.subtotal_amount, 0) AS subtotal_amount,
        COALESCE(oi.total_discount, 0) AS discount_amount,
        COALESCE(oi.total_tax, 0) AS tax_amount,
        COALESCE(o.order_total_amount, 0) AS order_total_amount,
        COALESCE(oi.total_cost, 0) AS total_cost,
        COALESCE(oi.total_margin, 0) AS gross_margin,
        COALESCE(oi.avg_margin_percentage, 0) AS margin_percentage,
        
        -- Métriques de paiement
        COALESCE(p.payment_count, 0) AS payment_count,
        p.last_payment_date,
        p.payment_methods,
        COALESCE(p.has_successful_payment, 0) AS has_successful_payment,
        COALESCE(p.has_refund, 0) AS has_refund,
        
        -- Livraison
        o.shipping_city,
        o.shipping_country,
        
        -- Catégories produits
        oi.product_categories,
        
        -- Métriques calculées
        CASE 
            WHEN oi.subtotal_amount > 0 
            THEN (oi.total_discount / oi.subtotal_amount) * 100
            ELSE 0
        END AS discount_rate,
        
        CASE 
            WHEN oi.total_items > 0 
            THEN o.order_total_amount / oi.total_items
            ELSE 0
        END AS average_item_price,
        
        -- Indicateurs de performance
        CASE 
            WHEN oi.avg_margin_percentage >= 40 THEN 'High'
            WHEN oi.avg_margin_percentage >= 25 THEN 'Medium'
            ELSE 'Low'
        END AS profitability_tier,
        
        CASE 
            WHEN o.is_completed = TRUE 
            AND p.has_successful_payment = 1 
            AND p.has_refund = 0
            THEN TRUE
            ELSE FALSE
        END AS is_successful_order,
        
        -- Métadonnées
        o.days_since_order,
        CURRENT_TIMESTAMP AS _dbt_updated_at
        
    FROM orders o
    LEFT JOIN order_items oi ON o.order_id = oi.order_id
    LEFT JOIN payments p ON o.order_id = p.order_id
)

SELECT * FROM final