# Integrated Weather Monitoring and Prediction System
## Quick Overview
This project delivers a robust solution by integrating real-time hardware weather monitoring (via ESP32 micro-controller) with a Machine Learning (ML) model for predictive analytics. The entire system is packaged as a web application, providing users with an aesthetic, browser-based Graphical User Interface (GUI).

| Key Feature | Funcionality Description |
| :---------- | :----------------------- |
| Real-Time Monitoring (Live) | Acquisition and dynamic display of current weather data (e.g., temperature, humidity, pressure) streamed directly from the ESP32 micro-controller. |
| ML-Powered Prediction | Development and application of a Machine Learning algorithm trained on real data from ESP32 to generate accurate short-term weather forecasts. |
| Model Verification | Continuous comparison of the ML model's predictions against actual weather data for live performance validation and visualization. |
| Web Interface (GUI) | An intuitive, JavaScript/CSS-driven web application for clear visualization of current metrics and prediction results. |

## Technologies Used

The application is built on the following multi-stack architecture:<br>
Hardware: 💻 ESP32 micro-controller<br>
Back-end/Server: Python with the Flask framework (for handling the API, data streaming, and business logic).<br>
Machine Learning: Python libraries such as Scikit-learn, Pandas, and NumPy.<br>
Front-end: ☕ JavaScript, HTML5, and CSS3 (for the responsive and dynamic User Interface).<br>
Data Visualization: **Bartek and Wojtek I need your help here**<br>
Version Control: 🐙 Git & GitHub


## Instalation

These instructions will guide you through setting up and running the project locally.

### Installation and Running

### Hardware Setup (ESP32 micro-controller):

**Bruno please help**

### Software Setup:

Install Python dependencies (using a virtual environment is recommended):<br>
Create and activate a virtual environment (optional but recommended)<br>
python3 -m venv env<br>
`source venv/bin/activate`  # Linux/macOS<br>
`venv\Scripts\activate` # Windows<br>

### Install dependencies
`pip install -r requirements.txt`<br>
Run the Flask server: `flask run`<br>

The application will be accessible at: http://localhost:5000 (Flask's default port).

## Testing

**Wojtek please help**


We maintain code quality through a rigorous testing process:<br>
Automated Tests: <br>
Manual Tests:<br>

## Authors
* Wojciech Mycek (Tester / Machine Learning engineer)
* Bartosz Baran (pls write your role)
* Piotr Mania (Product Owner)
* Bruno Roszyk (pls write your role)
