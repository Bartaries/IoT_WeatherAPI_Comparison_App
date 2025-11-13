#include <WiFi.h>
#include <ESPAsyncWebServer.h>
#include <Adafruit_Sensor.h>
#include <DHT.h>
#include <FS.h>
#include <SPIFFS.h>
#include "time.h"
#include <HTTPClient.h>
#include <WiFiClientSecure.h>
#include <ArduinoJson.h>
#include <base64.h>

// ------------------------ C O N F I G ------------------------------

// --- Configure WiFi ---
const char* ssid = ""; //SSID your home network
const char* password = ""; // password

// --- Configure GitHub ---
const char* githubToken = "";  // <<< Your Github PAT token 


// -- If you want to use our Github repo then don't change it! Else if you want declare another GitHub repo then you must provide repo owner, repo name and file path to your .json file in your repo --
const char* githubUser = "Bartaries";     // repo owner name (if you have opened repo - you can find this in link, just after first slash (github.com/USERNAME/...))        
const char* githubRepo = "IoT_WeatherAPI_Comparison_App";          // repo name
const char* githubFilePath = "dane.json";          // name/path of updated .json file


// ---------------------- E N D -------------------------------

// --- Konfiguracja czujnika DHT11 ---
#define DHTPIN 18
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// --- Czujnik wilgotności gleby ---
#define SOIL_PIN 34

// --- Serwer HTTP ---
AsyncWebServer server(80);

// --- Serwer NTP ---
const char* ntpServer = "pool.ntp.org";
const long gmtOffset_sec = 3600;
const int daylightOffset_sec = 3600;

// --- Czas ostatniego wysłania pliku do githuba ---
unsigned long lastUpload = 0;
const unsigned long uploadInterval = 600000; // co 10 minut

// --- Funkcja pobierania czasu ---
String getFormattedTime() {
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) return "Brak czasu";
  char buffer[20];
  strftime(buffer, sizeof(buffer), "%d-%m-%y %H:%M:%S", &timeinfo);
  return String(buffer);
}

// --- Pomiar danych ---
float getTemperature() {
  float t = dht.readTemperature();
  return isnan(t) ? -1 : t;
}
float getHumidity() {
  float h = dht.readHumidity();
  return isnan(h) ? -1 : h;
}
int getSoil() {
  int raw = analogRead(SOIL_PIN);
  int soilValue = map(raw, 3250, 2220, 0, 100);
  return constrain(soilValue, 0, 100);
}

void appendDataToJson(float temperature, float humidity, int soil) {
  // Wczytaj istniejące dane
  String jsonContent = "[]";
  if (SPIFFS.exists("/dane.json")) {
    File file = SPIFFS.open("/dane.json", "r");
    if (file) {
      jsonContent = file.readString();
      file.close();
    }
  }

  // Jeśli plik jest pusty lub uszkodzony – zacznij od pustej tablicy
  DynamicJsonDocument doc(32768);
  DeserializationError error = deserializeJson(doc, jsonContent);
  if (error) {
    doc.clear();
    doc.to<JsonArray>();
  }

  // Dodaj nowy rekord
  JsonObject record = doc.createNestedObject();
  record["timestamp"] = getFormattedTime();
  record["temperature"] = temperature;
  record["humidity"] = humidity;
  record["soil"] = soil;

  // Zapisz z powrotem
  File file = SPIFFS.open("/dane.json", "w");
  if (file) {
    serializeJson(doc, file);
    file.close();
    Serial.println("✅ Zapisano dane: " + getFormattedTime());
  } else {
    Serial.println("❌ Błąd zapisu pliku!");
  }
}


// --- Upload pliku JSON do GitHub ---
void uploadToGitHub() {
  WiFiClientSecure client;
  client.setInsecure();
  HTTPClient http;

  String url = "https://api.github.com/repos/" + String(githubUser) + "/" + String(githubRepo) + "/contents/" + String(githubFilePath);

  // Pobierz SHA istniejącego pliku (jeśli istnieje) z GitHuba
  String sha = "";
  http.begin(client, url);
  http.addHeader("Authorization", "token " + String(githubToken));
  http.addHeader("User-Agent", "ESP32Uploader");
  int getCode = http.GET();
  if (getCode == 200) {
    DynamicJsonDocument doc(2048);
    deserializeJson(doc, http.getString());
    sha = doc["sha"].as<String>();
    Serial.println("📄 Znaleziono istniejący plik, SHA: " + sha);
  } else {
    Serial.println("ℹ️ Brak istniejącego pliku (GET kod: " + String(getCode) + ")");
  }
  http.end();

  // Otwórz lokalny plik zapisany w ESP32
  File file = SPIFFS.open("/dane.json", "r");
  if (!file) {
    Serial.println("❌ Brak pliku dane.json do wysłania!");
    return;
  }
  String fileContent = file.readString();
  file.close();

  // Kodowanie base64 (GitHub wymaga base64 treści :/ )
  String encoded = "";
  const char base64_chars[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
  int i = 0;
  unsigned char char_array_3[3];
  unsigned char char_array_4[4];
  int in_len = fileContent.length();
  int pos = 0;
  while (in_len--) {
    char_array_3[i++] = fileContent[pos++];
    if (i == 3) {
      char_array_4[0] = (char_array_3[0] & 0xfc) >> 2;
      char_array_4[1] = ((char_array_3[0] & 0x03) << 4) + ((char_array_3[1] & 0xf0) >> 4);
      char_array_4[2] = ((char_array_3[1] & 0x0f) << 2) + ((char_array_3[2] & 0xc0) >> 6);
      char_array_4[3] = char_array_3[2] & 0x3f;
      for (i = 0; i < 4; i++) encoded += base64_chars[char_array_4[i]];
      i = 0;
    }
  }
  if (i) {
    for (int j = i; j < 3; j++) char_array_3[j] = '\0';
    char_array_4[0] = (char_array_3[0] & 0xfc) >> 2;
    char_array_4[1] = ((char_array_3[0] & 0x03) << 4) + ((char_array_3[1] & 0xf0) >> 4);
    char_array_4[2] = ((char_array_3[1] & 0x0f) << 2) + ((char_array_3[2] & 0xc0) >> 6);
    for (int j = 0; j < i + 1; j++) encoded += base64_chars[char_array_4[j]];
    while (i++ < 3) encoded += '=';
  }

  // Przygotuj JSON PUT
  DynamicJsonDocument payload(4096);
  payload["message"] = "ESP32 auto-upload " + getFormattedTime();
  payload["content"] = encoded;
  if (sha != "") payload["sha"] = sha;
  String output;
  serializeJson(payload, output);

  // Wyślij PUT do GitHub
  http.begin(client, url);
  http.addHeader("Authorization", "token " + String(githubToken));
  http.addHeader("User-Agent", "ESP32Uploader");
  http.addHeader("Content-Type", "application/json");

  int httpCode = http.PUT((uint8_t*)output.c_str(), output.length());
  String response = http.getString();


  Serial.println("📤 GitHub upload -> HTTP " + String(httpCode));
  Serial.println("Odpowiedź GitHub:");
  Serial.println(response);
  http.end();
}


// --- HTML Strony localhost ---
const char index_html[] PROGMEM = R"rawliteral(
<!DOCTYPE HTML>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ESP32 Serwer DHT11</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      text-align: center;
      margin: 0;
      padding: 0;
      background: #f4f4f9;
      color: #333;
    }
    h1 {
      font-size: 2.5rem;
      margin: 20px 0;
      color: #2196F3;
    }
    .sensor-container {
      display: flex;
      justify-content: center;
      flex-wrap: wrap;
      gap: 30px;
      margin-top: 40px;
    }
    .sensor-box {
      background: #fff;
      padding: 20px 30px;
      border-radius: 15px;
      box-shadow: 0 4px 10px rgba(0,0,0,0.1);
      min-width: 150px;
    }
    .sensor-box p {
      margin: 10px 0;
      font-size: 1.2rem;
    }
    .sensor-value {
      font-size: 2.5rem;
      font-weight: bold;
      margin-top: 5px;
      color: #2196F3;
    }
    a.button {
      display: inline-block;
      padding: 12px 25px;
      margin: 20px 10px;
      background-color: #2196F3;
      color: white;
      text-decoration: none;
      font-size: 1.2rem;
      border-radius: 10px;
    }
    a.button:hover {
      background-color: #0b7dda;
    }
  </style>
</head>
<body>
  <h1>🌐 Projekt Zespołowy</h1>
  <div class="sensor-container">
    <div class="sensor-box">
      <p>🌡️ Temperatura</p>
      <p class="sensor-value" id="temperature">%TEMPERATURE%</p>
      <p>°C</p>
    </div>
    <div class="sensor-box">
      <p>💧 Wilgotność</p>
      <p class="sensor-value" id="humidity">%HUMIDITY%</p>
      <p>procent</p>
    </div>
    <div class="sensor-box">
      <p>🌱 Wilgotność gleby</p>
      <p class="sensor-value" id="soil">%SOIL%</p>
      <p>procent</p>
    </div>
  </div>
  <a class="button" href="/download">📥 Pobierz dane JSON</a>
  <a class="button" href="#" onclick="clearData()">🗑️ Wyczyść dane</a>
  <p>© Szymon Roszyk, Piotr Mania, Bartosz Baran, Wojciech Mycek</p>
  <script>
  function updateData() {
    fetch('/temperature').then(r => r.text()).then(data => { document.getElementById('temperature').innerHTML = data; });
    fetch('/humidity').then(r => r.text()).then(data => { document.getElementById('humidity').innerHTML = data; });
    fetch('/soil').then(r => r.text()).then(data => { document.getElementById('soil').innerHTML = data; });
  }
  function clearData() {
    if (confirm("Czy na pewno chcesz usunąć wszystkie dane?")) {
      fetch('/clear').then(r => r.text()).then(alert);
    }
  }
  setInterval(updateData, 5000);
  window.onload = updateData;
  </script>
</body>
</html>
)rawliteral";

String processor(const String& var) {
  if (var == "TEMPERATURE") return String(getTemperature(), 1);
  if (var == "HUMIDITY") return String(getHumidity(), 1);
  if (var == "SOIL") return String(getSoil());
  return String();
}


void setup() {
  Serial.begin(115200);
  dht.begin();
  if (!SPIFFS.begin(true)) { Serial.println("Błąd SPIFFS!"); return; }

  WiFi.begin(ssid, password);
  Serial.print("Łączenie z WiFi...");
  while (WiFi.status() != WL_CONNECTED) { delay(1000); Serial.print("."); }
  Serial.println("\nPołączono! IP: " + WiFi.localIP().toString());

  configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
  struct tm timeinfo;
  while (!getLocalTime(&timeinfo)) { delay(500); }

  // Endpointy
  server.on("/", HTTP_GET, [](AsyncWebServerRequest *r){ r->send_P(200, "text/html", index_html, processor); });
  server.on("/temperature", HTTP_GET, [](AsyncWebServerRequest *r){ r->send(200, "text/plain", String(getTemperature(), 1)); });
  server.on("/humidity", HTTP_GET, [](AsyncWebServerRequest *r){ r->send(200, "text/plain", String(getHumidity(), 1)); });
  server.on("/soil", HTTP_GET, [](AsyncWebServerRequest *r){ r->send(200, "text/plain", String(getSoil())); });
  server.on("/download", HTTP_GET, [](AsyncWebServerRequest *r){
    if (SPIFFS.exists("/dane.json")) r->send(SPIFFS, "/dane.json", "application/json", true);
    else r->send(200, "application/json", "[]");
  });
  server.on("/clear", HTTP_GET, [](AsyncWebServerRequest *r){
    if (SPIFFS.exists("/dane.json")) { SPIFFS.remove("/dane.json"); r->send(200, "text/plain", "✅ Dane usunięte."); }
    else r->send(200, "text/plain", "ℹ️ Brak danych.");
  });

  server.begin();
  Serial.println("Serwer uruchomiony!");
}

void loop() {
  float t = getTemperature();
  float h = getHumidity();
  int s = getSoil();
  if (t != -1 && h != -1) appendDataToJson(t, h, s);

  // wyślij dane na GitHub co 10 min (czas ten jest deklarowany w sekcji CONFIG)
  if (millis() - lastUpload > uploadInterval) {
    uploadToGitHub();
    lastUpload = millis();
  }

  delay(10000);
}
