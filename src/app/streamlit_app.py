import streamlit as st
from streamlit_drawable_canvas import st_canvas
import requests
import numpy as np
from PIL import Image
import io
import sys
import os

# Configuration de la page
st.set_page_config(
    page_title="Classification MNIST",
    page_icon="🔢",
    layout="wide"
)

# Titre principal
st.title("🔢 Classification de chiffres MNIST")
st.markdown("---")

# Configuration de l'API
API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1/predict")

# Sidebar avec informations
with st.sidebar:
    st.header("ℹ️ Informations")
    st.markdown("""
    Cette application utilise un réseau de neurones convolutionnel 
    pour classifier des images de chiffres manuscrits (0-9).
    
    **Instructions :**
    1. Dessinez un chiffre dans le canvas blanc
    2. Le dessin sera automatiquement redimensionné en 28x28 pixels
    3. Le modèle prédit le chiffre avec un score de confiance
    
    **Conseils de dessin :**
    - Utilisez un trait assez épais
    - Centrez le chiffre dans le canvas
    - Dessinez en noir sur fond blanc
    """)
    
    st.markdown("---")
    st.markdown("**API Status**")
    try:
        health_url = os.getenv("API_URL", "http://localhost:8000/api/v1/predict").replace("/api/v1/predict", "/")
        response = requests.get(health_url, timeout=2)
        if response.status_code == 200:
            st.success("🟢 API en ligne")
        else:
            st.error("🔴 API inaccessible")
    except:
        st.error("🔴 API non démarrée")
        st.markdown("Lancez d'abord : `uvicorn src.app.main:app --reload`")

# Interface principale
col1, col2 = st.columns([1, 1])

with col1:
    st.header("✏️ Dessinez un chiffre")
    
    # Canvas de dessin
    canvas_result = st_canvas(
        fill_color="rgba(255, 255, 255, 0.0)",  # Fond transparent
        stroke_width=20,
        stroke_color="#000000",
        background_color="#FFFFFF",
        width=280,
        height=280,
        drawing_mode="freedraw",
        point_display_radius=0,
        display_toolbar=True,
        key="canvas",
    )
    
    # Bouton pour vider le canvas
    if st.button("🗑️ Effacer", help="Efface le dessin"):
        st.rerun()
    
    drawn_image = None
    if canvas_result.image_data is not None:
        # Convertir en image PIL
        img_data = canvas_result.image_data
        img = Image.fromarray(img_data.astype('uint8'), 'RGBA')
        
        # Convertir en niveaux de gris
        img_gray = img.convert('L')
        
        # Redimensionner à 28x28
        img_resized = img_gray.resize((28, 28), Image.LANCZOS)
        
        # Afficher le résultat redimensionné
        st.image(img_resized, caption="Votre dessin (28x28)", width=200)
        
        drawn_image = img_resized

with col2:
    st.header("🎯 Résultats de prédiction")
    
    if drawn_image is not None:
        if st.button("🚀 Prédire", type="primary"):
            try:
                # Convertir l'image en bytes
                img_buffer = io.BytesIO()
                drawn_image.save(img_buffer, format='PNG')
                img_bytes = img_buffer.getvalue()
                
                # Préparer la requête
                files = {"file": img_bytes}
                
                with st.spinner("Prédiction en cours..."):
                    response = requests.post(API_URL, files=files, timeout=10)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Affichage des résultats
                    st.success("✅ Prédiction réussie!")
                    
                    # Résultat principal
                    predicted_class = result["predicted_class"]
                    confidence = result["confidence"]
                    
                    st.metric(
                        label="Chiffre prédit",
                        value=str(predicted_class),
                        delta=f"Confiance: {confidence:.2%}"
                    )
                    
                    # Graphique des probabilités
                    st.subheader("📊 Probabilités par classe")
                    probs = result["probabilities"]
                    
                    prob_data = {
                        'Chiffre': list(range(10)),
                        'Probabilité': probs
                    }
                    
                    st.bar_chart(prob_data, x='Chiffre', y='Probabilité')
                    
                    # Tableau détaillé
                    with st.expander("📋 Détails des probabilités"):
                        for i, prob in enumerate(probs):
                            col_a, col_b = st.columns([1, 3])
                            with col_a:
                                st.write(f"**{i}**")
                            with col_b:
                                st.progress(prob)
                                st.caption(f"{prob:.4f}")
                
                else:
                    st.error(f"❌ Erreur API: {response.status_code}")
                    st.json(response.json())
                    
            except requests.exceptions.ConnectionError:
                st.error("❌ Impossible de se connecter à l'API")
                st.info("Assurez-vous que le serveur FastAPI est démarré")
            except Exception as e:
                st.error(f"❌ Erreur: {str(e)}")
    else:
        st.info("👆 Dessinez un chiffre dans le canvas pour commencer la prédiction")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p>🧠 Modèle: ConvNet | 🔧 FastAPI + Streamlit</p>
    </div>
    """, 
    unsafe_allow_html=True
) 