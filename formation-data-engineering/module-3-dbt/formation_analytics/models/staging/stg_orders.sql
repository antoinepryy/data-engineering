{{
    config(
        materialized='view',
        tags=['staging', 'daily']
    )
}}

-- ============================================================================
-- STAGING: ORDERS
-- Nettoyage et enrichissement des données de commandes
-- ============================================================================

WITH source AS (
    SELECT * 
    FROM {{ source('raw', 'orders') }}
),

cleaned AS (
    SELECT
        -- Identifiants
        order_id,
        customer_id,
        
        -- Dates
        order_date,
        DATE(order_date) AS order_date_only,
        
        -- Statut normalisé
        LOWER(TRIM(status)) AS order_status,
        
        -- Montants
        total_amount AS order_total_amount,
        
        -- Méthode de paiement
        LOWER(TRIM(payment_method)) AS payment_method,
        
        -- Livraison
        TRIM(shipping_address) AS shipping_address,
        TRIM(shipping_city) AS shipping_city,
        TRIM(shipping_country) AS shipping_country,
        
        -- Métadonnées
        created_at,
        CURRENT_TIMESTAMP AS _dbt_loaded_at
        
    FROM source
),

enriched AS (
    SELECT
        *,
        
        -- Indicateurs de statut
        CASE 
            WHEN order_status = 'completed' THEN TRUE
            ELSE FALSE
        END AS is_completed,
        
        CASE 
            WHEN order_status = 'cancelled' THEN TRUE
            ELSE FALSE
        END AS is_cancelled,
        
        CASE 
            WHEN order_status = 'refunded' THEN TRUE
            ELSE FALSE
        END AS is_refunded,
        
        CASE 
            WHEN order_status IN ('pending', 'processing') THEN TRUE
            ELSE FALSE
        END AS is_in_progress,
        
        -- Segmentation par montant
        CASE 
            WHEN order_total_amount < 100 THEN 'Small'
            WHEN order_total_amount < 500 THEN 'Medium'
            WHEN order_total_amount < 1000 THEN 'Large'
            ELSE 'Premium'
        END AS order_size_category,
        
        -- Analyse temporelle
        DATE_PART('year', order_date) AS order_year,
        DATE_PART('quarter', order_date) AS order_quarter,
        DATE_PART('month', order_date) AS order_month,
        DATE_PART('week', order_date) AS order_week,
        DATE_PART('dow', order_date) AS order_day_of_week,
        
        CASE DATE_PART('dow', order_date)
            WHEN 0 THEN 'Sunday'
            WHEN 1 THEN 'Monday'
            WHEN 2 THEN 'Tuesday'
            WHEN 3 THEN 'Wednesday'
            WHEN 4 THEN 'Thursday'
            WHEN 5 THEN 'Friday'
            WHEN 6 THEN 'Saturday'
        END AS order_day_name,
        
        -- Indicateur weekend
        CASE 
            WHEN DATE_PART('dow', order_date) IN (0, 6) THEN TRUE
            ELSE FALSE
        END AS is_weekend_order,
        
        -- Jours depuis la commande
        DATE_PART('day', CURRENT_DATE - order_date::date) AS days_since_order,
        
        -- Segmentation géographique de livraison
        CASE shipping_country
            WHEN 'France' THEN 'Domestic'
            ELSE 'International'
        END AS shipping_type,
        
        -- Validation des montants
        CASE 
            WHEN order_total_amount > 0 
            AND order_total_amount < {{ var('max_order_amount') }}
            THEN TRUE
            ELSE FALSE
        END AS is_valid_amount
        
    FROM cleaned
)

SELECT * FROM enriched