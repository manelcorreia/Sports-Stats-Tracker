# PROJETO: PAREDE FC STATS TRACKER
ALUNO: MANUEL CORREIA
Nº 2403849
---
This project is a Command Line Interface (CLI) application developed in Python for sports management and statistical analysis of the Parede FC Roller Hockey team.

The application allows the technical team to register game events in real-time (goals, assists, saves, cards, etc.) and consult detailed statistics through a modern visual interface. The system ensures data persistence between sessions and implements advanced Object-Oriented Programming concepts.

---
## MAIN FEATURES
- **Squad Management:** Player listing distinguishing between Goalkeepers and Field Players.
- **Live Match Tracking:** Intuitive logging of match events (Goals, assists, set pieces, discipline, etc.).
- **Visual Interface:** Utilizes the `Rich` library to present formatted statistical tables, colorful panels, and interactive menus.
- **Automatic Statistics:** Calculation of totals (Wins/Losses, Goals Scored/Conceded) and individual metrics.
- **Data Persistence:** Automatic saving of the entire history into a JSON file.
- **Technical Architecture:** Implementation of Multiple Inheritance and Mixins for code modularity.

---
## HOW TO RUN
1. Ensure the `.venv` folder is present.
2. Run the main file:
```bash
python Projeto_StatsTracker.py
```

---
## TECHNICAL NOTE
In case of any compatibility errors, the `requirements.txt` file is included. To reinstall dependencies, you can use:
```bash
pip install -r requirements.txt
``` 

--- 
## ⚠️ NOTE ON VISUALIZATION (RICH COLORS)
This project uses the Rich library for colorful interfaces. If running the code inside **PyCharm**, please enable the option: `Emulate terminal in output console` in the Run Configuration settings.

If running via **Windows Terminal/CMD**, colors work automatically without extra configuration.

