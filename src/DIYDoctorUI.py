import streamlit as st
from pymongo import MongoClient
from bson.objectid import ObjectId
import hashlib

# Setup MongoDB connection
client = MongoClient("mongodb+srv://genai:genai123@diy-doctor.b82as.mongodb.net/")
db = client["DIY-Doctor"]  # Database name
users = db.users  # Collection name

def verify_login(username, password):
    # Query using lower_username
    user = users.find_one({"lower_username": username.lower()})
    if user:
        # Check if passwords are hashed
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        return user["password"] == hashed_password
    return False

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

def dashboard_page():
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
    model_options = ['Model 1 ', 'Model 2', 'Model 3']
    selected_model = st.selectbox("Choose an LLM model to use:", model_options, key='model_selector')
    st.write(f"You have selected {selected_model}.")


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

 