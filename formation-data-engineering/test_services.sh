#!/bin/bash

# Script pour tester l'accès aux services

echo "
╔════════════════════════════════════════════════════════════════╗
║           🔍 TEST DES SERVICES - FORMATION DATA ENGINEERING     ║
╚════════════════════════════════════════════════════════════════╝
"

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Fonction pour tester une URL
test_url() {
    local url=$1
    local name=$2
    
    # Test avec curl (timeout de 2 secondes)
    if curl -s -o /dev/null -w "%{http_code}" --connect-timeout 2 "$url" | grep -q "200\|302"; then
        echo -e "${GREEN}✅ $name : $url${NC}"
        return 0
    else
        echo -e "${RED}❌ $name : $url${NC}"
        return 1
    fi
}

# Test des services
echo -e "\n🧪 Test des services actifs:\n"

# Module Vocal
test_url "http://localhost:8501" "Module Vocal (Streamlit)"

# Jupyter
test_url "http://localhost:8889" "Jupyter Notebook"

# Airflow (peut ne pas être démarré)
test_url "http://localhost:8080" "Apache Airflow"

# Spark UI (peut ne pas être démarré)
test_url "http://localhost:9090" "Spark UI"

# Portainer (peut ne pas être démarré)
test_url "http://localhost:9000" "Portainer"

echo -e "\n📊 Résumé des containers Docker:\n"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo -e "\n💡 Commandes utiles:"
echo "  • Logs Streamlit: docker logs vocal-python"
echo "  • Accéder au container: docker exec -it vocal-python bash"
echo "  • Redémarrer Streamlit: docker exec vocal-python pkill streamlit && docker exec -d vocal-python streamlit run /app/app.py --server.port=8501 --server.address=0.0.0.0"
echo ""