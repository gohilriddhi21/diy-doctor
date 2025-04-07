import streamlit as st
from pymongo import MongoClient
from transformers import pipeline

from judge_OpenBioLLM import JudgeOpenBioLLM  

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
    st.sidebar.title("Login")
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

def get_response(model_name, user_query):
    # Initialize the generator
    generator = pipeline('text-generation', model=model_name)
    # Generate response
    results = generator(user_query, max_length=100, num_return_sequences=1, truncation=True)
    # Return a dictionary with the response and a dummy score
    return {'response': results[0]['generated_text'], 'score': 1.0}

# Display the dashboard page to the logged-in user.
def dashboard_page():
    model_dict = {
        'OpenBio': ('aaditya/Llama3-OpenBioLLM-8B', JudgeOpenBioLLM),
        'Model 2': ('model_2_identifier', JudgeOpenBioLLM),
        'Model 3': ('model_3_identifier', JudgeOpenBioLLM)
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

    st.write("This is your medical dashboard.")

    # Adding model selector for llm models
    model_options = list(model_dict.keys())
    selected_model = st.selectbox("Choose an LLM model to use:", model_options, key='model_selector')
    currentSelectedModel_name, JudgeClass = model_dict[selected_model]

     # Initialize the judge LLM based on selected model
    try:
        judge = JudgeClass(model_name=currentSelectedModel_name)
        st.write(f"Judge LLM Initialized for {selected_model}.")
    except Exception as e:
        st.error(f"Failed to initialize the model: {e}")

    # Query input and evaluation
    user_query = st.text_input("Enter your medical query here:", help="E.g., 'What are the symptoms of the flu?'")
    if st.button('Evaluate Query') and user_query:
        try:
             # Generate response using the LLM
            response_obj = get_response(currentSelectedModel_name, user_query)
            print(response_obj)
            # Evaluate the response using the Judge LLM
            verification = judge.verify_suggestions(user_query, response_obj, verbose=True)

            # Display the response and evaluation
            if verification == "GOOD":
                st.success(response_obj['response'])
            elif verification == "BAD":
                st.error(response_obj['response'])
            else:
                st.warning(response_obj['response'])
        except Exception as e:
            st.error(f"Error generating response: {e}")

def main():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    # Conditional rendering based on login status
    if st.session_state['logged_in']:
        dashboard_page()
    else:
        login_page()

if __name__ == "__main__":
    main()

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