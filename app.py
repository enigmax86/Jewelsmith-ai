import streamlit as st
import os
import base64
import io
from PIL import Image
from utils.api_calls import call_endpoint, store_in_mongodb
from utils.image_processing import get_image_response,save_image, generate_image_captions,generate_image_captions_froms3, upload_image_to_s3
from utils.conversation import get_chatbot_response,format_and_upload_conversation, basic_info_to_string, temp_sys_prompt_1 , display_image_options , process_image_followup_ques
from utils.api_calls import fetch_similar_images
from utils.kg_query import generate_recommendations
st.set_page_config(layout="wide")
st.title(f""":rainbow[Jewelry Design with Amazon Bedrock]""")
st.balloons()

# Initial Form for Basic Information
with st.form("initial_form"):
    username = st.text_input("Username")
    occasion = st.selectbox("Occasion", ["Engagement","Wedding", "Anniversary", "Birthday", "Daily-wear"])
    purchase_type = st.radio("Gift or Personal Purchase", ["Gift", "Personal"])
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    age_group = st.radio("Age Group", ["18-24", "25-30", "31-40", "41-50", "51+"])
    religion = st.text_input("Religion (optional)")
    jewelry_type = st.selectbox("Type of Jewelry", ["Rings", "Necklaces", "Pendants", "Bracelets", "Earrings"])
    budget = st.radio("Budget", ["<10k INR", "10k-20k INR", "20k-50k INR", "50k INR or more"])
    outfit_image = st.file_uploader("Would you like to match your jewelry with an outfit? Upload an image of your outfit for better recommendations.", type=["jpg", "jpeg", "png"])

    submitted = st.form_submit_button("Submit")
    

if submitted:
  
    st.session_state.basic_info = {
        "username": username,
        "occasion": occasion,
        "purchase_type": purchase_type,
        "gender": gender,
        "age_group": age_group,
        "religion": religion,
        "jewelry_type": jewelry_type,
        "budget": budget,
        "outfit_image": outfit_image
    }
    
    
    outfit_caption = generate_image_captions(outfit_image) if outfit_image else ""
    
    basic_info_str = basic_info_to_string(st.session_state.basic_info, outfit_caption)
    instruc = "Basic Info : " + basic_info_str + "[ Print only 1 follow up question and nothing extra ]" + "[ do not repeat questions in the basic info above ]"
    
    instruc1 = instruc = "Basic Info : " + basic_info_str 
    # follow_up_question1 = get_chatbot_response({'sys_prompt': temp_sys_prompt_1, 'user_prompt': instruc1})
    follow_up_question1 = generate_recommendations(st.session_state.basic_info)
    
    st.session_state.messages = [{"role": "user", "content": basic_info_str}]
    st.session_state.messages.append({"role": "assistant", "content": follow_up_question1})
    st.session_state.question_count = 0
    st.session_state.max_questions = 5

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
                with st.spinner("Thinking..."):
                    prompt_text = ""
                    for msg in st.session_state.messages:
                        if msg["role"] == "user" or msg["role"] == "assistant":
                            prompt_text += f" {msg['role']} : {msg['content']} \n\n"
                    
                    follow_up_question = get_chatbot_response({'sys_prompt': temp_sys_prompt_1, 'user_prompt': prompt_text})
                    message_placeholder.markdown(follow_up_question)
            st.session_state.messages.append({"role": "assistant", "content": follow_up_question})
            jtype = st.session_state.basic_info['jewelry_type']

            if st.session_state.question_count == 1:
                image_urls = fetch_similar_images(follow_up_question, jtype)
                columns = st.columns(len(image_urls))

                for idx, url in enumerate(image_urls):
                    with columns[idx]:
                        st.image(url, caption=f"Image {idx + 1}")

                if "chosen_image_url" not in st.session_state:

        #########################################################################################################3 
                    with st.form("image_selection_form"):
                        st.write("Please choose an image that matches your preference:")
                        chosen = st.radio("Image", ["0", "1", "2", "None"])

                        submitted = st.form_submit_button("Submit")
    
                    if submitted:
                        if chosen == "None": 
                            st.session_state.chosen_image_url = "None"
                        else: 
                            chosenidx = chosen[-1]-1
                            st.session_state.chosen_image_url = image_urls[chosenidx]


                    #########################################################################################################3 

                    print("chosen image url saved")
                    print(st.session_state.chosen_image_url)
                if st.session_state.chosen_image_url:
                    # Proceed after the user has made a choice
                    print("entered")
                    img_des = generate_image_captions_froms3(st.session_state.chosen_image_url)

                    process_image_followup_ques(st.session_state.chosen_image_url, img_des)
                    print("ready to exit")
            else:
                # st.write("Please select an image to proceed.")
                pass
                
        else:

            with st.chat_message("assistant"):
                final_prompt_placeholder = st.empty()
                message_placeholder = st.empty()
                
                image_count_submitted = True
                num_images = 2
                
                
                if image_count_submitted:
                    
                    with st.spinner("Generating images based on your inputs..."):
                        final_prompt_text = ""
                        for msg in st.session_state.messages:
                            if msg["role"] == "user" or msg["role"] == "assistant":
                                final_prompt_text += f" {msg['role']} : {msg['content']} \n\n"
                        
                        final_sys_prompt = "Using this context generate only one small prompt for a text to image generator model to create accurate jewelry designs according to user's requirements. Generate the short and concise text prompt properly according to the conversation given to you"
                        
                        final_prompt = get_chatbot_response({'sys_prompt': final_sys_prompt, 'user_prompt': final_prompt_text})
                        final_prompt_placeholder.markdown(f"Final Prompt : {final_prompt}")
                        st.session_state.messages.append({"role": "assistant", "content": final_prompt})
                        s3_conv_url = format_and_upload_conversation()
                        
                        images = []
                        for _ in range(num_images):
                            image_response = get_image_response({'prompt': final_prompt})
                            base64_image_data = image_response['body']
                            image_data = base64.b64decode(base64_image_data)
                            image = Image.open(io.BytesIO(image_data))
                            images.append(image)
                        
                        message_placeholder.markdown("Here are the images based on your inputs:")
                        s3_image_urls = {}
                        for idx, img in enumerate(images):
                            st.image(img, caption=f"Generated Image {idx + 1}" , width=300)
                            s3_image_urls[f'Image_{idx+1}'] = upload_image_to_s3(img)
                            st.markdown(f"Access your image here: [Image {idx + 1}]({s3_image_urls[f'Image_{idx+1}']})")
                        
                        st.success("Images created")
                        store_in_mongodb(s3_conv_url, s3_image_urls)
