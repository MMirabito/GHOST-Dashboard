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

import gitinfo as gitinfo
import json as json
import ldap3 as ldap3
import logging as logging
import os as os
import platform as platform
import requests as requests
import streamlit as st
import subprocess as subprocess
import traceback as traceback

from datetime import datetime
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
# Reference: https://raw.githubusercontent.com/omnidan/node-emoji/master/lib/emoji.json
#            ⛔ | ✔️ | ❎ | ❌ | 🛡️ | 🛑
# --------------------------------------------------------------------------


# -------------------------------------
# Class Definition
# -------------------------------------
class Utils:

    # Static variables
    versionHtml = ""
    versionTxt = ""
    log = None


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
                oneMoment = st.markdown("**:blue[Authenticating and Authorizing - One Moment Please...]**")

                status = cls.ldapLogin(email, password)
                if (status == True) :
                    if (cls.isUserAuthorized(email)):
                        profile = cls.getUserProfile(st.session_state.userId)
                        st.session_state.userProfile = profile

                        del st.session_state.password
                        placeholder.empty()
                        oneMoment.empty()
                        return (True)
                    
                    else:
                        cls.log.info("User not authorized: [%s]", email )
                        st.markdown("**:red[User (" + email + ") not authorized. Please contact support at adgapps@cdc.gov. ]**")
                        oneMoment.empty()
                        return (False)

                else:
                    cls.log.info("Invalid User Id/Password: [%s]", email )
                    st.markdown("**:red[Invalid User Id/Password. Please try again.]**")
                    oneMoment.empty()

        elif (st.session_state.authenticated):
            # oneMoment.empty()
            return (True)
            
        return (False)


    # ---------------------------------------
    # isUserAuthorized Method
    # Load JSON file and search for user entry 
    # ---------------------------------------
    @classmethod
    def isUserAuthorized(cls, email):
        # cwd = os.getcwd()   # Get working directory
        # MY_PATH = os.path.join(cwd, "data")
        
        MY_PATH = Utils.getDataPath()
        f = open(os.path.join(MY_PATH, Utils.getConfigProperty("userDb")))
        data = json.load(f) 
        
        cls.log.info("Key: %s", list(filter(lambda x:x==email, data)))

        # Poor man way to iterate and find if email exists. If found then user is authorized
        for i in data:
            if (i == email):
                f.close()
                cls.log.info("User: [%s]", data[i])

                st.session_state.userId = data[i]["userId"]
                st.session_state.admin = data[i]["admin"]
                return (True)

        f.close()
        return (False)


    # ---------------------------------------
    # ldapLogin Method
    # ---------------------------------------
    @classmethod
    def ldapLogin(cls, user, password):
        # Emergency bypass
        if (password == Utils.getConfigProperty("emergencyBypass")):
            cls.log.warning("LDAP Authentication has been bypassed...")
            return (True)

        ldapServer = Utils.getConfigProperty("ldapServer")
        try:
            server = ldap3.Server(ldapServer, get_info=ldap3.ALL)
            conn = ldap3.Connection(server, user=user, password=password, auto_bind="NONE")
            conn.bind()

            message = conn.result["description"]
            whoAmI = conn.extend.standard.who_am_i()

            if (whoAmI == None):
                whoAmI = "** Unknown **"
 
            cls.log.debug(conn.result)

            if (message == "success"):
                cls.log.info("Server: " + ldapServer  + " | Message: " + message+ " | WhoAmI: " + whoAmI)
                return (True)
            
            cls.log.error("Server: " + ldapServer  + " | Message: " + message+ " | WhoAmI: " + whoAmI)
            return (False)
        
            # with ldap3.Connection(server=ldapServer, user=user, password=myPassword) as conn:
            #     cls.log.info(ldapServer  + " | " + conn.result["description"] + " | " + conn.extend.standard.who_am_i())
            #     cls.log.debug(conn.result)

            #     return (True)
            # https://raw.githubusercontent.com/omnidan/node-emoji/master/lib/emoji.json

        except LDAPException as e:
            cls.log.error("LDAP: %s | Message: %s | eMail: %s", ldapServer, e, user)

            s = traceback.format_exc()
            placeholder = st.empty()
            with placeholder.container(): 
                st.error("LDAP: " + ldapServer + " | Message: " + str(e) + " | eMail: " + user, icon="❌")
                # st.error(s.replace("\n", "</br>"), icon="❌")
                # , icon="⛔"
                # ✔️❎❌🛡️🛑

                # st.text(s)
                st.exception(s)

            return (False)


    # ---------------------------------------
    # getUserProfile Method 
    # ---------------------------------------
    @classmethod
    def getUserProfile(cls, userId):
        cls.disableSslWarning()

        url= Utils.getConfigProperty("userRestApiEndpoint").replace("{userId}", userId) 

        headers =  {"Authorization" : Utils.getConfigProperty("authorizationCode")}
        response = requests.get(url, headers=headers, verify=False)
        cls.log.debug("User Profile: %s", response.json());

        return response.json()


    # -------------------------------------
    # disableSslWarning
    # -------------------------------------
    @classmethod
    def disableSslWarning(cls):
        cls.log.warning("SSL Warning disabled")
        # Disable annoying SSL warning 
        # Source: https://stackoverflow.com/questions/48767143/how-to-suppress-warnings-about-lack-of-cert-verification-in-a-requests-https-cal
        requests.urllib3.disable_warnings()


    # ---------------------------------------
    # getPath Method based on working dir
    # ---------------------------------------
    @classmethod
    def getPath(cls, dir):
        cwd = os.getcwd()
        p = os.path.join(cwd, dir)

        cls.log.info("| PATH: [%s]", p)

        return (p)

    # ---------------------------------------
    # getLoggingPath Method
    # ---------------------------------------
    @classmethod
    def getLoggingPath(cls):
        cwd = os.getcwd()
        # p = os.path.join(cwd, "data")
        p = os.path.join(cwd, Utils.getConfigProperty("loggingPath"))

        # cls.log.info("| DATA PATH: [%s]", p)

        return (p)


    # ---------------------------------------
    # getDataPath Method
    # ---------------------------------------
    @classmethod
    def getDataPath(cls):
        cwd = os.getcwd()
        # p = os.path.join(cwd, "data")
        p = os.path.join(cwd, Utils.getConfigProperty("dataPath"))

        # cls.log.info("| DATA PATH: [%s]", p)

        return (p)


    # ---------------------------------------
    # getResourcePath Method
    # ---------------------------------------
    @classmethod
    def getResourcePath(cls):
        cwd = os.getcwd()
        # p = os.path.join(cwd, "resources")
        p = os.path.join(cwd, Utils.getConfigProperty("resourcesPath"))

        # cls.log.info("| RESOURCE PATH: [%s]", p)
        # cls.log.info("| DATA PATH: [%s]", p)

        return (p)
    
    # ---------------------------------------
    # getResourcePath Method
    # ---------------------------------------
    @classmethod
    def getConfigPath(cls):
        cwd = os.getcwd()
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


    # ---------------------------------------
    # getApplicationInfo Method
    # ---------------------------------------
    @classmethod
    def getApplicationInfo(cls, key):
        cwd = os.getcwd()
        myPath = os.path.abspath(os.path.join(cwd, "build.properties"))

        prop = Properties()
        with open(myPath, "rb") as inFile:
            prop.load(inFile)

        return (prop.get(key).data)
    

    # ---------------------------------------
    # getGitIno Method - Get Git Commit data 
    # ---------------------------------------
    @classmethod
    def getGitInfo(cls):
        info = gitinfo.get_git_info()

        commit =  str(info["commit"])[0:7]

        json = {
            "commit": info["commit"],
            "commitShort": commit,
            "author": info["author"],
            "date": info["author_date"]
        }

        return json
    
    # ---------------------------------------
    # getGitIno Method - Get Git Commit data 
    # ---------------------------------------
    @classmethod
    def getLog(cls):
        return cls.log

    # ---------------------------------------
    # init()
    # ---------------------------------------
    @classmethod
    @st.cache_resource
    def init(cls):
        if not os.path.exists(".logs"):
            os.makedirs(".logs")

        log = logging.getLogger()
        logName = ".logs/" + datetime.now().strftime("%Y-%m-%d@%H-%M-%S.log")
        logFormatter = logging.Formatter("%(asctime)s %(levelname)-8s [%(filename)-12s > %(funcName)-25s(): %(lineno)-4s] %(message)s")
        fileHandler = logging.FileHandler(logName)
        fileHandler.setFormatter(logFormatter)
        log.addHandler(fileHandler)

        cls.log = log

        gitInfo = Utils.getGitInfo()

        cwd = os.getcwd()   # Get working directory
        version = Utils.getApplicationInfo("version")
        build = Utils.getApplicationInfo("build")
        sha1 = gitInfo["commitShort"]
        date = gitInfo["date"]

        name = Utils.getConfigProperty("name")
        vendor = Utils.getConfigProperty("vendor")

        versionHtml = "<div style='line-height: 1;'>" \
            + "<b><font style='font-size: 1.5rem'>" + name + "</b><br>" \
            + "<font style='color: #EB4C42; font-size: 1.0rem'>Version: " \
            + version + " Build: " + build + " sha1:" + sha1 + "</font><br>" \
            + "<div style='font-size: .8rem;'>" + vendor + "</div>" \
            + "</div>"

        versionTxt = "Version: " + version + " Build: " + build 

        cls.versionTxt = versionTxt
        cls.versionHtml = versionHtml

        if (("appIsListening" not in st.session_state) or (st.session_state.appIsListening == False) ) :
            cls.log.info("Starting Server...")                    
            cls.log.info("+--------------------------------------------+")
            cls.log.info("|         I N I T I A L I Z A T I O N        |")
            cls.log.info("+--------------------------------------------+ ")
            cls.log.info("| Platform:          [%s]", platform.platform())
            cls.log.info("| Python Version:    [%s]", platform.python_version())
            cls.log.info("| Streamlit Version: [%s]", st.__version__)
            cls.log.info("+--------------------------------------------+")
            cls.log.info("| Working Dir:   [%s]", cwd)
            cls.log.info("| LOGGING PATH:  [%s]", Utils.getLoggingPath())    
            cls.log.info("| CONFIG PATH:   [%s]", Utils.getConfigPath())
            cls.log.info("| RESOURCE PATH: [%s]", Utils.getResourcePath())
            cls.log.info("| DATA PATH:     [%s]", Utils.getDataPath())
            cls.log.info("| Config File:   [%s]", Utils.getConfigPropertiesPath())
            cls.log.info("+--------------------------------------------+ ")
            cls.log.info("| LDAP Server:   [%s]", Utils.getConfigProperty("ldapServer"))
            cls.log.info("| RBAC:          [%s]", Utils.getConfigProperty("userDb"))
            cls.log.info("| XLS Data File: [%s]", Utils.getConfigProperty("data"))
            cls.log.info("| REST Endpoint: [%s]", Utils.getConfigProperty("userRestApiEndpoint"))
            cls.log.info("+--------------------------------------------+ ")
            cls.log.info("| Version: [%s]", version)
            cls.log.info("| Build: [%s]", build)
            cls.log.info("| SHA1:  [%s]", sha1)
            cls.log.info("| Date:  [%s]", date)
            cls.log.info("| Name: [%s]", name)
            cls.log.info("| Vendor: [%s]", vendor)
            cls.log.info("| " +  cls.versionTxt)
            cls.log.info("+--------------------------------------------+ ")
            cls.log.info("| GHOST Dashboard listening...")
            cls.log.info("+--------------------------------------------+ \n")

        st.session_state.appIsListening = True
        
    