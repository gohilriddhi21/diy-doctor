import streamlit as st
import easyocr

def loadCSS(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Load the CSS file
loadCSS('styles.css')

st.title('⚕️DIY Doctor')  
st.header('Enter Your Details') 
st.text_input("Name")  
st.date_input("Date of Birth")  
st.button('Submit')  

uploadFile = st.file_uploader("Choose a file", type=['jpg', 'png', 'jpeg'])
if uploadFile is not None:
    # Display the uploaded image
    st.image(uploadFile, caption='Uploaded ID')

    # Create an EasyOCR reader
    reader = easyocr.Reader(['en']) 

    # Perform OCR on the uploaded image and extract text
    results = reader.readtext(uploadFile.getvalue()) 

    # Display OCR results
    for result in results:
        position, text, confidence = result
        st.write(f"Extracted Text: {text}, Confidence: {confidence:.2f}")