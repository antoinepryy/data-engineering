-- ============================================================================
-- MACRO: generate_alias_name
-- Personnalise le nom des modèles en production
-- ============================================================================

{% macro generate_alias_name(custom_alias_name=none, node=none) -%}

    {%- if custom_alias_name is none -%}
        
        {%- if target.name == 'prod' -%}
            {{ node.name }}
        {%- else -%}
            {{ node.name }}_{{ target.name }}
        {%- endif -%}
        
    {%- else -%}
        
        {%- if target.name == 'prod' -%}
            {{ custom_alias_name }}
        {%- else -%}
            {{ custom_alias_name }}_{{ target.name }}
        {%- endif -%}
        
    {%- endif -%}
    
{%- endmacro %}