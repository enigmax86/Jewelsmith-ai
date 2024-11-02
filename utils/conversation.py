import json
import uuid
import streamlit as st
from utils.api_calls import call_endpoint, store_in_mongodb
from config import upload_conversation_endpoint , chatbot_response_endpoint


# Retailer Profile Data (could be fetched from a DB or external source)
retailer_profile = {
  "geographic_region": {
      "country": "India",
      "state": "Maharashtra",
      "city": "Mumbai",
      "urban_rural": "Urban"
  },
  "jewelry_types_offered": {
      "design_styles": ["Traditional", "Modern", "Fusion"],
      "product_range": ["Rings", "Necklaces", "Bridal Sets", "Earrings", "Bangles"]
  },
  "target_demographics": {
      "predominant_age_groups": ["21-30", "31-40"],
      "gender_focus": ["Female", "Unisex"]
  },
  "market_trends_and_preferences": {
      "trending_designs": ["Kundan and Polki Jewelry", "Minimalist Gold Jewelry"],
  },
  "customer_preferences": {
      "style_preferences": ["Ethnic", "Contemporary"],
      "cultural_influences": {
          "local_festivals": ["Diwali", "Ganesh Chaturthi"],
          "events_and_seasons": ["Weddings", "Festivals"]
      }
  }
}

# The system prompt being sent to get follow up questions giving all the previous chat as the context
temp_sys_prompt_2 = f"""
You are a friendly and engaging chatbot assistant for a jewelry company . Based on the information provided below, please ask one follow-up question to the customer to understand their needs better. Follow these guidelines:

Generate only the assistant response part according to the following guidelines , do not generate anything from the user's side. 

1. Question Specificity: Ask one short, one-liner question containing only one key entity to understand the customer's needs better.
2. Inclusion of Options: Yes : Frame every question to include options in the framed sentence itself related to the question providing the user a choice.
3. Explanation : Explain the options if using some complex terms in options like 'filigree' or 'embellishments'.
4. Entity Specification: Clearly mention the key entity in the question. Do not include entities such as metal or size.
5. Context Awareness: Do not repeat key entities already covered in the basic information provided below.
6. Conciseness: Print only the follow-up question and nothing extra, such as explanations or additional comments.
7. Tone: Use a warm and friendly tone to make the user feel welcomed and valued.

**Important**: Respond **only** as the assistant. Do not simulate or generate user responses. 

You can include options for a question with alphabetical indices ( A. , B. , C. ) and explain complex terms if used in the question or options.
Make sure to give suggestions ( from the options ) according to the previous conversation till now . 
Give compliments to user's choices and suggest if something better can be done. f

Make sure to format your response properly ( separated by new lines ).



"""

temp_sys_prompt_1 = """
You are an AI assistant designed to provide personalized and friendly suggestions based on user input. Your goal is to assist users by offering tailored recommendations with multiple clear options, helping them choose based on their preferences.

Generate only the assistant response part according to the following guidelines 

Key characteristics of your responses:
1. **Friendly and Polite**: Always communicate in a courteous and welcoming manner.
2. **Concise and Clear**: Provide information that is easy to understand, using concise language without unnecessary details.
3. **Suggestions in List Format**: Present recommendations in a numbered or bulleted list for easy readability.
4. **Encourage Engagement**: After offering suggestions, invite the user to make a choice or ask follow-up questions.
5. **Customization**: Where relevant, offer alternatives or customizations to meet the user's preferences more precisely.

When responding, adhere to this structure of dividing the response into 3 parts : 
- In the 1st line Acknowledge the user's request  and in the first line Present and mention 1 top recommendation  based on their preferences, ocassion, current trends and the retailer profile : {retailer_profile}
- In the following lines offer a list of alternative options.
- Invite the user to confirm or ask for additional help.

### Example Response:

**Assistant**: "Based on your preferences, I recommend a gold bracelet with a minimal design. Other alternatives include:
1. Silver bracelet with gemstones.
2. Platinum bracelet with intricate designs.
3. Customized engraved bracelet.
Please select one of the options above or let me know if you'd like something else."

### Example Response ends 

Your responses should always be friendly, structured, and aim to guide the user in a helpful way, ensuring they feel comfortable and supported in making their choice.
**Important**: Respond **only** as the assistant. Do not simulate or generate user responses.  
"""

# temp_sys_prompt_2 = """


# """
# temp_sys_prompt_1 = """
# You are a friendly and engaging chatbot for a jewelry company with the following profile: {retailer_profile}. Your role is to assist the customer by asking one specific follow-up question per interaction to better understand their preferences.

# **Guidelines:**
# 1. **Do Not Generate User Inputs**: Only generate responses as the assistant. Do not create or mimic user responses. 
# 2. **Question Specificity**: Ask one short, specific question that focuses on a single key entity to clarify the customer's needs. 
# 3. **Include Options**: Frame every question with options (using A., B., C.), giving the customer clear choices in your question. and print the options in separate lines. 
# 4. **Use of Complex Terms**: If you use terms like 'filigree' or 'embellishments', provide brief explanations of these terms to help the customer understand.
# 5. **Compliment the Customer's Choices**: If the customer has made a selection, compliment their choice and offer helpful suggestions if something might suit their preferences better.
# 6. **Outfit Consideration**: If the customer has provided outfit details, tailor your question to match their outfit and the jewelry options.
# 7. **Tone**: Maintain a warm, friendly tone to make the customer feel valued.
# 8. **Avoid Unnecessary Details**: Only ask the follow-up question, without adding extra information or comments.

# **Important**: Respond **only** as the assistant. Do not simulate or generate responses for the customer. 

# """

# Function to convert the basic info json data and outfit_caption data into a string to be passed to the llm for further response
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

# Function to call the chatbot_response_endpoint 
# Input : json_data = {'system_prompt' : system_prompt , 'user_prompt' : user_prompt}
def get_chatbot_response(json_data):
    return call_endpoint(chatbot_response_endpoint, json_data)['body']


# def display_image_options(image_urls: list):
#     """
#     Displays the images with radio buttons for the user to select using Streamlit, 
#     showing the images in a row with radio buttons beside them.

#     Args:
#     image_urls (list): A list of image URLs to display with radio buttons.

#     """
#     st.write("Please choose an image that matches your preference:")

#     # Create columns for each image and radio button
#     columns = st.columns(len(image_urls) + 1)  # Add 1 for the "None" option

#     # Initialize selected_option as None (default)
#     selected_option = None

#     # Display images with radio buttons
#     for idx, url in enumerate(image_urls):
#         with columns[idx]:
#             # Show the image in the current column
#             st.image(url, caption=f"Image {idx+1}")
#             # Add radio button for each image, defaulting to no selection
#             radio_button = st.radio("Select", [None, f"Image {idx+1}"], key=f'image_{idx}', index=0)
#             if radio_button == f"Image {idx+1}":
#                 selected_option = image_urls[idx]

#     # Add "None" option in the last column
#     with columns[-1]:
#         st.write("None")
#         # Add radio button for the "None" option, defaulting to no selection
#         none_radio_button = st.radio("Select", [None, "None"], key='none', index=0)
#         if none_radio_button == "None":
#             selected_option = "None"

#     return selected_option

# def display_image_options(image_urls: list):
#     """
#     Displays the images with radio buttons for the user to select using Streamlit,
#     showing the images in a row with radio buttons below them.

#     Args:
#     image_urls (list): A list of image URLs to display with radio buttons.

#     Returns:
#     str: The user's selected option (the image URL or 'None').
#     """
#     st.write("Please choose an image that matches your preference:")

#     # Create columns for each image
#     columns = st.columns(len(image_urls))  # One column per image
    
#     # Radio button options: list of image labels and "None" as the last option
#     options = [f"Image {idx+1}" for idx in range(len(image_urls))] + ["None"]

#     # Initialize the radio button group
#     selected_option = st.radio(
#         label="Select an image or choose 'None'",
#         options=options,
#         index=None,  # No initial selection
#         horizontal=True  # Display options horizontally
#     )
    
#     # Show each image in its respective column
#     for idx, url in enumerate(image_urls):
#         with columns[idx]:
#             st.image(url, caption=f"Image {idx+1}")

#     while selected_option == None:
#         print("selection is None")
#         print("selected options")
#         pass 

#     print("\n Option selected \n")

#     # Check if "None" is selected, handle it separately
#     if selected_option == "None":
#         print("hello selected option is None ")
#         return "None"
#     else:
#         print("hello")
#         print(selected_option)
#         print(options.index(selected_option))
#         return image_urls[options.index(selected_option)]  # Return selected image URL


def display_image_options(image_urls: list):
    """
    Displays the images with radio buttons for the user to select using Streamlit,
    showing the images in a row with radio buttons below them within a form.

    Args:
    image_urls (list): A list of image URLs to display with radio buttons.

    Returns:
    str: The user's selected option (the image URL or 'None').
    """
    
    # Initialize session state if it's the first time running the app
    if "selected_image" not in st.session_state:
        st.session_state.selected_image = "None"  # Default to 'None' option
    if "submitted" not in st.session_state:
        st.session_state.submitted = False  # Track submission state

    # Reset submission if we're rendering the page again (i.e., form interaction)
    if st.session_state.submitted:
        st.write(f"You have selected: {st.session_state.selected_image}")
        return st.session_state.selected_image

    # Create a form to contain the radio buttons and submission
    with st.form("image_selection_form"):
        st.write("Please choose an image that matches your preference:")

        # Display the images in columns
        columns = st.columns(len(image_urls))

        for idx, url in enumerate(image_urls):
            with columns[idx]:
                st.image(url, caption=f"Image {idx + 1}")

        # Display the radio buttons inside the form, with session state persistence
        options = [f"Image {idx + 1}" for idx in range(len(image_urls))] + ["None"]
        
        # Maintain the selection from session state across reruns
        selected_option = st.radio(
            label="Select an image or choose 'None'",
            options=options,
            index=options.index(st.session_state.selected_image),
            horizontal=True
        )

        # Submit button to finalize the choice
        submitted = st.form_submit_button("Submit")

        if submitted:
            st.session_state.selected_image = selected_option
            st.session_state.submitted = True
            if selected_option == "None":
                return "None"
            else:
                return image_urls[options.index(selected_option)] 

    # If submit is not clicked, return None
    # return None







def process_image_followup_ques(chosen_image_url,image_des): 
    if chosen_image_url == "None":
        st.session_state.messages.append({"role":"user" , "content":"No, these images do not properly represent the style that I want. Ask some more questions on my choice to help me personalize the style properly to my likings"})
    else: 
        st.session_state.messages.append({"role":"user" , "content" : f"I like this design a lot. Image Description : {image_des} Ask me do I want to personalize this image design or finalize this only"})



    
# Function to properly format the conversation from st.session_state.messages and upload the conversation to the s3_bucket
# returns the link to the file stored in s3_bucket
def format_and_upload_conversation():
    conversation_dict = {}
    for idx, message in enumerate(st.session_state.messages):
        key = f"{message['role']}_{idx}"
        conversation_dict[key] = message['content']
    
    json_conversation = json.dumps(conversation_dict)
    
    event_payload = {
        "body": json_conversation
    }
    
    response = call_endpoint(upload_conversation_endpoint, event_payload)
    response_body = response['body']
    s3_conv_url = response_body.strip('"')
    st.success(f"Conversation saved and successfully uploaded ! Access it [here]({s3_conv_url}).")
    return s3_conv_url
