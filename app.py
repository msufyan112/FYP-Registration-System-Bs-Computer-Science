import streamlit as st
import pandas as pd
import os

# --- PATH LOGIC ---
current_dir = os.path.dirname(os.path.abspath(__file__))
students_path = os.path.join(current_dir, 'students.csv')
groups_path = os.path.join(current_dir, 'final_groups.csv')

# --- CONFIGURATION ---
st.set_page_config(page_title="FYP Registration Portal", page_icon="🎓", layout="centered")

# --- ADMIN PASSWORD ---
ADMIN_PASSWORD = "host123"  # Change this to your preferred password

# --- BACKGROUND & STYLING ---
def add_custom_style():
    st.markdown(
         f"""
         <style>
         .stApp {{
             background-image: url("https://images.unsplash.com/photo-1517694712202-14dd9538aa97");
             background-attachment: fixed;
             background-size: cover;
         }}
         [data-testid="stForm"] {{
             background-color: rgba(0, 0, 0, 0.4) !important; 
             padding: 30px !important;
             border-radius: 15px !important;
             border: 2px solid rgba(255, 255, 255, 0.5) !important;
             backdrop-filter: blur(8px);
         }}
         /* Bottom container for table */
         .main-table-container {{
             background-color: rgba(0, 0, 0, 0.4);
             padding: 20px;
             border-radius: 15px;
             border: 2px solid rgba(255, 255, 255, 0.5);
             backdrop-filter: blur(8px);
         }}
         h1, h2, h3, label, p, .stMarkdown {{
             color: white !important;
             text-shadow: 2px 2px 8px rgba(0, 0, 0, 1);
         }}
         label {{ font-weight: bold !important; }}
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

# --- SIDEBAR ADMIN CONTROL ---
st.sidebar.title("🔐 Host Access")
admin_key = st.sidebar.text_input("Enter Host Password", type="password")

if admin_key == ADMIN_PASSWORD:
    st.sidebar.success("Logged in as Host")
    st.sidebar.subheader("Admin Controls")
    if st.sidebar.button("🗑️ Clear All Registrations"):
        if os.path.exists(groups_path):
            os.remove(groups_path)
            st.sidebar.warning("File deleted! Refreshing...")
            st.rerun()
else:
    if admin_key != "":
        st.sidebar.error("Incorrect Password")

# --- UI DESIGN ---
st.title("🎓 FYP Registration Portal")
st.markdown("### Final Year Project Group & Supervisor Selection")

# --- THE FORM (Public) ---
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
    
    st.subheader("2. Group Members")
    available = sorted([s for s in all_students if s not in assigned_students])
    
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
    selected_sups = [s for s in [s1, s2, s3] if s != "-- Select --"]
    current_members = [m for m in [m1, m2, m3] if m not in ["-- Select --", "None"]]
    
    if not group_name or len(selected_sups) < 3:
        st.error("⚠️ Please fill in the Title and select ALL 3 supervisor priorities.")
    elif len(set(selected_sups)) < 3:
        st.error("⚠️ Each supervisor choice must be unique.")
    elif len(current_members) < 2:
        st.error("⚠️ A group must have at least 2 members.")
    elif len(current_members) != len(set(current_members)):
        st.error("⚠️ You cannot select the same student twice!")
    else:
        new_row = {
            "Group Name": group_name,
            "1st Choice": s1, "2nd Choice": s2, "3rd Choice": s3,
            "Member 1": m1, "Member 2": m2, "Member 3": m3 if m3 != "None" else ""
        }
        new_data = pd.DataFrame([new_row])
        file_exists = os.path.exists(groups_path)
        new_data.to_csv(groups_path, mode='a', index=False, header=not file_exists)
        st.success(f"✅ Registered successfully!")
        st.balloons()
        st.rerun()

# --- DISPLAY SECTION ---
st.divider()
st.subheader("📋 Registered Groups")

st.markdown('<div class="main-table-container">', unsafe_allow_html=True)
if os.path.exists(groups_path):
    display_df = pd.read_csv(groups_path)
    display_df.index = display_df.index + 1
    
    # Only the Host sees the "Delete Row" logic
    if admin_key == ADMIN_PASSWORD:
        st.info("Host Mode: You can select a row index to delete a specific group.")
        row_to_delete = st.number_input("Enter Row Number to Delete", min_value=1, max_value=len(display_df), step=1)
        if st.button("❌ Delete Selected Row"):
            display_df = display_df.drop(display_df.index[row_to_delete-1])
            display_df.to_csv(groups_path, index=False)
            st.rerun()
            
    st.dataframe(display_df, use_container_width=True)
else:
    st.info("No groups registered yet.")
st.markdown('</div>', unsafe_allow_html=True)
