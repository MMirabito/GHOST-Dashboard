@REM When the '–no-cache' option is passed to 'Docker build…', then that build will always start from scratch, writing a 
@REM new image to the file system even if nothing in the Dockerfile has changed. This is guaranteed to not reuse stale results, 
@REM but will always take the maximum amount of time.

CLS
ECHO OFF

ECHO Building Docker Image...
CALL .win-setup.cmd

ECHO +---------------------------------------------------+
ECHO   B U I L D I N G   D O C K E R   I M A G E
ECHO +---------------------------------------------------+

docker build --no-cache --rm --pull --progress=plain --tag=%adg-azContainerRegistryName%/%adg-containerName% . 
@REM docker build --rm --pull --tag=%adg-azContainerRegistryName%/%adg-containerName% .

@REM  --progress string         Set type of progress output (auto, plain, tty). Use plain to show container output
@REM                             (default "auto")
@REM docker build --no-cache --rm --pull --progress=plain -tag=adg-azContainerRegistryName%/%containerName% .
    