# --------------------------------------------------------------------------
# Name: dasboard.py
# Created: Feb 1, 2023 3:11:43 PM
#  
# Organization:
#   The Centers for Disease Control and Prevention,
#   Office for Infectious Diseases
#   National Center for HIV, Viral Hepatitis, STD and TB Prevention
#   Division of Viral Hepatitis
# 
#   1600 Clifton Road, Atlanta, GA 30333
# --------------------------------------------------------------------------

import dashboard as dashboard
import streamlit as st
import traceback as traceback

from utils import Utils

# NOTE: Move from dashboard.py
# Streamlit global setup needs to run first and only one time
if 'sidebar_state' not in st.session_state:
    st.session_state.sidebar_state = 'collapsed'

st.set_page_config(page_title="GHOST Dashboard",
            page_icon=":bar_chart:",
            layout="wide",
            initial_sidebar_state=st.session_state.sidebar_state
)

# ---------------------------------------
# Main Method
# ---------------------------------------
def main():
    dashboard.display()

# -------------------------------------
# Main entry point
# NOTE: To prevent code in the module from being executed when imported, but only when run directly, you can guard it with this
# 
# Source: https://stackoverflow.com/questions/6523791/why-is-python-running-my-module-when-i-import-it-and-how-do-i-stop-it
# -------------------------------------
if __name__ == "__main__":
    try:
        Utils.init()
        dataFound = Utils.isDataFound()
        if (dataFound) :
            st.session_state.authenticated =  Utils.isUserAuthenticated()

            if (st.session_state.authenticated):
                main()

    except Exception as e:
        s = traceback.format_exc()
        st.text(s)
        log = Utils().getLog()
        log.error(s)








