AI-Powered Habit Tracker and Productivity Dashboard

An AI-powered web application for tracking daily habits, monitoring productivity, and visualizing personal progress through a simple dashboard.

🚀 Features

✅ Create and track daily habits

📊 View habit and productivity progress

🤖 AI-powered productivity insights

📈 Dashboard for monitoring performance

🗓️ Track daily habit completion

🌐 Flask-based web application

🔌 REST API endpoints for application data

🎨 Responsive web interface

🛠️ Tech Stack

Backend

Python

Flask

Flask-CORS

Frontend

HTML

CSS

JavaScript

Jinja2 Templates

Database

SQLite / project database

Database scripts are available in the database folder

📁 Project Structure

AI-Powered-Habit-Tracker-and-Productivity-Dashboard/
│
├── database/
│   └── Database files / scripts
│
├── static/
│   ├── css/
│   ├── js/
│   └── other static assets
│
├── templates/
│   └── HTML / Jinja2 templates
│
├── app.py
├── requirements.txt
└── README.md

⚙️ Installation

1. Clone the repository

git clone https://github.com/revanthsaibomma/AI-Powered-Habit-Tracker-and-Productivity-Dashboard.git

2. Move into the project directory

cd AI-Powered-Habit-Tracker-and-Productivity-Dashboard

3. Create a virtual environment

Windows:

python -m venv venv
venv\Scripts\activate

macOS/Linux:

python3 -m venv venv
source venv/bin/activate

4. Install dependencies

pip install -r requirements.txt

If Flask-CORS is not included in requirements.txt, install it with:

pip install flask-cors

▶️ Run the Application

Start the Flask application:

python app.py

The application will normally be available at:

http://127.0.0.1:5000

Open the address in your browser.

🔧 Configuration

If the application uses environment variables or API keys, create a .env file locally and add the required values.

Do not commit secrets, passwords, API keys, virtual environments, or generated cache files to GitHub.

📊 Application Workflow

User
  │
  ▼
Habit Tracker / Dashboard
  │
  ├── Create / Update Habits
  │
  ├── Record Daily Progress
  │
  ▼
Flask Backend
  │
  ├── API Routes
  ├── Business Logic
  └── Data Processing
  │
  ▼
Database
  │
  ▼
Productivity Data
  │
  ▼
Dashboard & AI Insights

🎯 Project Objectives

The main objectives of this project are:

Help users build and maintain productive habits.

Track daily activities and habit completion.

Provide meaningful productivity statistics.

Use AI-based analysis to generate useful insights.

Present progress through an easy-to-understand dashboard.

🔮 Future Enhancements

User authentication and individual profiles

Advanced AI-generated habit recommendations

Productivity prediction

Habit streak tracking

Notifications and reminders

Weekly and monthly productivity reports

Interactive charts and analytics

Cloud database integration

Deployment to a production hosting platform

🤝 Contributing

Contributions are welcome.

Fork the repository.

Create a new branch:

git checkout -b feature/new-feature

Make your changes.

Commit your changes:

git commit -m "Add new feature"

Push the branch:

git push origin feature/new-feature

Open a Pull Request.

📄 License

This project is currently intended for educational and development purposes. Add an appropriate open-source license if you decide to distribute the project under specific licensing terms.

👨‍💻 Author

Revanth Sai Bomma

GitHub: https://github.com/revanthsaibomma

⭐ Support

If you find this project useful, consider giving the repository a ⭐ on GitHub.