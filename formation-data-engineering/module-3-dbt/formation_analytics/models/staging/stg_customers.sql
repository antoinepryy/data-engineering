{{
    config(
        materialized='view',
        tags=['staging', 'daily']
    )
}}

-- ============================================================================
-- STAGING: CUSTOMERS
-- Nettoyage et standardisation des données clients
-- ============================================================================

WITH source AS (
    SELECT * 
    FROM {{ source('raw', 'customers') }}
),

cleaned AS (
    SELECT
        -- Identifiants
        customer_id,
        
        -- Informations personnelles nettoyées
        TRIM(LOWER(email)) AS customer_email,
        TRIM(first_name) AS first_name,
        TRIM(last_name) AS last_name,
        CONCAT(
            INITCAP(TRIM(first_name)), 
            ' ', 
            INITCAP(TRIM(last_name))
        ) AS customer_full_name,
        
        -- Contact
        REGEXP_REPLACE(phone, '[^0-9+]', '', 'g') AS phone_cleaned,
        
        -- Localisation
        TRIM(city) AS city,
        TRIM(country) AS country,
        CONCAT(city, ', ', country) AS customer_location,
        
        -- Adresse complète
        TRIM(address) AS address,
        
        -- Dates
        created_at AS customer_created_at,
        updated_at AS customer_updated_at,
        
        -- Métadonnées
        CURRENT_TIMESTAMP AS _dbt_loaded_at
        
    FROM source
),

validation AS (
    SELECT
        *,
        
        -- Validations
        CASE 
            WHEN customer_email LIKE '%@%.%' 
            AND LENGTH(customer_email) > 5
            THEN TRUE 
            ELSE FALSE 
        END AS is_valid_email,
        
        CASE
            WHEN phone_cleaned LIKE '+%'
            AND LENGTH(phone_cleaned) >= 10
            THEN TRUE
            ELSE FALSE
        END AS is_valid_phone,
        
        -- Segmentation géographique
        CASE country
            WHEN 'France' THEN 'FR'
            WHEN 'Germany' THEN 'DE'
            WHEN 'Spain' THEN 'ES'
            WHEN 'Italy' THEN 'IT'
            WHEN 'United Kingdom' THEN 'UK'
            ELSE 'OTHER'
        END AS country_code,
        
        -- Calculs temporels
        DATE_PART('day', CURRENT_DATE - customer_created_at::date) AS days_since_registration,
        
        CASE 
            WHEN DATE_PART('day', CURRENT_DATE - customer_created_at::date) <= 30 THEN 'New'
            WHEN DATE_PART('day', CURRENT_DATE - customer_created_at::date) <= 180 THEN 'Active'
            WHEN DATE_PART('day', CURRENT_DATE - customer_created_at::date) <= 365 THEN 'Regular'
            ELSE 'Loyal'
        END AS customer_tenure_segment
        
    FROM cleaned
)

SELECT * FROM validation