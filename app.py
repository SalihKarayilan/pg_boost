import streamlit as st
import google.generativeai as genai
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

# Sayfa yapılandırması
st.set_page_config(page_title="pg_boost", page_icon="🐘", layout="wide")

# Login Check
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("Giriş Yap")
    username = st.text_input("Kullanıcı Adı")
    password = st.text_input("Şifre", type="password")

    # Güvenlik için ortam değişkenlerini kullanın
    expected_user = os.getenv("APP_USERNAME", "admin")
    expected_pass = os.getenv("APP_PASSWORD")

    if st.button("Giriş"):
        if not expected_pass:
            st.error("Sistem hatası: Parola yapılandırılmamış.")
        elif username == expected_user and password == expected_pass:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Hatalı kullanıcı adı veya şifre.")
    st.stop()

st.title("🐘 pg_boost")
st.markdown("""
Bu araç, sorgu yapısını ve tabloları değiştirmeden sadece **veritabanı motoru seviyesinde**
(İndeks, ANALYZE, work_mem) performans iyileştirmeleri üretir.
""")

# Yan menü: API Anahtarı girişi ve Dinamik Model Seçimi
with st.sidebar:
    st.header("⚙️ Ayarlar")

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

    if api_key and provider_choice == "Gemini":
        genai.configure(api_key=api_key)
    elif not api_key:
        st.info("Model seçebilmek için lütfen API anahtarınızı girin.")

st.subheader("Girdiler")

tab1, tab2, tab3 = st.tabs(["SQL Sorgusu", "DDL & İndeksler", "EXPLAIN Çıktısı"])

with tab1:
    sql_query = st.text_area(
        "SQL Sorgusu veya Prosedür",
        height=250,
        placeholder="SELECT * FROM ..."
    )

with tab2:
    ddl_info = st.text_area(
        "Tablo DDL ve Mevcut İndeksler",
        height=250,
        placeholder="CREATE TABLE musteri (...); CREATE INDEX idx_adi ON musteri(adi);"
    )

with tab3:
    explain_output = st.text_area(
        "EXPLAIN Çıktısı (Tercihen JSON formatında)",
        height=250,
        placeholder="EXPLAIN (ANALYZE, COSTS, BUFFERS, FORMAT JSON) SELECT ..."
    )

st.divider()
st.subheader("Optimizasyon Süreci")

if st.button("🚀 Performans Analizi Yap", use_container_width=True):
        if not api_key:
            st.error("Lütfen sol menüden Gemini API anahtarınızı girin.")
        elif not model_choice:
            st.error("Lütfen geçerli bir model seçin.")
        elif not sql_query or not explain_output:
            st.warning("Lütfen SQL sorgusunu ve EXPLAIN çıktısını girin.")
        else:
            with st.spinner(f"{model_choice} analiz ediyor..."):
                try:
                    # LLM'e verilecek kesin talimatlar
                    system_instruction = """
                    Sen kıdemli bir PostgreSQL performans uzmanısın. Kuralların şunlardır:
                    1. Kullanıcının sağladığı sorgunun mantığını, seçilen kolonları veya tablo yapısını KESİNLİKLE DEĞİŞTİRME.
                    2. Sadece sağlanan EXPLAIN ANALYZE çıktısını inceleyerek darboğazları (Seq Scan, yüksek buffers, maliyetli Hash Join vb.) tespit et.
                    3. Çözüm olarak YALNIZCA eksik indeksler için 'CREATE INDEX', istatistik güncellemeleri için 'ANALYZE' ve o oturuma özel 'work_mem' gibi konfigürasyon ayarları üret. KESİNLİKLE 'CONCURRENTLY' kullanma.
                    """

                    # Kullanıcı mesajı
                    user_message = f"""
                    Aşağıdaki PostgreSQL verilerini inceleyerek optimizasyon önerilerini sun:

                    --- DDL VE MEVCUT İNDEKSLER ---
                    {ddl_info if ddl_info else "Belirtilmedi."}

                    --- HEDEF SORGU ---
                    {sql_query}

                    --- EXPLAIN ÇIKTISI ---
                    {explain_output}
                    """

                    async def fetch_analysis():
                        if provider_choice == "Gemini":
                            model = genai.GenerativeModel(
                                model_name=model_choice,
                                system_instruction=system_instruction
                            )
                            response = await model.generate_content_async(user_message)
                            return response.text

                        elif provider_choice == "OpenAI":
                            from openai import AsyncOpenAI
                            client = AsyncOpenAI(api_key=api_key)
                            response = await client.chat.completions.create(
                                model=model_choice,
                                messages=[
                                    {"role": "system", "content": system_instruction},
                                    {"role": "user", "content": user_message}
                                ]
                            )
                            return response.choices[0].message.content

                        elif provider_choice == "Claude":
                            from anthropic import AsyncAnthropic
                            client = AsyncAnthropic(api_key=api_key)
                            response = await client.messages.create(
                                model=model_choice,
                                system=system_instruction,
                                messages=[
                                    {"role": "user", "content": user_message}
                                ],
                                max_tokens=1024
                            )
                            return response.content[0].text

                    response_text = asyncio.run(fetch_analysis())

                    st.success("Analiz Tamamlandı!")

                    # Çıktıyı ekrana yazdır
                    st.markdown("### Sonuç:")
                    st.write(response_text)

                except Exception as e:
                    st.error(f"Bir hata oluştu: {str(e)}")