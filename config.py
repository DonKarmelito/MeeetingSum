import streamlit as st
from dotenv import dotenv_values
import openai
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance

load_dotenv_values = dotenv_values(".env")

def get_secret(key):
    """Czyta sekret z .env (lokalnie) lub st.secrets (Streamlit Cloud)."""
    if key in load_dotenv_values:
        return load_dotenv_values[key]
    if key in st.secrets:
        return st.secrets[key]
    return None

def init_openai():
    """Inicjalizuje i zwraca klienta OpenAI."""
    if not st.session_state.get("openai_api_key"):
        api_key = get_secret("OPENAI_API_KEY")
        if api_key:
            st.session_state["openai_api_key"] = api_key
        else:
            st.info("Dodaj klucz API OpenAI")
            st.session_state["openai_api_key"] = st.text_input("Klucz API", type="password")
            if st.session_state["openai_api_key"]:
                st.rerun()

    if not st.session_state.get("openai_api_key"):
        st.stop()

    return openai.OpenAI(api_key=st.session_state["openai_api_key"])

def init_qdrant():
    """Inicjalizuje i zwraca klienta Qdrant oraz status połączenia."""
    COLLECTION_NAME = "spotkania"
    try:
        qdrant = QdrantClient(
            url=get_secret("QDRANT_URL"),
            api_key=get_secret("QDRANT_API_KEY")
        )
        if not qdrant.collection_exists(COLLECTION_NAME):
            qdrant.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
            )
        return qdrant, COLLECTION_NAME, True
    except Exception as e:
        st.warning(f"Brak połączenia z Qdrant: {e}")
        return None, COLLECTION_NAME, False
