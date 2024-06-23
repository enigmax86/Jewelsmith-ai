import streamlit as st
import requests
from PIL import Image
import io
import os
import base64

# # Custom CSS to increase the width
# custom_css = """
# <style>
#     .css-1d391kg {  # This class name might change, inspect your Streamlit app to find the correct class
#         max-width: 100% !important;
#     }
# </style>
# """

# st.markdown(custom_css, unsafe_allow_html=True)
st.set_page_config(layout="wide")

# Define the Flask server URL
# FLASK_SERVER_URL = "http://localhost:5000"
chatbot_response_endpoint = "https://yh6w674h63.execute-api.us-east-1.amazonaws.com/default/"
image_generator_endpoint = "https://pi85ecdrbi.execute-api.us-east-1.amazonaws.com/default/"
image_caption_endpoint = "https://i8g5wzii0m.execute-api.us-east-1.amazonaws.com/default"

temp_sys_prompt_1 = """
You are a friendly and engaging chatbot for a jewelry company. Based on the information provided below, please ask one follow-up question to the customer to understand their needs better. Follow these guidelines:

1. Question Specificity: Ask one short, one-liner question containing only one key entity to understand the customer's needs better.
2. Inclusion of Options: Yes : Frame every question to include options in the framed sentence itself related to the question providing the user a choice.
3. Explanation : Explain the options if using some complex terms in options like 'filigree' or 'embellishments'.
4. Entity Specification: Clearly mention the key entity in the question. Do not include entities such as metal or size.
5. Context Awareness: Do not repeat key entities already covered in the basic information provided below.
6. Conciseness: Print only the follow-up question and nothing extra, such as explanations or additional comments.
7. Tone: Use a warm and friendly tone to make the user feel welcomed and valued.
8. Relvance to Outfit : If outfit description is provided also consider the details of the outfit to ask the follow up question.


Make sure to include options for every question and explain complex terms if used in the question or options.
"""

def basic_info_to_string(basic_info, outfit_caption):
    info_str = ( 
        f"Occasion: {basic_info['occasion']}, \n"
        f"Gift or Personal Purchase: {basic_info['purchase_type']} , \n"
        f"Gender: {basic_info['gender']} , \n"
        f"Age Group: {basic_info['age_group']} , \n"
        f"Religion: {basic_info.get('religion', 'Not specified')} , \n"
        f"Type of Jewelry: {basic_info['jewelry_type']} , \n"
        f"Budget: {basic_info['budget']} , \n"
        f"Outfit Image Provided: {'Yes' if basic_info['outfit_image'] else 'No'} , "
        f"Outfit Description : {outfit_caption if basic_info['outfit_image'] else 'No'} "
    )
    return info_str

def call_flask_endpoint(endpoint, json_data):
    try:
        response = requests.post(f"{endpoint}", json=json_data)
        print(response.json())
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except requests.exceptions.RequestException as req_err:
        print(f'Request error occurred: {req_err}')
    except requests.exceptions.JSONDecodeError as json_err:
        print(f'JSON decode error occurred: {json_err}')
        print("Response text:", response.text)

st.title(f""":rainbow[Jewelry Design with Amazon Bedrock]""")

# Special effects: balloons animations
st.balloons()

# Initial Form for Basic Information
with st.form("initial_form"):
    occasion = st.selectbox("Occasion", ["Engagement","Wedding", "Anniversary", "Birthday", "Daily-wear"])
    purchase_type = st.radio("Gift or Personal Purchase", ["Gift", "Personal"])
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    age_group = st.radio("Age Group", ["18-24", "25-30", "31-40", "41-50", "51+"])
    religion = st.text_input("Religion (optional)")
    jewelry_type = st.selectbox("Type of Jewelry", ["Rings", "Necklaces", "Pendants", "Bracelets", "Earrings"])
    budget = st.radio("Budget", ["<10k INR", "10k-20k INR", "20k-50k INR", ">50k INR"])
    outfit_image = st.file_uploader("Would you like to match your jewelry with an outfit? Upload an image of your outfit for better recommendations.", type=["jpg", "jpeg", "png"])

    submitted = st.form_submit_button("Submit")

# Special effects: balloons animations
st.balloons()

if submitted:
    st.session_state.basic_info = {
        "occasion": occasion,
        "purchase_type": purchase_type,
        "gender": gender,
        "age_group": age_group,
        "religion": religion,
        "jewelry_type": jewelry_type,
        "budget": budget,
        "outfit_image": outfit_image
    }
    
    outfit_caption = ""
    
    if outfit_image:
        # Save the uploaded image
        outfit_image_path = os.path.join("outfit_images", outfit_image.name)
        with open(outfit_image_path, "wb") as f:
            f.write(outfit_image.getbuffer())

        # Generate a caption for the uploaded image
        outfit_caption = call_flask_endpoint( image_caption_endpoint, {'image_path': outfit_image_path})['body']
        
        # printing success mssg 
        st.success(f"Outfit caption generated: {outfit_caption}")
        
    basic_info_str = basic_info_to_string(st.session_state.basic_info, outfit_caption)
    instruc = "Basic Info : " + basic_info_str + "[ Print only 1 follow up question and nothing extra ]" + "[ do not repeat questions in the basic info above ]"
    
    prompt1_placeholder = st.empty()
    ########################################################################################################################## OUTPUT FOR DEBUGGING
    # prompt1_placeholder.markdown(temp_sys_prompt_1 + '\n\n' + instruc) # Output for Debugging
    
    # Call Flask endpoint for chatbot response
    follow_up_question1 = call_flask_endpoint(chatbot_response_endpoint, {'sys_prompt': temp_sys_prompt_1, 'user_prompt': instruc})['body']
    
    st.session_state.messages = [{"role": "assistant", "content": follow_up_question1}]
    st.session_state.messages.append({"role": "user", "content": basic_info_str})
    st.session_state.question_count = 0
    st.session_state.max_questions = 5  # Can adjust the max number of questions here

# Displaying initial information
if "basic_info" in st.session_state:
    st.write("### Initial Information")
    for key, value in st.session_state.basic_info.items():
        st.write(f"**{key.capitalize().replace('_', ' ')}:** {value}")

# Chatbot Interaction
if "messages" in st.session_state:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if question := st.chat_input(""):
        with st.chat_message("user"):
            st.markdown(question)
        st.session_state.messages.append({"role": "user", "content": question})
        st.session_state.question_count += 1

        if st.session_state.question_count < st.session_state.max_questions:
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                prompt_placeholder = st.empty()
                with st.spinner("Thinking..."):
                    prompt_text = ""
                    for msg in st.session_state.messages:
                        if msg["role"] == "user" or msg["role"] == "assistant":
                            prompt_text += f" {msg['role']} : {msg['content']} \n\n"
                    
                    # Call Flask endpoint for chatbot response
                    follow_up_question = call_flask_endpoint( chatbot_response_endpoint, {'sys_prompt': temp_sys_prompt_1, 'user_prompt': prompt_text})['body']
                    
                    ########################################################################################################################## OUTPUT FOR DEBUGGING
                    # prompt_placeholder.markdown(f"Prompt Sent to Claude : {temp_sys_prompt_1} \n\n {prompt_text}") # Printing prompts sent to Claude
                    message_placeholder.markdown(follow_up_question) # Printing follow_up_question
            st.session_state.messages.append({"role": "assistant", "content": follow_up_question})
        else:
            with st.chat_message("assistant"):
                final_prompt_placeholder = st.empty()
                message_placeholder = st.empty()
                
                # Input field for the number of images
                num_images = st.number_input("Enter the number of images to generate:", min_value=1, value=1, step=1)

                with st.spinner("Generating images based on your inputs..."):
                    final_prompt_text = ""
                    for msg in st.session_state.messages:
                        if msg["role"] == "user" or msg["role"] == "assistant":
                            final_prompt_text += f" {msg['role']} : {msg['content']} \n\n"
                    
                    final_sys_prompt = "Using this context generate only one small prompt for a text to image generator model to create accurate jewelry designs according to user's requirements"
                    
                    # Call Flask endpoint for final prompt and image generation
                    final_prompt = call_flask_endpoint( chatbot_response_endpoint, {'sys_prompt': final_sys_prompt, 'user_prompt': final_prompt_text})['body']
                    final_prompt_placeholder.markdown(f"Final Prompt : {final_prompt}")
                    
                    images = []
                    for _ in range(num_images):
                        image_response = call_flask_endpoint(image_generator_endpoint, {'prompt': final_prompt})
                        base64_image_data = image_response['body']
                        # Decode the base64 string into bytes
                        image_data = base64.b64decode(base64_image_data)
                        image = Image.open(io.BytesIO(image_data))
                        images.append(image)
                    
                    message_placeholder.markdown("Here are the images based on your inputs:")
                    for idx, img in enumerate(images):
                        st.image(img, caption=f"Generated Image {idx + 1}")
                    
                    st.success("Images created")

        # st.session_state.messages.append({"role": "assistant", "content": "Please provide more details if needed."})
