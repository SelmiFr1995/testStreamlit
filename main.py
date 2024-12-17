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

openai.api_key = os.getenv("OPENAI_API_KEY")

def openai_api_call(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4", 
            messages=[
                {"role": "system", "content": "Vous êtes un assistant expert en détection d'erreurs de code."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        return f"Erreur lors de l'appel à OpenAI : {str(e)}"


def detect_code_errors(code):
    prompt = f"Analyse le code suivant et détecte les erreurs ou propose des améliorations :\n\n{code}"
    return openai_api_call(prompt)


def fetch_code_from_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            return f"Erreur: Impossible de récupérer le fichier à partir du lien {url}"
    except Exception as e:
        return f"Erreur lors de la récupération du fichier: {str(e)}"


st.title("Assistant de Détection d'Erreurs de Code")


code_input = st.text_area("Entrez votre code ici :", height=200)


code_link = st.text_input("Entrez l'URL d'un fichier de code GitHub ou autre lien :")

if code_link:
    code_input = fetch_code_from_url(code_link)

if st.button("Analyser le code"):
    if code_input:
        result = detect_code_errors(code_input)
        st.subheader("Suggestions et erreurs détectées :")
        st.write(result)
    else:
        st.error("Veuillez entrer du code pour l'analyse.")

