from openai import OpenAI
import streamlit as st
import os
from dotenv import load_dotenv
from pathlib import Path
import re
import time
import json

load_dotenv()
API_KEY=os.getenv("OPEN_API_KEY")
client = OpenAI(api_key=API_KEY)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Fonction pour générer un texte pour le livre
def generer_livre(content):
    completion = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "tu es un assistant qui rédige des livres pour enfants."},
                  {"role": "user", "content": content}],
        max_tokens=2000
    )
    article_text = completion.choices[0].message.content
    article_text = article_text.replace("Titre: ", "# ")  # Formater les titres
    return article_text

# Fonction pour générer des images avec DALL-E
def generate_image(text):
    try:
        response = client.images.generate(
            model="dall-e-2",
            prompt=text,
            n=1,
            size="256x256"
        )
        return response.data[0].url
    except Exception as e:
        print(f"Erreur lors de la génération de l'image: {e}")
        return None

# Fonction pour générer de l'audio avec OpenAI TTS
def generate_audio(text):
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text
        )
        file_path = Path(__file__).parent.parent / "tmp/output.mp3"
        response.setram_to_file(file_path)
        return file_path
    except Exception as e:
        print(f"Erreur lors de la génération de l'audio: {e}")
        return None

# Vérifier si le texte est un titre
def is_title(text):
    return len(text) <= 100 and re.search("^#", text)

# Fonction principale pour générer l'histoire
def generate_story(prompt):
    with st.chat_message("user"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.write(prompt)

    with st.chat_message("assistant"):
        field = st.info("Génération de l'histoire...")
        article_text = generer_livre(prompt)
        paragraphs = article_text.split("\n\n")
        
        # Sélectionner un choix de début d'histoire
        for paragraph in paragraphs:
            if paragraph.strip() == 0:
                continue
            st.session_state.messages.append({"role": "assistant", "content": paragraph})
            st.markdown(paragraph)

            # Générer l'image
            image_prompt = f"Illustration pour : {paragraph[:100]}"
            field.info(f"Génération de l'image pour : {paragraph[:100]}")
            image_url = generate_image(image_prompt)
            if image_url:
                st.session_state.messages.append({"role": "assistant", "content": image_url})
                st.image(image_url, caption=paragraph)

            # Générer l'audio
            field.info(f"Génération de l'audio pour : {paragraph[:100]}")
            audio_path = generate_audio(paragraph)
            if audio_path:
                st.audio(audio_path, autoplay=True)

        field.empty()

# Afficher les messages existants dans la session
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant":
            if isinstance(message["content"], str) and message["content"].startswith("http"):
                st.image(message["content"])
            else:
                st.text(message["content"])
        elif message["role"] == "user":
            st.text(message["content"])

# Titre de l'application
st.title("Histoire Interactive : L'aventure dont vous êtes le héros")

# Entrée de l'utilisateur pour le thème
value = st.text_input("Choisissez un thème pour l'histoire (par exemple, aventure, magie, etc.)")

# Si un thème est fourni, générer une histoire
if value and value != "":
    generate_story(value)
    value = ""

# Ajouter des boutons de choix pour l'interactivité
if "current_page" not in st.session_state:
    st.session_state.current_page = 0

# Ajouter des boutons pour naviguer dans l'histoire
def next_page():
    st.session_state.current_page += 1

def previous_page():
    st.session_state.current_page -= 1

if st.session_state.current_page < len(st.session_state.messages) - 1:
    st.button("Suivant", on_click=next_page)
else:
    st.button("Fin de l'histoire")
