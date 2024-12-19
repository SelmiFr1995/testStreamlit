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

def generer_livre(content):
    completion = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "tu es un assistant qui rédige des livres"},
            {"role": "user", "content": content}
        ],
        max_tokens=2000
    )
    article_text = completion.choices[0].message.content
    
    # Ajouter un formatage pour les titres (par exemple, ajouter un # devant chaque titre)
    article_text = article_text.replace("Titre: ", "# ")  # Vous pouvez ajuster cette logique pour détecter les titres dans le texte
    return article_text

def generate_image(content):
    try:
        response = client.images.generate(
            model="dall-e-2",
            prompt=content,
            n=1,
            size="512x512"
        )
        
        # Debug: Affiche la réponse de l'API
        print(response)  # Affiche la réponse complète pour vérification
        
        # Vérifiez si la réponse contient une URL valide
        if response and "data" in response and len(response["data"]) > 0:
            image_url = response["data"][0]["url"]
            return image_url
        else:
            print("Erreur : Pas d'image générée.")
            return None
    except Exception as e:
        print(f"Erreur lors de la génération de l'image: {e}")
        return None

def generate_audio(text):
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text
    )
    file_path = Path(__file__).parent.parent / "tmp/output.mp3"
    response.setram_to_file(file_path)
    return file_path



def is_title(text):
    """ Détermine si une ligne est un titre """
    return (len(text) <= 100) and re.search("^#", text)

def openai_create_book(content):

    with st.chat_message("user"):
        st.session_state.messages.append({"role": "user", "content": content})
        st.write(content)

    with st.chat_message("assistant"):
        field = st.info("Génération de livre en cours...")
        article_text = generer_livre(content)
        field.success("Livre généré avec succès")
        paragraphs = article_text.split("\n\n")
        for paragraph in paragraphs:
            if paragraph.strip() == 0:
                continue
            st.session_state.messages.append({"role": "assistant", "content": paragraph})
            st.markdown(paragraph)

            if is_title(paragraph):
                image_prompt = f"Illustration pour : {paragraph}"
                field.info(f"Génération de l'image pour : {paragraph}")
                image_url = generate_image(image_prompt)
                
                # Vérifiez si une URL d'image valide a été générée
                if image_url:
                    st.session_state.messages.append({"role": "assistant", "content": image_url})
                    st.image(image_url, caption=paragraph)
                else:
                    print(f"Erreur: Aucun lien d'image généré pour '{paragraph}'")
        field.empty()

# Afficher les messages existants dans la session
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant":
            # Si le message est une URL d'image, afficher l'image
            if isinstance(message["content"], str) and message["content"].startswith("http"):
                st.image(message["content"])
            else:
                st.text(message["content"])
        elif message["role"] == "user":
            st.text(message["content"])
st.title("Histoire Interactive : L'aventure dont vous êtes le héros")

value = st.text_input("Choisissez un thème pour l'histoire (par exemple, aventure, magie, etc.)")

if value and value != "":
    openai_create_book(value)
    value = ""
