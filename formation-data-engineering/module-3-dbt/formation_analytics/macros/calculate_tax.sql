-- ============================================================================
-- MACRO: calculate_tax
-- Calcule la TVA basée sur le montant et le taux
-- ============================================================================

{% macro calculate_tax(amount_column, tax_rate=none) %}
    
    {% if tax_rate is none %}
        {% set tax_rate = var('tax_rate', 0.20) %}
    {% endif %}
    
    ROUND({{ amount_column }} * {{ tax_rate }}, 2)
    
{% endmacro %}

-- ============================================================================
-- MACRO: calculate_margin
-- Calcule la marge entre prix de vente et coût
-- ============================================================================

{% macro calculate_margin(revenue_column, cost_column, format='amount') %}
    
    {% if format == 'percentage' %}
        CASE 
            WHEN {{ revenue_column }} > 0 
            THEN ROUND((({{ revenue_column }} - {{ cost_column }}) / {{ revenue_column }}) * 100, 2)
            ELSE 0
        END
    {% else %}
        ROUND({{ revenue_column }} - {{ cost_column }}, 2)
    {% endif %}
    
{% endmacro %}