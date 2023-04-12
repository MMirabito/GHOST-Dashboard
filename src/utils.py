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

from distutils.core import setup
import gitinfo as gitinfo
import json as json
import ldap3 as ldap3
import logging as logging
import os as os
import platform as platform
import requests as requests
import shutil as shutil
import streamlit as st
import subprocess as subprocess
import sys as sys 
import traceback as traceback
import uuid as uuid

from datetime import datetime
from jproperties import Properties 
from ldap3.core.exceptions import LDAPException
from PIL import Image
from streamlit import runtime
from streamlit.runtime.scriptrunner import get_script_run_ctx

# --------------------------------------------------------------------------
# Description:
# 
# UTILS is a utility class used to encapsulate functionality used by a 
# streamlit application 
# 
# Reference: https://raw.githubusercontent.com/omnidan/node-emoji/master/lib/emoji.json
#            ⛔ | ✔️ | ❎ | ❌ | 🛡️ | 🛑 | ℹ️
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
            s = traceback.format_exc()
            cls.log.error(s)
            return (None)

        return (session_info.request.remote_ip)
    

    # ---------------------------------------
    # isUserAuthenticated() Method
    # ---------------------------------------
    @classmethod
    def isUserAuthenticated(cls):
        if (("authenticated" not in st.session_state) or (st.session_state.authenticated == False) ) :
            login = st.empty()
            errorMessage = st.empty()
            with login.form("login", clear_on_submit=False):
                st.title("GHOST Dashboard")
                st.subheader("LOGIN")
                st.text_input("eMail:", key="email", value="")
                st.text_input("AD Password:", type="password", key="password", value="")
                st.form_submit_button(label="Login", type="primary") 
                st.markdown(Utils.versionHtml, unsafe_allow_html=True)

                # for name, value in os.environ.items():
                #     val = "<div style='line-height: 1;'><b>" + name + "</b> :: "  + value + "</div>"
                #     st.markdown(val, unsafe_allow_html=True)
                    
                # st.markdown("DEBUG - DEBUG - DEBUG - DEBUG", unsafe_allow_html=True)

                # st.markdown("Data Path: " + str(Utils.getDataPath()), unsafe_allow_html=True)

                
            if ( ("email" in st.session_state and "password" in st.session_state) 
                and (st.session_state.email and st.session_state.password) ):

                email = st.session_state.email
                password = st.session_state.password
                
                cls.log.info("User Id: [%s] :: Password: [%s]", email, "*"*len(password))
                oneMoment = st.info("Authenticating and Authorizing - One Moment Please.", icon="ℹ️")

                errorMessage.empty()

                status = cls.ldapLogin(email, password)
                if (status == True) :
                    if (cls.isUserAuthorized(email)):
                        profile = cls.getUserProfile(st.session_state.userId)
                        st.session_state.userProfile = profile

                        del st.session_state.password
                        login.empty()
                        oneMoment.empty()
                        return (True)
                    
                    else:
                        cls.log.info("User not authorized: [%s]", email )
                        errorMessage.error("User (" + email + ") not authorized. Please contact support at adgapps@cdc.gov.", icon="⛔")
                        oneMoment.empty()
                        
                        return (False)

                else:
                    cls.log.info("Invalid User Id/Password: [%s]", email )
                    errorMessage.error('Invalid User Id/Password. Please try again.', icon="⛔")
                    oneMoment.empty()

        elif (st.session_state.authenticated):
            # oneMoment.empty()
            return (True)
            
        return (False)


    # ---------------------------------------
    # isUserAuthorized() Method
    # Load JSON file and search for user entry 
    # ---------------------------------------
    @classmethod
    def isUserAuthorized(cls, email):
        # cwd = os.getcwd()   # Get working directory
        # MY_PATH = os.path.join(cwd, "data")

        # Remember need to use random key for access 
        if(email == "admin"):
            cls.log.info("User: [%s]", email)
            st.session_state.userId = "admin"
            st.session_state.admin = "Y"            
            return (True)
        
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
    # ldapLogin() Method
    # ---------------------------------------
    @classmethod
    def ldapLogin(cls, user, password):
        # print(password)
        # print(user + "|" + Utils.getEmergencyKey())

        # Emergency bypass - panic button
        if (password == (user + "|" + Utils.getEmergencyKitKey())):
            cls.log.warning("PANIC BUTTON! - [%s] - LDAP Authentication has been bypassed...", user)
            return (True)

        ldapServer = Utils.getConfigProperty("ldapServer")
        try:
            server = ldap3.Server(ldapServer, get_info=ldap3.ALL)
            conn = ldap3.Connection(server, user=user, password=password, auto_bind="NONE")
            # return False
        
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
                cls.log.error(s)
                


            return (False)


    # ---------------------------------------
    # getUserProfile() Method 
    # ---------------------------------------
    @classmethod
    def getUserProfile(cls, userId):
        cls.disableSslWarning()

        url= Utils.getConfigProperty("userRestApiEndpoint").replace("{userId}", userId) 

        headers =  {"Authorization" : Utils.getConfigProperty("authorizationCode")}
        response = requests.get(url, headers=headers, verify=False)
        profile = response.json()

        cls.log.debug("User Profile: %s", response.json())
        cls.log.info("User Id: [%s]  Name: [%s]  Center: [%s]", profile["userId"], profile["name"], profile["divisionShortName"])
        
        return (profile)


    # -------------------------------------
    # disableSslWarning()
    # -------------------------------------
    @classmethod
    def disableSslWarning(cls):
        cls.log.warning("SSL Warning disabled")
        # Disable annoying SSL warning 
        # Source: https://stackoverflow.com/questions/48767143/how-to-suppress-warnings-about-lack-of-cert-verification-in-a-requests-https-cal
        requests.urllib3.disable_warnings()


    # ---------------------------------------
    # getPath() Method based on working dir
    # this value should be "/app"
    # ---------------------------------------
    @classmethod
    def getPath(cls, dir):
        cwd = os.getcwd()
        p = os.path.join(cwd, dir)

        return (p)

    # ---------------------------------------
    # getLogPath() Method
    # ---------------------------------------
    @classmethod
    def getLogPath(cls):
        # ----------------------
        # cwd = os.getcwd()
        cwd = "/" if Utils.isAzureAppService() else os.getcwd()
        # p = os.path.join(cwd, "data")
        p = os.path.join(cwd, Utils.getConfigProperty("logPath"))

        if (Utils.isLinux()): 
            p = p.replace("\\", "/")
        else: 
            p = p.replace("/", "\\")

        return (p)


    # ---------------------------------------
    # getDataPath() Method
    # ---------------------------------------
    @classmethod
    def getDataPath(cls):
        # ----------------------
        # cwd = os.getcwd()
        cwd = "/" if Utils.isAzureAppService() else os.getcwd()
        # p = os.path.join(cwd, "data")
                
        p = os.path.join(cwd, Utils.getConfigProperty("dataPath"))
        if (Utils.isLinux()): 
            p = p.replace("\\", "/")
        else: 
            p = p.replace("/", "\\")

        return (p)

    # ---------------------------------------
    # getEmergencyKitPath() Method
    # ---------------------------------------
    @classmethod
    def getEmergencyKitPath(cls):
        # ----------------------
        # cwd = os.getcwd()
        cwd = "/" if Utils.isAzureAppService() else os.getcwd()
        # p = os.path.join(cwd, "data")
        p = os.path.join(cwd, Utils.getConfigProperty("emergencyKitPath"))

        if (Utils.isLinux()): 
            p = p.replace("\\", "/")
        else: 
            p = p.replace("/", "\\")

        return (p)

    # ---------------------------------------
    # getResourcePath() Method
    # ---------------------------------------
    @classmethod
    def getResourcePath(cls):
        cwd = os.getcwd()
        # ----------------------
        # p = os.path.join(cwd, "resources")
        p = os.path.join(cwd, Utils.getConfigProperty("resourcePath"))

        # cls.log.info("| RESOURCE PATH: [%s]", p)
        # cls.log.info("| DATA PATH: [%s]", p)

        return (p)
    
    # ---------------------------------------
    # getResourcePath() Method
    # Path is assumed to be located the working directory 
    # ---------------------------------------
    @classmethod
    def getConfigPath(cls):
        cwd = os.getcwd()
        p = os.path.join(cwd, "conf")

        return (p)

    # ---------------------------------------
    # getEmergencyKey() Method
    # ---------------------------------------
    @classmethod
    def getEmergencyKitKey(cls):
        with open(Utils.getEmergencyKitPath() + "/key.txt", "r") as file:
            return (file.read())

        return (None)

    # ---------------------------------------
    # getConfigProperty() Method
    # ---------------------------------------
    @classmethod
    def getConfigProperty(cls, key):
        myPath = os.path.abspath(os.path.join(Utils.getConfigPath(), "config.properties"))
        prop = Properties()
        
        with open(myPath, "rb") as inFile:
            prop.load(inFile)

        return (str(prop.get(key).data))
    
    # ---------------------------------------
    # getConfigPropertiesPath() Method
    # ---------------------------------------
    @classmethod
    def getConfigPropertiesPath(cls):
        myPath = os.path.abspath(os.path.join(Utils.getConfigPath(), "config.properties"))

        return (myPath)


    # ---------------------------------------
    # getApplicationInfo() Method
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
    # getGitIno() Method - Get Git Commit data 
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

        return (json)
    
    # ---------------------------------------
    # isAzureAppService() Method 
    # ---------------------------------------      
    @classmethod  
    def isAzureAppService(cls):
        id = os.getenv("WEBSITE_INSTANCE_ID")

        return (id is not None)

    # ---------------------------------------
    # isAzureAppService() Method 
    # ---------------------------------------      
    @classmethod  
    def isLocalPythonExecution(cls):
        value = os.getenv("ADG-LOCAL-PYTHON-EXECUTION")

        return (value is not None)

    # ---------------------------------------
    # isLinux() Method 
    # ---------------------------------------      
    @classmethod  
    def isLinux(cls):
        return (str.lower(sys.platform) in "linux")
    
    # ---------------------------------------
    # getLog() Method
    # ---------------------------------------
    @classmethod
    def getLog(cls):
        return cls.log

    # ---------------------------------------
    # dirSetup() Method 
    # One time setup of directories and files 
    # Check if directory exist and create it 
    # ---------------------------------------
    @classmethod
    def dirSetup(cls):
        MY_PATH = Utils.getEmergencyKitPath()        
        if not os.path.exists(MY_PATH): 
            os.makedirs(MY_PATH)

        MY_PATH = Utils.getLogPath()
        if not os.path.exists(MY_PATH): 
            os.makedirs(MY_PATH)

        MY_PATH = Utils.getDataPath()
        if not os.path.exists(MY_PATH): 
            os.makedirs(MY_PATH)

    # ---------------------------------------
    # showAppInfo() Method 
    # One time setup of directories and files 
    # Check if directory exist and create it 
    # ---------------------------------------
    @classmethod
    def showAppInfo(cls):
        image = Image.open(os.path.join(Utils.getResourcePath(), "GHOST_LOGO.png"))
        st.image(image, width=500)
        st.markdown(Utils.versionHtml, unsafe_allow_html=True)
        
        if (st.session_state.userId != "admin"):
            st.markdown("<b>User ID:</b> {0} | <b>Name:</b> {1} | <b>Admin:</b> {2} | <b>User IP:</b> {3} | <b>LDAP:</b> {4}<br><b>Data Path:</b> {5}<br><b>Log Path:</b> {6}"
                        .format(st.session_state.userId
                                , st.session_state.userProfile["name"] + " (" + st.session_state.userProfile["title"] + ")"
                                , st.session_state.admin
                                , Utils.getRemoteIp()
                                , Utils.getConfigProperty("ldapServer")
                                , str(Utils.getDataPath())
                                , str(Utils.getLogPath()))
                                , unsafe_allow_html=True)
        else:
            st.markdown("<b>User ID:</b> {0} | <b>Name:</b> {1} | <b>Admin:</b> {2} | <b>User IP:</b> {3} | <b>LDAP:</b> {4}<br><b>Data Path:</b> {5}<br><b>Log Path:</b> {6}"
                        .format(st.session_state.userId
                                , "Administrator"
                                , st.session_state.admin
                                , Utils.getRemoteIp()
                                , Utils.getConfigProperty("ldapServer")
                                , str(Utils.getDataPath())
                                , str(Utils.getLogPath()))
                                , unsafe_allow_html=True)                    
    
        st.markdown("""---""")

    # ---------------------------------------
    # logSetup() Method 
    # ---------------------------------------
    @classmethod
    def logSetup(cls):
        logPath = Utils.getLogPath()
        log = logging.getLogger()
        logFile = logPath + "/" + datetime.now().strftime("%Y-%m-%d@%H-%M-%S.log")

        logFormatter = logging.Formatter("%(asctime)s %(levelname)-8s [%(filename)-12s > %(funcName)-25s(): %(lineno)-4s] %(message)s")
        fileHandler = logging.FileHandler(logFile)
        fileHandler.setFormatter(logFormatter)
        log.addHandler(fileHandler)

        cls.log = log


    # ---------------------------------------
    # isDataFound() Method 
    # Sanity check to verify data files are available
    # if not then display warning message
    # ---------------------------------------
    @classmethod
    def isDataFound(cls):
        found = True

        msg1 = msg2 = ""
        MY_PATH = Utils.getDataPath() + "/" + Utils.getConfigProperty("data")
        # cls.log.error(MY_PATH)  
        if os.path.isfile(MY_PATH)  == False:
            found = False
            cls.log.error("File not Found: [%s]", MY_PATH)    
            msg1 = "[" + MY_PATH +"]"
            
        MY_PATH = Utils.getDataPath() + "/" + Utils.getConfigProperty("userDb")
        # cls.log.error(MY_PATH)  
        if os.path.isfile(MY_PATH)  == False:
            found = False
            cls.log.error("File not Found: [%s]", MY_PATH)      
            msg2 = "[" + MY_PATH +"]"

        if (found == False):
            # cwd = os.getcwd()
            cwd = "/" if Utils.isAzureAppService() else os.getcwd()
            
            errorMessage = st.empty()
            st.markdown("<b>File(s) not Found:</b><br>" + msg1 + "<br>" + msg2, unsafe_allow_html=True)
            st.markdown("<b>Current working Directory" + cwd + "</b><br>", unsafe_allow_html=True)
            errorMessage.error("Startup aborted. Please add the file(s) listed below", icon="⛔")

            for name, value in os.environ.items():
                cls.log.info("| %s: [%s]", name, value) 

            instance_id = os.environ.get("WEBSITE_INSTANCE_ID")
            if instance_id:
                # The application is running inside an Azure App Service
                cls.log.info("This application is running inside an Azure App Service.")
            else:
                # The application is not running inside an Azure App Service
                cls.log.info("This application is not running inside an Azure App Service.")

        return (found)


    # ---------------------------------------
    # init() Method 
    # ---------------------------------------
    @classmethod
    @st.cache_resource
    def init(cls):

        print("init() ...")
        Utils.dirSetup()
        Utils.logSetup()

        # logPath = Utils.getLogPath()
        # log = logging.getLogger()
        # logFile = logPath + "/" + datetime.now().strftime("%Y-%m-%d@%H-%M-%S.log")

        # logFormatter = logging.Formatter("%(asctime)s %(levelname)-8s [%(filename)-12s > %(funcName)-25s(): %(lineno)-4s] %(message)s")
        # fileHandler = logging.FileHandler(logFile)
        # fileHandler.setFormatter(logFormatter)
        # log.addHandler(fileHandler)

        # cls.log = log


        # Generate random key and save to file user for emergency bypass only
        with open(Utils.getEmergencyKitPath()  + "/key.txt", "w") as file:
            file.write(str(uuid.uuid4()))

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
            + "<font style='color: #0055BD; font-size: 1.0rem'>Version: " \
            + version + " Build: " + build + " sha1:" + sha1 + "</font><br>" \
            + "<div style='font-size: .8rem;'>" + vendor + "</div>" \
            + "</div>"

        versionTxt = "Version: " + version + " Build: " + build 

        cls.versionTxt = versionTxt
        cls.versionHtml = versionHtml

        # if (("appIsListening" not in st.session_state) or (st.session_state.appIsListening == False) ) :
        #     mounts = "-na-"
        myOs = sys.platform

        # import subprocess as subprocess
        # import json
        # data = subprocess.check_output("findmnt --l -t 9p --json", shell=True);
        # data = json.loads(data)

        cls.log.info("Starting Server...")                    
        cls.log.info("+---------------------------------------------+")
        cls.log.info("|  __    _  _____    _                         ")
        cls.log.info("| /__|_|/ \(_  | ---| \ _  _ |_ |_  _  _  __ _|")
        cls.log.info("| \_|| |\_/__) |    |_/(_|_> | ||_)(_)(_| | (_|")
        cls.log.info("+----------------------------------------------")
        cls.log.info("| " + cls.versionTxt)
        cls.log.info("+---------------------------------------------+")
        cls.log.info("|         I N I T I A L I Z A T I O N         |")
        cls.log.info("+---------------------------------------------+")
        cls.log.info("| Platform:           [%s]", platform.platform())
        cls.log.info("| Operating System:   [%s]", myOs)
        cls.log.info("| Python Version:     [%s]", platform.python_version())
        cls.log.info("| Azure AppService:   [%s]", Utils.isAzureAppService())
        cls.log.info("| Linux OS:           [%s]", Utils.isLinux())
        cls.log.info("| Local Execution     [%s]", Utils.isLocalPythonExecution())
        cls.log.info("| Streamlit Version:  [%s]", st.__version__)
        cls.log.info("+---------------------------------------------+")
        cls.log.info("| Working Dir:        [%s]", cwd)
        cls.log.info("| CONFIG PATH:        [%s]", Utils.getConfigPath())
        cls.log.info("| RESOURCE PATH:      [%s]", Utils.getResourcePath())
        cls.log.info("| Config File:        [%s]", Utils.getConfigPropertiesPath())
        cls.log.info("| LOG PATH:           [%s]", Utils.getLogPath())    
        cls.log.info("| DATA PATH:          [%s]", Utils.getDataPath())
        cls.log.info("| EMERGENCY KIT PATH: [%s]", Utils.getEmergencyKitPath())        
        cls.log.info("| Emergency Kit Key:  [%s]", Utils.getEmergencyKitKey())

        # c = 0
        # for mount in data['filesystems']:
        #     c += 1
        #     cls.log.info("| Mount(%s): [%s] -> [%s]", c, mount['target'], mount['source'])
        #     # cls.log.info(mount['target'] + " :: " + mount['source'])

        cls.log.info("+---------------------------------------------+ ")
        cls.log.info("| LDAP Server:   [%s]", Utils.getConfigProperty("ldapServer"))
        cls.log.info("| RBAC:          [%s]", Utils.getConfigProperty("userDb"))
        cls.log.info("| XLS Data File: [%s]", Utils.getConfigProperty("data"))
        cls.log.info("| REST Endpoint: [%s]", Utils.getConfigProperty("userRestApiEndpoint"))
        cls.log.info("+---------------------------------------------+ ")
        cls.log.info("| Version: [%s]", version)
        cls.log.info("| Build:   [%s]", build)
        cls.log.info("| SHA1:    [%s]", sha1)
        cls.log.info("| Date:    [%s]", date)
        cls.log.info("| Name:    [%s]", name)
        cls.log.info("| Vendor:  [%s]", vendor)
        cls.log.info("| " +  cls.versionTxt)
        cls.log.info("+---------------------------------------------+ ")
        cls.log.info("| ENVIRONMENT VARIABLES                       | ")
        cls.log.info("+---------------------------------------------+ ")

        for name, value in os.environ.items():
            cls.log.info("| %s: [%s]", name, value) 

        cls.log.info("+---------------------------------------------+ \n")
        # ---------------------------------------
        # Note: Only Used for local development for simulation
        #       Once running in docker or app service external 
        #       volume will be mapped externally
        # ---------------------------------------
        if (Utils.isLocalPythonExecution()):
            # Get Data directory source and destination
            src = Utils.getPath("data")
            dst = Utils.getDataPath() 

            if (not os.path.exists(dst)):
                cls.log.info("One time setup: Creating data directory and copying data files from: [%s] TO:[%s] \n", src, dst)
                shutil.copytree(src, dst)

            # Log directory
            # src = Utils.getPath(".log")
            # dst = Utils.getLoggingPath() 

            # if (not os.path.exists(dst)):
            #     cls.log.info("One time setup: Creating .log directory: [%s]", dst)
            #     os.mkdir(dst)
                
            #     # shutil.copytree(src, dst)

        cls.log.info("+---------------------------------------------+ ")
        cls.log.info("| GHOST Dashboard listening...")
        cls.log.info("+---------------------------------------------+ \n")
        st.session_state.appIsListening = True

