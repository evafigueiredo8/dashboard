import json
import os
from openai import OpenAI
from src.config import LLM_API_KEY

if not LLM_API_KEY:
    print("Warning: LLM_API_KEY not found in environment variables.")

# Initialisation du client OpenAI (ou compatible)
client = OpenAI(api_key=LLM_API_KEY) if LLM_API_KEY else None

def analyze_feedback(feedback_text):
    """
    Analyse un feedback client avec un LLM.
    Retourne un dictionnaire avec { 'sentiment': 'Positif'|'Négatif'|'Neutre', 'themes': ['theme1', 'theme2'] }
    """
    if not client:
        return {"error": "API Key missing"}

    prompt = f"""
    Tu es un expert en analyse de feedback client.
    Analyse le feedback suivant et extrait:
    1. Le sentiment global (choisis uniquement : Positif, Négatif ou Neutre)
    2. 2 à 3 thèmes principaux (ex: "livraison", "produit", "service client", "prix")

    Feedback : "{feedback_text}"

    Réponds STRICTEMENT au format JSON avec cette structure :
    {{
      "sentiment": "Positif/Négatif/Neutre",
      "themes": ["theme1", "theme2"]
    }}
    Ne rajoute pas de markdown ou de texte autour. Uniquement du JSON valide.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", # Modèle par défaut (modifiable)
            messages=[
                {"role": "system", "content": "Tu es un assistant qui renvoie uniquement du JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            response_format={ "type": "json_object" }
        )
        
        result_text = response.choices[0].message.content
        result_json = json.loads(result_text)
        return result_json

    except Exception as e:
        print(f"Error during LLM analysis: {e}")
        return {"error": str(e), "sentiment": "Erreur", "themes": []}
