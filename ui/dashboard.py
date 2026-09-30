import streamlit as st
from utils.config import get_provider_config
from services.llm_service import perform_analysis

def render_dashboard():
    st.title("🐘 pg_boost")
    st.markdown("""
    Bu araç, sorgu yapısını ve tabloları değiştirmeden sadece **veritabanı motoru seviyesinde**
    (İndeks, ANALYZE, work_mem) performans iyileştirmeleri üretir.
    """)

    # Yan menü: Ayarlar
    with st.sidebar:
        st.header("⚙️ Ayarlar")

        provider_choice, api_key, model_choice = get_provider_config()

        if not api_key:
            st.info("Model seçebilmek için lütfen API anahtarınızı girin.")

    # Ana İçerik: Girdiler
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
            st.error("Lütfen sol menüden API anahtarınızı girin.")
        elif not model_choice:
            st.error("Lütfen geçerli bir model seçin.")
        elif not sql_query or not explain_output:
            st.warning("Lütfen SQL sorgusunu ve EXPLAIN çıktısını girin.")
        else:
            with st.spinner(f"{model_choice} analiz ediyor..."):
                response_text = perform_analysis(provider_choice, model_choice, api_key, sql_query, ddl_info, explain_output)
                if response_text:
                    st.success("Analiz Tamamlandı!")
                    st.markdown("### Sonuç:")
                    st.write(response_text)
