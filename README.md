# 🏙️ Skyscrapers — A CSP-Based Puzzle Game

A fully functional web-based Skyscrapers puzzle game built with **Python (FastAPI)** on the backend and **HTML/CSS/JavaScript** on the frontend. The puzzle is modeled as a **Constraint Satisfaction Problem (CSP)** and solved using classic AI algorithms.

## 🎯 What is Skyscrapers?

You have an N×N grid (4×4, 5×5, or 6×6). Each cell contains a skyscraper of height 1 to N. Every row and column must contain each height exactly once. Numbers on the outside edges tell you how many buildings are visible from that direction — a taller building hides all shorter ones behind it.

The player must fill the grid so every clue is satisfied.

## 🧠 CSP Algorithms Implemented

| Algorithm | Purpose |
|-----------|---------|
| **Backtracking Search** | Core recursive search framework |
| **Forward Checking** | Prunes impossible values from neighbors |
| **MRV (Minimum Remaining Values)** | Picks the most-constrained variable first |
| **Degree Heuristic** | Tie-breaker for MRV |
| **LCV (Least Constraining Value)** | Tries values that constrain neighbors least |
| **AC-3 (Arc Consistency 3)** | Constraint propagation preprocessing |

## 🚀 Features

- 🎮 3 grid sizes (4×4, 5×5, 6×6)
- 🎚️ 3 difficulty levels (Easy, Medium, Hard)
- 💡 Hint system (client-side, instant)
- 🤖 Two solve modes: **Backtracking+FC+MRV** and **AC-3+Backtracking**
- 📊 Real-time statistics (nodes explored, backtracks, time)
- ✓ Board validation with conflict detection
- 🎨 Beautiful dark-themed 3D-styled UI
- ⌨️ Keyboard support (number keys + backspace)
- ⏱️ Timer and mistake counter

## 🧠 Tech Stack

- **Backend:** Python, FastAPI, Uvicorn, Pydantic
- **CSP Engine:** Pure Python (no external solver libraries)
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Font:** Poppins (Google Fonts)

## 📁 Project Structure
skyscrapers-csp/
├── main.py # FastAPI backend + endpoints
├── csp_solver.py # CSP algorithms
├── generator.py # Puzzle generator
├── requirements.txt # Dependencies
├── README.md # This file
└── static/
├── index.html # Main UI
├── style.css # Styling
└── script.js # Game logic

## ⚙️ How to Run Locally

1. Clone the repository: git clone https://github.com/YOUR_USERNAME/skyscrapers-csp.git
                         cd skyscrapers-csp

2. Install dependencies: pip install -r requirements.txt

3. Start the server: uvicorn main:app

4. Open your browser at `http://127.0.0.1:8000`

## 🔬 Algorithm Comparison Demo

1. Click **New Game** with any difficulty
2. Click **🤖 Solve (CSP)** — note the "Nodes" value in the stats bar
3. Click **New Game** again
4. Click **⚡ Solve (AC-3)** — compare the "Nodes" value

**AC-3 preprocessing consistently explores fewer nodes**, demonstrating the power of constraint propagation.

## 📄 License

MIT — free to use for academic purposes.
