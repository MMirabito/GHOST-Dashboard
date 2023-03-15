# --------------------------------------------------------------------------
# Name: utils.py
# Created: Mar 1, 2023 10:11:43 PM
#  
# Organization:
#   The Centers for Disease Control and Prevention,
#   Office for Infectious Diseases
#   National Center for HIV, Viral Hepatitis, STD and TB Prevention
#   Division of Viral Hepatitis
# 
#   1600 Clifton Road, Atlanta, GA 30333
# --------------------------------------------------------------------------

import json as json
import ldap3 as ldap3
import logging as logging
import os as os
import streamlit as st

from jproperties import Properties 
from ldap3.core.exceptions import LDAPException
from streamlit import runtime
from streamlit.runtime.scriptrunner import get_script_run_ctx

# --------------------------------------------------------------------------
# Description:
# 
# UTILS is a utility class used to encapsulate functionality used by a 
# streamlit application 
# 
# --------------------------------------------------------------------------


# -------------------------------------
# Class Definition
# -------------------------------------
class Utils:

    log = logging.getLogger(__name__)

    # ---------------------------------------O
    # getRemoteIp()
    # Source: https://stackoverflow.com/questions/75410059/how-to-log-user-activity-in-a-streamlit-app
    # ---------------------------------------
    @classmethod
    def getRemoteIp(cls) -> str:
        try:
            ctx = get_script_run_ctx()
            if ctx is None:
                return (None)

            session_info = runtime.get_instance().get_client(ctx.session_id)

            if session_info is None:
                return (None)

        except Exception as e:
            return (None)

        return (session_info.request.remote_ip)
    

    # ---------------------------------------
    # isUserAuthenticated Method
    # ---------------------------------------
    @classmethod
    def isUserAuthenticated(cls):
        if (("authenticated" not in st.session_state) or (st.session_state.authenticated == False) ) :
            placeholder = st.empty()
            with placeholder.form("login", clear_on_submit=True):
                st.title("GHOST Dashboard")
                st.subheader("LOGIN")
                st.text_input("eMail:", key="email", value="")
                st.text_input("AD Password:", type="password", key="password", value="")
                st.form_submit_button(label="Login", type="primary") 


            if ( ("email" in st.session_state and "password" in st.session_state) 
                and (st.session_state.email and st.session_state.password) ):

                email = st.session_state.email
                password = st.session_state.password

                cls.log.info("User Id: [%s] :: Password: [%s]", email, "*"*len(password))
                status = cls.ldapLogin(email, password)
                if (status == True) :
                    if (cls.isAuthorized(email)):
                        placeholder.empty()
                        del st.session_state.password
                        return (True)
                    
                    else:
                        cls.log.info("User not authorized: [%s]", email )
                        st.markdown("**:red[User (" + email + ") not authorized. Please contact support at adgapps@cdc.gov. ]**")
                        return (False)

                else:
                    cls.log.info("Invalid User Id/Password: [%s]", email )
                    st.markdown("**:red[Invalid User Id/Password. Please try again.]**")

        elif (st.session_state.authenticated):
            return (True)
            
        return (False)


    # ---------------------------------------
    # isAuthorized Method
    # Load JSON file and search for user entry 
    # ---------------------------------------
    @classmethod
    def isAuthorized(cls, email):
        # cwd = os.getcwd()   # Get working directory
        # MY_PATH = os.path.join(cwd, "data")
        
        MY_PATH = Utils.getDataPath()
        f = open(os.path.join(MY_PATH, Utils.getConfigProperty("userDb")))
        data = json.load(f) 
        
        cls.log.info("Key: %s", list(filter(lambda x:x==email, data)))

        # Poorman way to iterate and find if email exists. If found then user is authorized
        for i in data:
            if (i == email):
                f.close()
                cls.log.info("User: [%s]", data[i])

                st.session_state.userId = data[i]["userId"]
                st.session_state.name = data[i]["name"]
                st.session_state.admin = data[i]["admin"]
                return (True)

        f.close()
        return (False)


    # ---------------------------------------
    # ldapLogin Method
    # ---------------------------------------
    @classmethod
    def ldapLogin(cls, user, myPassword):
        ldapServer = Utils.getConfigProperty("ladpServer")

        try:
            with ldap3.Connection(ldapServer, user=user, password=myPassword) as conn:
                cls.log.info(ldapServer  + " | " + conn.result["description"] + " | " + conn.extend.standard.who_am_i())
                cls.log.debug(conn.result)

                return (True)

        except LDAPException as e:
            cls.log.error("LADP: %s | Message: %s | eMail: %s", ldapServer, e, user)
            return (False)




    # ---------------------------------------
    # getPath Method based on working dir
    # ---------------------------------------
    @classmethod
    def getPath(cls, dir):
        cwd = os.getcwd()                       # Get working directory
        p = os.path.join(cwd, dir)

        cls.log.info("| PATH: [%s]", p)

        return (p)

    # ---------------------------------------
    # getDataPath Method
    # ---------------------------------------
    @classmethod
    def getDataPath(cls):
        cwd = os.getcwd()                       # Get working directory
        p = os.path.join(cwd, "data")

        # cls.log.info("| DATA PATH: [%s]", p)

        return (p)


    # ---------------------------------------
    # getResourcePath Method
    # ---------------------------------------
    @classmethod
    def getResourcePath(cls):
        cwd = os.getcwd()                           # Get working directory
        p = os.path.join(cwd, "resources")

        # cls.log.info("| RESOURCE PATH: [%s]", p)
        # cls.log.info("| DATA PATH: [%s]", p)

        return (p)
    
    # ---------------------------------------
    # getResourcePath Method
    # ---------------------------------------
    @classmethod
    def getConfigPath(cls):
        cwd = os.getcwd()                           # Get working directory
        p = os.path.join(cwd, "config")

        return (p)

    # ---------------------------------------
    # getConfigProperty Method
    # ---------------------------------------
    @classmethod
    def getConfigProperty(cls, key):
        myPath = os.path.abspath(os.path.join(Utils.getConfigPath(), "config.properties"))

        prop = Properties()
        with open(myPath, "rb") as inFile:
            prop.load(inFile)

        return (prop.get(key).data)
    
    # ---------------------------------------
    # getConfigPropertiesPath Method
    # ---------------------------------------
    @classmethod
    def getConfigPropertiesPath(cls):
        myPath = os.path.abspath(os.path.join(Utils.getConfigPath(), "config.properties"))

        return (myPath)
