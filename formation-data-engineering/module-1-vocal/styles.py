"""
Styles CSS personnalisés pour l'application Streamlit
"""

CUSTOM_CSS = """
<style>
.stApp {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.main-header {
    text-align: center;
    padding: 2rem;
    background: rgba(255,255,255,0.1);
    border-radius: 10px;
    margin-bottom: 2rem;
}
.demo-card {
    background: white;
    padding: 2rem;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    margin-bottom: 1rem;
}
.metric-card {
    background: rgba(255,255,255,0.9);
    padding: 1rem;
    border-radius: 8px;
    text-align: center;
}
.emotion-badge {
    display: inline-block;
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-weight: bold;
    margin: 0.25rem;
}
.emotion-calme {
    background: #3498db;
    color: white;
}
.emotion-joyeux {
    background: #2ecc71;
    color: white;
}
.emotion-triste {
    background: #9b59b6;
    color: white;
}
.emotion-energique {
    background: #e74c3c;
    color: white;
}
</style>
"""

HEADER_HTML = """
<div class="main-header">
    <h1>Module 1: Traitement Vocal</h1>
    <p>Text-to-Speech | Speech-to-Text | Speech-to-Speech | Analyse Audio | Enregistrement Live</p>
</div>
"""


def apply_styles(st):
    """
    Applique les styles CSS personnalisés à l'application Streamlit.

    Args:
        st: Module streamlit
    """
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_header(st):
    """
    Affiche l'en-tête de l'application.

    Args:
        st: Module streamlit
    """
    st.markdown(HEADER_HTML, unsafe_allow_html=True)
