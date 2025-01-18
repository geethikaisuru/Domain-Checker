import streamlit as st
import whois
from datetime import datetime
import time
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Domain Checker Pro",
    page_icon="🔍"
)

# Custom CSS with fixed footer styling
st.markdown("""
    <style>
    .main-title {
        text-align: center;
        color: #1E88E5;
        padding: 20px;
    }
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #f0f2f6;
        padding: 10px 0;
        text-align: center;
        z-index: 999;
    }
    .social-links {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 20px;
        margin-bottom: 10px;
    }
    .social-links a {
        text-decoration: none;
        color: #1E88E5;
        display: inline-flex;
        align-items: center;
    }
    /* Add padding to main content to prevent footer overlap */
    .main {
        padding-bottom: 100px;
    }
    </style>
    """, unsafe_allow_html=True)

def clean_domain_name(domain_name):
    """
    Clean the domain name by:
    1. Removing spaces
    2. Converting to lowercase
    3. Removing any special characters
    """
    return domain_name.strip().replace(" ", "").lower()

def check_single_domain(domain_name):
    """
    Check the availability of a single .com domain.
    Returns a tuple of (status, error_message if any)
    """
    cleaned_domain = clean_domain_name(domain_name)
    domain = f"{cleaned_domain}.com"
    
    try:
        time.sleep(1)
        domain_info = whois.whois(domain)
        
        if domain_info.domain_name is None:
            return "Available ✅", None
        else:
            if isinstance(domain_info.expiration_date, list):
                expiration_date = domain_info.expiration_date[0]
            else:
                expiration_date = domain_info.expiration_date
            
            if expiration_date and expiration_date > datetime.now():
                return "Not Available ❌", None
            else:
                return "Available ✅", None
                
    except whois.parser.PywhoisError:
        return "Available ✅", None
    except Exception as e:
        return "Error ⚠️", str(e)

def process_domain_list(domains):
    """
    Process a list of domains and return results
    """
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, domain in enumerate(domains):
        if domain:  # Skip empty lines
            status_text.text(f"🔍 Checking domain: {domain}")
            cleaned_domain = clean_domain_name(domain)
            status, error = check_single_domain(cleaned_domain)
            
            results.append({
                'Original Domain': domain,
                'Cleaned Domain': f"{cleaned_domain}.com",
                'Status': status,
                'Error': error if error else ''
            })
            
            progress_bar.progress((i + 1) / len(domains))
    
    return results

def main():
    # Main content wrapper div
    st.markdown('<div class="main">', unsafe_allow_html=True)
    
    # Title with custom styling
    st.markdown("<h1 class='main-title'>🔍 Domain Availability Checker Pro</h1>", unsafe_allow_html=True)
    st.markdown("### Find your perfect domain name! 🎯")
    
    # Create two tabs with emojis
    tab1, tab2 = st.tabs(["📑 Bulk Domain Check", "🎯 Single Domain Check"])
    
    # Bulk Domain Check Tab
    with tab1:
        st.header("📑 Bulk Domain Check")
        
        # Radio button for input method selection
        input_method = st.radio(
            "Choose input method",
            ["Upload TXT File 📂", "Paste Domain List 📝"]
        )
        
        domains = None
        
        if input_method == "Upload TXT File 📂":
            st.info("Upload a text file with one domain name per line")
            uploaded_file = st.file_uploader("Choose a file", type=['txt'])
            
            if uploaded_file is not None:
                domains = [line.decode('utf-8').strip() for line in uploaded_file]
        
        else:  # Paste Domain List
            st.info("Enter domain names (one per line)")
            text_input = st.text_area(
                "Paste your domains here",
                height=200,
                placeholder="example1\nexample2\nexample3"
            )
            
            if text_input:
                domains = [line.strip() for line in text_input.split('\n')]
        
        if domains:  # Process domains regardless of input method
            if st.button("🚀 Check All Domains"):
                results = process_domain_list(domains)
                
                df = pd.DataFrame(results)
                st.success("✨ Check completed!")
                st.dataframe(df)
                
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Results as CSV",
                    data=csv,
                    file_name="domain_check_results.csv",
                    mime="text/csv"
                )
    
    # Single Domain Check Tab
    with tab2:
        st.header("🎯 Single Domain Check")
        st.info("Quick check for a single domain name")
        domain_name = st.text_input("Enter domain name (without .com) 🌐:")
        
        if st.button("🔍 Check Availability"):
            if domain_name:
                with st.spinner('🔄 Checking domain availability...'):
                    status, error = check_single_domain(domain_name)
                    
                    if error:
                        st.error(f"⚠️ Error checking domain: {error}")
                    else:
                        if "Available" in status:
                            st.success(f"🎉 Domain {domain_name}.com is Available!")
                            st.balloons()
                        else:
                            st.warning(f"😔 Domain {domain_name}.com is Not Available")
            else:
                st.warning("⚠️ Please enter a domain name")
    
    # Footer with social links
    st.markdown("""
        <div class='footer'>
            <div class='social-links'>
                <a href='https://www.linkedin.com/in/geethikaisuru/' target='_blank'>🔗 LinkedIn</a>
                <a href='https://github.com/geethikaisuru' target='_blank'>💻 GitHub</a>
            </div>
            <p>Built with ❤️ by Geethika</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()