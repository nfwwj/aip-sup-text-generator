import streamlit as st
import os

def check_password():
    """Requires the password on every single page load or interaction."""
    if st.session_state.get("aipic_authenticated"):
        return True
    
    # Create an explicit login container layout
    with st.container():
        st.title("🔒 Restricted for AIP IC only.")
        
        # We use a form so hitting 'Enter' or clicking submit handles the validation in one pass
        with st.form("aipic_login_form"):
            password = st.text_input("Enter AIP IC Password:", type="password")
            submitted = st.form_submit_button("Submit")
            
            if submitted:
                target_password = os.environ.get("aipic_password")
                
                if password == target_password:
                    # Clean the screen space immediately so content renders smoothly
                    st.session_state["aipic_authenticated"] = True
                    st.rerun()
                else:
                    st.error("❌ Wrong password!")
                    return False
                    
    return False
            
def remove_auth():
    st.session_state["aipic_authenticated"] = False


