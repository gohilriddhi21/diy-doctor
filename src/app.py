import streamlit as st
from node_manager import NodeManager
from llm_model import QueryEngine
from dotenv import load_dotenv
import os

def main():
    load_dotenv()
    st.set_page_config(page_title="DIY Doctor", page_icon="🩺")
    st.title("🩺 DIY Doctor: AI-Powered Medical Verification")
    
    st.write("Enter your query below to receive verified medical guidance.")
    
    query = st.text_area("Your Medical Query:")

    # TODO remove this later/improve how it works when additional data/functionality added
    pdf_file = "src\\tests\\WebMD.pdf"

    # TODO seems like node manager resets when put outside query call... this slows things down considerably
    node_manager = NodeManager(pdf_file)  # TODO should have a loading message while this loads
    query_manager = QueryEngine(node_manager.get_nodes())
    
    if st.button("Submit"):
        if query.strip():# Set up node manager and retriever

            output = query_manager.generate_response(query)
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