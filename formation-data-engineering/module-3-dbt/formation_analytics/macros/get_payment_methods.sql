-- ============================================================================
-- MACRO: get_payment_methods
-- Retourne la liste des méthodes de paiement valides
-- ============================================================================

{% macro get_payment_methods() %}
    {{ return(['credit_card', 'debit_card', 'paypal', 'bank_transfer', 'cash', 'crypto']) }}
{% endmacro %}