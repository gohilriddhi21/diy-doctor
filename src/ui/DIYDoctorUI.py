import os
import sys
import streamlit as st
from pymongo import MongoClient
from transformers import pipeline

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.models.query_engine import QueryEngine
from src.models.judge_llm import JudgeLLM
from src.models.model_loading_function import load_llm
from src.service.node_manager import NodeManager
from src.backend.database.PatientDAO import PatientDAO
from src.backend.database.MongoDBConnector import MongoDBConnector

# Check for required environment variable for the API key
api_key = os.getenv('OPENROUTER_API_KEY')
if not api_key:
    raise ValueError("Missing OpenRouter API key. Please set the OPENROUTER_API_KEY environment variable.")

#TODO: Figure out how to connect with patient
# Connect to MongoDB
CONFIG_FILE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'config.yaml')
)
try:
    db_connector = MongoDBConnector(CONFIG_FILE_PATH)
    db = db_connector.get_database()

    if db is None:
        st.error("Database connection failed. Database object is None. Check config format or connection.")
        st.stop()

except FileNotFoundError:
    st.error(f"Configuration file not found at {CONFIG_FILE_PATH}.")
    st.stop()

except Exception as e:
    st.error(f"Database connection failed due to unexpected error: {str(e)}")
    st.stop()

users = db["login"]
patient_dao = PatientDAO(db_connector)

# Verify if a user's login credentials are correct
# Params: 
#  - username (str): The username of the user trying to log in.
#  - password (str): The password provided by the user for login.
# Returns:
#  - bool: True if the username and password match a database entry, False otherwise.
def verify_login(username, password):
    print(f"Logging in with username: {username} and password: {password}")
    user = users.find_one({"lower_username": username.lower()})
    if user:
        print(f"Found user: {user}")
        print(f"Stored password: {user['password']} - Input password: {password}")
        if user["password"] == password:
            return user  # return the whole user document!
    else:
        print("No user found with the username:", username)
    return None

# Display the login page and handle user authentication.
def login_page():
    st.title("🩺 DIY Doctor: AI-Powered Medical Verification")
    st.sidebar.title("Login")
    st.image("testImage.jpg")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        user = verify_login(username, password)
        if user:
            st.session_state['logged_in'] = True
            st.session_state['username'] = username  # Save username in session
            st.session_state['patient_id'] = user.get("Patient_ID")
        else:
            st.sidebar.error("Incorrect Username/Password")
     # Bypass login button for development purposes
    if st.sidebar.button("Bypass Login (Dev Only)"):
        st.session_state['logged_in'] = True
        st.session_state['username'] = "Developer"

def dashboard_page():
    model_dict = {
        'OpenBio': 'aaditya/Llama3-OpenBioLLM-8B',
        'Meta Llama': 'meta-llama/llama-3.2-3b-instruct',
        'Mistral': 'mistralai/mistral-7b-instruct',
        'Qwen Turbo': 'qwen/qwen-turbo'
    }

    st.title(f"DIY Doctor - Welcome {st.session_state['username']}!")
    st.subheader("Medical Query")

    if st.button("Logout", key="logout"):
        st.session_state['logged_in'] = False
        st.session_state['username'] = None
        st.session_state['patient_id'] = None
        st.experimental_rerun()

    selected_model_key = st.selectbox("Choose a Query LLM model to use:", list(model_dict.keys()))
    model_name = model_dict[selected_model_key]

    judgeSelected_model_key = st.selectbox("Choose a Judge LLM model to use:", list(model_dict.keys()), key='judgeSelected')
    judgeModel_name = model_dict[judgeSelected_model_key]

    existent_patient_id = st.session_state.get('patient_id')

    if existent_patient_id is None:
        st.error("No patient ID found. Please login properly.")
        return

    st.info(f"Looking up patient records for ID: {existent_patient_id}")

    records = patient_dao.get_patient_records_from_all_collections(existent_patient_id)
    st.write("Fetched patient records:", records)

    node_manager = NodeManager()

    try:
        llm = load_llm(model_name)

        if not records:
            st.error("No patient records found for the given patient ID.")
            return

        node_manager.set_nodes_from_patient_data(records)
        nodes = node_manager.get_nodes()

        if nodes:
            query_engine = QueryEngine(model_name, nodes)
            judge = JudgeLLM(judgeModel_name)
            st.success(f"Nodes loaded and query engine initialized for: {selected_model_key}")
        else:
            st.error("Failed to generate nodes from patient records.")
    except Exception as e:
        st.error(f"Failed to initialize models: {str(e)}")
        return

    user_query = st.text_input("Enter your query here:", help="Type your medical question and press evaluate.")
    if st.button('Evaluate Query') and user_query:
        try:
            response_obj = query_engine.generate_full_response(user_query)
            verification = judge.verify_suggestions(user_query, response_obj, verbose=True)

            if verification == "GOOD":
                st.success(response_obj.response)
            elif verification == "BAD":
                st.error(response_obj.response)
            else:
                st.warning(response_obj.response)
        except Exception as e:
            st.error(f"Error evaluating query: {str(e)}")
            
def main():
    st.set_page_config(page_title="DIY Doctor", page_icon="🩺")
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    # Conditional rendering based on login status
    if st.session_state['logged_in']:
        dashboard_page()
    else:
        login_page()

if __name__ == "__main__":
    main()