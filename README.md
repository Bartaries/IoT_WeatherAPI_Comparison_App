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

At first you must declare your **Wi-Fi connection and GitHub PAT Key in ESP_CODE.ino**. To do this follow to the 'CONFIG' section in code:

// ------------------------ C O N F I G ------------------------------

// --- Configure WiFi ---

const char* ssid = ""; **//SSID your home network**

const char* password = ""; **// password**

// --- Configure GitHub ---

const char* githubToken = "";  // <<< **Your Github PAT token **


// -- **If you want to use our Github repo then don't change it! Else if you want declare another GitHub repo then you must provide repo owner, repo name and file path to your .json file in your repo** --

const char* githubUser = "Bartaries";     // **repo owner name** (if you have opened repo - you can find this in link, just after first slash (github.com/**USERNAME**/...))    

const char* githubRepo = "IoT_WeatherAPI_Comparison_App";          // **repo name**

const char* githubFilePath = "dane.json";          // **name/path of updated .json file**


// ---------------------- E N D -------------------------------

The second one is just connect device to the power supply (USB A) with at least 5V and 1000mA.
Now you can PLUG your device into the ground outside where you want to collect your data **(check if your Wi-Fi connection is in range and have access to the internet to upload your data!)**

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

If you notice problem with flask command not found please try:

`python -m flask run`<br>

## Testing

**CI Python Application Workflow**

- This workflow runs automatically on every push to the main branch.
- It also runs on every pull request targeting the main branch.

**Environment:**

- The job runs on the latest Ubuntu virtual environment.
- It checks out the repository code.
- It sets up and configures Python 3.10.

**Testing and Validation Steps:**

**Install Dependencies:**

- Upgrades pip (Python's package installer).
- Installs necessary testing and application libraries, including pytest, pytest-mock, flake8, requests, Flask, and any packages listed in requirements.txt (if the file exists).

**Lint with flake8:**

- Performs static code analysis using flake8.
- This step checks for major syntax errors (like E9, F63) and basic code style.

**Run Application (Background):**

- Executes the main app.py script in the background (&).

**Run Pytests:**

- Executes the main test suite using the pytest command. This is expected to run all discovered unit tests.

**Logs Config Check:**

- Runs the logs_config.py script.

## Authors
* Wojciech Mycek (Tester / Machine Learning Engineer)
* Bartosz Baran (Full Stack Dev)
* Piotr Mania (Product Owner)
* Szymon Roszyk (Embedded System Engineer)
