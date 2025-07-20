import streamlit as st
import json
import os
from PIL import Image 

# amogus

if 'language' not in st.session_state:
    st.session_state.language = 'en'

resume = {}
selected_category_ = ''
st.set_page_config(page_title="Rozgaar | Employer Portal", page_icon="👨‍💼")

def load_resumes_from_directory(org_name):
    global resume, selected_category_
    """
    Load resumes from JSON files in the 'upload' directory for a specific organization
    
    :param org_name: Name of the organization
    :return: List of resumes or empty list if no matching files found
    """
    upload_dir = 'uploads'
    resumes = []
    
    # Ensure the upload directory exists
    if not os.path.exists(upload_dir):
        st.warning(f"Upload directory '{upload_dir}' does not exist.")
        return resumes
    
    # Look for JSON files matching the organization name
    for filename in os.listdir(upload_dir):
        if filename.lower().startswith(org_name.lower()) and filename.endswith('.json'):
            filepath = os.path.join(upload_dir, filename)
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    
                    # Transform the data to match the expected resume structure
                    resume_ = {
                        'name': data.get('personal_info', {}).get('name', 'Unknown'),
                        'age': data.get('personal_info', {}).get('age', 0),
                        'gender': data.get('personal_info', {}).get('gender', 'Unknown'),
                        'locality': data.get('personal_info', {}).get('locality', 'Unknown'),
                        'experience': data.get('additional_text', 'No experience details'),
                        'skills': data.get('additional_text', 'No skills specified')
                    }

                    resume =resume_
                    
                    # Check if the resume is for the correct organization
                    selected_category_ = data.get('selected_category')
                    if data.get('selected_category') == org_name:
                        resumes.append(resume)
            except json.JSONDecodeError:
                st.error(f"Error decoding JSON file: {filename}")
            except Exception as e:
                st.error(f"Error reading file {filename}: {str(e)}")
    
    return resumes

# Organizations data
organizations = {
    "Construction Work": {
        "logo": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSKmnB4qqUHCSxP3vyzkJ3aPgqhGTUoZeT5tg&s",
        "description": {
            'en': "Seeking skilled construction workers for various infrastructure projects.",
            'hi': "विभिन्न बुनियादी ढांचा परियोजनाओं के लिए कुशल निर्माण श्रमिकों की तलाश।"
        },
        "requirements": {
            'en': [
                "Minimum 2 years of experience in construction work",
                "Knowledge of safety protocols at construction sites",
                "Physical fitness and ability to work in challenging environments",
                "Proficiency in using construction tools and equipment",
                "Basic understanding of construction techniques",
            ],
            'hi': [
                "निर्माण कार्य में न्यूनतम 2 वर्ष का अनुभव",
                "निर्माण स्थलों पर सुरक्षा प्रोटोकॉल का ज्ञान",
                "शारीरिक फिटनेस और चुनौतीपूर्ण वातावरण में काम करने की क्षमता",
                "निर्माण उपकरणों के उपयोग में कुशलता",
                "निर्माण तकनीकों की बुनियादी समझ",
            ]
        },
        "link": "https://parkersconsultings.com/",
    },
    "Domestic Work": {
        "logo": "https://www.shutterstock.com/image-vector/cleaning-service-design-house-broom-600nw-2486911437.jpg",
        "description": {
            'en': "Seeking compassionate and skilled domestic workers for household support.",
            'hi': "घरेलू सहायता के लिए करुणामय और कुशल घरेलू कामगारों की तलाश।"
        },
        "requirements": {
            'en': [
                "Experience in household management and cleaning",
                "Excellent communication and interpersonal skills",
                "Ability to work flexible hours",
                "Cooking skills and knowledge of meal preparation",
                "Basic first aid and childcare knowledge",
            ],
            'hi': [
                "घरेलू प्रबंधन और सफाई में अनुभव",
                "उत्कृष्ट संचार और अंतर-व्यक्तिगत कौशल",
                "लचीले घंटों में काम करने की क्षमता",
                "पाक कला और भोजन तैयारी का ज्ञान",
                "बुनियादी प्राथमिक चिकित्सा और बाल देखभाल का ज्ञान",
            ]
        },
        "link": "https://www.sulekha.com/domestic-help-services/bangalore",
    },
    "Handicraft Workshop": {
        "logo": "https://ashahandicrafts.in/wp-content/uploads/2021/04/MAROON-ASHA-Logo.png",
        "description": {
            'en': "Seeking talented handicraft artists to join our creative team.",
            'hi': "अपनी रचनात्मक टीम में शामिल होने के लिए प्रतिभाशाली हस्तशिल्प कलाकारों की तलाश।"
        },
        "requirements": {
            'en': [
                "Proficiency in handicraft techniques (e.g., weaving, pottery, or embroidery)",
                "Portfolio showcasing past work",
                "Attention to detail and creativity",
                "Ability to work independently and in teams",
                "Passion for preserving traditional arts",
            ],
            'hi': [
                "हस्तशिल्प तकनीकों में कुशलता (जैसे बुनाई, मिट्टी के बर्तन या कढ़ाई)",
                "पिछले काम को प्रदर्शित करने वाला पोर्टफोलियो",
                "विवरण और रचनात्मकता पर ध्यान",
                "स्वतंत्र और टीम में काम करने की क्षमता",
                "पारंपरिक कलाओं को संरक्षित करने का जुनून",
            ]
        },
        "link": "https://ashahandicrafts.in/",
    },
}

def toggle_language():
    """Toggle between English and Hindi languages"""
    st.session_state.language = 'hi' if st.session_state.language == 'en' else 'en'

def filter_resumes(resumes, min_age=None, max_age=None, gender=None, locality=None):
    """
    Filter resumes based on age, gender, and locality
    
    :param resumes: List of resume dictionaries
    :param min_age: Minimum age (inclusive)
    :param max_age: Maximum age (inclusive)
    :param gender: Specific gender to filter
    :param locality: Specific locality to filter
    :return: Filtered list of resumes
    """
    filtered_resumes = resumes.copy()
    
    # Filter by minimum age
    if min_age is not None:
        filtered_resumes = [r for r in filtered_resumes if r['age'] >= min_age]
    
    # Filter by maximum age
    if max_age is not None:
        filtered_resumes = [r for r in filtered_resumes if r['age'] <= max_age]
    
    # Filter by gender
    if gender and gender != "All":
        filtered_resumes = [r for r in filtered_resumes if r['gender'].lower() == gender.lower()]
    
    # Filter by locality
    if locality and locality != "All":
        filtered_resumes = [r for r in filtered_resumes if r['locality'].lower() == locality.lower()]
    
    return filtered_resumes

# Sidebar setup
st.sidebar.title("Select Organization")
st.sidebar.button("Switch Language", on_click=toggle_language)
selected_org = st.sidebar.radio("Organizations", list(organizations.keys()))

# Main page content
org_details = organizations[selected_org]
st.title(selected_org)

# Display logo and description
col1, col2 = st.columns([2, 1])
with col1:
    st.subheader("About the Organization" if st.session_state.language == 'en' else "संगठन के बारे में")
    st.write(org_details["description"][st.session_state.language])

with col2:
    if org_details["logo"]:
        st.image(org_details["logo"], caption=f"{selected_org} Logo", use_container_width=True)
    else:
        st.write("Logo not available")

# Display requirements
st.subheader("Key Requirements" if st.session_state.language == 'en' else "मुख्य आवश्यकताएं")
current_requirements = org_details["requirements"][st.session_state.language]
st.write("- " + "\n- ".join(current_requirements))

# Resume Filtering Section
st.header("Applicant Resumes")

# Load resumes for the selected organization
org_resumes = load_resumes_from_directory(selected_org)

# Prepare unique localities for filtering
localities = ["All"] + sorted(list(set(resume.get('locality', '') for resume in org_resumes)))

# Filter inputs
col1, col2, col3, col4 = st.columns(4)
with col1:
    min_age = st.number_input("Minimum Age", min_value=18, max_value=70, value=18)
with col2:
    max_age = st.number_input("Maximum Age", min_value=18, max_value=70, value=70)
with col3:
    gender_filter = st.selectbox("Gender", ["All", "Male", "Female"])
with col4:
    locality_filter = st.selectbox("Locality", localities)

# Filter resumes
filtered_resumes = filter_resumes(
    org_resumes, 
    min_age=min_age, 
    max_age=max_age, 
    gender=gender_filter,
    locality=locality_filter
)

# Display filtered resumes
if filtered_resumes:
    col1, col2 = st.columns([1, 1]) 
    with col1:
        md_list = []
        for i in os.listdir("uploads"): 
            if i.endswith('.md'):
                md_list.append(i.lower())

        for i in md_list:
            with open("uploads/"+i, 'r') as file:
                st.markdown(file.read())
    with col2: 
        st.image(Image.open(os.path.join("uploads", f"{selected_category_.lower()}_{resume['name'].lower()}.png")).resize((256,256)), caption="Profile Image", use_container_width=True)
else:
    st.warning("No resumes match the current filter criteria.")

# Existing link button
if st.button("Visit Organization Page" if st.session_state.language == 'en' else "संगठन पृष्ठ पर जाएं"):
    st.markdown(f"[Click here to visit]({org_details['link']})", unsafe_allow_html=True)

