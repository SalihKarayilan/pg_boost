import streamlit as st
import google.generativeai as genai
import asyncio

# Sayfa yapılandırması
st.set_page_config(page_title="pg_boost", page_icon="🐘", layout="wide")

st.title("🐘 pg_boost")
st.divider()

st.info("""
Bu araç, sorgu yapısını ve tabloları değiştirmeden sadece **veritabanı motoru seviyesinde**
(İndeks, ANALYZE, work_mem) performans iyileştirmeleri üretir.
""")

# Modernize the Main Dashboard CSS
st.markdown("""
<style>
.stTextInput, .stTextArea { border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# Session State for Authentication
if 'api_key' not in st.session_state:
    st.session_state.api_key = ''

if not st.session_state.api_key:
    # Compact Login Screen
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 🔐 Giriş Yap")
        with st.form("login_form"):
            api_key_input = st.text_input("Gemini API Key", type="password", help="Google AI Studio'dan aldığınız API anahtarını girin.")
            st.markdown("[API Key Almak İçin Tıklayın (Google AI Studio)](https://aistudio.google.com/app/apikey)")
            submit_button = st.form_submit_button("Giriş", use_container_width=True)
            if submit_button:
                if api_key_input:
                    st.session_state.api_key = api_key_input
                    st.rerun()
                else:
                    st.error("Lütfen bir API anahtarı girin.")
else:
    # Main Dashboard
    # Yan menü: Dinamik Model Seçimi
    with st.sidebar:
        st.header("⚙️ Ayarlar")
        st.success("API Anahtarı başarıyla alındı! ✅")

        if st.button("Çıkış Yap"):
            st.session_state.api_key = ''
            st.rerun()

        st.divider()

        model_choice = None
        try:
            genai.configure(api_key=st.session_state.api_key)

            # API anahtarına tanımlı ve generateContent destekleyen modelleri dinamik olarak çek
            available_models = []
            for m in genai.list_models():
                if "generateContent" in m.supported_generation_methods and not any(x in m.name.lower() for x in ["preview", "tts", "vision", "gemma"]):
                    # 'models/' önekini temizleyerek listeye ekle
                    model_name = m.name.replace("models/", "")
                    available_models.append(model_name)

            if available_models:
                model_choice = st.selectbox("Kullanılabilir Modeller", available_models)
                st.caption("Eğer listede 'gemini-1.5-pro' gibi modeller görüyorsanız, karmaşık EXPLAIN çıktıları için onu tercih edebilirsiniz.")
            else:
                st.error("Bu API anahtarıyla kullanılabilecek geçerli bir model bulunamadı.")

        except Exception as e:
            st.error(f"Modeller listelenirken bir hata oluştu: {str(e)}")

    # Yan yana iki kolon oluşturarak ekranı verimli kullanalım
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("1. Girdiler")

        sql_query = st.text_area(
            "SQL Sorgusu veya Prosedür",
            height=150,
            placeholder="SELECT * FROM ..."
        )

        ddl_info = st.text_area(
            "Tablo DDL ve Mevcut İndeksler",
            height=150,
            placeholder="CREATE TABLE musteri (...); CREATE INDEX idx_adi ON musteri(adi);"
        )

        explain_output = st.text_area(
            "EXPLAIN Çıktısı (Tercihen JSON formatında)",
            height=200,
            placeholder="EXPLAIN (ANALYZE, COSTS, BUFFERS, FORMAT JSON) SELECT ..."
        )

    with col2:
        st.subheader("2. Optimizasyon Süreci")

        if st.button("🚀 Performans Analizi Yap", use_container_width=True):
            if not st.session_state.api_key:
                st.error("Lütfen Gemini API anahtarınızı girin.")
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
                        3. Çözüm olarak YALNIZCA eksik indeksler için 'CREATE INDEX CONCURRENTLY', istatistik güncellemeleri için 'ANALYZE' ve o oturuma özel 'work_mem' gibi konfigürasyon ayarları üret.
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
                            # Modeli başlat (Sistem talimatı ile)
                            model = genai.GenerativeModel(
                                model_name=model_choice,
                                system_instruction=system_instruction
                            )

                            # İsteği gönder
                            return await model.generate_content_async(user_message)

                        response = asyncio.run(fetch_analysis())

                        st.success("Analiz Tamamlandı!")

                        # Çıktıyı ekrana yazdır
                        st.markdown("### Sonuç:")
                        st.write(response.text)

                    except Exception as e:
                        st.error(f"Bir hata oluştu: {str(e)}")
