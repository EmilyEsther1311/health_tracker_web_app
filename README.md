# Health Tracker Web App

A web-based health tracking application that enables users to monitor, analyse, and improve their daily health metrics. This project provides tools for recording personal health data, visualising trends, and setting achievable wellness goals.

---

## Features

- **User Authentication**: Secure registration and login functionality.
- **Activity Tracking**: Record daily physical activities with start/end times and personalized notes.
- **Body Measurements**: Track changes in weight (kg) and resting pulse (bpm).
- **Exercise Management**: Create, edit, and categorize exercise types by duration and intensity. Upload supporting documents (images, PDFs) for exercise routines.
- **Support Groups**: Create and manage support groups, join existing ones, and view group members.
- **Activity Calendar**: Generate custom date-range reports for logged activities and body measurements.
- 
---

## Tech Stack

- **Backend:** Python (Flask)  
- **Frontend:** HTML, CSS
- **Database:** SQLite  
- **ORM:** Flask-SQLAlchemy  
- **Authentication:** Flask-Login  

---

## Project Structure
```
├── app/
│   ├── static/             # CSS styling (style.css)
│   ├── templates/          # Jinja2 HTML templates
│   ├── uploads/            # Uploaded exercise reference files
│   ├── __init__.py         # App factory and configuration setup
│   ├── forms.py            # WTForms definitions
│   ├── models.py           # SQLAlchemy database models
│   └── routes.py           # Application endpoints and view functions
├── config.py               # App configuration (Secret Key, DB URI)
├── requirements.txt        # Python dependencies
├── setup.py                # Database initialisation script
└── .flaskenv               # Flask environment variables
```
---

## Installation & Setup

1. **Clone the repository**

        git clone https://github.com/EmilyEsther1311/health_tracker_web_app.git
        cd health_tracker_web_app

2. **Create a virtual environment**

        python -m venv venv
        source venv/bin/activate   # On Windows: venv\Scripts\activate

3. **Install dependencies**

        pip install -r requirements.txt

4. **Run the application**

        python run.py

5. **Open in browser**

        http://localhost:5000
