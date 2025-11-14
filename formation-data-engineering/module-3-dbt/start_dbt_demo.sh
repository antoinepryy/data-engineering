#!/bin/bash

# ============================================================================
# Script de démonstration DBT
# Module 3 - Formation Data Engineering
# ============================================================================

set -e

echo "
╔════════════════════════════════════════════════════════════════╗
║                  🎯 MODULE 3: DBT DEMO                         ║
║                 Data Build Tool - Analytics Engineering        ║
╚════════════════════════════════════════════════════════════════╝
"

# Couleurs pour l'affichage
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Fonction pour afficher les étapes
show_step() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}▶ $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

# Fonction pour pause interactive
pause() {
    echo -e "\n${YELLOW}Appuyez sur Entrée pour continuer...${NC}"
    read -r
}

# Menu principal
show_menu() {
    echo -e "\n${BLUE}Choisissez une option:${NC}"
    echo "1) 🚀 Démarrage rapide (Setup complet)"
    echo "2) 🔍 Vérifier la connexion DBT"
    echo "3) 📊 Exécuter les modèles Staging"
    echo "4) 🔄 Exécuter les modèles Intermediate"
    echo "5) 🎯 Exécuter les modèles Marts"
    echo "6) 🧪 Lancer les tests"
    echo "7) 📚 Générer la documentation"
    echo "8) 📈 Voir les métriques"
    echo "9) 🔄 Full refresh (Reconstruire tout)"
    echo "10) 🎓 Tutoriel interactif"
    echo "0) ❌ Quitter"
    echo -e "\nVotre choix: "
}

# Fonction de setup initial
setup_dbt() {
    show_step "Setup Initial DBT"
    
    echo "📦 Installation des dépendances..."
    dbt deps
    
    echo "🔌 Vérification de la connexion..."
    dbt debug
    
    echo "🌱 Chargement des seeds..."
    dbt seed
    
    echo -e "${GREEN}✅ Setup terminé avec succès!${NC}"
}

# Fonction pour exécuter les modèles staging
run_staging() {
    show_step "Exécution des modèles Staging"
    
    echo "🏗️ Construction des vues staging..."
    dbt run --models staging.*
    
    echo "📊 Modèles créés:"
    dbt ls --models staging.*
    
    echo -e "${GREEN}✅ Modèles staging créés!${NC}"
}

# Fonction pour exécuter les modèles intermediate
run_intermediate() {
    show_step "Exécution des modèles Intermediate"
    
    echo "🔄 Construction des modèles intermédiaires..."
    dbt run --models intermediate.*
    
    echo "📊 Modèles créés:"
    dbt ls --models intermediate.*
    
    echo -e "${GREEN}✅ Modèles intermediate créés!${NC}"
}

# Fonction pour exécuter les modèles marts
run_marts() {
    show_step "Exécution des modèles Marts"
    
    echo "🎯 Construction des tables finales..."
    dbt run --models marts.*
    
    echo "📊 Modèles créés:"
    dbt ls --models marts.*
    
    echo -e "${GREEN}✅ Tables marts créées!${NC}"
}

# Fonction pour lancer les tests
run_tests() {
    show_step "Exécution des Tests"
    
    echo "🧪 Lancement des tests de qualité..."
    dbt test
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Tous les tests sont passés!${NC}"
    else
        echo -e "${RED}❌ Certains tests ont échoué${NC}"
    fi
}

# Fonction pour générer la documentation
generate_docs() {
    show_step "Génération de la Documentation"
    
    echo "📚 Génération de la documentation..."
    dbt docs generate
    
    echo -e "${GREEN}✅ Documentation générée!${NC}"
    echo -e "${YELLOW}Pour visualiser: dbt docs serve --port 8080${NC}"
}

# Fonction pour voir les métriques
show_metrics() {
    show_step "Affichage des Métriques"
    
    echo "📈 Exécution des requêtes de métriques..."
    
    cat << 'EOF' > /tmp/metrics_query.sql
-- Métriques générales
SELECT 
    'Total Customers' as metric,
    COUNT(*) as value
FROM marts.dim_customers
UNION ALL
SELECT 
    'Total Orders' as metric,
    COUNT(*) as value
FROM marts.fct_orders
UNION ALL
SELECT 
    'Total Revenue' as metric,
    ROUND(SUM(order_total_amount)) as value
FROM marts.fct_orders
WHERE is_completed = true
UNION ALL
SELECT 
    'Average Order Value' as metric,
    ROUND(AVG(order_total_amount)) as value
FROM marts.fct_orders
WHERE is_completed = true;
EOF

    psql -h postgres-dbt -U dbt_user -d analytics -f /tmp/metrics_query.sql
    
    echo -e "${GREEN}✅ Métriques affichées!${NC}"
}

# Tutoriel interactif
interactive_tutorial() {
    show_step "Tutoriel Interactif DBT"
    
    echo "Bienvenue dans le tutoriel interactif DBT! 🎓"
    pause
    
    echo -e "${BLUE}Étape 1: Comprendre la structure${NC}"
    echo "DBT organise les transformations en couches:"
    echo "  • Raw → Staging → Intermediate → Marts"
    echo ""
    echo "Explorons la structure:"
    ls -la models/
    pause
    
    echo -e "${BLUE}Étape 2: Examiner un modèle Staging${NC}"
    echo "Les modèles staging nettoient les données brutes:"
    head -30 models/staging/stg_customers.sql
    pause
    
    echo -e "${BLUE}Étape 3: Compiler un modèle${NC}"
    echo "DBT compile le Jinja en SQL pur:"
    dbt compile --select stg_customers
    echo ""
    echo "Le SQL compilé se trouve dans: target/compiled/..."
    pause
    
    echo -e "${BLUE}Étape 4: Exécuter un modèle spécifique${NC}"
    dbt run --select stg_customers
    pause
    
    echo -e "${BLUE}Étape 5: Tester un modèle${NC}"
    dbt test --select stg_customers
    pause
    
    echo -e "${BLUE}Étape 6: Voir le lineage${NC}"
    echo "Le lineage montre les dépendances entre modèles:"
    dbt ls --select +stg_customers+
    pause
    
    echo -e "${GREEN}🎉 Tutoriel terminé!${NC}"
    echo "Pour approfondir, consultez la documentation: dbt docs serve"
}

# Fonction principale
main() {
    cd /usr/app/formation_analytics
    
    while true; do
        show_menu
        read -r choice
        
        case $choice in
            1)
                setup_dbt
                run_staging
                run_intermediate
                run_marts
                run_tests
                generate_docs
                echo -e "${GREEN}🎉 Démarrage rapide terminé!${NC}"
                ;;
            2)
                dbt debug
                ;;
            3)
                run_staging
                ;;
            4)
                run_intermediate
                ;;
            5)
                run_marts
                ;;
            6)
                run_tests
                ;;
            7)
                generate_docs
                ;;
            8)
                show_metrics
                ;;
            9)
                echo "🔄 Full refresh en cours..."
                dbt run --full-refresh
                dbt test
                echo -e "${GREEN}✅ Full refresh terminé!${NC}"
                ;;
            10)
                interactive_tutorial
                ;;
            0)
                echo -e "${BLUE}Au revoir! 👋${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}Option invalide${NC}"
                ;;
        esac
        
        pause
    done
}

# Vérifier si on est dans le bon environnement
if [ ! -f "dbt_project.yml" ]; then
    echo -e "${RED}❌ Erreur: dbt_project.yml non trouvé${NC}"
    echo "Assurez-vous d'être dans le container DBT:"
    echo "  docker exec -it dbt bash"
    echo "  cd /usr/app/formation_analytics"
    exit 1
fi

# Lancer le programme principal
main