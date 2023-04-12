@REM Setup configuration files to run locally or build docker image. 

CLS
ECHO OFF

CALL .win-env.cmd

ECHO +---------------------------------------------------+
ECHO   E N V I R O N M E N T     S E T U P
ECHO +---------------------------------------------------+
ECHO  AZ ID:                 [%adg-azId%] 
ECHO  AZ Password:           [%adg-azPwd%]
ECHO  AZ Container Registry: [%adg-azContainerRegistryName%]
ECHO  Container:             [%adg-containerName%]
ECHO +---------------------------------------------------+
ECHO  LDAP Server:           [%adg-ldapServer%] 
ECHO  User RestApi Endpoint: [%adg-userRestApiEndpoint%]
ECHO  Authorization Code:    [%adg-authorizationCode%]
ECHO +---------------------------------------------------+
ECHO  Local Python Execution:[%adg-local-python-execution%]
ECHO +---------------------------------------------------+ 
TYPE build.properties
ECHO +---------------------------------------------------+ 

@REM Modify config.properties and inject values to tags
powershell -Command "(Get-Content .\conf\configTemplate.properties) | ForEach-Object { $_.Replace('{ldapServer}', '%adg-ldapServer%').Replace('{emergencyBypass}', '%adg-emergencyBypass%').Replace('{userRestApiEndpoint}', '%adg-userRestApiEndpoint%').Replace('{authorizationCode}', '%adg-authorizationCode%') } | Set-Content .\conf\config.properties"
