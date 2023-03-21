# GHOST Dashboard

To install the dependencies needed:

- ```pip install -r requirements.txt```

Run using a streamlit environment:

- ```streamlit run dashboard.py``` this should open a new tab on your browser with the application running.

**Running on Windows**

**NOTE:** The application use a simple authentication using active directory. You will need access to AD or simple comment out AD authentication

- **Python** needs to be installed and configured.
- ```win-env.cmd``` needs to to have the **{VALUE-GOES-HERE}** replaced in order to be able to run the application. To Run type the following command  
- ```start.cmd``` to run the application locally  


**In Docker (Windows)**

- Docker Desktop should be running   
- Use ```build.cmd``` to create image to then run ```up.cmd``` with docker compose then go to [http://localhost:8501/](http://localhost:8501/ "http://localhost:8501/")
- To deploy image to Azure use ```deply.cmd```

**Other Information**

- ```pip freeze``` includes more dependencies but appears to work better with Docker over 
- ```pipreqs``` when using git commands in the python code
- ```pip freeze > requirements.txt``` Include all Python requirements
- ```pipreqs --encoding utf-8 . --force```

**NOTE:** Try to avoid committing files with sensitive data and/or URLs

## Application Architecture
![Application Architecture)](images/2023-03-21_13-23-45.png) 

## Docker Desktop View
![Running a container in Docker)](images/2023-03-21_11-38-45.png)


## Application View
![Application Landing Page)](images/2023-03-21_11-45-09.png)