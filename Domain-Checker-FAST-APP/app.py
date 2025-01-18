import streamlit as st
from frontend import render_bulk_check, render_single_check

def main():
    st.markdown('<div class="main">', unsafe_allow_html=True)

    st.markdown("<h1 class='main-title'>\U0001F50D Domain Availability Checker Pro</h1>", unsafe_allow_html=True)
    st.markdown("### Find your perfect domain name! \U0001F3AF")

    tab1, tab2 = st.tabs(["\U0001F4D1 Bulk Domain Check", "\U0001F3AF Single Domain Check"])

    with tab1:
        render_bulk_check()

    with tab2:
        render_single_check()

    st.markdown("""
        <div class='footer'>
            <div class='social-links'>
                <a href='https://www.linkedin.com/in/geethikaisuru/' target='_blank'>\U0001F517 LinkedIn</a>
                <a href='https://github.com/geethikaisuru' target='_blank'>\U0001F4BB GitHub</a>
            </div>
            <p>Built with \u2764\uFE0F by Geethika</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
