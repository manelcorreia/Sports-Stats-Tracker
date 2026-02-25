# 🏑 Parede FC Stats Tracker

This project is an interactive Web Application developed in Python for the sports management and statistical analysis of the Parede FC Roller Hockey team.

The application allows the technical staff to record game events in real-time (goals, assists, saves, cards, fouls, etc.) and consult detailed statistics through a modern visual interface. The system ensures data persistence between sessions and implements advanced Object-Oriented Programming concepts, keeping a clean separation between the backend engine and the frontend interface.

---
## ✨ MAIN FEATURES
- **Squad Management:** Player listing with clear distinction between Goalkeepers and Outfield Players, adapting the UI automatically to each role.
- **Live Match Tracking:** Intuitive and fast event logging during the game (Goals, Assists, Set Pieces, Cards, Fouls, Loss of Possession, etc.).
- **Modern Web Interface:** Built with Streamlit, replacing the old CLI, providing a responsive and interactive Match Center.
- **Automated Statistics & Reports:** Instant calculation of team totals and individual metrics. Includes 1-click export to Excel/CSV for both single-match reports and full-season statistics.
- **Data Persistence:** Robust backend that automatically saves the entire historical data in a local JSON database (`dados_equipa.json`).
- **Technical Architecture:** Implementation of modular code, Object-Oriented design, and strict Separation of Concerns (Frontend vs. Backend).

---
## 🚀 HOW TO RUN
1. Make sure you have Python installed on your machine.
2. Install the required dependencies (mainly `streamlit` and `pandas`). You can use the requirements file:
```bash
pip install -r requirements.txt
```

---
## RUN THE APPLICATION
Via terminal:
```bash
streamlit run app.py
```

---
## ⚠️ Note on Data Persistense
The persistence system (JSON) serves as the core database. Always ensure you click the "Save Game" button at the end of a match before exporting the CSV reports. If you are running this app on a cloud server (like Streamlit Community Cloud), remember to download the updated JSON backup file to keep your local database in sync.