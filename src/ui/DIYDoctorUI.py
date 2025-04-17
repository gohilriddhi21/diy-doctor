import os
import sys
import streamlit as st

import easyocr
from PIL import Image
import re
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.models.query_engine import QueryEngine
from src.models.judge_llm import JudgeLLM
from src.models.model_loading_function import load_llm
from src.service.node_manager import NodeManager
from src.backend.database.PatientDAO import PatientDAO
from src.backend.database.MongoDBConnector import MongoDBConnector

# Check for required environment variable for the API key
load_dotenv()
api_key = os.getenv('OPENROUTER_API_KEY')
if not api_key:
    raise ValueError("Missing OpenRouter API key. Please set the OPENROUTER_API_KEY environment variable.")

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


BAD_MATCH = {
    # US States (full names)
    "ALABAMA", "ALASKA", "ARIZONA", "ARKANSAS", "CALIFORNIA", "COLORADO", "CONNECTICUT",
    "DELAWARE", "FLORIDA", "GEORGIA", "HAWAII", "IDAHO", "ILLINOIS", "INDIANA",
    "IOWA", "KANSAS", "KENTUCKY", "LOUISIANA", "MAINE", "MARYLAND", "MASSACHUSETTS",
    "MICHIGAN", "MINNESOTA", "MISSISSIPPI", "MISSOURI", "MONTANA", "NEBRASKA",
    "NEVADA", "NEW HAMPSHIRE", "NEW JERSEY", "NEW MEXICO", "NEW YORK",
    "NORTH CAROLINA", "NORTH DAKOTA", "OHIO", "OKLAHOMA", "OREGON", "PENNSYLVANIA",
    "RHODE ISLAND", "SOUTH CAROLINA", "SOUTH DAKOTA", "TENNESSEE", "TEXAS", "UTAH",
    "VERMONT", "VIRGINIA", "WASHINGTON", "WEST VIRGINIA", "WISCONSIN", "WYOMING",
    # Common junk words
    "USA", "STATE", "CITY", "DRIVER", "LICENSE", "ID", "STREET", "ROAD", "BLVD", "AVE"
}


def extract_name_from_text(text):
    """
    Improved version: extract two consecutive uppercase words, ignoring bad words,
    and flip them into First Last format.
    """
    matches = re.findall(r'\b[A-Z]{2,}\b\s+\b[A-Z]{2,}\b', text)

    for match in matches:
        words = match.split()

        if all(word not in BAD_MATCH for word in words):
            # Flip the words
            flipped = f"{words[1]} {words[0]}"
            # Proper case: Nick Sample
            proper_case_name = ' '.join(w.capitalize() for w in flipped.split())
            return proper_case_name

    return None


def find_user_by_name(name):
    """
    Search MongoDB 'login' collection for a matching user based on name.
    """
    query = {"lower_username": name.lower()}
    user = users.find_one(query)
    return user


def login_page():
    st.set_page_config(page_title="DIY Doctor", page_icon="🩺")
    st.title("🩺 DIY Doctor: AI-Powered Medical Verification")

    st.sidebar.title("User Login")

    if st.session_state.get('logged_in'):
        st.sidebar.success(f"👤 Logged in as: {st.session_state['username']}")
        st.sidebar.info(f"🆔 Patient ID: {st.session_state.get('patient_id', 'N/A')}")
        if st.sidebar.button("Logout", key="logout_sidebar"):
            st.session_state.clear()
            st.rerun()
        return

    st.image("testImage.jpg", use_container_width=True)

    login_method = st.sidebar.radio("Choose login method:", ("Username/Password", "Upload ID"))

    if login_method == "Username/Password":
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")

        login_col, bypass_col = st.sidebar.columns([2, 1])

        with login_col:
            if st.button("🔒 Login"):
                user = verify_login(username, password)
                if user:
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = username
                    st.session_state['patient_id'] = user.get("Patient_ID")
                    st.sidebar.success(f"✅ Welcome {username}!")
                    st.rerun()
                else:
                    st.sidebar.error("❌ Incorrect Username/Password")

        with bypass_col:
            if st.button("🚀 Dev Bypass", key="bypass_login"):
                st.session_state['logged_in'] = True
                st.session_state['username'] = "Developer"
                st.session_state['patient_id'] = "9999"
                st.rerun()

    elif login_method == "Upload ID":
        uploaded_file = st.sidebar.file_uploader("Upload your ID (jpg, png):", type=["jpg", "jpeg", "png"])

        if uploaded_file:
            try:
                img = Image.open(uploaded_file)
                reader = easyocr.Reader(['en'])
                ocr_result = reader.readtext(img, detail=0)
                ocr_text = " ".join(ocr_result)
                st.write("OCR Raw Text Output:")
                st.code(ocr_text)
                extracted_name = extract_name_from_text(ocr_text)

                if extracted_name:
                    st.sidebar.success(f"Extracted Name: `{extracted_name}`")
                    user = find_user_by_name(extracted_name)

                    if user:
                        st.success(f"✅ Welcome {extracted_name}!")
                        st.session_state['logged_in'] = True
                        st.session_state['username'] = extracted_name
                        st.session_state['patient_id'] = user.get("Patient_ID")
                        st.rerun()
                    else:
                        st.error("❌ No matching user found for extracted name.")
                else:
                    st.error("❌ Could not extract a recognizable name from the uploaded ID.")
            except Exception as e:
                st.error(f"❌ Error processing image: {str(e)}")


def dashboard_page():
    model_dict = {
        'OpenBio': 'aaditya/Llama3-OpenBioLLM-8B',
        'MMed-Llama': 'Henrychur/MMed-Llama-3-8B',
        'Meta Llama': 'meta-llama/llama-3.2-3b-instruct',
        'Mistral': 'mistralai/mistral-7b-instruct',
        'Qwen Turbo': 'qwen/qwen-turbo',
        'StarCoder2': 'bigcode/starcoder2-7b'
    }

    st.title(f"Welcome {st.session_state['username']}!")
    st.subheader("Medical Query")

    if st.button("Logout", key="logout"):
        st.session_state['logged_in'] = False
        st.session_state['username'] = None
        st.session_state['patient_id'] = None
        st.experimental_rerun()

    selected_model_key = st.selectbox("Choose a Query LLM model to use:", list(model_dict.keys()))
    model_name = model_dict[selected_model_key]

    judgeSelected_model_key = st.selectbox("Choose a Judge LLM model to use:", list(model_dict.keys()),
                                           key='judgeSelected')
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
        with st.spinner('🔄 Loading AI models and patient records...'):
            llm = load_llm(model_name)

            if not records:
                st.error("❌ No patient records found for the given patient ID.")
                return

            node_manager.set_nodes_from_patient_data(records)
            nodes = node_manager.get_nodes()

            if nodes:
                query_engine = QueryEngine(model_name, nodes)
                judge = JudgeLLM(judgeModel_name)
                st.success(f"✅ Nodes loaded and query engine initialized for: {selected_model_key}")
            else:
                st.error("❌ Failed to generate nodes from patient records.")
    except Exception as e:
        st.error(f"❌ Failed to initialize models: {str(e)}")
        return

    user_query = st.text_input("Enter your query here:", help="Type your medical question and press evaluate.")
    if st.button('Evaluate Query') and user_query:
        try:
            # Initialize progress bar
            progress = st.progress(0, text="Analyzing your query...")

            # Simulate progress (optional: fake small loading for realism)
            for percent_complete in range(0, 100, 10):
                progress.progress(percent_complete + 10)
                import time
                time.sleep(0.05)

            response_obj = query_engine.generate_full_response(user_query)
            verification = judge.verify_suggestions(user_query, response_obj, verbose=True)

            # Remove progress bar after done
            progress.empty()

            if verification == "GOOD":
                st.success(response_obj.response)
            elif verification == "BAD":
                st.error(response_obj.response)
            else:
                st.warning(response_obj.response)

        except Exception as e:
            st.error(f"Error evaluating query: {str(e)}")


def main():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    login_page()

    if st.session_state['logged_in']:
        dashboard_page()


if __name__ == "__main__":
    main()