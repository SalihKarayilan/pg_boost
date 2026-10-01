import streamlit as st
import os

def render_login():
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
