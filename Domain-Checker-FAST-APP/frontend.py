import streamlit as st
import pandas as pd
from domain_checker import DomainChecker

def render_bulk_check():
    st.header("\U0001F4D1 Bulk Domain Check")

    input_method = st.radio(
        "Choose input method",
        ["Upload TXT File \U0001F4C2", "Paste Domain List \U0001F4DD"]
    )

    domains = None

    if input_method == "Upload TXT File \U0001F4C2":
        st.info("Upload a text file with one domain name per line")
        uploaded_file = st.file_uploader("Choose a file", type=['txt'])

        if uploaded_file is not None:
            domains = [line.decode('utf-8').strip() for line in uploaded_file]

    else:
        st.info("Enter domain names (one per line)")
        text_input = st.text_area(
            "Paste your domains here",
            height=200,
            placeholder="example1\nexample2\nexample3"
        )

        if text_input:
            domains = [line.strip() for line in text_input.split('\n')]

    if domains:
        if st.button("\U0001F680 Check All Domains"):
            checker = DomainChecker(max_workers=10, rate_limit=0.1)
            results = checker.check_domains(domains)

            df = pd.DataFrame(results)
            st.success("\u2728 Check completed!")
            st.dataframe(df)

            csv = df.to_csv(index=False)
            st.download_button(
                label="\U0001F4E5 Download Results as CSV",
                data=csv,
                file_name="domain_check_results.csv",
                mime="text/csv"
            )

def render_single_check():
    st.header("\U0001F3AF Single Domain Check")
    st.info("Quick check for a single domain name")
    domain_name = st.text_input("Enter domain name (without .com) \U0001F310:")

    if st.button("\U0001F50D Check Availability"):
        if domain_name:
            with st.spinner('\U0001F504 Checking domain availability...'):
                from utils import check_single_domain
                status, error = check_single_domain(domain_name)

                if error:
                    st.error(f"\u26A0\uFE0F Error checking domain: {error}")
                else:
                    if "Available" in status:
                        st.success(f"\U0001F389 Domain {domain_name}.com is Available!")
                        st.balloons()
                    else:
                        st.warning(f"\U0001F614 Domain {domain_name}.com is Not Available")
        else:
            st.warning("\u26A0\uFE0F Please enter a domain name")