#  Blackjack Ultimate - HSG Python Project

**Blackjack Ultimate** is a robust, interactive desktop game built entirely in Python using the `tkinter` library. It features a custom vector-based interface, a strategic AI advisor, and strictly implements official casino rules.

---

##  Key Features

### 1. Game Mechanics
* **Official Rules**: Dealer must draw to 16 and stand on 17.
* **Betting System**: Complete bankroll management with input validation.
* **Split Functionality**: Players can split pairs into two separate hands (handled via list data structures).
* **Game Over State**: Detects bankruptcy and offers a restart option.

### 2. Strategic Advisor (AI)
* **"Pro Advice" Feature**: A built-in algorithm calculates the mathematically optimal move (Hit or Stand) based on the player's hand and the dealer's visible card.

### 3. Technical Highlights
* **Custom GUI**: The table and cards are drawn programmatically using `tkinter.Canvas` (no external image files required).
* **MacOS Stability**: Includes a specific fix (`os._exit`) to prevent UI freezing on Mac systems upon exit.
* **Clean Architecture**: The project follows **Object-Oriented Programming (OOP)** principles with separated classes for `Card` and `BlackJackUltimate` (Game Logic).

---

##  Code Quality & Best Practices

In accordance with coding best practices, this project focuses on maintainability and readability:
* **Type Hinting**: All functions use Python type hints (e.g., `-> None`, `: List[Card]`) for clarity.
* **PEP 8 Compliance**: Consistent naming conventions (`calculate_hand_score` vs `c`) and formatting.
* **Input Validation**: Protects against crashes by validating user bets (preventing negative numbers or text inputs).
* **No Hardcoding**: Constants (like `COLOR_TABLE`, `PI`) are defined at the top level for easy configuration.

---

## 📦 How to Run

No external libraries (like Pygame or Pandas) are required. The game runs on standard Python.

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git)
    ```

2.  **Navigate to the folder:**
    ```bash
    cd YOUR_REPO_NAME
    ```

3.  **Run the game:**
    ```bash
    python BlackJack_final.py
    ```

---

## 👤 Author

* **Name:** Xavier Grand
* **University:** University of St. Gallen (HSG)
* **Course:** Programming
* **Date:** December 2025
