import streamlit as st
import speech_recognition as sr
from audiorecorder import audiorecorder
from pydub import AudioSegment
import ollama
import uuid
import os
import json
from PIL import Image
import os

# Ensure upload directory exists
os.makedirs('uploads', exist_ok=True)

eng_works = ['Domestic Work','Handicraft Workshop','Construction Work']
# Localization Dictionaries
LOCALIZATION = {
    'en': {
        'title': "📝 Multilingual Resume Builder",
        'subtitle': "Helping Job Seekers Create Resumes Easily",
        'input_modes': ['Voice Input', 'Manual Input'],
        'personal_details': {
            'name': "Your Name (Optional)",
            'age': "Age (Optional)",
            'gender': "Gender (Optional)",
            'locality': "Locality/City (Optional)",
            'genders': ["Not Specified", "Male", "Female", "Other"],
        },
        'voice_input': {
            'record_additional': "Record Additional Experience Details",
            'record_instructions': "Click the button below to record additional details",
            'start_recording': "Start Recording",
            'stop_recording': "Stop Recording"
        },
        'manual_input': {
            'enter_additional': "Enter Additional Experience Details",
            'placeholder': "Provide any extra information about your experience, achievements, or work history..."
        },
        'job_category': "Select Your Work Type",
        'job_categories': [
            "Domestic Work", 
            "Handicraft Workshop", 
            "Construction Work"
        ]
    },
    'hi': {
        'title': "📝 बहुभाषी रेज्यूमे निर्माता",
        'subtitle': "नौकरी चाहने वालों के लिए रेज्यूमे बनाने में आसानी",
        'input_modes': ['ध्वनि इनपुट', 'मैनुअल इनपुट'],
        'personal_details': {
            'name': "आपका नाम (वैकल्पिक)",
            'age': "आयु (वैकल्पिक)",
            'gender': "लिंग (वैकल्पिक)",
            'locality': "स्थान/शहर (वैकल्पिक)",
            'genders': ["अनिर्दिष्ट", "पुरुष", "महिला", "अन्य"],
        },
        'voice_input': {
            'record_additional': "अतिरिक्त अनुभव विवरण रिकॉर्ड करें",
            'record_instructions': "अतिरिक्त विवरण रिकॉर्ड करने के लिए नीचे दिए गए बटन को दबाएं",
            'start_recording': "रिकॉर्डिंग शुरू करें",
            'stop_recording': "रिकॉर्डिंग रोकें"
        },
        'manual_input': {
            'enter_additional': "अतिरिक्त अनुभव विवरण दर्ज करें",
            'placeholder': "अपने अनुभव, उपलब्धियों या काम के इतिहास के बारे में अतिरिक्त जानकारी प्रदान करें..."
        },
        'job_category': "अपना काम का प्रकार चुनें",
        'job_categories': [
            "घरेलू कार्य", 
            "हस्तशिल्प कार्यशाला", 
            "निर्माण कार्य"
        ]
    }
}

# App Configuration
st.set_page_config(
    page_title="Rozgaar | Employee portal", 
    page_icon="📝", 
    layout="centered"
)

if 'language' not in st.session_state:
    st.session_state.language = 'en'
if 'input_mode' not in st.session_state:
    st.session_state.input_mode = LOCALIZATION['en']['input_modes'][0]

def toggle_language():
    st.session_state.language = 'hi' if st.session_state.language == 'en' else 'en'

def toggle_input_mode():
    current_modes = LOCALIZATION[st.session_state.language]['input_modes']
    # Use the first mode as default if current mode not found
    try:
        current_index = current_modes.index(st.session_state.input_mode)
    except ValueError:
        current_index = 0
    
    # Cycle to the next mode
    st.session_state.input_mode = current_modes[(current_index + 1) % len(current_modes)]

def generate_resume(personal_info, selected_category, additional_text):
    # Prepare context from personal info
    context_details = []
    if personal_info['name']:
        context_details.append(f"Name: {personal_info['name']}")
    if personal_info['age']:
        context_details.append(f"Age: {personal_info['age']}")
    if personal_info['gender'] and personal_info['gender'] != "Not Specified":
        context_details.append(f"Gender: {personal_info['gender']}")
    if personal_info['locality']:
        context_details.append(f"Locality: {personal_info['locality']}")

    # Combine context details with additional text
    full_context = "\n".join(context_details)
    if additional_text:
        full_context += f"\n\nAdditional Details:\n{additional_text}"

    # Generate Resume Prompt
    resume_prompt = f"""
    Create a professional resume for a {selected_category} worker.
    Language of Resume: {st.session_state.language}
    
    Context of Professional Experience:
    {full_context}
    
    Guidelines:
    - Use simple, clear language
    - Highlight practical skills
    - Consider limited formal education
    - Focus on real-world experiences
    - Suitable for entry-level positions
    - Do not make up experience or data
    - Use only provided information
    - Do not output anything other than the resume's contents
    - Do not falsely add experience, you can however elaborate on the skills given
    - If not enough experienced is provided just say "not enough info given"
    """
    
    # Generate Resume using Ollama
    resume_response = ollama.chat(
        model='llama3.1', 
        messages=[{'role': 'user', 'content': resume_prompt}]
    )
    resume_content = resume_response['message']['content']

    # Save resume as .md file
    resume_filename = f"uploads/{selected_category.lower()}_{personal_info['name'].lower()}.md"
    with open(resume_filename, "w", encoding="utf-8") as md_file:
        md_file.write(resume_content)

    # Save context as JSON file
    if selected_category not in eng_works:
        if selected_category == "घरेलू कार्य":
            selected_category = "Domestic Work"
        if selected_category == "हस्तशिल्प कार्यशाला":
            selected_category = "Handicraft Workshop"
        if selected_category == "निर्माण कार्य":
            selected_category = "Construction Work"
    context_filename = f"uploads/{selected_category.lower()}_{personal_info['name'].lower()}_context.json"
    context_data = {
        "personal_info": personal_info,
        "selected_category": selected_category,
        "additional_text": additional_text
    }
    with open(context_filename, "w", encoding="utf-8") as json_file:
        json.dump(context_data, json_file, indent=4, ensure_ascii=False)

    return resume_content, resume_filename, context_filename

def main():
    # Language and Input Mode Toggles
    col1, col2 = st.columns(2)
    with col1:
        st.button(
            "🌐 Switch Language" if st.session_state.language == 'en' else "🌐 भाषा बदलें", 
            on_click=toggle_language
        )
    with col2:
        st.button(
            "🔄 Switch Input Mode", 
            on_click=toggle_input_mode
        )

    # Get current localization
    loc = LOCALIZATION[st.session_state.language]

    # Main Title and Subtitle
    st.title(loc['title'])
    st.markdown(f"""
    ### {loc['subtitle']}
    """)

    # Personal Details Section
    st.header("Personal Details")
    
    # Create columns for personal details
    col1, col2 = st.columns(2)
    
    with col1:
        # Name and Age
        name = st.text_input(loc['personal_details']['name'], key='name')
        age = st.number_input(loc['personal_details']['age'], min_value=0, max_value=100, key='age', step=1)
    
    with col2:
        # Gender and Locality
        gender = st.selectbox(
            loc['personal_details']['gender'], 
            loc['personal_details']['genders'], 
            key='gender'
        )
        locality = st.text_input(loc['personal_details']['locality'], key='locality')

    # Job Category Selection
    selected_category = st.selectbox(
        loc['job_category'], 
        loc['job_categories']
    )

    # Input Mode Selection
    additional_text = ""
    if st.session_state.input_mode == loc['input_modes'][0]:  # Voice Input
        # Voice Input Section
        st.subheader(loc['voice_input']['record_additional'])
        st.info(loc['voice_input']['record_instructions'])
        
        audio = audiorecorder(
            loc['voice_input']['start_recording'], 
            loc['voice_input']['stop_recording']
        )

        if len(audio) > 0:
            # Generate unique filename
            unique_filename = f"uploads/{uuid.uuid4()}"
            mp3_path = f"{unique_filename}.mp3"
            wav_path = f"{unique_filename}.wav"
            
            try:
                # Save MP3
                audio.export(mp3_path, format="mp3")
                
                # Convert to WAV
                audio_segment = AudioSegment.from_mp3(mp3_path)
                audio_segment.export(wav_path, format="wav")
                
                # Display audio details
                st.audio(audio.export().read())
                
                # Speech Recognition
                recognizer = sr.Recognizer()
                with sr.AudioFile(wav_path) as source:
                    audio_data = recognizer.record(source)
                
                # Transcribe
                additional_text = recognizer.recognize_google(
                    audio_data, 
                    language='en' if st.session_state.language == 'en' else 'hi'
                )
                
                st.subheader("Transcribed Text")
                st.write(additional_text)
            
            except Exception as e:
                st.error(f"An error occurred during voice recording: {e}")
                return

    else:  # Manual Input
        st.subheader(loc['manual_input']['enter_additional'])
        additional_text = st.text_area(
            "Additional Experience Details", 
            placeholder=loc['manual_input']['placeholder'],
            height=200
        )

    # Resume Generation
    if st.button("Generate Resume"):
        # Prepare personal info dictionary
        personal_info = {
            'name': name,
            'age': age,
            'gender': gender,
            'locality': locality
        }

        if additional_text.strip() or any(personal_info.values()):
            with st.spinner('Generating Resume...'):
                try:
                    resume_content = generate_resume(
                        personal_info, 
                        selected_category, 
                        additional_text
                    )
                    
                    # Display Resume
                    st.subheader("Generated Resume")
                    st.markdown(f'{resume_content[0]}')
                    
                    # Save Resume Option
                    if st.button("💾 Save Resume"):
                        resume_filename = f"uploads/{uuid.uuid4()}_resume_{st.session_state.language}.txt"
                        with open(resume_filename, 'w', encoding='utf-8') as f:
                            f.write(resume_content)
                        st.success(f"Resume saved as {resume_filename}")
                
                except Exception as e:
                    st.error(f"An error occurred while generating resume: {e}")
        else:
            st.warning("Please provide some information before generating a resume.")

    uploaded_file = st.camera_input("Take your PHOTO!")

    if uploaded_file is not None:
    # Open the uploaded image using PIL
        image = Image.open(uploaded_file)
    
        st.image(image, caption="Uploaded Photo", use_column_width=True)

        paath = os.path.join("uploads", f'{selected_category.lower()}_{name.lower()}.png')
        print(paath)
        image.save(paath)
        st.write("Photo uploaded successfully!")
        

# Additional UI Enhancements
def add_sidebar():
    st.sidebar.title("About This App")
    st.sidebar.info("""
    ### Job Seekers Support Tool
    - Switch between voice and manual input
    - Create resumes in multiple languages
    - AI-powered resume generation
    - Designed for workers with limited formal education
    """)

    st.sidebar.markdown("### Support Information")
    st.sidebar.markdown("""
    📞 Helpline: +91-8618377281
    📧 Email: support@resumebuilder.org
    """)

# Run the App
if __name__ == "__main__":
    add_sidebar()
    main()