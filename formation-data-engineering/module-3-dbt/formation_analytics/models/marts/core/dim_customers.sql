{{
    config(
        materialized='table',
        tags=['marts', 'core', 'dimension']
    )
}}

-- ============================================================================
-- DIMENSION TABLE: CUSTOMERS
-- Table dimension client enrichie avec toutes les métriques
-- ============================================================================

WITH customer_summary AS (
    SELECT * FROM {{ ref('int_customer_order_summary') }}
),

customer_categories AS (
    SELECT 
        customer_id,
        STRING_AGG(DISTINCT product_category, ', ' ORDER BY product_category) AS preferred_categories,
        MODE() WITHIN GROUP (ORDER BY product_category) AS top_category,
        MODE() WITHIN GROUP (ORDER BY brand) AS favorite_brand
    FROM {{ ref('int_order_items_enriched') }}
    WHERE is_completed = TRUE
    GROUP BY customer_id
),

web_behavior AS (
    SELECT 
        customer_id,
        COUNT(DISTINCT session_id) AS total_sessions,
        COUNT(*) AS total_events,
        COUNT(DISTINCT DATE(event_timestamp)) AS active_days,
        MAX(event_timestamp) AS last_activity_date,
        COUNT(CASE WHEN event_type = 'add_to_cart' THEN 1 END) AS cart_additions,
        COUNT(CASE WHEN event_type = 'checkout' THEN 1 END) AS checkout_views,
        COUNT(DISTINCT device_type) AS devices_used,
        MODE() WITHIN GROUP (ORDER BY device_type) AS primary_device
    FROM {{ source('raw', 'web_events') }}
    WHERE customer_id IS NOT NULL
    GROUP BY customer_id
),

final AS (
    SELECT
        -- Identifiants
        cs.customer_id,
        cs.customer_full_name,
        cs.customer_email,
        
        -- Localisation
        cs.customer_location,
        cs.country_code,
        
        -- Segmentation
        cs.customer_tenure_segment,
        cs.customer_segment,
        cs.rfm_score,
        cs.purchase_frequency_tier,
        
        -- Métriques de commandes
        cs.total_orders,
        cs.cancelled_orders,
        cs.refunded_orders,
        cs.lifetime_value,
        cs.average_order_value,
        cs.min_order_value,
        cs.max_order_value,
        
        -- Dates importantes
        cs.first_order_date,
        cs.last_order_date,
        cs.days_since_last_order,
        cs.days_since_registration,
        cs.avg_days_between_orders,
        
        -- Scores RFM
        cs.recency_score,
        cs.frequency_score,
        cs.monetary_score,
        
        -- Produits
        cs.unique_products_purchased,
        cs.unique_categories_purchased,
        cs.unique_brands_purchased,
        cs.avg_items_per_order,
        cs.total_items_purchased,
        cc.preferred_categories,
        cc.top_category,
        cc.favorite_brand,
        
        -- Comportement promotionnel
        cs.avg_discount_percentage,
        cs.discount_usage_rate,
        
        -- Comportement web
        COALESCE(wb.total_sessions, 0) AS web_sessions,
        COALESCE(wb.total_events, 0) AS web_events,
        COALESCE(wb.active_days, 0) AS web_active_days,
        wb.last_activity_date AS last_web_activity,
        COALESCE(wb.cart_additions, 0) AS cart_additions,
        COALESCE(wb.checkout_views, 0) AS checkout_views,
        wb.primary_device,
        
        -- Taux de conversion
        CASE 
            WHEN wb.checkout_views > 0 
            THEN cs.total_orders::FLOAT / wb.checkout_views * 100
            ELSE 0
        END AS conversion_rate,
        
        -- Indicateurs
        cs.is_at_risk,
        CASE 
            WHEN cs.lifetime_value > 1000 THEN TRUE
            ELSE FALSE
        END AS is_vip,
        
        CASE 
            WHEN cs.days_since_last_order <= 30 THEN 'Active'
            WHEN cs.days_since_last_order <= 90 THEN 'Lapsing'
            WHEN cs.days_since_last_order <= 180 THEN 'Dormant'
            ELSE 'Lost'
        END AS activity_status,
        
        -- Customer Lifetime Value prédit (simplifié)
        CASE 
            WHEN cs.total_orders > 0 
            THEN cs.lifetime_value * (1 + (cs.frequency_score * 0.2))
            ELSE 0
        END AS predicted_ltv,
        
        -- Score de valeur client (0-100)
        GREATEST(0, LEAST(100,
            (cs.recency_score * 15) + 
            (cs.frequency_score * 15) + 
            (cs.monetary_score * 20) +
            (CASE WHEN cs.is_at_risk THEN -20 ELSE 0 END) +
            (CASE WHEN cs.discount_usage_rate < 50 THEN 10 ELSE 0 END) +
            (CASE WHEN wb.primary_device IS NOT NULL THEN 10 ELSE 0 END)
        )) AS customer_value_score,
        
        -- Métadonnées
        CURRENT_TIMESTAMP AS _dbt_updated_at
        
    FROM customer_summary cs
    LEFT JOIN customer_categories cc ON cs.customer_id = cc.customer_id
    LEFT JOIN web_behavior wb ON cs.customer_id = wb.customer_id
)

SELECT * FROM final