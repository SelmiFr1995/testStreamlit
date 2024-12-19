# from openai import OPENAI
# import streamlit as st

# client = OPENAI()

# value = st.txt_input("Prompt...")
# if (value):
#     txt = st.header("waiting for api ...")
#     completion = client.chat.completions.create(
#         model = "gpt-4o-mini",
#         messages=[
#             {"role":"user","content":value}
#         ]
#     )
# txt.text(completion.choices[0].message.content)


import openai
import streamlit as st
import requests
import os

# Charger la clé API OpenAI depuis l'environnement
openai.api_key = os.getenv("OPENAI_API_KEY")

# Fonction pour appeler l'API OpenAI avec la nouvelle méthode
def openai_api_call(prompt):
    try:
        response = openai.completions.create(
            model="gpt-4",  # Utiliser un modèle comme gpt-4
            messages=[
                {"role": "system", "content": "Vous êtes un assistant expert en détection d'erreurs de code."},
                {"role": "user", "content": prompt}
            ]
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Erreur lors de l'appel à OpenAI : {str(e)}"

# Fonction pour détecter les erreurs de code
def detect_code_errors(code):
    prompt = f"Analyse le code suivant et détecte les erreurs ou propose des améliorations :\n\n{code}"
    return openai_api_call(prompt)

# Fonction pour récupérer le code à partir d'une URL
def fetch_code_from_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            return f"Erreur: Impossible de récupérer le fichier à partir du lien {url}"
    except Exception as e:
        return f"Erreur lors de la récupération du fichier: {str(e)}"

# Interface Streamlit
st.title("Assistant de Détection d'Erreurs de Code")

# Créer un espace pour afficher les messages de chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Afficher tous les messages précédents
for message in st.session_state.messages:
    st.chat_message(message["role"]).markdown(message["content"])

# Ajouter une nouvelle question via st.chat_input
user_input = st.chat_input("Entrez votre code ou votre demande de détection d'erreurs :")

if user_input:
    # Ajouter le message de l'utilisateur à la conversation
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Vérifier si l'entrée est un lien, si oui, récupérer le code
    if user_input.startswith("http"):
        code_input = fetch_code_from_url(user_input)
    else:
        code_input = user_input

    # Analyser le code ou la question de l'utilisateur
    result = detect_code_errors(code_input)

    # Ajouter la réponse du chatbot à la conversation
    st.session_state.messages.append({"role": "assistant", "content": result})

    # Afficher le message du chatbot dans le chat
    st.chat_message("assistant").markdown(result)



