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


# Fonction pour générer un texte pour l'histoire
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


# Fonction pour générer l'histoire avec des choix
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

        # Afficher le contenu de la page
        st.session_state.story_pages.append(page_content)
        display_page(page_content)

        field.empty()


# Fonction pour afficher une page d'histoire et proposer des choix
def display_page(content):
    # Afficher le texte de la page
    for paragraph in content:
        st.markdown(paragraph)

    # Proposer des choix (par exemple, trois options de suite)
    options = ["Aller dans la forêt", "Aller au village", "Aller à la montagne"]
    st.session_state.choices.append(options)

    # Générer une clé unique en fonction de la page et de l'index du choix
    for idx, option in enumerate(options):
        # Générer une clé unique pour chaque élément radio
        key = f"choices_{st.session_state.current_page}_{idx}"

        # Afficher les boutons de choix avec une clé unique
        selected_choice = st.radio(
            "Que voulez-vous faire ?",
            options=[option],
            key=key
        )

        # Lorsque l'utilisateur choisit une option
        if selected_choice:
            st.session_state.current_choice = selected_choice
            st.button("Suivant", on_click=next_page)


# Fonction pour naviguer à la page suivante selon le choix de l'utilisateur
def next_page():
    # Logique pour gérer les différents scénarios selon les choix de l'utilisateur
    if st.session_state.current_choice == "Aller dans la forêt":
        next_prompt = "L'histoire continue avec un voyage dans la forêt magique."
    elif st.session_state.current_choice == "Aller au village":
        next_prompt = "L'histoire continue avec un voyage dans le village mystérieux."
    else:
        next_prompt = "L'histoire continue avec un voyage à la montagne enneigée."

    # Générer la nouvelle page de l'histoire
    generate_story(next_prompt)


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
