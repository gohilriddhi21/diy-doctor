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

# Check for required environment variable for the API key
api_key = os.getenv('OPENROUTER_API_KEY')
if not api_key:
    raise ValueError("Missing OpenRouter API key. Please set the OPENROUTER_API_KEY environment variable.")

# Define the offload directory
#offload_directory = "C:\\Users\\PC\\Desktop\\Northeastern\\CS 7180\\Final Project\\diy-doctor\\src\\ui\\Offload"

# Setup MongoDB connection
client = MongoClient("mongodb+srv://genai:genai123@diy-doctor.b82as.mongodb.net/")
 # Database name based on MongoDB
db = client["diy-doctor"] 
# Collection name based on MongoDB
users = db.login  
print(db.list_collection_names())

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
        return user["password"] == password
    else:
        print("No user found with the username:", username)
    return False

# Display the login page and handle user authentication.
def login_page():
    st.title("🩺 DIY Doctor: AI-Powered Medical Verification")
    st.sidebar.title("Login")
    st.image("testImage.jpg")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if verify_login(username, password):
            st.session_state['logged_in'] = True
            st.session_state['username'] = username  # Save username in session
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
    
    # Create a row at the top for the welcome message and logout button
    header_cols = st.columns([0.85, 0.15])
    with header_cols[0]:
        st.title(f"DIY Doctor - Welcome {st.session_state['username']}!")
    with header_cols[1]:
        if st.button("Logout", key="logout"):
            # Reset the session state to log the user out
            st.session_state['logged_in'] = False
            st.session_state['username'] = None
            # Redirect to the login page
            st.experimental_rerun()

    st.subheader("Medical Query")
    # Display model selection
    model_options = list(model_dict.keys())
    selected_model_key = st.selectbox("Choose an LLM model to use:", model_options, key='model_selector')
    model_name = model_dict[selected_model_key]
    
    # Predefined PDF path
    pdf_path = "C:\\Users\HyPC\\Desktop\\Northeastern\\CS 7180\\Final Project\\diy-doctor\\tests\\WebMD.pdf"
    # Instantiate NodeManager and load models
    node_manager = NodeManager()
    try:
        llm = load_llm(model_name)
        node_manager.set_nodes_from_pdf(pdf_path)
        nodes = node_manager.get_nodes()
        
        if nodes:
            query_engine = QueryEngine(model_name, nodes)
            judge = JudgeLLM(model_name)
            st.success(f"Nodes loaded and query engine initialized for: {selected_model_key}")
        else:
            st.error("Failed to load nodes from PDF. Please check the predefined path and PDF content.")
    except Exception as e:
        st.error(f"Failed to initialize components for {selected_model_key}: {str(e)}")
        return

    # User input for queries and processing
    user_query = st.text_input("Enter your query here:", help="Type your query and press evaluate.")
    if st.button('Evaluate Query') and user_query:
        try:
            response_obj = query_engine.generate_full_response(user_query)
            verification = judge.verify_suggestions(user_query, response_obj, verbose=True)
            
            if verification == "GOOD":
                st.success(response_obj['response'])
            elif verification == "BAD":
                st.error(response_obj['response'])
            else:
                st.warning(response_obj['response'])
        except Exception as e:
            st.error(f"Error in processing query: {str(e)}")

            
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

#     st.write("This is your medical dashboard.")
# def get_response(model_name, user_query):
#     # Initialize the generator
#     generator = pipeline('text-generation', model=model_name)
#     # Generate response
#     results = generator(user_query, max_length=100, num_return_sequences=1, truncation=True)
#     # Return a dictionary with the response and a dummy score
#     return {'response': results[0]['generated_text'], 'score': 1.0}

# def get_response(model_or_identifier, user_query):
#     """
#     Generates a response for a given user query using a specified model.
    
#     Args:
#         model_or_identifier (str or object): A string identifier for HuggingFace models or an object for custom models like QueryEngine.
#         user_query (str): The query input from the user.
        
#     Returns:
#         dict: A dictionary containing the generated response text and a dummy score.
#     """
#     if isinstance(model_or_identifier, str):
#         # Use the transformers pipeline for string-identified models
#         generator = pipeline('text-generation', model=model_or_identifier)
#         results = generator(user_query, max_length=100, num_return_sequences=1, truncation=True)
#         response_text = results[0]['generated_text']
#     elif callable(getattr(model_or_identifier, 'generate_response', None)):
#         # Use the generate_response method if it's a custom model like QueryEngine
#         response_text = model_or_identifier.generate_response(user_query)
#     else:
#         raise ValueError("Unsupported model type provided.")
        
#     return {'response': response_text, 'score': 1.0}

# This is with Query
# def dashboard_page():
#     """
#     Displays the dashboard page for the logged-in user, allowing them to interact with different LLM and judge models,
#     manage their session, and input queries for evaluation.
#     """
#     # Setup model dictionaries with class references or proper initializers
#     query_model_dict = {
#         'QueryEngine': QueryEngine,  # Assuming QueryEngine is a class that can be instantiated directly
#     }
#     judge_dict = {
#         'OpenBio': ('aaditya/Llama3-OpenBioLLM-8B', JudgeOpenBioLLM),
#         'Model 2': ('model_2_identifier', JudgeOpenBioLLM),
#         'Model 3': ('model_3_identifier', JudgeOpenBioLLM)  # Assuming these are tuples of model identifier and class
#     }

#     # Create a row at the top for the welcome message and logout button
#     header_cols = st.columns([0.85, 0.15])
#     with header_cols[0]:
#         st.title(f"DIY Doctor - Welcome {st.session_state['username']}!")
#     with header_cols[1]:
#         if st.button("Logout", key="logout"):
#             # Reset the session state to log the user out
#             st.session_state['logged_in'] = False
#             st.session_state['username'] = None
#             # Redirect to the login page
#             st.experimental_rerun()

#     st.write("This is your medical dashboard.")

#     # Model selector for query models
#     model_options = list(query_model_dict.keys())
#     selected_query_model = st.selectbox("Query Model:", model_options, key='query_model_selector')

#     # Judge model selector
#     judge_options = list(judge_dict.keys())
#     selected_judge = st.selectbox("Judge Model:", judge_options, key='judge_selector')

#     # Initialize the query model
#     query_model_class = query_model_dict[selected_query_model]
#     try:
#         if callable(query_model_class):
#             query_model = query_model_class()  # Instantiate the query model if it is a class
#         else:
#             query_model = query_model_class  # Use the model directly if it's not a class
#     except Exception as e:
#         st.error(f"Failed to initialize the query model '{selected_query_model}': {e}")
#         return

#     # Initialize the judge model
#     model_identifier, JudgeClass = judge_dict[selected_judge]
#     try:
#         judge = JudgeClass(model_name=model_identifier)  # Pass the model identifier to the judge model class
#     except Exception as e:
#         st.error(f"Failed to initialize the judge model '{selected_judge}': {e}")
#         return

#     # Query input and evaluation
#     user_query = st.text_input("Enter your medical query here:", help="E.g., 'What are the symptoms of the flu?'")
#     if st.button('Evaluate Query') and user_query:
#         try:
#             # Generate response using the query model
#             response_obj = get_response(query_model, user_query)  # Adjusted to use the instantiated query model
#             # Evaluate the response using the Judge LLM
#             verification = judge.verify_suggestions(user_query, response_obj, verbose=True)

#             # Display the response and evaluation
#             if verification == "GOOD":
#                 st.success(response_obj['response'])
#             elif verification == "BAD":
#                 st.error(response_obj['response'])
#             else:
#                 st.warning(response_obj['response'])
#         except Exception as e:
#             st.error(f"Error generating response: {e}")

# Old without Query
# def dashboard_page():
#     query_model_dict = {
#         'QueryEngine': QueryEngine,
#     }
#     judge_dict = {
#         'OpenBio': ('aaditya/Llama3-OpenBioLLM-8B', JudgeOpenBioLLM),
#         'Model 2': ('model_2_identifier', JudgeOpenBioLLM),
#         'Model 3': ('model_3_identifier', JudgeOpenBioLLM)  # Assuming JudgeModel3LLM is defined
#     }
#     # Create a row at the top for the welcome message and logout button
#     header_cols = st.columns([0.85, 0.15])  
#     with header_cols[0]:
#         st.title(f"DIY Doctor - Welcome {st.session_state['username']}!")
#     with header_cols[1]:
#         if st.button("Logout", key="logout"):
#             # Reset the session state to log the user out
#             st.session_state['logged_in'] = False
#             st.session_state['username'] = None
#             # Redirect to the login page
#             st.experimental_rerun()

#     st.write("This is your medical dashboard.")

#     # Model selector for LLM models
#     model_options = list(query_model_dict.keys())
#     selected_model = st.selectbox("LLM Model:", model_options, key='model_selector')
    
#     # Judge model selector
#     judge_options = list(judge_dict.keys())
#     selected_judge = st.selectbox("Judge Model:", judge_options, key='judge_selector')

#     currentSelectedModel_name = query_model_dict[selected_model]
#     JudgeClass = judge_dict[selected_judge]

#      # Initialize the judge LLM based on selected model
#     try:
#         judge = JudgeClass(model_name=currentSelectedModel_name)
#         st.write(f"LLM Model '{selected_model}' and Judge '{selected_judge}' initialized.")
#     except Exception as e:
#         st.error(f"Failed to initialize the model: {e}")

#     # Query input and evaluation
#     user_query = st.text_input("Enter your medical query here:", help="E.g., 'What are the symptoms of the flu?'")
#     if st.button('Evaluate Query') and user_query:
#         try:
#              # Generate response using the LLM
#             response_obj = get_response(currentSelectedModel_name, user_query)
#             print(response_obj)
#             # Evaluate the response using the Judge LLM
#             verification = judge.verify_suggestions(user_query, response_obj, verbose=True)

#             # Display the response and evaluation
#             if verification == "GOOD":
#                 st.success(response_obj['response'])
#             elif verification == "BAD":
#                 st.error(response_obj['response'])
#             else:
#                 st.warning(response_obj['response'])
#         except Exception as e:
#             st.error(f"Error generating response: {e}")


# uploadFile = st.file_uploader("Choose a file", type=['jpg', 'png', 'jpeg'])
# if uploadFile is not None:
#     # Display the uploaded image
#     st.image(uploadFile, caption='Uploaded ID')

#     # Create an EasyOCR reader
#     reader = easyocr.Reader(['en']) 

#     # Perform OCR on the uploaded image and extract text
#     results = reader.readtext(uploadFile.getvalue()) 

#     # Display OCR results
#     for result in results:
#         position, text, confidence = result
#         st.write(f"Extracted Text: {text}, Confidence: {confidence:.2f}")