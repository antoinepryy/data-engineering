# 📊 Module 3: DBT (Data Build Tool)
## Formation Data Engineering - Analytics Engineering

---

## 🎯 Objectifs du Module

- Comprendre la philosophie de l'Analytics Engineering
- Maîtriser la transformation de données avec DBT
- Implémenter des pipelines de données testables et documentés
- Appliquer les best practices de modélisation en couches
- Créer des tests automatisés et de la documentation

---

## 🏗️ Architecture DBT

```
┌─────────────────────────────────────────────────────────┐
│                     Sources (Raw Data)                   │
├─────────────────────────────────────────────────────────┤
│                         ↓                                │
├─────────────────────────────────────────────────────────┤
│                   Staging Models                         │
│              (Nettoyage, Standardisation)               │
├─────────────────────────────────────────────────────────┤
│                         ↓                                │
├─────────────────────────────────────────────────────────┤
│                 Intermediate Models                      │
│              (Jointures, Enrichissement)                │
├─────────────────────────────────────────────────────────┤
│                         ↓                                │
├─────────────────────────────────────────────────────────┤
│                     Marts Models                         │
│              (Tables finales pour BI)                   │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Démarrage Rapide

### 1. Lancer l'environnement DBT

```bash
# Depuis le dossier principal
cd formation-data-engineering

# Démarrer PostgreSQL et DBT
docker-compose up -d postgres-dbt dbt

# Accéder au container DBT
docker exec -it dbt bash

# Se placer dans le projet DBT
cd /usr/app/formation_analytics
```

### 2. Initialiser DBT

```bash
# Installer les dépendances
dbt deps

# Vérifier la connexion
dbt debug

# Lancer les seeds (données de référence)
dbt seed

# Exécuter tous les modèles
dbt run

# Lancer les tests
dbt test
```

### 3. Générer la documentation

```bash
# Générer la documentation
dbt docs generate

# Servir la documentation (accessible sur http://localhost:8080)
dbt docs serve --port 8080
```

---

## 📚 Structure du Projet

```
formation_analytics/
├── dbt_project.yml          # Configuration principale
├── profiles.yml             # Connexions aux bases
├── models/                  # Modèles SQL
│   ├── staging/            # Couche staging
│   ├── intermediate/       # Couche intermédiaire
│   └── marts/              # Couche marts
├── macros/                 # Fonctions réutilisables
├── tests/                  # Tests personnalisés
├── snapshots/              # Historisation
└── seeds/                  # Données de référence
```

---

## 💻 Exercices Pratiques

### Exercice 1: Créer un modèle Staging (30 min)

**Objectif**: Créer un modèle staging pour une nouvelle source

1. Créer le fichier `models/staging/stg_payments.sql`:

```sql
{{
    config(
        materialized='view',
        tags=['staging', 'daily']
    )
}}

WITH source AS (
    SELECT * FROM {{ source('raw', 'payments') }}
),

cleaned AS (
    SELECT
        payment_id,
        order_id,
        payment_date,
        LOWER(TRIM(payment_method)) AS payment_method,
        amount AS payment_amount,
        LOWER(TRIM(status)) AS payment_status,
        
        -- Indicateurs
        CASE 
            WHEN status = 'completed' THEN TRUE
            ELSE FALSE
        END AS is_successful,
        
        -- Validation
        CASE 
            WHEN amount > 0 THEN TRUE
            ELSE FALSE
        END AS is_valid_amount
        
    FROM source
)

SELECT * FROM cleaned
```

2. Ajouter la documentation dans `schema.yml`
3. Exécuter: `dbt run -s stg_payments`
4. Tester: `dbt test -s stg_payments`

### Exercice 2: Créer une Macro (20 min)

**Objectif**: Créer une macro pour classifier les clients

1. Créer `macros/classify_customer.sql`:

```sql
{% macro classify_customer_value(lifetime_value) %}
    CASE 
        WHEN {{ lifetime_value }} >= 10000 THEN 'Platinum'
        WHEN {{ lifetime_value }} >= 5000 THEN 'Gold'
        WHEN {{ lifetime_value }} >= 1000 THEN 'Silver'
        ELSE 'Bronze'
    END
{% endmacro %}
```

2. Utiliser dans un modèle:

```sql
SELECT
    customer_id,
    lifetime_value,
    {{ classify_customer_value('lifetime_value') }} AS customer_tier
FROM {{ ref('int_customer_order_summary') }}
```

### Exercice 3: Modèle Incrémental (45 min)

**Objectif**: Créer un modèle incrémental pour les événements web

1. Créer `models/marts/core/fct_web_events.sql`:

```sql
{{
    config(
        materialized='incremental',
        unique_key='event_id',
        on_schema_change='fail'
    )
}}

SELECT
    event_id,
    session_id,
    customer_id,
    event_type,
    event_timestamp,
    DATE(event_timestamp) AS event_date,
    page_url,
    device_type,
    browser,
    country
FROM {{ source('raw', 'web_events') }}

{% if is_incremental() %}
    WHERE event_timestamp > (
        SELECT MAX(event_timestamp) 
        FROM {{ this }}
    )
{% endif %}
```

2. Exécuter deux fois pour voir le comportement incrémental
3. Vérifier avec: `SELECT COUNT(*) FROM marts.fct_web_events`

### Exercice 4: Tests Personnalisés (30 min)

**Objectif**: Créer des tests de qualité des données

1. Créer un test dans `tests/test_order_amounts.sql`:

```sql
-- Test: Vérifier que le total des lignes = total commande
SELECT
    o.order_id,
    o.order_total_amount,
    SUM(oi.total_amount) AS calculated_total,
    ABS(o.order_total_amount - SUM(oi.total_amount)) AS difference
FROM {{ ref('stg_orders') }} o
JOIN {{ source('raw', 'order_items') }} oi
    ON o.order_id = oi.order_id
GROUP BY o.order_id, o.order_total_amount
HAVING ABS(o.order_total_amount - SUM(oi.total_amount)) > 0.01
```

2. Exécuter: `dbt test`

### Exercice 5: Snapshot (45 min)

**Objectif**: Créer un snapshot pour historiser les changements

1. Créer `snapshots/snap_customers.sql`:

```sql
{% snapshot snap_customers %}

{{
    config(
      target_schema='snapshots',
      unique_key='customer_id',
      strategy='timestamp',
      updated_at='updated_at',
    )
}}

SELECT * FROM {{ source('raw', 'customers') }}

{% endsnapshot %}
```

2. Exécuter: `dbt snapshot`
3. Modifier des données dans la source
4. Re-exécuter et voir l'historique

### Exercice 6: Pipeline Complet (1h30)

**Objectif**: Créer un pipeline complet de A à Z

**Contexte**: Analyse des performances marketing

1. **Staging**: Créer `stg_marketing_campaigns.sql` et `stg_marketing_attributions.sql`
2. **Intermediate**: Créer `int_campaign_performance.sql` avec métriques
3. **Mart**: Créer `marts/marketing/marketing_dashboard.sql`
4. **Tests**: Ajouter tests de validation
5. **Documentation**: Documenter dans `schema.yml`

Template de départ:

```sql
-- int_campaign_performance.sql
WITH campaigns AS (
    SELECT * FROM {{ ref('stg_marketing_campaigns') }}
),

attributions AS (
    SELECT * FROM {{ ref('stg_marketing_attributions') }}
),

orders AS (
    SELECT * FROM {{ ref('fct_orders') }}
),

campaign_metrics AS (
    SELECT
        c.campaign_id,
        c.campaign_name,
        c.channel,
        c.budget,
        COUNT(DISTINCT a.order_id) AS attributed_orders,
        SUM(o.order_total_amount) AS attributed_revenue,
        AVG(a.attribution_weight) AS avg_attribution_weight
    FROM campaigns c
    LEFT JOIN attributions a ON c.campaign_id = a.campaign_id
    LEFT JOIN orders o ON a.order_id = o.order_id
    GROUP BY 1,2,3,4
)

SELECT
    *,
    attributed_revenue / NULLIF(budget, 0) AS roi,
    attributed_revenue / NULLIF(attributed_orders, 0) AS revenue_per_order
FROM campaign_metrics
```

---

## 🧪 Tests DBT

### Tests Intégrés

```yaml
# schema.yml
models:
  - name: stg_customers
    columns:
      - name: customer_id
        tests:
          - unique
          - not_null
      - name: email
        tests:
          - unique
          - not_null
      - name: country_code
        tests:
          - accepted_values:
              values: ['FR', 'DE', 'ES', 'IT', 'UK', 'OTHER']
```

### Tests Personnalisés

```sql
-- tests/assert_positive_amounts.sql
SELECT *
FROM {{ ref('fct_orders') }}
WHERE order_total_amount < 0
```

### Tests avec Macros

```sql
-- Utiliser le test macro créé
models:
  - name: fct_orders
    columns:
      - name: order_total_amount
        tests:
          - positive_values
```

---

## 📈 Métriques et KPIs

### Définir des métriques avec DBT Metrics

```yaml
# models/metrics.yml
version: 2

metrics:
  - name: revenue
    label: Total Revenue
    model: ref('fct_orders')
    calculation_method: sum
    expression: order_total_amount
    timestamp: order_date
    time_grains: [day, week, month, quarter, year]
    dimensions:
      - order_status
      - shipping_country
    
  - name: order_count
    label: Number of Orders
    model: ref('fct_orders')
    calculation_method: count
    expression: order_id
    timestamp: order_date
    time_grains: [day, week, month]
    
  - name: aov
    label: Average Order Value
    calculation_method: derived
    expression: "{{ metric('revenue') }} / {{ metric('order_count') }}"
    timestamp: order_date
    time_grains: [month, quarter, year]
```

---

## 🔍 Commandes DBT Essentielles

```bash
# Commandes de base
dbt run                     # Exécuter tous les modèles
dbt test                    # Lancer tous les tests
dbt build                   # run + test + snapshot
dbt compile                 # Compiler sans exécuter

# Sélection de modèles
dbt run -s model_name       # Un modèle spécifique
dbt run -s +model_name      # Modèle et ses parents
dbt run -s model_name+      # Modèle et ses enfants
dbt run -s tag:staging      # Tous les modèles avec tag

# Modes d'exécution
dbt run --full-refresh      # Reconstruire tous les modèles
dbt run --models @tag       # Modèles modifiés depuis dernier run

# Documentation
dbt docs generate           # Générer la doc
dbt docs serve              # Servir la doc

# Debug
dbt debug                   # Vérifier connexion
dbt compile --select model  # Voir le SQL compilé
dbt show --select model     # Aperçu des données

# Snapshots
dbt snapshot                # Exécuter les snapshots

# Seeds
dbt seed                    # Charger les CSV
```

---

## 🎓 Best Practices

### 1. **Nommage des Modèles**
- `stg_` : Staging models
- `int_` : Intermediate models
- `fct_` : Fact tables
- `dim_` : Dimension tables

### 2. **Matérialisation**
- **View** : Staging, données fraîches
- **Table** : Marts, performances
- **Incremental** : Gros volumes, historique

### 3. **Documentation**
- Toujours documenter les colonnes importantes
- Utiliser des descriptions claires
- Ajouter des exemples de valeurs

### 4. **Tests**
- Tester les clés primaires (unique, not_null)
- Tester les clés étrangères (relationships)
- Tester la logique métier

### 5. **Structure en Couches**
```
Raw → Staging → Intermediate → Marts
```

---

## 🚨 Troubleshooting

### Problème: "Connection refused"
```bash
# Vérifier PostgreSQL
docker-compose ps postgres-dbt
docker-compose logs postgres-dbt

# Redémarrer si nécessaire
docker-compose restart postgres-dbt
```

### Problème: "Model not found"
```bash
# Recompiler
dbt clean
dbt deps
dbt compile
```

### Problème: "Test failures"
```bash
# Voir les détails
dbt test --select test_name --vars '{"debug": true}'

# Ignorer temporairement
dbt test --exclude test_name
```

---

## 📚 Ressources

- [Documentation DBT](https://docs.getdbt.com/)
- [DBT Learn](https://courses.getdbt.com/)
- [DBT Slack](https://www.getdbt.com/community/)
- [Best Practices](https://docs.getdbt.com/guides/best-practices)
- [SQL Style Guide](https://github.com/dbt-labs/corp/blob/master/dbt_style_guide.md)

---

## 🎯 Projet Final DBT

**Créer un Data Mart Complet**

1. Analyser les besoins métier
2. Concevoir le modèle en étoile
3. Implémenter les transformations
4. Ajouter tests et documentation
5. Créer un dashboard de métriques
6. Présenter avec DBT docs

**Livrables**:
- 10+ modèles DBT
- 20+ tests
- Documentation complète
- Métriques définies
- Snapshot historique

---

✨ **Félicitations!** Vous maîtrisez maintenant DBT pour transformer vos données de manière professionnelle et scalable!