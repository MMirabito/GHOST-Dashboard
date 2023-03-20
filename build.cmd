@REM When the '–no-cache' option is passed to 'Docker build…', then that build will always start from scratch, writing a 
@REM new image to the file system even if nothing in the Dockerfile has changed. This is guaranteed to not reuse stale results, 
@REM but will always take the maximum amount of time.
@REM NOTE: Pass a container name (ie gostlit or ghost-dashboard)

CLS
ECHO OFF

SET containerName=%1
IF "%~1" == "" SET containerName=ghost-dashboard

ECHO 
ECHO Container Name: %containerName% 
docker build --no-cache --rm --pull --tag=${azContainerRegistry}/%containerName% .


@REM  --progress string         Set type of progress output (auto, plain, tty). Use plain to show container output
@REM                             (default "auto")
@REM docker build --no-cache --rm --pull --progress=plain -tag=nchhstpoddevcontainerregistry.azurecr.io/%containerName% .
    