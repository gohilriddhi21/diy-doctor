import streamlit as st
from llm_model import generate_response

# ✅ Streamlit App UI
st.title("Hello, I am your DIY-Doctor")
query = st.text_input("Ask your questions:")
if st.button("Provide suggestion", use_container_width=True):
    st.session_state["advice"] = generate_response(query)

if "advice" in st.session_state:
    st.markdown("### Suggestions:")
    st.text_area("Advice:", st.session_state["advice"], height=200)