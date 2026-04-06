import streamlit as st
import pandas as pd
import os

# --- PATH LOGIC ---
current_dir = os.path.dirname(os.path.abspath(__file__))
students_path = os.path.join(current_dir, 'students.csv')
groups_path = os.path.join(current_dir, 'final_groups.csv')

# --- CONFIGURATION ---
st.set_page_config(page_title="FYP Registration Portal", page_icon="🎓", layout="centered")

# --- RENAMED ADMIN VARIABLE ---
FORM_NAME = "FYPREGISTRATION"  # This was previously ADMIN_PASSWORD

# --- BACKGROUND & STYLING ---
def add_custom_style():
    st.markdown(
         f"""
         <style>
         /* 1. Global Background Image */
         .stApp {{
             background-image: url("https://images.unsplash.com/photo-1517694712202-14dd9538aa97");
             background-attachment: fixed;
             background-size: cover;
         }}
         
         /* 2. Styling the Form Container */
         [data-testid="stForm"] {{
             background-color: rgba(0, 0, 0, 0.4) !important; 
             padding: 30px !important;
             border-radius: 15px !important;
             border: 2px solid rgba(255, 255, 255, 0.5) !important;
             backdrop-filter: blur(8px);
         }}

         /* 3. Styling the Registered Groups Area Container */
         .main-table-container {{
             background-color: rgba(0, 0, 0, 0.4);
             padding: 20px;
             border-radius: 15px;
             border: 2px solid rgba(255, 255, 255, 0.5);
             backdrop-filter: blur(8px);
             margin-top: 20px;
         }}

         /* 4. Text Colors and Shadows */
         h1, h2, h3, label, p, .stMarkdown {{
             color: white !important;
             text-shadow: 2px 2px 8px rgba(0, 0, 0, 1);
         }}

         /* Make labels bold */
         label {{
             font-weight: bold !important;
         }}

         /* Styling the Info/Alert boxes */
         .stAlert {{
             background-color: rgba(255, 255, 255, 0.1) !important;
             color: white !important;
             border: 1px solid rgba(255, 255, 255, 0.3) !important;
         }}
         </style>
         """,
         unsafe_allow_html=True
     )

add_custom_style()

# --- DATA LOADING ---
def load_data():
    if not os.path.exists(students_path):
        st.error(f"Error: '{students_path}' not found!")
        return [], []
        
    all_students_df = pd.read_csv(students_path)
    all_students = all_students_df['Name'].tolist()
    
    assigned_students = []
    if os.path.exists(groups_path):
        try:
            df = pd.read_csv(groups_path)
            for col in ['Member 1', 'Member 2', 'Member 3']:
                if col in df.columns:
                    assigned_students.extend(df[col].dropna().tolist())
        except:
            pass
            
    return all_students, assigned_students

# Fixed Supervisor List
supervisors_list = ["Dr. Anwar Muhammad", "Dr. Waseeq ul Islam Zafar", "Mr. Usman Rafi"]
all_students, assigned_students = load_data()

# --- SIDEBAR ADMIN CONTROL (HIDDEN IN EXPANDER) ---
with st.sidebar.expander("🛠️ Admin Portal"):
    st.write("Restricted to Host use only.")
    # Check against FORM_NAME logic
    admin_key = st.text_input("Enter Host Password", type="password")

    if admin_key == FORM_NAME:
        st.success("Logged in as Host")
        st.subheader("Admin Controls")
        
        if st.button("🗑️ Clear All Registrations"):
            if os.path.exists(groups_path):
                os.remove(groups_path)
                st.warning("File deleted! Refreshing...")
                st.rerun()
    else:
        if admin_key != "":
            st.error("Incorrect Password")

# --- UI DESIGN ---
st.title("🎓 FYP Registration Portal")
st.markdown("### Final Year Project Group & Supervisor Selection")

# --- THE FORM ---
with st.form("registration_form", clear_on_submit=True):
    st.subheader("1. Project Details")
    group_name = st.text_input("Project Title / Group Name", placeholder="Enter your project title...")
    
    st.write("**Supervisor Priorities (Select three unique supervisors)**")
    c1, c2, c3 = st.columns(3)
    with c1:
        s1 = st.selectbox("1st Choice (Highest)", ["-- Select --"] + supervisors_list)
    with c2:
        s2 = st.selectbox("2nd Choice", ["-- Select --"] + supervisors_list)
    with c3:
        s3 = st.selectbox("3rd Choice (Lowest)", ["-- Select --"] + supervisors_list)
    
    st.divider()
    
    st.
