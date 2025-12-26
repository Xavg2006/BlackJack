import tkinter as tk
from tkinter import messagebox
import random
import os  # 
from typing import List, Tuple

# --- 1. CONFIGURATION & CONSTANTS ---
COLOR_BG = "#2c3e50"           
COLOR_TABLE = "#27ae60"        
COLOR_TABLE_OUTLINE = "#2ecc71"
COLOR_ACCENT = "#f1c40f"       
COLOR_BTN_ACTION = "#3498db"   
COLOR_BTN_STOP = "#e67e22"     
COLOR_BTN_SPLIT = "#9b59b6"    
COLOR_BTN_DEAL = "#2ecc71"     
COLOR_BTN_QUIT = "#e74c3c"     
COLOR_GAME_OVER = "#c0392b"    

FONT_MAIN = ("Arial", 14)
FONT_BOLD = ("Arial", 14, "bold")
FONT_TITLE = ("Arial", 30, "bold")
FONT_ADVICE = ("Arial", 16, "bold")

SUITS = {'C': '♥', 'D': '♦', 'H': '♣', 'S': '♠'}
VALUES = {
    2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 
    9: '9', 10: '10', 11: 'J', 12: 'Q', 13: 'K', 14: 'A'
}

class Card:
    """Represents a standard playing card."""
    def __init__(self, value: int, suit: str):
        self.value = value
        self.suit = suit

    def get_blackjack_value(self) -> int:
        if 10 <= self.value < 14: return 10
        if self.value == 14: return 11
        return self.value

    def get_face_value(self) -> int:
        if 10 <= self.value < 14: return 10
        return self.value

    def is_red(self) -> bool:
        return self.suit in ['D', 'H']

class BlackJackUltimate:
    """Main Game Class."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("BlackJack Ultimate - Mac Edition")
        self.root.geometry("1100x850")
        self.root.configure(bg=COLOR_BG)

        # Game State
        self.deck: List[Card] = []
        self.player_hands: List[List[Card]] = []
        self.player_bets: List[int] = []
        self.hand_statuses: List[str] = []
        self.current_hand_index = 0
        self.dealer_hand: List[Card] = []
        
        self.bankroll = 1000 
        self.base_bet = 0
        self.is_game_active = False

        # Build UI Structure
        self._setup_ui_structure()
        self._update_controls("betting")

        # Bind the window close button (X) to our force kill function
        self.root.protocol("WM_DELETE_WINDOW", self.force_kill_app)

    def _setup_ui_structure(self) -> None:
        """Sets up the static UI containers."""
        # 1. Header
        self.frame_top = tk.Frame(self.root, bg=COLOR_BG)
        self.frame_top.pack(side="top", fill="x", pady=10)
        
        self.lbl_bankroll = tk.Label(
            self.frame_top, 
            text="BANKROLL: $1000", 
            font=("Arial", 22, "bold"), 
            fg=COLOR_ACCENT, 
            bg=COLOR_BG
        )
        self.lbl_bankroll.pack()

        # 2. Bottom Container (For Buttons)
        self.bottom_container = tk.Frame(self.root, bg=COLOR_BG, pady=20)
        self.bottom_container.pack(side="bottom", fill="x")

        # 3. Game Table (Canvas)
        self.canvas = tk.Canvas(self.root, bg=COLOR_TABLE, highlightthickness=0)
        self.canvas.pack(side="top", expand=True, fill="both", padx=20, pady=(0, 20))
        
        self.canvas.bind("<Configure>", self._draw_table_background)
        
        # Static Elements
        self.txt_dealer_lbl = self.canvas.create_text(0, 0, text="DEALER", font=("Arial", 16, "bold"), fill="#1e8449")
        self.txt_dealer_score = self.canvas.create_text(0, 0, text="", font=FONT_MAIN, fill="white")
        self.txt_result = self.canvas.create_text(0, 0, text="PLACE YOUR BET", font=FONT_TITLE, fill="white")
        self.bg_advice = self.canvas.create_rectangle(0, 0, 0, 0, fill=COLOR_BG, outline=COLOR_ACCENT, width=2, state='hidden')
        self.txt_advice = self.canvas.create_text(0, 0, text="", font=FONT_ADVICE, fill=COLOR_ACCENT)

    def _draw_table_background(self, event=None):
        """Responsive table drawing."""
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        self.canvas.delete("table_line")
        self.canvas.create_oval(50, 50, w-50, h-50, outline=COLOR_TABLE_OUTLINE, width=5, tags="table_line")
        self.canvas.tag_lower("table_line")
        
        cx, cy = w // 2, h // 2
        self.canvas.coords(self.txt_dealer_lbl, cx, 60)
        self.canvas.coords(self.txt_result, cx, cy)
        
        self.canvas.coords(self.bg_advice, cx - 250, h - 70, cx + 250, h - 20)
        self.canvas.coords(self.txt_advice, cx, h - 45)

   
    def force_kill_app(self):
        """Kill the process immediately (prevents Mac spinning wheel)."""
        print("Closing application...")
        try:
            self.root.destroy()
        except:
            pass
        os._exit(0) 

    def _update_controls(self, mode: str) -> None:
        # 1. Destroy all previous buttons
        for widget in self.bottom_container.winfo_children():
            widget.destroy()

        # 2. Build new buttons
        if mode == "betting":
            tk.Label(self.bottom_container, text="Bet Amount:", fg="white", bg=COLOR_BG, font=FONT_MAIN).pack(side="left", padx=10)
            
            self.entry_bet = tk.Entry(self.bottom_container, font=FONT_MAIN, width=10, justify='center')
            self.entry_bet.insert(0, "50")
            self.entry_bet.pack(side="left", padx=10)
            
            tk.Button(self.bottom_container, text="DEAL", bg=COLOR_BTN_DEAL, font=FONT_BOLD, 
                      command=self.validate_bet, width=15).pack(side="left", padx=20)
            
            self.canvas.itemconfigure(self.txt_result, text="PLACE YOUR BET", fill="white")
            self.canvas.delete("cards")
            self.canvas.delete("scores")
            self.canvas.delete("indicator")
            self.canvas.itemconfigure(self.txt_dealer_score, text="")
            self.canvas.itemconfigure(self.txt_advice, text="")
            self.canvas.itemconfigure(self.bg_advice, state='hidden')

        elif mode == "playing":
            tk.Button(self.bottom_container, text="HIT", font=FONT_BOLD, width=12, 
                      command=self.hit).pack(side="left", padx=15)
            tk.Button(self.bottom_container, text="STAND", font=FONT_BOLD, width=12, 
                      command=self.stand).pack(side="left", padx=15)
            
            self.btn_split = tk.Button(self.bottom_container, text="SPLIT", bg=COLOR_BTN_SPLIT, 
                                     font=FONT_BOLD, width=12, command=self.split_pair)
            self.btn_split.pack(side="left", padx=15)

        elif mode == "end":
            tk.Button(self.bottom_container, text="REPLAY", bg=COLOR_BTN_ACTION, font=FONT_BOLD, 
                      command=self.replay_same_bet, width=12).pack(side="left", padx=10)
            
            tk.Button(self.bottom_container, text="CHANGE BET", font=FONT_MAIN, 
                      command=lambda: self._update_controls("betting"), width=15).pack(side="left", padx=10)
            
            # Utilise la nouvelle fonction force_kill_app
            tk.Button(self.bottom_container, text="QUIT", bg=COLOR_BTN_QUIT, font=FONT_BOLD, 
                      command=self.force_kill_app, width=10).pack(side="left", padx=20)

        elif mode == "game_over":
            tk.Label(self.bottom_container, text="YOU RAN OUT OF MONEY!", fg=COLOR_GAME_OVER, bg=COLOR_BG, font=FONT_BOLD).pack(side="left", padx=20)
            
            tk.Button(self.bottom_container, text="ADD $1000", bg=COLOR_BTN_DEAL, font=FONT_BOLD, 
                      command=self.refill_bankroll, width=15).pack(side="left", padx=10)
            
            # Utilise la nouvelle fonction force_kill_app
            tk.Button(self.bottom_container, text="QUIT", bg=COLOR_BTN_QUIT, font=FONT_BOLD, 
                      command=self.force_kill_app, width=10).pack(side="left", padx=20)

        self.bottom_container.update()

    # =========================================================================
    # GAME LOGIC
    # =========================================================================

    def refill_bankroll(self) -> None:
        self.bankroll = 1000
        self.lbl_bankroll.config(text=f"BANKROLL: ${self.bankroll}")
        self._update_controls("betting")

    def validate_bet(self) -> None:
        try:
            amount = int(self.entry_bet.get())
            if amount <= 0: raise ValueError
            if amount > self.bankroll:
                messagebox.showerror("Error", "Insufficient funds!")
                return
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number.")
            return

        self.base_bet = amount
        self.start_round()

    def start_round(self) -> None:
        self.bankroll -= self.base_bet
        self.lbl_bankroll.config(text=f"BANKROLL: ${self.bankroll}")
        
        self.deck = [Card(v, s) for v in range(2, 15) for s in SUITS.keys()]
        random.shuffle(self.deck)
        
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

        score, _ = self.calculate_hand_score(initial_hand)
        if score == 21:
            self.hand_statuses[0] = "Blackjack"
            self.stand()

    def hit(self) -> None:
        current_hand = self.player_hands[self.current_hand_index]
        current_hand.append(self.deck.pop())
        self.update_display(hide_dealer=True)
        
        score, _ = self.calculate_hand_score(current_hand)
        if score > 21:
            self.hand_statuses[self.current_hand_index] = "Bust"
            self.process_next_hand()
        elif score == 21:
            self.process_next_hand()

    def stand(self) -> None:
        self.hand_statuses[self.current_hand_index] = "Stand"
        self.process_next_hand()

    def process_next_hand(self) -> None:
        if self.current_hand_index < len(self.player_hands) - 1:
            self.current_hand_index += 1
            if len(self.player_hands[self.current_hand_index]) == 1:
                 self.player_hands[self.current_hand_index].append(self.deck.pop())
            
            self.update_display(hide_dealer=True)
            
            score, _ = self.calculate_hand_score(self.player_hands[self.current_hand_index])
            if score == 21:
                 self.hand_statuses[self.current_hand_index] = "Blackjack"
                 self.process_next_hand()
        else:
            self.play_dealer_turn()

    def split_pair(self) -> None:
        current_hand = self.player_hands[self.current_hand_index]
        if len(self.player_bets) >= 3: 
             messagebox.showinfo("Info", "Maximum 3 hands allowed.")
             return
        if self.bankroll < self.base_bet:
            messagebox.showwarning("Error", "Insufficient funds to split.")
            return

        self.bankroll -= self.base_bet
        self.lbl_bankroll.config(text=f"BANKROLL: ${self.bankroll}")
        
        card_to_move = current_hand.pop()
        new_hand = [card_to_move]
        
        self.player_hands.insert(self.current_hand_index + 1, new_hand)
        self.player_bets.insert(self.current_hand_index + 1, self.base_bet)
        self.hand_statuses.insert(self.current_hand_index + 1, "Active")
        
        current_hand.append(self.deck.pop())
        self.update_display(hide_dealer=True)

    def play_dealer_turn(self) -> None:
        if all(status == "Bust" for status in self.hand_statuses):
            self.resolve_game()
            return

        self.update_display(hide_dealer=False)
        self.root.update()
        
        while True:
            dealer_score, _ = self.calculate_hand_score(self.dealer_hand)
            if dealer_score < 17:
                self.root.after(600)
                self.dealer_hand.append(self.deck.pop())
                self.update_display(hide_dealer=False)
                self.root.update()
            else:
                break
        
        self.resolve_game()

    def resolve_game(self) -> None:
        dealer_score, _ = self.calculate_hand_score(self.dealer_hand)
        total_payout = 0

        for i, hand in enumerate(self.player_hands):
            status = self.hand_statuses[i]
            bet = self.player_bets[i]
            player_score, _ = self.calculate_hand_score(hand)
            
            if status == "Bust":
                pass
            elif status == "Blackjack":
                if dealer_score == 21 and len(self.dealer_hand) == 2:
                    total_payout += bet 
                else:
                    total_payout += bet * 2.5 
            else:
                if dealer_score > 21:
                    total_payout += bet * 2
                elif player_score > dealer_score:
                    total_payout += bet * 2
                elif player_score == dealer_score:
                    total_payout += bet
        
        self.bankroll += int(total_payout)
        self.lbl_bankroll.config(text=f"BANKROLL: ${self.bankroll}")
        
        total_wagered = sum(self.player_bets)
        if total_payout > total_wagered:
            msg = f"WIN (+${int(total_payout - total_wagered)})"
            color = COLOR_TABLE_OUTLINE
        elif total_payout < total_wagered:
            msg = "LOSS"
            color = COLOR_BTN_QUIT
        else:
            msg = "PUSH"
            color = COLOR_ACCENT
            
        self.canvas.itemconfigure(self.txt_result, text=msg, fill=color)
        self.canvas.tag_raise(self.txt_result)
        
        if self.bankroll <= 0:
            self.canvas.itemconfigure(self.txt_result, text="GAME OVER", fill=COLOR_GAME_OVER)
            self._update_controls("game_over")
        else:
            self._update_controls("end")

    def replay_same_bet(self) -> None:
        if self.bankroll < self.base_bet:
            messagebox.showwarning("Error", "Insufficient funds.")
            self._update_controls("betting")
        else:
            self.start_round()

    def calculate_hand_score(self, hand: List[Card]) -> Tuple[int, bool]:
        total = 0
        ace_count = 0
        for card in hand:
            val = card.get_blackjack_value()
            total += val
            if val == 11:
                ace_count += 1
        
        is_soft = (ace_count > 0 and total <= 21)

        while total > 21 and ace_count > 0:
            total -= 10
            ace_count -= 1
            if ace_count == 0:
                is_soft = False

        return total, is_soft

    def generate_basic_strategy(self) -> str:
        current_hand = self.player_hands[self.current_hand_index]
        score, is_soft = self.calculate_hand_score(current_hand)
        dealer_val = self.dealer_hand[1].get_blackjack_value()
        
        if score >= 17 and not is_soft: return "STAND"
        if score <= 11 and not is_soft: return "HIT"
        
        if is_soft:
            if score >= 19: return "STAND"
            if score == 18:
                return "STAND" if 2 <= dealer_val <= 8 else "HIT"
            return "HIT"
        else:
            if score == 12:
                return "STAND" if 4 <= dealer_val <= 6 else "HIT"
            if 13 <= score <= 16:
                return "STAND" if 2 <= dealer_val <= 6 else "HIT"
        return ""

    # =========================================================================
    # RENDERING
    # =========================================================================

    def update_display(self, hide_dealer: bool = True) -> None:
        self.canvas.delete("cards")
        self.canvas.delete("scores")
        self.canvas.delete("indicator")
        
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        cx = w // 2
        
        # 1. Dealer
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

        # 2. Player
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
                font=FONT_BOLD, tags="scores"
            )
            
            if idx == self.current_hand_index and self.is_game_active:
                self.canvas.create_polygon(
                    center_x, player_y - 10, center_x-15, player_y - 30, center_x+15, player_y - 30, 
                    fill=COLOR_ACCENT, tags="indicator"
                )

        # 3. Update Split Button State
        if self.is_game_active and hasattr(self, 'btn_split'):
            current_hand = self.player_hands[self.current_hand_index]
            can_split = (len(current_hand) == 2 and 
                         current_hand[0].get_face_value() == current_hand[1].get_face_value() and 
                         self.bankroll >= self.base_bet)
            
            if can_split:
                 self.btn_split.config(state="normal", bg=COLOR_BTN_SPLIT)
            else:
                 self.btn_split.config(state="disabled", bg="gray")

        # 4. Advice
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
        self.canvas.create_rectangle(x+5, y+5, x+85, y+125, fill="black", stipple="gray50", tags="cards")
        
        if hidden:
            self.canvas.create_rectangle(x, y, x+80, y+120, fill="#c0392b", outline="white", width=2, tags="cards")
            self.canvas.create_line(x, y, x+80, y+120, fill="#e74c3c", width=3, tags="cards")
            self.canvas.create_line(x+80, y, x, y+120, fill="#e74c3c", width=3, tags="cards")
        else:
            self.canvas.create_rectangle(x, y, x+80, y+120, fill="white", outline="black", width=2, tags="cards")
            color = "red" if card.is_red() else "black"
            
            self.canvas.create_text(x+15, y+20, text=VALUES[card.value], fill=color, font=FONT_BOLD, tags="cards")
            self.canvas.create_text(x+15, y+40, text=SUITS[card.suit], fill=color, font=FONT_BOLD, tags="cards")
            self.canvas.create_text(x+40, y+60, text=SUITS[card.suit], fill=color, font=("Arial", 36), tags="cards")

if __name__ == "__main__":
    root = tk.Tk()
    app = BlackJackUltimate(root)
    root.mainloop()
