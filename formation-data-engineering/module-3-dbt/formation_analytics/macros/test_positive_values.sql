-- ============================================================================
-- TEST MACRO: positive_values
-- Vérifie que toutes les valeurs d'une colonne sont positives
-- ============================================================================

{% test positive_values(model, column_name) %}

WITH validation AS (
    SELECT
        {{ column_name }} AS tested_value
    FROM {{ model }}
    WHERE {{ column_name }} IS NOT NULL
        AND {{ column_name }} <= 0
)

SELECT *
FROM validation

{% endtest %}