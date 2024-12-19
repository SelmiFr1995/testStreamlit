from openai import OpenAI
import streamlit as st
import os
from dotenv import load_dotenv
from pathlib import Path
import re
import time
import json

load_dotenv()
API_KEY = os.getenv("OPEN_API_KEY")
client = OpenAI(api_key=API_KEY)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "story_pages" not in st.session_state:
    st.session_state.story_pages = []  # Pour stocker l'ensemble des pages de l'histoire

if "choices" not in st.session_state:
    st.session_state.choices = []  # Pour stocker les choix à chaque page

if "current_page" not in st.session_state:
    st.session_state.current_page = 0  # Pour suivre la page actuelle

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
        # Appel à l'API de synthèse vocale (TTS)
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text
        )
        
        # Afficher la réponse brute pour débogage
        st.write(f"Réponse de l'API TTS: {response}")

        # Si la réponse contient un URL audio, le retourner
        if "audio_url" in response:
            audio_url = response["audio_url"]
            return audio_url
        else:
            st.error("Aucun audio URL retourné par l'API.")
            return None

    except Exception as e:
        st.error(f"Erreur lors de la génération de l'audio: {e}")
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
        page_content = []
        for paragraph in paragraphs:
            if paragraph.strip() == 0:
                continue
            page_content.append(paragraph)

        # Stocker la page générée
        st.session_state.story_pages.append(page_content)

        # Afficher la page
        display_page(page_content)

        field.empty()

# Fonction pour afficher une page d'histoire et proposer des choix
def display_page(content):
    # Afficher le texte de la page
    for paragraph in content:
        st.markdown(paragraph)

    # Générer l'image et l'audio
    image_prompt = f"Illustration pour : {content[0][:100]}"  # Utiliser le début de la première phrase pour l'illustration
    image_url = generate_image(image_prompt)
    if image_url:
        st.image(image_url, caption=content[0])

    # Générer l'audio pour cette page
    audio_url = generate_audio(content[0])
    if audio_url:
        st.audio(audio_url, autoplay=True)
    else:
        st.error("Erreur lors de la génération de l'audio.")

# Navigation entre les pages
def next_page():
    # Si ce n'est pas la dernière page, augmenter le compteur de pages
    if st.session_state.current_page < len(st.session_state.story_pages) - 1:
        st.session_state.current_page += 1
        display_page(st.session_state.story_pages[st.session_state.current_page])

def previous_page():
    # Si ce n'est pas la première page, diminuer le compteur de pages
    if st.session_state.current_page > 0:
        st.session_state.current_page -= 1
        display_page(st.session_state.story_pages[st.session_state.current_page])

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

# Navigation et affichage des boutons pour "Suivant" et "Précédent"
if len(st.session_state.story_pages) > 0:
    page_content = st.session_state.story_pages[st.session_state.current_page]
    display_page(page_content)

    if st.session_state.current_page < len(st.session_state.story_pages) - 1:
        st.button("Suivant", on_click=next_page)
    else:
        st.button("Fin de l'histoire")

    if st.session_state.current_page > 0:
        st.button("Précédent", on_click=previous_page)
