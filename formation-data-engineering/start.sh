#!/bin/bash

# Script de démarrage intelligent pour la formation Data Engineering

set -e

echo "
╔════════════════════════════════════════════════════════════════╗
║           🚀 FORMATION DATA ENGINEERING - LAUNCHER              ║
╚════════════════════════════════════════════════════════════════╝
"

# Couleurs pour l'affichage
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Fonction pour afficher le menu
show_menu() {
    echo -e "\n${BLUE}Choisissez une option:${NC}"
    echo "1) 🚀 Démarrage rapide (modules essentiels)"
    echo "2) 🎤 Module 1 - Traitement Vocal (version complète)"
    echo "3) 🎤 Module 1 - Traitement Vocal (version lite - sans pyaudio)"
    echo "4) 🌀 Module 2 - Apache Airflow"
    echo "5) 📊 Module 3 - DBT"
    echo "6) ⚡ Module 4 - Apache Spark"
    echo "7) 🔧 Services utilitaires (Jupyter, Portainer)"
    echo "8) 🛑 Arrêter tous les services"
    echo "9) 🗑️  Nettoyer tout (volumes inclus)"
    echo "0) ❌ Quitter"
    echo -e "\nVotre choix: "
}

# Fonction pour vérifier Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker n'est pas installé ou n'est pas démarré${NC}"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        echo -e "${RED}❌ Docker daemon n'est pas accessible${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Docker est prêt${NC}"
}

# Fonction pour créer le réseau si nécessaire
create_network() {
    if ! docker network ls | grep -q formation-network; then
        echo "Création du réseau Docker..."
        docker network create formation-network
    fi
}

# Démarrage rapide
quick_start() {
    echo -e "\n${GREEN}🚀 Démarrage rapide...${NC}"
    create_network
    
    echo "Démarrage des services essentiels..."
    docker-compose up -d \
        vocal-python-lite \
        postgres-dbt \
        dbt \
        jupyter
    
    echo -e "\n${GREEN}✅ Services démarrés:${NC}"
    echo "  - Vocal (lite): http://localhost:8501"
    echo "  - Jupyter: http://localhost:8889 (token: formation2024)"
    echo "  - PostgreSQL DBT: localhost:5433"
}

# Module Vocal complet
start_vocal_full() {
    echo -e "\n${GREEN}🎤 Démarrage Module Vocal (complet)...${NC}"
    create_network
    
    echo "Build de l'image (peut prendre quelques minutes)..."
    docker-compose build vocal-python
    
    echo "Démarrage du service..."
    docker-compose up -d vocal-python
    
    echo -e "\n${GREEN}✅ Module Vocal démarré:${NC}"
    echo "  - Streamlit: http://localhost:8501"
}

# Module Vocal lite
start_vocal_lite() {
    echo -e "\n${GREEN}🎤 Démarrage Module Vocal (lite)...${NC}"
    create_network
    
    echo "Build de l'image lite..."
    docker-compose -f docker-compose.yml -f docker-compose.override.yml build vocal-python-lite
    
    echo "Démarrage du service..."
    docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d vocal-python-lite
    
    echo -e "\n${GREEN}✅ Module Vocal Lite démarré:${NC}"
    echo "  - Streamlit: http://localhost:8501"
    echo -e "${YELLOW}Note: Version sans pyaudio (pas de microphone)${NC}"
}

# Module Airflow
start_airflow() {
    echo -e "\n${GREEN}🌀 Démarrage Module Airflow...${NC}"
    create_network
    
    echo "Démarrage de PostgreSQL et Redis..."
    docker-compose up -d postgres-airflow redis
    
    sleep 5
    
    echo "Initialisation d'Airflow..."
    docker-compose up airflow-init
    
    echo "Démarrage des services Airflow..."
    docker-compose up -d airflow-webserver airflow-scheduler airflow-worker
    
    echo -e "\n${GREEN}✅ Airflow démarré:${NC}"
    echo "  - Web UI: http://localhost:8080 (admin/admin)"
}

# Module DBT
start_dbt() {
    echo -e "\n${GREEN}📊 Démarrage Module DBT...${NC}"
    create_network
    
    echo "Démarrage de PostgreSQL pour DBT..."
    docker-compose up -d postgres-dbt
    
    sleep 5
    
    echo "Démarrage du container DBT..."
    docker-compose up -d dbt
    
    echo -e "\n${GREEN}✅ DBT démarré:${NC}"
    echo "  - Container: dbt"
    echo "  - PostgreSQL: localhost:5433"
    echo ""
    echo "Pour accéder à DBT:"
    echo "  docker exec -it dbt bash"
    echo "  cd /usr/app/formation_analytics"
    echo "  dbt run"
}

# Module Spark
start_spark() {
    echo -e "\n${GREEN}⚡ Démarrage Module Spark...${NC}"
    create_network
    
    echo "Démarrage du cluster Spark..."
    docker-compose up -d spark-master spark-worker-1 spark-worker-2
    
    echo -e "\n${GREEN}✅ Spark démarré:${NC}"
    echo "  - Spark UI: http://localhost:9090"
    echo "  - Master: spark://spark-master:7077"
    echo ""
    echo "Pour lancer PySpark:"
    echo "  docker exec -it spark-master pyspark"
}

# Services utilitaires
start_utilities() {
    echo -e "\n${GREEN}🔧 Démarrage services utilitaires...${NC}"
    create_network
    
    docker-compose up -d jupyter portainer
    
    echo -e "\n${GREEN}✅ Services démarrés:${NC}"
    echo "  - Jupyter: http://localhost:8889 (token: formation2024)"
    echo "  - Portainer: http://localhost:9000"
}

# Arrêter tous les services
stop_all() {
    echo -e "\n${YELLOW}🛑 Arrêt de tous les services...${NC}"
    docker-compose down
    echo -e "${GREEN}✅ Tous les services sont arrêtés${NC}"
}

# Nettoyer tout
clean_all() {
    echo -e "\n${RED}⚠️  ATTENTION: Ceci va supprimer tous les containers, volumes et données!${NC}"
    echo -n "Êtes-vous sûr? (y/N): "
    read -r response
    
    if [[ "$response" == "y" || "$response" == "Y" ]]; then
        echo "Nettoyage en cours..."
        docker-compose down -v
        docker network rm formation-network 2>/dev/null || true
        echo -e "${GREEN}✅ Nettoyage complet effectué${NC}"
    else
        echo "Nettoyage annulé"
    fi
}

# Programme principal
main() {
    check_docker
    
    while true; do
        show_menu
        read -r choice
        
        case $choice in
            1) quick_start ;;
            2) start_vocal_full ;;
            3) start_vocal_lite ;;
            4) start_airflow ;;
            5) start_dbt ;;
            6) start_spark ;;
            7) start_utilities ;;
            8) stop_all ;;
            9) clean_all ;;
            0) 
                echo -e "${BLUE}Au revoir! 👋${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}Option invalide${NC}"
                ;;
        esac
        
        echo -e "\n${YELLOW}Appuyez sur Entrée pour continuer...${NC}"
        read -r
    done
}

# Lancer le programme
main