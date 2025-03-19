import streamlit as st
from llm_model import generate_response

def main():
    st.set_page_config(page_title="DIY Doctor", page_icon="🩺")
    st.title("🩺 DIY Doctor: AI-Powered Medical Verification")
    
    st.write("Enter your query below to receive verified medical guidance.")
    
    query = st.text_area("Your Medical Query:")
    
    if st.button("Submit"):
        if query.strip():
            output = generate_response(query)  
            if output:
                st.success(output)
            else:
                st.error("No relevant information found. Please consult a professional.")
        else:
            st.warning("Please enter a query before submitting.")
    with st.sidebar:
        st.header("About DIY Doctor")
        st.write("""DIY Doctor utilizes OCR and AI to verify medical advice based on user data. Ensure to consult a professional for final verification.""")
        st.markdown("**Contact: support@diydoctor.com**")

if __name__ == "__main__":
    main()