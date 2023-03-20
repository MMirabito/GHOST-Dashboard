CLS
ECHO OFF

SET containerName=%1
IF "%~1" == "" SET containerName=ghost-dashboard

@REM Azure 
SET azId=${azId}
SET azPwd=${azPwd}
SET azContainerRegistry=${azContainerRegistry}

SET azRepoName=${azRepoName}/%containerName%

ECHO(
ECHO +----------------------------------------------------------------+                                                               
ECHO  AZ Docker Push
ECHO +----------------------------------------------------------------+
ECHO Azure Repo Name: %azRepoName%
ECHO        Azure ID: %azId%
ECHO +----------------------------------------------------------------+
ECHO  Step 1: Get Existing Image Id
ECHO +----------------------------------------------------------------+

docker images -q %azRepoName% > id.txt
SET /p oldImageId=<.\id.txt

DEL id.txt

ECHO Old Image ID: %oldImageId%
ECHO.

@REM ECHO +----------------------------------------------------------------+
@REM ECHO  Step 2: Remove Image %oldImageId%
@REM ECHO +----------------------------------------------------------------+

@REM docker image rm %oldImageId% -f

@REM ECHO Removed Image ID: %oldImageId%
@REM ECHO.

ECHO +----------------------------------------------------------------+
ECHO  Step 2: Show current images 
ECHO +----------------------------------------------------------------+

docker images 
ECHO.

@REM ECHO +----------------------------------------------------------------+
@REM ECHO  Step 4: Pull Latest Image and get Image ID
@REM ECHO +----------------------------------------------------------------+

@REM docker pull %awsRepoName%:latest
@REM docker images -q %awsRepoName%:latest > id.txt

@REM SET /p newImageId=<.\id.txt
@REM ECHO New Image ID: %newImageId%
@REM ECHO.

@REM ECHO +----------------------------------------------------------------+
@REM ECHO  Step 5: Tag Image: %newImageId%
@REM ECHO +----------------------------------------------------------------+

@REM docker image tag %newImageId% %azRepoName%:latest 

@REM ECHO Tag Image: %newImageId%
@REM ECHO.

ECHO +----------------------------------------------------------------+
ECHO  Step 3: Push Image to Azure
ECHO +----------------------------------------------------------------+

docker login -u %azId% -p %azPwd% %azContainerRegistry%
docker push %azRepoName%:latest 

ECHO +----------------------------------------------------------------+
ECHO  Step 4: Show current images local and Azure
ECHO +----------------------------------------------------------------+

docker images 
ECHO.
docker images %azRepoName%
ECHO.

@REM ECHO +----------------------------------------------------------------+
@REM ECHO  Step 5: Cleanup
@REM ECHO +----------------------------------------------------------------+
@REM del id.txt

ECHO.
ECHO Done!




