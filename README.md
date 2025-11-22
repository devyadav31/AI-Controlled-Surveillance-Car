
---

# 🚗🔍 AI-Controlled Surveillance Car

An **AI-powered surveillance vehicle** built using **ESP12E, Python, OpenCV, and Voice Recognition**, capable of **real-time video monitoring, voice-controlled navigation, and autonomous object tracking**.

---

## 🎥 Demo Video

▶️ **Watch the Project Demo:**
[https://photos.app.goo.gl/4RgwVPH4ksv6G8pA7](https://photos.app.goo.gl/4RgwVPH4ksv6G8pA7)

---

## 🧠 Project Overview

This project integrates **IoT**, **computer vision**, and **wireless communication** to create a smart surveillance car that can:

* Respond to **voice commands** (e.g., *“find bottle,” “find person”*).
* Detect and locate objects in a room using **OpenCV**.
* Autonomously drive toward specific objects.
* Stream live video over Wi-Fi with a remote monitoring interface.

---

## 🛠️ Tech Stack

### **Hardware**

* ESP12E (ESP8266 module)
* Motor driver
* DC motors / chassis
* Camera module
* Power supply

### **Software**

* **Python**
* **OpenCV**
* **Flask / Web server (if applicable)**
* **Speech Recognition API**
* **ESP12E Arduino Firmware**

---

## ✨ Features

* 🎤 **Voice-Controlled Navigation** – Control the car hands-free.
* 🎯 **Object Detection & Localization** – Detects and follows specific objects.
* 📡 **Wi-Fi Remote Control** – Real-time commands and live monitoring.
* 🖥️ **User Interface** – Web interface or Python UI (depending on your setup).
* 🛡️ **Indoor Surveillance** – Designed to navigate and monitor indoor environments.

---

## 🚀 Getting Started

### **1. Flash the ESP12E**

* Upload the firmware using Arduino IDE or PlatformIO.
* Configure Wi-Fi SSID & password inside the `.ino` file.

### **2. Install Python Dependencies**

```bash
pip install opencv-python speechrecognition flask requests numpy
```

### **3. Run the Python App**

```bash
python app.py
```

### **4. Connect and Control**

* Open the UI or terminal interface.
* Use voice commands or buttons to control the car.

---

## 📸 Object Detection

The system uses OpenCV for:

* Real-time video streaming
* Object tracking
* Position estimation for navigation decisions

You can modify object classes or detection logic in `object_detection.py`.

---

## 🎤 Voice Control

Uses Python’s speech recognition library to interpret commands such as:
* **"find cup"**
* **"find person"**
* **"find bottle"**
* **"forward"**
* **"backward"**
* **"left"**
* **"right"**
* **"stop"**

These commands are sent to the ESP12E via HTTP requests.

---

## 🧪 Future Improvements

* Add SLAM for better indoor navigation
* Improve path planning
* Implement mobile app control
* Upgrade to ESP32-CAM for better image quality

---





