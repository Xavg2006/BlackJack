"""
PROJECT: BLACKJACK ULTIMATE (Stable Mac Version)
AUTHOR: Xavier Grand
COURSE: Programming - HSG
DATE: December 2025

DESCRIPTION:
This Blackjack game implements official casino rules, a vector-based GUI (no external assets),
and a strategic decision-support algorithm (AI).

KEY FEATURES:
- Object-Oriented Design (Classes for Card and Game Logic).
- Robust Input Validation.
- Crash prevention on macOS using os._exit.
"""

# =============================================================================
# BLOCK 1: IMPORTS & CONFIGURATION
# =============================================================================
import tkinter as tk
from tkinter import messagebox
import random
import os 
from typing import List, Tuple

# --- Constants -----------------------------------------------------
COLOR_BG = "#2c3e50"            
COLOR_TABLE = "#27ae60"         
COLOR_TABLE_OUTLINE = "#2ecc71" 
COLOR_ACCENT = "#f1c40f"        
COLOR_BTN_ACTION = "#3498db"    
COLOR_BTN_SPLIT = "#9b59b6"     
COLOR_BTN_DEAL = "#2ecc71"      
COLOR_BTN_QUIT = "#e74c3c"      
COLOR_GAME_OVER = "#c0392b"     

# Mapping codes to visual symbols for better readability 
SUITS = {'C': '♥', 'D': '♦', 'H': '♣', 'S': '♠'}
VALUES = {
    2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 
    9: '9', 10: '10', 11: 'J', 12: 'Q', 13: 'K', 14: 'A'
}

# =============================================================================
# BLOCK 2: DATA MODELS
# =============================================================================

class Card:
    """
    Represents a single playing card.
    Encapsulates value logic to keep the main code clean.
    """
    def __init__(self, value: int, suit: str):
        self.value = value
        self.suit = suit

    def get_blackjack_value(self) -> int:
        """
        Returns the card's value according to Blackjack rules.
        Face cards (J, Q, K) are 10. Ace is 11 by default.
        """
        if 10 <= self.value < 14: return 10
        if self.value == 14: return 11
        return self.value

    def get_face_value(self) -> int:
        """Returns the raw face value, useful for checking pairs."""
        if 10 <= self.value < 14: return 10
        return self.value

    def is_red(self) -> bool:
        """Helper to determine if the card suit should be painted red."""
        return self.suit in ['D', 'H']

# =============================================================================
# BLOCK 3: GAME CONTROLLER
# =============================================================================

class BlackJackUltimate:
    """
    Main controller class handling Game Logic, UI Rendering, and State Management.
    Follows separation of concerns by isolating logic from drawing methods.
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("BlackJack Ultimate - HSG Project")
        self.root.geometry("1100x850")
        self.root.configure(bg=COLOR_BG)

        # -- Game State Variables --
        self.deck: List[Card] = []
        self.player_hands: List[List[Card]] = [] 
        self.player_bets: List[int] = []
        self.hand_statuses: List[str] = []       
        self.current_hand_index = 0
        self.dealer_hand: List[Card] = []
        
        self.bankroll = 1000  
        self.base_bet = 0
        self.is_game_active = False

        # Initialize UI Components
        self._setup_ui_structure()
        self._update_controls("betting")

        # -- MacOS Stability Fix --
        # Overrides the default close behavior to ensure the process terminates completely.
        self.root.protocol("WM_DELETE_WINDOW", self.force_kill_app)

    # -------------------------------------------------------------------------
    # UI SETUP & RENDERING
    # -------------------------------------------------------------------------
    def _setup_ui_structure(self) -> None:
        """Builds the static containers for the Header, Table, and Controls."""
        # Top Section: Bankroll Display
        self.frame_top = tk.Frame(self.root, bg=COLOR_BG)
        self.frame_top.pack(side="top", fill="x", pady=10)
        
        self.lbl_bankroll = tk.Label(
            self.frame_top, text="BANKROLL: $1000", 
            font=("Arial", 22, "bold"), fg=COLOR_ACCENT, bg=COLOR_BG
        )
        self.lbl_bankroll.pack()

        # Bottom Section: Dynamic Buttons
        self.bottom_container = tk.Frame(self.root, bg=COLOR_BG, pady=20)
        self.bottom_container.pack(side="bottom", fill="x")

        # Center Section: The Green Table (Canvas)
        self.canvas = tk.Canvas(self.root, bg=COLOR_TABLE, highlightthickness=0)
        self.canvas.pack(side="top", expand=True, fill="both", padx=20, pady=(0, 20))
        
        # Bind resize event for responsive drawing
        self.canvas.bind("<Configure>", self._draw_table_background)
        
        # Initialize Text Elements on Canvas
        self.txt_dealer_lbl = self.canvas.create_text(0, 0, text="DEALER", font=("Arial", 16, "bold"), fill="#1e8449")
        self.txt_dealer_score = self.canvas.create_text(0, 0, text="", font=("Arial", 14), fill="white")
        self.txt_result = self.canvas.create_text(0, 0, text="PLACE YOUR BET", font=("Arial", 30, "bold"), fill="white")
        
        # "Pro Advice" Box (Hidden by default)
        self.bg_advice = self.canvas.create_rectangle(0, 0, 0, 0, fill=COLOR_BG, outline=COLOR_ACCENT, width=2, state='hidden')
        self.txt_advice = self.canvas.create_text(0, 0, text="", font=("Arial", 16, "bold"), fill=COLOR_ACCENT)

    def _draw_table_background(self, event=None):
        """
        Redraws the table outline and repositions text when window is resized.
        Ensures the UI remains centered and responsive.
        """
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        self.canvas.delete("table_line")
        
        # Draw the oval table border
        self.canvas.create_oval(50, 50, w-50, h-50, outline=COLOR_TABLE_OUTLINE, width=5, tags="table_line")
        self.canvas.tag_lower("table_line")
        
        # Center elements
        cx, cy = w // 2, h // 2
        self.canvas.coords(self.txt_dealer_lbl, cx, 60)
        self.canvas.coords(self.txt_result, cx, cy)
        
        # Position Advice Box at the bottom
        self.canvas.coords(self.bg_advice, cx - 250, h - 70, cx + 250, h - 20)
        self.canvas.coords(self.txt_advice, cx, h - 45)

    def _update_controls(self, mode: str) -> None:
        """
        Dynamically rebuilds the button panel based on the current game state.
        
        Args:
            mode (str): Current game state ('betting', 'playing', 'end', 'game_over').
        """
        # Clear existing buttons
        for widget in self.bottom_container.winfo_children():
            widget.destroy()

        if mode == "betting":
            tk.Label(self.bottom_container, text="Bet Amount:", fg="white", bg=COLOR_BG, font=("Arial", 14)).pack(side="left", padx=10)
            self.entry_bet = tk.Entry(self.bottom_container, font=("Arial", 14), width=10, justify='center')
            self.entry_bet.insert(0, "50")
            self.entry_bet.pack(side="left", padx=10)
            tk.Button(self.bottom_container, text="DEAL", bg=COLOR_BTN_DEAL, font=("Arial", 14, "bold"), 
                      command=self.validate_bet, width=15).pack(side="left", padx=20)
            
            # Reset Visuals for new round
            self.canvas.itemconfigure(self.txt_result, text="PLACE YOUR BET", fill="white")
            self.canvas.delete("cards")
            self.canvas.delete("scores")
            self.canvas.delete("indicator")
            self.canvas.itemconfigure(self.txt_dealer_score, text="")
            self.canvas.itemconfigure(self.bg_advice, state='hidden')
            self.canvas.itemconfigure(self.txt_advice, text="")

        elif mode == "playing":
            tk.Button(self.bottom_container, text="HIT", font=("Arial", 14, "bold"), width=12, 
                      command=self.hit).pack(side="left", padx=15)
            tk.Button(self.bottom_container, text="STAND", font=("Arial", 14, "bold"), width=12, 
                      command=self.stand).pack(side="left", padx=15)
            self.btn_split = tk.Button(self.bottom_container, text="SPLIT", bg=COLOR_BTN_SPLIT, 
                                     font=("Arial", 14, "bold"), width=12, command=self.split_pair)
            self.btn_split.pack(side="left", padx=15)

        elif mode == "end":
            tk.Button(self.bottom_container, text="REPLAY", bg=COLOR_BTN_ACTION, font=("Arial", 14, "bold"), 
                      command=self.replay_same_bet, width=12).pack(side="left", padx=10)
            tk.Button(self.bottom_container, text="CHANGE BET", font=("Arial", 14), 
                      command=lambda: self._update_controls("betting"), width=15).pack(side="left", padx=10)
            tk.Button(self.bottom_container, text="QUIT", bg=COLOR_BTN_QUIT, font=("Arial", 14, "bold"), 
                      command=self.force_kill_app, width=10).pack(side="left", padx=20)

        elif mode == "game_over":
            tk.Label(self.bottom_container, text="YOU RAN OUT OF MONEY!", fg=COLOR_GAME_OVER, bg=COLOR_BG, font=("Arial", 14, "bold")).pack(side="left", padx=20)
            tk.Button(self.bottom_container, text="ADD $1000", bg=COLOR_BTN_DEAL, font=("Arial", 14, "bold"), 
                      command=self.refill_bankroll, width=15).pack(side="left", padx=10)
            tk.Button(self.bottom_container, text="QUIT", bg=COLOR_BTN_QUIT, font=("Arial", 14, "bold"), 
                      command=self.force_kill_app, width=10).pack(side="left", padx=20)

        # Force UI update to prevent rendering glitches on some OS versions
        self.bottom_container.update()

    # -------------------------------------------------------------------------
    # CORE GAME LOGIC
    # -------------------------------------------------------------------------
    def validate_bet(self) -> None:
        """
        Validates the user input for the bet.
        Ensures the input is a positive number and within bankroll limits[cite: 91].
        """
        try:
            amount = int(self.entry_bet.get())
            if amount <= 0:
                raise ValueError("Bet must be positive.")
            if amount > self.bankroll:
                messagebox.showerror("Error", "Insufficient funds!")
                return
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number.")
            return

        self.base_bet = amount
        self.start_round()

    def start_round(self) -> None:
        """Initializes the deck, hands, and deals the first two cards."""
        self.bankroll -= self.base_bet
        self.lbl_bankroll.config(text=f"BANKROLL: ${self.bankroll}")
        
        # Create and shuffle deck
        self.deck = [Card(v, s) for v in range(2, 15) for s in SUITS.keys()]
        random.shuffle(self.deck)
        
        # Deal initial cards
        initial_hand = [self.deck.pop(), self.deck.pop()]
        self.player_hands = [initial_hand]
        self.player_bets = [self.base_bet]
        self.hand_statuses = ["Active"]
        self.current_hand_index = 0
        self.dealer_hand = [self.deck.pop(), self.deck.pop()]
        
        self.is_game_active = True
        self.canvas.itemconfigure(self.txt_result, text="")
        self._update_controls("playing")
        self.update_display(hide_dealer=True)

        # Check for immediate Blackjack (Natural 21)
        score, _ = self.calculate_hand_score(initial_hand)
        if score == 21:
            self.hand_statuses[0] = "Blackjack"
            self.stand()

    def hit(self) -> None:
        """Player action: Take another card."""
        current_hand = self.player_hands[self.current_hand_index]
        current_hand.append(self.deck.pop())
        self.update_display(hide_dealer=True)
        
        score, _ = self.calculate_hand_score(current_hand)
        if score > 21:
            self.hand_statuses[self.current_hand_index] = "Bust"
            self.process_next_hand()
        elif score == 21:
            # Auto-stand on 21 to speed up gameplay
            self.process_next_hand()

    def stand(self) -> None:
        """Player action: End turn for current hand."""
        self.hand_statuses[self.current_hand_index] = "Stand"
        self.process_next_hand()

    def split_pair(self) -> None:
        """
        Splits a pair into two separate hands.
        Doubles the total wager and deals a new card to each split hand.
        """
        current_hand = self.player_hands[self.current_hand_index]
        
        # Validate Split constraints
        if len(self.player_bets) >= 3: 
             messagebox.showinfo("Info", "Maximum 3 hands allowed.")
             return
        if self.bankroll < self.base_bet:
            messagebox.showwarning("Error", "Insufficient funds to split.")
            return

        # Deduct bet for the new hand
        self.bankroll -= self.base_bet
        self.lbl_bankroll.config(text=f"BANKROLL: ${self.bankroll}")
        
        # Perform the split
        card_to_move = current_hand.pop()
        new_hand = [card_to_move]
        
        # Insert new hand into game state
        self.player_hands.insert(self.current_hand_index + 1, new_hand)
        self.player_bets.insert(self.current_hand_index + 1, self.base_bet)
        self.hand_statuses.insert(self.current_hand_index + 1, "Active")
        
        # Deal second card to the first split hand
        current_hand.append(self.deck.pop())
        self.update_display(hide_dealer=True)

    def process_next_hand(self) -> None:
        """Moves focus to the next hand (if split) or proceeds to Dealer's turn."""
        if self.current_hand_index < len(self.player_hands) - 1:
            self.current_hand_index += 1
            # If the next hand has only 1 card (from a split), deal the second card
            if len(self.player_hands[self.current_hand_index]) == 1:
                 self.player_hands[self.current_hand_index].append(self.deck.pop())
            self.update_display(hide_dealer=True)
            
            # Check for Blackjack on the new hand
            score, _ = self.calculate_hand_score(self.player_hands[self.current_hand_index])
            if score == 21:
                 self.hand_statuses[self.current_hand_index] = "Blackjack"
                 self.process_next_hand()
        else:
            self.play_dealer_turn()

    def play_dealer_turn(self) -> None:
        """
        Executes Dealer logic based on strict Casino rules.
        Dealer MUST draw to 16 and STAND on 17.
        """
        # If all player hands busted, Dealer doesn't need to play
        if all(status == "Bust" for status in self.hand_statuses):
            self.resolve_game()
            return

        self.update_display(hide_dealer=False)
        self.root.update()
        
        while True:
            dealer_score, _ = self.calculate_hand_score(self.dealer_hand)
            if dealer_score < 17:
                self.root.after(600) # Small delay for animation
                self.dealer_hand.append(self.deck.pop())
                self.update_display(hide_dealer=False)
                self.root.update()
            else:
                break
        self.resolve_game()

    def resolve_game(self) -> None:
        """Compares scores and resolves bets (Win, Loss, Push)."""
        dealer_score, _ = self.calculate_hand_score(self.dealer_hand)
        total_payout = 0

        for i, hand in enumerate(self.player_hands):
            status = self.hand_statuses[i]
            bet = self.player_bets[i]
            player_score, _ = self.calculate_hand_score(hand)
            
            if status == "Bust":
                pass # Player loses bet
            elif status == "Blackjack":
                if dealer_score == 21 and len(self.dealer_hand) == 2:
                    total_payout += bet # Push (Tie)
                else:
                    total_payout += bet * 2.5 # Blackjack Payout 3:2
            else:
                if dealer_score > 21:
                    total_payout += bet * 2 # Dealer Busts
                elif player_score > dealer_score:
                    total_payout += bet * 2 # Player Wins
                elif player_score == dealer_score:
                    total_payout += bet # Push
        
        self.bankroll += int(total_payout)
        self.lbl_bankroll.config(text=f"BANKROLL: ${self.bankroll}")
        
        # Display Result Message
        total_wagered = sum(self.player_bets)
        if total_payout > total_wagered:
            msg = f"WIN (+${int(total_payout - total_wagered)})"
            col = COLOR_TABLE_OUTLINE
        elif total_payout < total_wagered:
            msg = "LOSS"
            col = COLOR_BTN_QUIT
        else:
            msg = "PUSH"
            col = COLOR_ACCENT
            
        self.canvas.itemconfigure(self.txt_result, text=msg, fill=col)
        self.canvas.tag_raise(self.txt_result)
        
        # Check for Bankruptcy
        if self.bankroll <= 0:
            self.canvas.itemconfigure(self.txt_result, text="GAME OVER", fill=COLOR_GAME_OVER)
            self._update_controls("game_over")
        else:
            self._update_controls("end")

    # -------------------------------------------------------------------------
    # UTILITIES & AI
    # -------------------------------------------------------------------------
    def calculate_hand_score(self, hand: List[Card]) -> Tuple[int, bool]:
        """
        Calculates hand score handling Aces dynamically.
        
        Args:
            hand: List of Card objects.
        Returns:
            Tuple(total_score, is_soft_hand)
        """
        total = 0
        ace_count = 0
        for card in hand:
            val = card.get_blackjack_value()
            total += val
            if val == 11:
                ace_count += 1
        
        is_soft = (ace_count > 0 and total <= 21)
        
        # Adjust Aces from 11 to 1 if total exceeds 21
        while total > 21 and ace_count > 0:
            total -= 10
            ace_count -= 1
            if ace_count == 0:
                is_soft = False
        return total, is_soft

    def generate_basic_strategy(self) -> str:
        """
        AI Advisor: Recommends the mathematically optimal move.
        Based on Basic Strategy charts.
        """
        current_hand = self.player_hands[self.current_hand_index]
        score, is_soft = self.calculate_hand_score(current_hand)
        dealer_val = self.dealer_hand[1].get_blackjack_value()
        
        # Hard Totals
        if score >= 17 and not is_soft: return "STAND"
        if score <= 11 and not is_soft: return "HIT"
        
        # Soft Totals (Hand with an Ace counted as 11)
        if is_soft:
            if score >= 19: return "STAND"
            if score == 18:
                return "STAND" if 2 <= dealer_val <= 8 else "HIT"
            return "HIT"
        else:
            # Intermediate Hard Totals
            if score == 12:
                return "STAND" if 4 <= dealer_val <= 6 else "HIT"
            if 13 <= score <= 16:
                return "STAND" if 2 <= dealer_val <= 6 else "HIT"
        return ""

    def update_display(self, hide_dealer: bool = True) -> None:
        """Refreshes the Canvas with current cards and scores."""
        self.canvas.delete("cards")
        self.canvas.delete("scores")
        self.canvas.delete("indicator")
        
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        cx = w // 2
        
        # Draw Dealer Hand
        start_x_d = cx - (len(self.dealer_hand) * 45)
        for i, card in enumerate(self.dealer_hand):
            is_hidden = (i == 0 and hide_dealer)
            self.draw_card(start_x_d + i * 50, 90, card, hidden=is_hidden)
            
        if not hide_dealer:
            score, _ = self.calculate_hand_score(self.dealer_hand)
            self.canvas.itemconfigure(self.txt_dealer_score, text=f"Score: {score}")
            self.canvas.coords(self.txt_dealer_score, cx, 240)
            self.canvas.tag_raise(self.txt_dealer_score)
        else:
            self.canvas.itemconfigure(self.txt_dealer_score, text="Score: ?")
            self.canvas.coords(self.txt_dealer_score, cx, 240)
            self.canvas.tag_raise(self.txt_dealer_score)

        # Draw Player Hand(s)
        num_hands = len(self.player_hands)
        width_per_hand = 300
        total_width = num_hands * width_per_hand
        start_x_base = cx - (total_width / 2) + (width_per_hand / 2)

        for idx, hand in enumerate(self.player_hands):
            center_x = start_x_base + (idx * width_per_hand)
            total_card_width = (len(hand) - 1) * 30 + 80
            start_card_x = center_x - (total_card_width / 2)
            player_y = h - 260 
            
            for i, card in enumerate(hand):
                self.draw_card(start_card_x + i * 30, player_y, card, hidden=False)
            
            score, _ = self.calculate_hand_score(hand)
            self.canvas.create_text(
                center_x, player_y + 140, text=f"Score: {score}", fill="white", 
                font=("Arial", 14, "bold"), tags="scores"
            )
            
            # Active hand indicator (Yellow Triangle)
            if idx == self.current_hand_index and self.is_game_active:
                self.canvas.create_polygon(
                    center_x, player_y - 10, center_x-15, player_y - 30, center_x+15, player_y - 30, 
                    fill=COLOR_ACCENT, tags="indicator"
                )

        # Update Split Button availability
        if self.is_game_active and hasattr(self, 'btn_split'):
            current_hand = self.player_hands[self.current_hand_index]
            can_split = (len(current_hand) == 2 and 
                         current_hand[0].get_face_value() == current_hand[1].get_face_value() and 
                         self.bankroll >= self.base_bet)
            if can_split:
                 self.btn_split.config(state="normal", bg=COLOR_BTN_SPLIT)
            else:
                 self.btn_split.config(state="disabled", bg="gray")

        # Update AI Advice
        if self.is_game_active and hide_dealer:
            advice = self.generate_basic_strategy()
            self.canvas.itemconfigure(self.bg_advice, state='normal')
            self.canvas.itemconfigure(self.txt_advice, text=f"PRO ADVICE: {advice}")
            self.canvas.tag_raise(self.bg_advice)
            self.canvas.tag_raise(self.txt_advice)
        else:
            self.canvas.itemconfigure(self.txt_advice, text="")
            self.canvas.itemconfigure(self.bg_advice, state='hidden')

    def draw_card(self, x: float, y: float, card: Card, hidden: bool) -> None:
        """
        Renders a card on the canvas using vector shapes.
        Avoids external image dependencies for portability.
        """
        # Shadow effect
        self.canvas.create_rectangle(x+5, y+5, x+85, y+125, fill="black", stipple="gray50", tags="cards")
        
        if hidden:
            # Card Back (Red pattern)
            self.canvas.create_rectangle(x, y, x+80, y+120, fill="#c0392b", outline="white", width=2, tags="cards")
            self.canvas.create_line(x, y, x+80, y+120, fill="#e74c3c", width=3, tags="cards")
            self.canvas.create_line(x+80, y, x, y+120, fill="#e74c3c", width=3, tags="cards")
        else:
            # Card Front
            self.canvas.create_rectangle(x, y, x+80, y+120, fill="white", outline="black", width=2, tags="cards")
            color = "red" if card.is_red() else "black"
            self.canvas.create_text(x+15, y+20, text=VALUES[card.value], fill=color, font=("Arial", 14, "bold"), tags="cards")
            self.canvas.create_text(x+15, y+40, text=SUITS[card.suit], fill=color, font=("Arial", 14, "bold"), tags="cards")
            self.canvas.create_text(x+40, y+60, text=SUITS[card.suit], fill=color, font=("Arial", 36), tags="cards")

    def force_kill_app(self):
        """
        Forcefully terminates the application.
        This is a workaround for Tkinter on macOS, where the window sometimes hangs on close.
        """
        print("Closing application...")
        try:
            self.root.destroy()
        except:
            pass
        os._exit(0)

    def refill_bankroll(self) -> None:
        self.bankroll = 1000
        self.lbl_bankroll.config(text=f"BANKROLL: ${self.bankroll}")
        self._update_controls("betting")

    def replay_same_bet(self) -> None:
        if self.bankroll < self.base_bet:
            messagebox.showwarning("Error", "Insufficient funds.")
            self._update_controls("betting")
        else:
            self.start_round()

# =============================================================================
# BLOCK 5: ENTRY POINT
# =============================================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = BlackJackUltimate(root)
    root.mainloop()
