CLS

SET path=C:\ProgramData\Anaconda3\envs\Streamlit;^
C:\ProgramData\Anaconda3\envs\Streamlit\Library\mingw-w64\bin;^
C:\ProgramData\Anaconda3\envs\Streamlit\Library\usr\bin;^
C:\ProgramData\Anaconda3\envs\Streamlit\Library\bin;^
C:\ProgramData\Anaconda3\envs\Streamlit\Scripts;^
C:\ProgramData\Anaconda3\envs\Streamlit\bin;^
C:\ProgramData\Anaconda3\condabin;

REM %path% 

CLS
@REM CD src

streamlit run .\src\dashboard.py



@REM CD..