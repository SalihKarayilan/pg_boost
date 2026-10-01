import streamlit as st
import os

def get_provider_config():
    provider_choice = st.selectbox("Sağlayıcı Seçin", ["Gemini", "OpenAI", "Claude"])

    env_api_key = ""
    if provider_choice == "Gemini":
        env_api_key = os.getenv("GEMINI_API_KEY")
    elif provider_choice == "OpenAI":
        env_api_key = os.getenv("OPENAI_API_KEY")
    elif provider_choice == "Claude":
        env_api_key = os.getenv("ANTHROPIC_API_KEY")

    if env_api_key:
        api_key = env_api_key
        st.success(f"{provider_choice} API Anahtarı .env'den yüklendi! ✅")
    else:
        api_key = st.text_input(f"{provider_choice} API Key", type="password", help="API anahtarınızı girin.")

    st.markdown("[API Key Almak İçin Tıklayın (Google AI Studio)](https://aistudio.google.com/app/apikey)")

    # Dinamik olarak sağlayıcıya uygun modelleri listele
    if provider_choice == "Gemini":
        available_models = ['gemini-1.5-pro', 'gemini-1.5-flash']
    elif provider_choice == "OpenAI":
        available_models = ['gpt-4o', 'gpt-4-turbo']
    elif provider_choice == "Claude":
        available_models = ['claude-3.5-sonnet', 'claude-3-opus-20240229']

    model_choice = st.selectbox("Kullanılabilir Modeller", available_models)

    return provider_choice, api_key, model_choice
