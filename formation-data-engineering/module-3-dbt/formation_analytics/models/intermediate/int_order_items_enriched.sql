{{
    config(
        materialized='view',
        tags=['intermediate', 'daily']
    )
}}

-- ============================================================================
-- INTERMEDIATE: ORDER ITEMS ENRICHED
-- Jointure des lignes de commande avec produits et commandes
-- ============================================================================

WITH order_items AS (
    SELECT * FROM {{ source('raw', 'order_items') }}
),

orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
),

products AS (
    SELECT * FROM {{ ref('stg_products') }}
),

joined AS (
    SELECT
        -- Identifiants
        oi.order_item_id,
        oi.order_id,
        oi.product_id,
        o.customer_id,
        
        -- Informations commande
        o.order_date,
        o.order_status,
        o.is_completed,
        o.payment_method,
        o.order_size_category,
        o.order_year,
        o.order_month,
        o.order_day_name,
        o.is_weekend_order,
        
        -- Informations produit
        p.product_name,
        p.product_category,
        p.product_category_group,
        p.brand,
        p.price_tier,
        p.margin_tier,
        p.abc_classification,
        
        -- Quantités et prix
        oi.quantity,
        oi.unit_price,
        p.selling_price AS current_price,
        p.product_cost,
        
        -- Montants ligne
        oi.discount_amount,
        oi.tax_amount,
        oi.total_amount AS line_total_with_tax,
        
        -- Calculs dérivés
        oi.quantity * oi.unit_price AS line_subtotal,
        oi.quantity * p.product_cost AS line_cost,
        (oi.quantity * oi.unit_price) - (oi.quantity * p.product_cost) AS line_margin,
        
        -- Taux et ratios
        CASE 
            WHEN oi.unit_price > 0 
            THEN oi.discount_amount / (oi.quantity * oi.unit_price) * 100
            ELSE 0
        END AS discount_percentage,
        
        CASE 
            WHEN oi.unit_price > 0
            THEN ((oi.unit_price - p.product_cost) / oi.unit_price) * 100
            ELSE 0
        END AS line_margin_percentage,
        
        -- Indicateurs
        CASE 
            WHEN oi.discount_amount > 0 THEN TRUE
            ELSE FALSE
        END AS has_discount,
        
        CASE 
            WHEN oi.unit_price < p.selling_price THEN TRUE
            ELSE FALSE
        END AS is_discounted_price
        
    FROM order_items oi
    LEFT JOIN orders o ON oi.order_id = o.order_id
    LEFT JOIN products p ON oi.product_id = p.product_id
),

with_rankings AS (
    SELECT
        *,
        
        -- Rankings par commande
        ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY line_total_with_tax DESC) AS line_rank_by_amount,
        ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY quantity DESC) AS line_rank_by_quantity,
        
        -- Part du total de la commande
        SUM(line_total_with_tax) OVER (PARTITION BY order_id) AS order_total,
        line_total_with_tax / NULLIF(SUM(line_total_with_tax) OVER (PARTITION BY order_id), 0) * 100 AS percentage_of_order,
        
        -- Statistiques produit
        AVG(unit_price) OVER (PARTITION BY product_id) AS avg_selling_price_by_product,
        COUNT(*) OVER (PARTITION BY product_id) AS times_ordered,
        SUM(quantity) OVER (PARTITION BY product_id) AS total_quantity_sold
        
    FROM joined
)

SELECT * FROM with_rankings