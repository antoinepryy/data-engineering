"""
Application Streamlit pour la visualisation des POI
Module 3 - Formation Data Engineering

Cette application permet de:
- Visualiser les POI sur une carte
- Explorer les données par source/type/région
- Suivre les métriques du pipeline ETL
- Analyser les résultats de déduplication
"""

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Dict, Any
import folium
from streamlit_folium import st_folium

# Configuration de la page
st.set_page_config(
    page_title="POI Dashboard - Module 3",
    page_icon="📍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 1.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .source-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.8rem;
        margin: 0.1rem;
    }
    </style>
""", unsafe_allow_html=True)


# ============================================================================
# CONSTANTES
# ============================================================================

DATA_DIR = os.environ.get('DATA_DIR', '/data')
PROCESSED_DIR = f'{DATA_DIR}/processed'
OUTPUT_DIR = f'{DATA_DIR}/output'
DEDUP_DIR = f'{DATA_DIR}/deduplication'

SOURCE_COLORS = {
    'Datatourisme': '#3498db',
    'Apidae': '#2ecc71',
    'TripAdvisor': '#e74c3c',
    'Tourinsoft': '#f39c12',
    'GooglePlaces': '#9b59b6'
}

TYPE_ICONS = {
    'sites': '🏛️',
    'activities': '🎯',
    'accommodations': '🏨',
    'restaurants': '🍽️',
    'events': '🎉'
}


# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

@st.cache_data(ttl=300)
def load_poi_data() -> List[Dict]:
    """Charge les données POI les plus récentes."""
    # Chercher dans l'ordre: deduplicated > output > processed
    search_dirs = [DEDUP_DIR, OUTPUT_DIR, PROCESSED_DIR]
    
    for directory in search_dirs:
        if os.path.exists(directory):
            files = [f for f in os.listdir(directory) if f.endswith('.json') and 'pois' in f]
            if files:
                latest_file = os.path.join(directory, sorted(files)[-1])
                with open(latest_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
    
    return []


@st.cache_data(ttl=300)
def load_dedup_stats() -> Dict:
    """Charge les statistiques de déduplication."""
    if os.path.exists(DEDUP_DIR):
        files = [f for f in os.listdir(DEDUP_DIR) if f.startswith('dedup_stats_')]
        if files:
            latest_file = os.path.join(DEDUP_DIR, sorted(files)[-1])
            with open(latest_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    return {}


def generate_sample_data() -> List[Dict]:
    """Génère des données d'exemple si aucune donnée n'est disponible."""
    import random
    
    pois = []
    sources = list(SOURCE_COLORS.keys())
    types = list(TYPE_ICONS.keys())
    regions = ['Ile-de-France', 'Provence-Alpes-Côte d\'Azur', 'Auvergne-Rhône-Alpes', 
               'Nouvelle-Aquitaine', 'Occitanie', 'Bretagne']
    
    for i in range(100):
        region = random.choice(regions)
        lat_base = {
            'Ile-de-France': 48.8,
            'Provence-Alpes-Côte d\'Azur': 43.5,
            'Auvergne-Rhône-Alpes': 45.5,
            'Nouvelle-Aquitaine': 44.5,
            'Occitanie': 43.5,
            'Bretagne': 48.0
        }.get(region, 46.0)
        
        lon_base = {
            'Ile-de-France': 2.3,
            'Provence-Alpes-Côte d\'Azur': 5.5,
            'Auvergne-Rhône-Alpes': 4.5,
            'Nouvelle-Aquitaine': -0.5,
            'Occitanie': 2.0,
            'Bretagne': -2.5
        }.get(region, 2.0)
        
        poi = {
            'id': i + 1,
            'poi_name': {'fr': f"POI Test {i+1}"},
            'types': [random.choice(types)],
            'tags': [f"tag_{random.randint(1, 10)}" for _ in range(random.randint(1, 3))],
            'addresses': [{
                'city': f"Ville_{random.randint(1, 50)}",
                'region': region,
                'zip_code': str(random.randint(10000, 99999))
            }],
            'geopoints': [{
                'latitude': lat_base + random.uniform(-1, 1),
                'longitude': lon_base + random.uniform(-1, 1)
            }],
            'sources': [{
                'source': random.choice(sources),
                'reference': f"REF{random.randint(10000, 99999)}"
            }],
            'closed': random.random() < 0.05,
            'display': random.random() > 0.02,
            'ratings': {
                'distributions': [{
                    'type': 'general',
                    'values': [{'nb_ratings': random.randint(10, 500), 'value': v} 
                              for v in [0, 0.25, 0.5, 0.75, 1]]
                }]
            } if random.random() > 0.3 else None
        }
        pois.append(poi)
    
    return pois


def pois_to_dataframe(pois: List[Dict]) -> pd.DataFrame:
    """Convertit les POI en DataFrame pour l'analyse."""
    rows = []
    
    for poi in pois:
        row = {
            'id': poi.get('id'),
            'name': poi.get('poi_name', {}).get('fr', 'Sans nom'),
            'type': poi.get('types', ['unknown'])[0] if poi.get('types') else 'unknown',
            'tags_count': len(poi.get('tags', [])),
            'closed': poi.get('closed', False),
            'display': poi.get('display', True),
        }
        
        # Source
        if poi.get('sources'):
            row['source'] = poi['sources'][0].get('source', 'unknown')
            row['reference'] = poi['sources'][0].get('reference', '')
        else:
            row['source'] = 'unknown'
            row['reference'] = ''
        
        # Adresse
        if poi.get('addresses'):
            addr = poi['addresses'][0]
            row['city'] = addr.get('city', '')
            row['region'] = addr.get('region', '')
            row['zip_code'] = addr.get('zip_code', '')
        else:
            row['city'] = ''
            row['region'] = ''
            row['zip_code'] = ''
        
        # Coordonnées
        if poi.get('geopoints'):
            geo = poi['geopoints'][0]
            row['latitude'] = geo.get('latitude')
            row['longitude'] = geo.get('longitude')
        else:
            row['latitude'] = None
            row['longitude'] = None
        
        # Ratings
        if poi.get('ratings') and poi['ratings'].get('distributions'):
            dist = poi['ratings']['distributions'][0]
            total_ratings = sum(v.get('nb_ratings', 0) for v in dist.get('values', []))
            weighted_sum = sum(v.get('nb_ratings', 0) * v.get('value', 0) for v in dist.get('values', []))
            row['avg_rating'] = weighted_sum / total_ratings if total_ratings > 0 else None
            row['total_ratings'] = total_ratings
        else:
            row['avg_rating'] = None
            row['total_ratings'] = 0
        
        rows.append(row)
    
    return pd.DataFrame(rows)


# ============================================================================
# COMPOSANTS UI
# ============================================================================

def render_header():
    """Affiche l'en-tête de l'application."""
    st.markdown("""
    <div class="main-header">
        <h1>📍 POI Dashboard</h1>
        <p>Module 3 - Pipeline ETL Airflow pour Points Of Interest</p>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar(df: pd.DataFrame) -> Dict:
    """Affiche la sidebar avec les filtres."""
    with st.sidebar:
        st.title("⚙️ Filtres")
        
        filters = {}
        
        # Filtre par source
        sources = ['Toutes'] + sorted(df['source'].unique().tolist())
        filters['source'] = st.selectbox("Source", sources)
        
        # Filtre par type
        types = ['Tous'] + sorted(df['type'].unique().tolist())
        filters['type'] = st.selectbox("Type", types)
        
        # Filtre par région
        regions = ['Toutes'] + sorted(df['region'].dropna().unique().tolist())
        filters['region'] = st.selectbox("Région", regions)
        
        # Filtre statut
        st.subheader("Statut")
        filters['show_closed'] = st.checkbox("Afficher les POI fermés", value=True)
        filters['show_hidden'] = st.checkbox("Afficher les POI masqués", value=True)
        
        st.divider()
        
        # Informations
        st.info(f"""
        **Données chargées:**
        - {len(df)} POI
        - {df['source'].nunique()} sources
        - {df['region'].nunique()} régions
        """)
        
        return filters


def apply_filters(df: pd.DataFrame, filters: Dict) -> pd.DataFrame:
    """Applique les filtres au DataFrame."""
    filtered = df.copy()
    
    if filters['source'] != 'Toutes':
        filtered = filtered[filtered['source'] == filters['source']]
    
    if filters['type'] != 'Tous':
        filtered = filtered[filtered['type'] == filters['type']]
    
    if filters['region'] != 'Toutes':
        filtered = filtered[filtered['region'] == filters['region']]
    
    if not filters['show_closed']:
        filtered = filtered[filtered['closed'] == False]
    
    if not filters['show_hidden']:
        filtered = filtered[filtered['display'] == True]
    
    return filtered


def render_metrics(df: pd.DataFrame, dedup_stats: Dict):
    """Affiche les métriques principales."""
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total POI", len(df))
    
    with col2:
        st.metric("Sources", df['source'].nunique())
    
    with col3:
        st.metric("Régions", df['region'].nunique())
    
    with col4:
        closed_rate = df['closed'].sum() / len(df) * 100 if len(df) > 0 else 0
        st.metric("Taux fermés", f"{closed_rate:.1f}%")
    
    with col5:
        if dedup_stats:
            reduction = dedup_stats.get('reduction_rate', 0) * 100
            st.metric("Réduction doublons", f"{reduction:.1f}%")
        else:
            st.metric("Réduction doublons", "N/A")


def render_map(df: pd.DataFrame):
    """Affiche la carte des POI."""
    st.subheader("🗺️ Carte des POI")
    
    # Filtrer les POI avec coordonnées
    map_df = df.dropna(subset=['latitude', 'longitude'])
    
    if len(map_df) == 0:
        st.warning("Aucun POI avec coordonnées valides")
        return
    
    # Créer la carte centrée sur la France
    center_lat = map_df['latitude'].mean()
    center_lon = map_df['longitude'].mean()
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=6)
    
    # Ajouter les marqueurs
    for _, row in map_df.iterrows():
        color = {
            'Datatourisme': 'blue',
            'Apidae': 'green',
            'TripAdvisor': 'red',
            'Tourinsoft': 'orange',
            'GooglePlaces': 'purple'
        }.get(row['source'], 'gray')
        
        icon = TYPE_ICONS.get(row['type'], '📍')
        
        popup_html = f"""
        <b>{row['name']}</b><br>
        Type: {icon} {row['type']}<br>
        Source: {row['source']}<br>
        Ville: {row['city']}<br>
        Région: {row['region']}
        """
        
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=6,
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.7,
            popup=folium.Popup(popup_html, max_width=300)
        ).add_to(m)
    
    # Afficher la carte
    st_folium(m, width=None, height=500)
    
    st.caption(f"📍 {len(map_df)} POI affichés sur la carte")


def render_charts(df: pd.DataFrame):
    """Affiche les graphiques d'analyse."""
    st.subheader("📊 Analyse des données")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Par Source", "Par Type", "Par Région", "Ratings"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribution par source
            source_counts = df['source'].value_counts()
            fig = px.pie(
                values=source_counts.values,
                names=source_counts.index,
                title="Distribution par Source",
                color=source_counts.index,
                color_discrete_map=SOURCE_COLORS
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Barplot par source
            fig = px.bar(
                x=source_counts.index,
                y=source_counts.values,
                title="Nombre de POI par Source",
                labels={'x': 'Source', 'y': 'Nombre de POI'},
                color=source_counts.index,
                color_discrete_map=SOURCE_COLORS
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribution par type
            type_counts = df['type'].value_counts()
            fig = px.pie(
                values=type_counts.values,
                names=type_counts.index,
                title="Distribution par Type"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Barplot par type et source
            cross_tab = pd.crosstab(df['type'], df['source'])
            fig = px.bar(
                cross_tab,
                title="Types de POI par Source",
                barmode='group'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # Top régions
        region_counts = df['region'].value_counts().head(10)
        fig = px.bar(
            x=region_counts.values,
            y=region_counts.index,
            orientation='h',
            title="Top 10 Régions par nombre de POI",
            labels={'x': 'Nombre de POI', 'y': 'Région'}
        )
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        # Distribution des ratings
        rated_df = df.dropna(subset=['avg_rating'])
        
        if len(rated_df) > 0:
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.histogram(
                    rated_df,
                    x='avg_rating',
                    nbins=20,
                    title="Distribution des Notes Moyennes",
                    labels={'avg_rating': 'Note moyenne'}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.scatter(
                    rated_df,
                    x='total_ratings',
                    y='avg_rating',
                    color='source',
                    title="Notes vs Nombre d'avis",
                    labels={'total_ratings': 'Nombre d\'avis', 'avg_rating': 'Note moyenne'},
                    color_discrete_map=SOURCE_COLORS
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Aucune donnée de rating disponible")


def render_data_table(df: pd.DataFrame):
    """Affiche le tableau des données."""
    st.subheader("📋 Données détaillées")
    
    # Colonnes à afficher
    display_cols = ['id', 'name', 'type', 'source', 'city', 'region', 'avg_rating', 'closed']
    
    # Formatage
    display_df = df[display_cols].copy()
    display_df['avg_rating'] = display_df['avg_rating'].apply(
        lambda x: f"{x:.2f}" if pd.notna(x) else "-"
    )
    display_df['closed'] = display_df['closed'].apply(lambda x: "🔴 Fermé" if x else "🟢 Ouvert")
    
    # Afficher avec recherche
    search = st.text_input("🔍 Rechercher", placeholder="Nom, ville, région...")
    
    if search:
        mask = display_df.apply(
            lambda row: search.lower() in str(row).lower(),
            axis=1
        )
        display_df = display_df[mask]
    
    st.dataframe(display_df, use_container_width=True, height=400)
    
    # Export
    col1, col2 = st.columns([1, 4])
    with col1:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Exporter CSV",
            csv,
            f"pois_export_{datetime.now().strftime('%Y%m%d')}.csv",
            "text/csv"
        )


def render_dedup_analysis(dedup_stats: Dict):
    """Affiche l'analyse de déduplication."""
    st.subheader("🔍 Analyse de Déduplication")
    
    if not dedup_stats:
        st.info("Aucune statistique de déduplication disponible. Exécutez le DAG de déduplication.")
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "POI avant déduplication",
            dedup_stats.get('input_count', 'N/A')
        )
    
    with col2:
        st.metric(
            "POI après déduplication",
            dedup_stats.get('output_count', 'N/A')
        )
    
    with col3:
        reduction = dedup_stats.get('reduction_rate', 0) * 100
        st.metric(
            "Taux de réduction",
            f"{reduction:.2f}%"
        )
    
    # Détails de l'agrégation
    if 'aggregation_stats' in dedup_stats:
        stats = dedup_stats['aggregation_stats']
        
        st.markdown("### Méthodes de détection")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = go.Figure(data=[
                go.Bar(
                    x=['Références communes', 'Similarité'],
                    y=[
                        stats.get('by_method', {}).get('common_reference', 0),
                        stats.get('by_method', {}).get('similarity', 0)
                    ],
                    marker_color=['#3498db', '#2ecc71']
                )
            ])
            fig.update_layout(title="Groupes détectés par méthode")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Pie chart
            labels = ['POI agrégés', 'POI uniques']
            values = [
                stats.get('pois_aggregated', 0),
                stats.get('unique_pois_kept', 0)
            ]
            
            fig = px.pie(
                values=values,
                names=labels,
                title="Répartition des POI"
            )
            st.plotly_chart(fig, use_container_width=True)


# ============================================================================
# APPLICATION PRINCIPALE
# ============================================================================

def main():
    """Point d'entrée de l'application."""
    
    # En-tête
    render_header()
    
    # Charger les données
    with st.spinner("Chargement des données..."):
        pois = load_poi_data()
        
        if not pois:
            st.warning("Aucune donnée trouvée. Génération de données d'exemple...")
            pois = generate_sample_data()
        
        df = pois_to_dataframe(pois)
        dedup_stats = load_dedup_stats()
    
    # Sidebar avec filtres
    filters = render_sidebar(df)
    
    # Appliquer les filtres
    filtered_df = apply_filters(df, filters)
    
    # Afficher les données filtrées
    st.caption(f"📊 {len(filtered_df)} POI affichés (sur {len(df)} total)")
    
    # Métriques
    render_metrics(filtered_df, dedup_stats)
    
    st.divider()
    
    # Tabs principales
    main_tab1, main_tab2, main_tab3, main_tab4 = st.tabs([
        "🗺️ Carte", "📊 Graphiques", "📋 Données", "🔍 Déduplication"
    ])
    
    with main_tab1:
        render_map(filtered_df)
    
    with main_tab2:
        render_charts(filtered_df)
    
    with main_tab3:
        render_data_table(filtered_df)
    
    with main_tab4:
        render_dedup_analysis(dedup_stats)
    
    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #888;'>
        <p>Module 3 - Pipeline ETL Airflow | Formation Data Engineering</p>
        <p>📍 Points Of Interest Dashboard</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == '__main__':
    main()
