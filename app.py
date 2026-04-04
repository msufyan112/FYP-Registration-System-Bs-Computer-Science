import streamlit as st
import pandas as pd
import os

# --- PATH LOGIC (Prevents FileNotFoundError on Cloud) ---
current_dir = os.path.dirname(os.path.abspath(__file__))
students_path = os.path.join(current_dir, 'students.csv')
groups_path = os.path.join(current_dir, 'final_groups.csv')

# --- CONFIGURATION ---
st.set_page_config(page_title="FYP Registration Portal", page_icon="🎓", layout="centered")

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
         
         /* 2. Styling the Form Container - TRANSPARENT WITH BORDER */
         [data-testid="stForm"] {{
             background-color: rgba(0, 0, 0, 0.4) !important; 
             padding: 30px !important;
             border-radius: 15px !important;
             border: 2px solid rgba(255, 255, 255, 0.5) !important;
             backdrop-filter: blur(8px);
         }}

         /* 3. Styling the Registered Groups Area - TRANSPARENT WITH BORDER */
         [data-testid="stVerticalBlock"] > div:last-child {{
             background-color: rgba(0, 0, 0, 0.4) !important;
             padding: 20px !important;
             border-radius: 15px !important;
             border: 2px solid rgba(255, 255, 255, 0.5) !important;
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
            # Collect all members already registered to filter them out
            for col in ['Member 1', 'Member 2', 'Member 3']:
                if col in df.columns:
                    assigned_students.extend(df[col].dropna().tolist())
        except:
            pass
            
    return all_students, assigned_students

# Supervisor and Priority Data
supervisors = ["Dr. Anwar Muhammad", "Dr. Waseeq ul Islam Zafar", "Mr. Usman Rafi"]
priorities = ["1 (Highest)", "2 (Middle)", "3 (Lowest)"]

all_students, assigned_students = load_data()

# --- UI DESIGN ---
st.title("🎓 FYP Registration Portal")
st.markdown("### Final Year Project Group & Supervisor Selection")

# --- THE FORM ---
with st.form("registration_form", clear_on_submit=True):
    st.subheader("1. Project Details")
    group_name = st.text_input("Project Title / Group Name", placeholder="Enter your project title...")
    
    # Priority on Supervisor Selection
    col_sup, col_prio = st.columns([2, 1])
    with col_sup:
        selected_supervisor = st.selectbox("Select Supervisor", ["-- Select Supervisor --"] + supervisors)
    with col_prio:
        selected_priority = st.selectbox("Selection Priority", priorities)
    
    st.divider()
    
    st.subheader("2. Group Members")
    available = [s for s in all_students if s not in assigned_students]
    available.sort()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        m1 = st.selectbox("Member 1 (Leader)", ["-- Select --"] + available)
    with col2:
        m2 = st.selectbox("Member 2", ["-- Select --"] + available)
    with col3:
        m3 = st.selectbox("Member 3 (Optional)", ["-- Select --", "None"] + available)

    submit = st.form_submit_button("Submit Registration")

# --- LOGIC ---
if submit:
    current_selection = [m for m in [m1, m2, m3] if m not in ["-- Select --", "None"]]
    
    if not group_name or selected_supervisor == "-- Select Supervisor --":
        st.error("⚠️ Please fill in the Project Title and select a Supervisor.")
    elif len(current_selection) < 2:
        st.error("⚠️ A group must have at least 2 members.")
    elif len(current_selection) != len(set(current_selection)):
        st.error("⚠️ You cannot select the same student twice!")
    else:
        new_row = {
            "Group Name": group_name,
            "Supervisor": selected_supervisor,
            "Priority": selected_priority[0], # Saves '1', '2', or '3'
            "Member 1": m1,
            "Member 2": m2,
            "Member 3": m3 if m3 != "None" else ""
        }
        
        new_data = pd.DataFrame([new_row])
        
        file_exists = os.path.exists(groups_path)
        new_data.to_csv(groups_path, mode='a', index=False, header=not file_exists)
        
        st.success(f"✅ Group Registered! Priority: {selected_priority[0]}")
        st.balloons()
        st.rerun()

# --- DISPLAY SECTION ---
st.divider()
st.subheader("📋 Registered Groups")
if os.path.exists(groups_path):
    display_df = pd.read_csv(groups_path)
    # Start Index from 1
    display_df.index = display_df.index + 1
    st.dataframe(display_df, use_container_width=True)
else:
    st.info("No groups registered yet.")
