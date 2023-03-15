@REM When the '–no-cache' option is passed to 'Docker build…', then that build will always start from scratch, writing a 
@REM new image to the file system even if nothing in the Dockerfile has changed. This is guaranteed to not reuse stale results, 
@REM but will always take the maximum amount of time.
@REM NOTE: Pass a container name (ie gostlit or ghost-dashboard)

CLS
ECHO OFF
SET containerName=%1

ECHO ON

IF "%~1" == "" SET containerName=ghost-dashboard

ECHO Container Name: %containerName% 
docker build --no-cache --rm --pull --tag=nchhstpoddevcontainerregistry.azurecr.io/%containerName% .

    