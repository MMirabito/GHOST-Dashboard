# GHOST Dashboard

To install the dependencies needed:

```
pip install -r requirements.txt
```

Run using:

```
streamlit run dashboard.py 
```
It should open a new tab on your browser. 

**Use windows Windows**

Prerequisite  Python needs to be installed and configured

```
start.cmd
```

**In Docker (Windows)**

Docker Desktop should be running   

Use ```build.cmd``` to create image to then run ```up.cmd``` with docker compose

**Miscellaneous Information**

```pip freeze``` include more dependencies but appears to work better with Docker over ````pipreqs``` when using git commands in the python code

```
pip freeze > requirements.txt
pipreqs --encoding utf-8 . --force
```