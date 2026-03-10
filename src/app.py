import streamlit as st
import pandas as pd
from datetime import datetime
import uuid

from src.storage import load_data, save_data
from src.analyzer import analyze_feedback
from src.config import LLM_API_KEY

def main():
    st.set_page_config(page_title="Feedback Dashboard", page_icon="📊", layout="wide")
    st.title("Dashboard d'analyse de Feedback Client")
    
    if not LLM_API_KEY:
        st.warning("Clé API LLM non trouvée. Veuillez configurer le fichier .env.")
        st.stop()

    # Charger les données existantes
    feedbacks = load_data()

    # --- Section Upload ---
    st.sidebar.header("Importer des Feedbacks")
    uploaded_file = st.sidebar.file_uploader("Fichier CSV", type=["csv"])
    
    if uploaded_file is not None:
        try:
            df_new = pd.read_csv(uploaded_file)
            st.sidebar.success(f"{len(df_new)} lignes détectées.")
            
            # Sélectionner la colonne contenant le texte
            text_col = st.sidebar.selectbox("Colonne de texte", df_new.columns)
            
            # Bouton d'analyse
            if st.sidebar.button("Analyser les nouveaux feedbacks"):
                num_to_analyze = len(df_new)
                progress_bar = st.sidebar.progress(0)
                status_text = st.sidebar.empty()
                
                new_data = []
                for i, row in df_new.iterrows():
                    feedback_text = str(row[text_col])
                    if not feedback_text.strip():
                        continue
                        
                    status_text.text(f"Analyse {i+1}/{num_to_analyze}...")
                    analysis = analyze_feedback(feedback_text)
                    
                    item = {
                        "id": str(uuid.uuid4()),
                        "date": datetime.now().isoformat(),
                        "text": feedback_text,
                        "sentiment": analysis.get("sentiment", "Neutre"),
                        "themes": analysis.get("themes", [])
                    }
                    new_data.append(item)
                    progress_bar.progress((i + 1) / num_to_analyze)
                
                feedbacks.extend(new_data)
                save_data(feedbacks)
                st.sidebar.success("Analyse terminée ! Données sauvegardées.")
                st.rerun() # Refresh dashboard
                
        except Exception as e:
            st.sidebar.error(f"Erreur de lecture: {e}")

    # --- Section Dashboard ---
    if not feedbacks:
        st.info("Aucun feedback analysé pour le moment. Veuillez importer un fichier CSV avec des textes.")
        return

    df = pd.DataFrame(feedbacks)
    
    # KPIs
    st.markdown("### Vue Globale")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Feedbacks", len(df))
    
    # Répartition des sentiments
    sentiment_counts = df['sentiment'].value_counts()
    pos_count = sentiment_counts.get("Positif", 0)
    neg_count = sentiment_counts.get("Négatif", 0)
    
    col2.metric("Feedbacks Positifs", f"{pos_count} ({pos_count/len(df):.0%})" if len(df) > 0 else "0")
    col3.metric("Feedbacks Négatifs", f"{neg_count} ({neg_count/len(df):.0%})" if len(df) > 0 else "0")

    st.divider()

    col_charts1, col_charts2 = st.columns(2)

    with col_charts1:
        st.markdown("### Répartition des Sentiments")
        st.bar_chart(sentiment_counts)

    with col_charts2:
        st.markdown("### Top Thèmes Abordés")
        # Explode themes logic: since each feedback has a list of themes, we flatten them
        all_themes = []
        for themes in df['themes']:
            if isinstance(themes, list):
                all_themes.extend(themes)
        
        if all_themes:
            theme_counts = pd.Series(all_themes).value_counts().head(10)
            st.bar_chart(theme_counts)
        else:
            st.write("Aucun thème détecté.")

    st.divider()

    col_top1, col_top2 = st.columns(2)
    
    with col_top1:
        st.markdown("###  Exemples Récents Positifs")
        df_pos = df[df['sentiment'] == 'Positif'].tail(3)
        for _, row in df_pos.iterrows():
            with st.container(border=True):
                st.write(f'"{row["text"]}"')
                st.caption(f"Thèmes: {', '.join(row['themes'])}")

    with col_top2:
        st.markdown("###  Exemples Récents Négatifs")
        df_neg = df[df['sentiment'] == 'Négatif'].tail(3)
        for _, row in df_neg.iterrows():
            with st.container(border=True):
                st.write(f'"{row["text"]}"')
                st.caption(f"Thèmes: {', '.join(row['themes'])}")

if __name__ == "__main__":
    main()
