# Smart Parking 

## Introduction
This document provides a step-by-step guide to set up the Smart Parking Django project. Follow these instructions to clone the repository, create a virtual environment, install dependencies, run migrations, and start the server.

## Prerequisites
- **Python**: Ensure Python is installed on your machine. Download it from the [official Python website](https://www.python.org/downloads/).
- **Git**: Make sure Git is installed for cloning the repository. Download it from [git-scm.com](https://git-scm.com/).

## Steps to Set Up the Project
### 1. Clone the Repository
Open your command prompt and execute the following commands:
```  
git clone git@github.com:jaycode8/Smart-Parking.git
```
```
cd Smart-Parking
```

### 2. Create a Python Virtual Environment
To create a virtual environment, run:  
```
python -m venv venv
```

This command creates a new directory named `venv` in your project folder.  

### 3. Activate the Virtual Environment
Activate the virtual environment with the following command:  
```
venv\Scripts\activate
```

Once activated, your command prompt will show `(venv)` indicating that you are now working within the virtual environment.  

### 4. Install Dependencies
Install the required dependencies listed in `requirements.txt` by running:  
```
pip install -r requirements.txt
```

### 5. Run Migrations
To set up your database schema, run:  
```
python manage.py makemigrations
```
```
python manage.py migrate
```


This command applies all migrations to your database.  

### 6. Start the Development Server
Finally, start the Django development server with:
```  
python manage.py runserver
```

You can now access your application by navigating to `http://127.0.0.1:8000/` in your web browser.  

## Conclusion
You have successfully set up your Django project on a Windows machine! For further development, refer to additional documentation or explore Django's official resources.

