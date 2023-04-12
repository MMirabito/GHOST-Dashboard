ECHO OFF
@REM Windows Shell Script to test and run streamlist application for windoows for development
@REM Pass --clean argument to do to some clean up
@REM Source: chatGPT

CLS

@REM Only set when runing localy.  Other enviroments like Docker or AppService it's not required
SET adg-local-python-execution=True

SET path=C:\WINDOWS\System32\WindowsPowerShell\v1.0\;^
C:\ProgramData\Anaconda3\envs\Streamlit;^
C:\ProgramData\Anaconda3\envs\Streamlit\Library\mingw-w64\bin;^
C:\ProgramData\Anaconda3\envs\Streamlit\Library\usr\bin;^
C:\ProgramData\Anaconda3\envs\Streamlit\Library\bin;^
C:\ProgramData\Anaconda3\envs\Streamlit\Scripts;^
C:\ProgramData\Anaconda3\envs\Streamlit\bin;^
C:\ProgramData\Anaconda3\condabin;

CALL .win-setup.cmd

@REM Clean up 
FOR %%i IN (%*) DO (
    IF "%%i"=="--clean" (
        RMDIR .logs /S /Q
        RMDIR mounts /S /Q
        ECHO  Starting in clean mode...        
    )
)

ECHO(
ECHO +---------------------------------------------------+
ECHO   S T A R T I N G    S T R E A M L I T
ECHO +---------------------------------------------------+

streamlit run .\src\app.py
