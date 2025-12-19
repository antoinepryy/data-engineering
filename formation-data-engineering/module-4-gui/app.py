"""
Module 4 - GUI Test des APIs Publiques
Application Streamlit pour tester les APIs touristiques publiques gratuites

APIs utilisees:
- API Geo gouv.fr: Communes, departements, regions de France
- OpenStreetMap Nominatim: Geocoding
- Overpass API: POI depuis OpenStreetMap
"""

import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import st_folium
import json
from typing import List, Dict, Any, Optional
import time

# Configuration de la page
st.set_page_config(
    page_title="Test APIs Publiques - POI",
    page_icon="🗺️",
    layout="wide"
)

# =============================================================================
# INITIALISATION SESSION STATE
# =============================================================================
if "communes_results" not in st.session_state:
    st.session_state.communes_results = None
if "departements_results" not in st.session_state:
    st.session_state.departements_results = None
if "regions_results" not in st.session_state:
    st.session_state.regions_results = None
if "nominatim_results" not in st.session_state:
    st.session_state.nominatim_results = None
if "overpass_results" not in st.session_state:
    st.session_state.overpass_results = None
if "datagouv_results" not in st.session_state:
    st.session_state.datagouv_results = None

# =============================================================================
# FONCTIONS API
# =============================================================================

@st.cache_data(ttl=300)
def fetch_geo_api_communes(search: str = None, code_departement: str = None, limit: int = 20) -> List[Dict]:
    """
    Fetch communes depuis l'API Geo gouv.fr
    Documentation: https://geo.api.gouv.fr/decoupage-administratif/communes
    """
    base_url = "https://geo.api.gouv.fr/communes"
    params = {
        "fields": "nom,code,codesPostaux,centre,population,departement,region",
        "limit": limit
    }
    
    if search:
        params["nom"] = search
    if code_departement:
        params["codeDepartement"] = code_departement
    
    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Erreur API Geo: {e}")
        return []


@st.cache_data(ttl=300)
def fetch_geo_api_departements() -> List[Dict]:
    """Fetch tous les departements depuis l'API Geo gouv.fr"""
    url = "https://geo.api.gouv.fr/departements"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Erreur API Geo: {e}")
        return []


@st.cache_data(ttl=300)
def fetch_geo_api_regions() -> List[Dict]:
    """Fetch toutes les regions depuis l'API Geo gouv.fr"""
    url = "https://geo.api.gouv.fr/regions"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Erreur API Geo: {e}")
        return []


@st.cache_data(ttl=300)
def fetch_nominatim_search(query: str, limit: int = 10) -> List[Dict]:
    """
    Recherche de lieux via OpenStreetMap Nominatim
    Documentation: https://nominatim.org/release-docs/latest/api/Search/
    """
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": query,
        "format": "json",
        "limit": limit,
        "addressdetails": 1
    }
    headers = {
        "User-Agent": "FormationDataEngineering/1.0 (educational project)"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Erreur Nominatim: {e}")
        return []


@st.cache_data(ttl=300)
def fetch_overpass_poi(lat: float, lon: float, radius: int = 1000, poi_type: str = "tourism") -> List[Dict]:
    """
    Fetch POI depuis Overpass API (OpenStreetMap)
    Documentation: https://wiki.openstreetmap.org/wiki/Overpass_API
    
    Types disponibles: tourism, amenity, historic, leisure, shop
    """
    url = "https://overpass-api.de/api/interpreter"
    
    # Query Overpass QL
    query = f"""
    [out:json][timeout:25];
    (
      node["{poi_type}"](around:{radius},{lat},{lon});
      way["{poi_type}"](around:{radius},{lat},{lon});
    );
    out center body;
    """
    
    try:
        response = requests.post(url, data={"data": query}, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("elements", [])
    except Exception as e:
        st.error(f"Erreur Overpass: {e}")
        return []


@st.cache_data(ttl=300)
def fetch_data_gouv_datasets(search: str = "tourisme", limit: int = 10) -> List[Dict]:
    """
    Recherche de datasets sur data.gouv.fr
    Documentation: https://doc.data.gouv.fr/api/reference/
    """
    url = "https://www.data.gouv.fr/api/1/datasets/"
    params = {
        "q": search,
        "page_size": limit
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("data", [])
    except Exception as e:
        st.error(f"Erreur data.gouv.fr: {e}")
        return []


# =============================================================================
# INTERFACE STREAMLIT
# =============================================================================

def main():
    st.title("🗺️ Test des APIs Publiques - POI France")
    st.markdown("""
    Cette application permet de tester differentes APIs publiques gratuites 
    pour recuperer des donnees touristiques et geographiques.
    """)
    
    # Sidebar pour la navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Choisir une API:",
        [
            "🏛️ API Geo gouv.fr",
            "🔍 Nominatim (OSM)",
            "📍 Overpass (POI OSM)",
            "📊 Data.gouv.fr"
        ]
    )
    
    # ==========================================================================
    # PAGE: API Geo gouv.fr
    # ==========================================================================
    if page == "🏛️ API Geo gouv.fr":
        st.header("API Geo gouv.fr")
        st.markdown("""
        **URL**: https://geo.api.gouv.fr  
        **Documentation**: https://geo.api.gouv.fr/decoupage-administratif  
        **Authentification**: Aucune requise ✅
        """)
        
        tab1, tab2, tab3 = st.tabs(["Communes", "Departements", "Regions"])
        
        with tab1:
            st.subheader("Recherche de communes")
            
            col1, col2 = st.columns(2)
            with col1:
                search_commune = st.text_input("Nom de commune", value="Paris")
            with col2:
                limit = st.slider("Limite de resultats", 5, 50, 20)
            
            if st.button("🔍 Rechercher communes", key="search_communes"):
                with st.spinner("Chargement..."):
                    st.session_state.communes_results = fetch_geo_api_communes(search=search_commune, limit=limit)
            
            # Afficher les resultats stockes
            if st.session_state.communes_results:
                communes = st.session_state.communes_results
                st.success(f"{len(communes)} commune(s) trouvee(s)")
                
                # Affichage JSON brut
                with st.expander("📄 Reponse JSON brute"):
                    st.json(communes[:3])  # Premiers 3
                
                # Tableau
                df = pd.DataFrame([{
                    "Nom": c.get("nom"),
                    "Code INSEE": c.get("code"),
                    "Population": c.get("population"),
                    "Departement": c.get("departement", {}).get("nom"),
                    "Region": c.get("region", {}).get("nom"),
                    "Latitude": c.get("centre", {}).get("coordinates", [None, None])[1],
                    "Longitude": c.get("centre", {}).get("coordinates", [None, None])[0]
                } for c in communes])
                
                st.dataframe(df, use_container_width=True)
                
                # Carte
                communes_with_coords = [c for c in communes if c.get("centre")]
                if communes_with_coords:
                    first = communes_with_coords[0]
                    coords = first["centre"]["coordinates"]
                    m = folium.Map(location=[coords[1], coords[0]], zoom_start=8)
                    
                    for c in communes_with_coords:
                        coords = c["centre"]["coordinates"]
                        folium.Marker(
                            [coords[1], coords[0]],
                            popup=f"{c['nom']} (pop: {c.get('population', 'N/A')})",
                            tooltip=c["nom"]
                        ).add_to(m)
                    
                    st_folium(m, width=700, height=400, returned_objects=[])
        
        with tab2:
            st.subheader("Liste des departements")
            if st.button("📥 Charger departements"):
                with st.spinner("Chargement..."):
                    st.session_state.departements_results = fetch_geo_api_departements()
            
            if st.session_state.departements_results:
                departements = st.session_state.departements_results
                st.success(f"{len(departements)} departement(s)")
                
                with st.expander("📄 Reponse JSON brute"):
                    st.json(departements[:5])
                
                df = pd.DataFrame([{
                    "Code": d.get("code"),
                    "Nom": d.get("nom"),
                    "Code Region": d.get("codeRegion")
                } for d in departements])
                
                st.dataframe(df, use_container_width=True)
        
        with tab3:
            st.subheader("Liste des regions")
            if st.button("📥 Charger regions"):
                with st.spinner("Chargement..."):
                    st.session_state.regions_results = fetch_geo_api_regions()
            
            if st.session_state.regions_results:
                regions = st.session_state.regions_results
                st.success(f"{len(regions)} region(s)")
                
                with st.expander("📄 Reponse JSON brute"):
                    st.json(regions)
                
                df = pd.DataFrame([{
                    "Code": r.get("code"),
                    "Nom": r.get("nom")
                } for r in regions])
                
                st.dataframe(df, use_container_width=True)
    
    # ==========================================================================
    # PAGE: Nominatim
    # ==========================================================================
    elif page == "🔍 Nominatim (OSM)":
        st.header("OpenStreetMap Nominatim")
        st.markdown("""
        **URL**: https://nominatim.openstreetmap.org  
        **Documentation**: https://nominatim.org/release-docs/latest/api/Search/  
        **Authentification**: Aucune requise ✅  
        **Limite**: 1 requete/seconde (respectee automatiquement)
        """)
        
        query = st.text_input("Recherche de lieu", value="Tour Eiffel, Paris")
        limit = st.slider("Nombre de resultats", 1, 20, 5, key="nominatim_limit")
        
        if st.button("🔍 Rechercher", key="nominatim_search"):
            with st.spinner("Recherche en cours..."):
                st.session_state.nominatim_results = fetch_nominatim_search(query, limit)
        
        if st.session_state.nominatim_results:
            results = st.session_state.nominatim_results
            st.success(f"{len(results)} resultat(s)")
            
            with st.expander("📄 Reponse JSON brute"):
                st.json(results[:2])
            
            # Tableau
            df = pd.DataFrame([{
                "Nom": r.get("display_name", "")[:60] + "...",
                "Type": r.get("type"),
                "Classe": r.get("class"),
                "Latitude": r.get("lat"),
                "Longitude": r.get("lon"),
                "Importance": round(float(r.get("importance", 0)), 3)
            } for r in results])
            
            st.dataframe(df, use_container_width=True)
            
            # Carte
            first = results[0]
            m = folium.Map(
                location=[float(first["lat"]), float(first["lon"])],
                zoom_start=14
            )
            
            for r in results:
                folium.Marker(
                    [float(r["lat"]), float(r["lon"])],
                    popup=r.get("display_name", "")[:100],
                    tooltip=r.get("type", "lieu")
                ).add_to(m)
            
            st_folium(m, width=700, height=400, returned_objects=[])
    
    # ==========================================================================
    # PAGE: Overpass API
    # ==========================================================================
    elif page == "📍 Overpass (POI OSM)":
        st.header("Overpass API - POI OpenStreetMap")
        st.markdown("""
        **URL**: https://overpass-api.de/api/interpreter  
        **Documentation**: https://wiki.openstreetmap.org/wiki/Overpass_API  
        **Authentification**: Aucune requise ✅  
        """)
        
        st.subheader("Recherche de POI autour d'un point")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            lat = st.number_input("Latitude", value=48.8566, format="%.4f")
        with col2:
            lon = st.number_input("Longitude", value=2.3522, format="%.4f")
        with col3:
            radius = st.slider("Rayon (metres)", 100, 5000, 1000, key="overpass_radius")
        
        poi_type = st.selectbox(
            "Type de POI",
            ["tourism", "amenity", "historic", "leisure", "shop"],
            help="Categorie OpenStreetMap a rechercher"
        )
        
        # Description des types
        type_descriptions = {
            "tourism": "Hotels, musees, attractions, viewpoints...",
            "amenity": "Restaurants, cafes, banques, hopitaux...",
            "historic": "Monuments, chateaux, ruines, memorials...",
            "leisure": "Parcs, piscines, sports, jardins...",
            "shop": "Magasins, supermarches, boutiques..."
        }
        st.info(f"**{poi_type}**: {type_descriptions.get(poi_type, '')}")
        
        if st.button("🔍 Rechercher POI", key="overpass_search"):
            with st.spinner("Requete Overpass en cours (peut prendre quelques secondes)..."):
                pois = fetch_overpass_poi(lat, lon, radius, poi_type)
                # Parser et stocker
                poi_data = []
                for p in pois:
                    tags = p.get("tags", {})
                    p_lat = p.get("lat") or p.get("center", {}).get("lat")
                    p_lon = p.get("lon") or p.get("center", {}).get("lon")
                    poi_data.append({
                        "Nom": tags.get("name", "Sans nom"),
                        "Type": tags.get(poi_type, "N/A"),
                        "Adresse": tags.get("addr:street", ""),
                        "Ville": tags.get("addr:city", ""),
                        "Website": tags.get("website", ""),
                        "Latitude": p_lat,
                        "Longitude": p_lon,
                        "OSM ID": p.get("id")
                    })
                st.session_state.overpass_results = {"raw": pois, "parsed": poi_data, "lat": lat, "lon": lon, "radius": radius}
        
        if st.session_state.overpass_results:
            data = st.session_state.overpass_results
            pois = data["raw"]
            poi_data = data["parsed"]
            
            if pois:
                st.success(f"{len(pois)} POI trouve(s)")
                
                with st.expander("📄 Reponse JSON brute"):
                    st.json(pois[:3])
                
                df = pd.DataFrame(poi_data)
                st.dataframe(df, use_container_width=True)
                
                # Carte
                m = folium.Map(location=[data["lat"], data["lon"]], zoom_start=14)
                folium.Circle(
                    [data["lat"], data["lon"]],
                    radius=data["radius"],
                    color="blue",
                    fill=True,
                    fillOpacity=0.1
                ).add_to(m)
                
                for poi in poi_data:
                    if poi["Latitude"] and poi["Longitude"]:
                        folium.Marker(
                            [poi["Latitude"], poi["Longitude"]],
                            popup=f"{poi['Nom']}<br>{poi['Type']}",
                            tooltip=poi["Nom"],
                            icon=folium.Icon(color="red", icon="info-sign")
                        ).add_to(m)
                
                st_folium(m, width=700, height=450, returned_objects=[])
            else:
                st.warning("Aucun POI trouve dans cette zone")
    
    # ==========================================================================
    # PAGE: Data.gouv.fr
    # ==========================================================================
    elif page == "📊 Data.gouv.fr":
        st.header("API Data.gouv.fr")
        st.markdown("""
        **URL**: https://www.data.gouv.fr/api/1/  
        **Documentation**: https://doc.data.gouv.fr/api/reference/  
        **Authentification**: Aucune requise ✅  
        """)
        
        search = st.text_input("Recherche de datasets", value="tourisme")
        limit = st.slider("Nombre de resultats", 5, 50, 10, key="datagouv_limit")
        
        if st.button("🔍 Rechercher datasets", key="datagouv_search"):
            with st.spinner("Recherche..."):
                st.session_state.datagouv_results = fetch_data_gouv_datasets(search, limit)
        
        if st.session_state.datagouv_results:
            datasets = st.session_state.datagouv_results
            st.success(f"{len(datasets)} dataset(s) trouve(s)")
            
            with st.expander("📄 Reponse JSON brute"):
                st.json(datasets[:2])
            
            for ds in datasets:
                with st.expander(f"📁 {ds.get('title', 'Sans titre')[:80]}"):
                    org = ds.get('organization') or {}
                    st.write(f"**Organisation**: {org.get('name', 'N/A')}")
                    st.write(f"**Description**: {(ds.get('description') or 'N/A')[:300]}...")
                    last_mod = ds.get('last_modified') or 'N/A'
                    st.write(f"**Derniere MAJ**: {last_mod[:10] if len(last_mod) > 10 else last_mod}")
                    st.write(f"**Ressources**: {len(ds.get('resources', []))} fichier(s)")
                    
                    resources = ds.get("resources", [])[:3]
                    if resources:
                        st.write("**Fichiers disponibles:**")
                        for r in resources:
                            st.write(f"- [{r.get('title', 'fichier')}]({r.get('url', '#')}) ({r.get('format', 'N/A')})")
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    **APIs testees:**
    - geo.api.gouv.fr ✅
    - nominatim.openstreetmap.org ✅
    - overpass-api.de ✅
    - data.gouv.fr ✅
    
    *Toutes ces APIs sont gratuites et ne necessitent pas d'authentification.*
    """)


if __name__ == "__main__":
    main()
