@REM Windows Shell Script to test and run streamlist application for windoows

CLS

SET path=C:\WINDOWS\System32\WindowsPowerShell\v1.0\;^
C:\ProgramData\Anaconda3\envs\Streamlit;^
C:\ProgramData\Anaconda3\envs\Streamlit\Library\mingw-w64\bin;^
C:\ProgramData\Anaconda3\envs\Streamlit\Library\usr\bin;^
C:\ProgramData\Anaconda3\envs\Streamlit\Library\bin;^
C:\ProgramData\Anaconda3\envs\Streamlit\Scripts;^
C:\ProgramData\Anaconda3\envs\Streamlit\bin;^
C:\ProgramData\Anaconda3\condabin;

CALL .win-setup.cmd

ECHO +---------------------------------------------------+
ECHO   S T A R T I N G    S T R E A M L I T
ECHO +---------------------------------------------------+
streamlit run .\src\app.py
