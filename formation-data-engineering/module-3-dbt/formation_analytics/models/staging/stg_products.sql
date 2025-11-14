{{
    config(
        materialized='view',
        tags=['staging', 'daily']
    )
}}

-- ============================================================================
-- STAGING: PRODUCTS
-- Nettoyage et enrichissement du catalogue produits
-- ============================================================================

WITH source AS (
    SELECT * 
    FROM {{ source('raw', 'products') }}
),

cleaned AS (
    SELECT
        -- Identifiants
        product_id,
        
        -- Informations produit
        TRIM(product_name) AS product_name,
        LOWER(TRIM(category)) AS product_category,
        TRIM(brand) AS brand,
        
        -- Prix et coûts
        price AS selling_price,
        cost AS product_cost,
        
        -- Calcul de la marge
        price - cost AS margin_amount,
        CASE 
            WHEN price > 0 THEN ((price - cost) / price) * 100
            ELSE 0
        END AS margin_percentage,
        
        -- Caractéristiques physiques
        weight AS weight_kg,
        
        -- Statut
        LOWER(TRIM(status)) AS product_status,
        
        -- Dates
        created_at AS product_created_at,
        discontinued_at,
        
        -- Métadonnées
        CURRENT_TIMESTAMP AS _dbt_loaded_at
        
    FROM source
),

enriched AS (
    SELECT
        *,
        
        -- Indicateurs de statut
        CASE 
            WHEN product_status = 'active' THEN TRUE
            ELSE FALSE
        END AS is_active,
        
        CASE 
            WHEN discontinued_at IS NOT NULL THEN TRUE
            ELSE FALSE
        END AS is_discontinued,
        
        -- Catégorisation par prix
        CASE 
            WHEN selling_price < 50 THEN 'Budget'
            WHEN selling_price < 200 THEN 'Standard'
            WHEN selling_price < 500 THEN 'Premium'
            ELSE 'Luxury'
        END AS price_tier,
        
        -- Catégorisation par marge
        CASE 
            WHEN margin_percentage < 20 THEN 'Low Margin'
            WHEN margin_percentage < 40 THEN 'Medium Margin'
            WHEN margin_percentage < 60 THEN 'High Margin'
            ELSE 'Premium Margin'
        END AS margin_tier,
        
        -- Regroupement des catégories
        CASE product_category
            WHEN 'électronique' THEN 'Electronics'
            WHEN 'audio' THEN 'Electronics'
            WHEN 'accessoires' THEN 'Accessories'
            WHEN 'wearables' THEN 'Electronics'
            ELSE INITCAP(product_category)
        END AS product_category_group,
        
        -- Indicateur de rentabilité
        CASE 
            WHEN margin_percentage >= 30 THEN TRUE
            ELSE FALSE
        END AS is_profitable,
        
        -- Jours depuis création
        DATE_PART('day', CURRENT_DATE - product_created_at::date) AS days_in_catalog,
        
        -- Jours depuis discontinuation
        CASE 
            WHEN discontinued_at IS NOT NULL 
            THEN DATE_PART('day', CURRENT_DATE - discontinued_at::date)
            ELSE NULL
        END AS days_since_discontinued,
        
        -- Classification ABC (simplifiée basée sur le prix)
        CASE 
            WHEN selling_price >= 500 THEN 'A'
            WHEN selling_price >= 100 THEN 'B'
            ELSE 'C'
        END AS abc_classification,
        
        -- Validation des données
        CASE 
            WHEN selling_price > 0 
            AND product_cost > 0
            AND selling_price > product_cost
            THEN TRUE
            ELSE FALSE
        END AS has_valid_pricing
        
    FROM cleaned
)

SELECT * FROM enriched