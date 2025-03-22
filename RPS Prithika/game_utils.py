import random
from datetime import datetime

class RPSGame:
    def __init__(self):
        self.game_history = []
        self.move_counts = {'rock': 0, 'paper': 0, 'scissors': 0}
        self.win_rates = [0]  # Initialize with 0
        self.wins = 0
        self.total_games = 0

    def play(self, player_choice):
        choices = ['rock', 'paper', 'scissors']
        computer_choice = random.choice(choices)
        
        # Update move counts
        self.move_counts[player_choice.lower()] += 1
        
        # Determine winner
        if player_choice == computer_choice:
            result = 'ties'
        elif (
            (player_choice == 'rock' and computer_choice == 'scissors') or
            (player_choice == 'paper' and computer_choice == 'rock') or
            (player_choice == 'scissors' and computer_choice == 'paper')
        ):
            result = 'wins'
            self.wins += 1
        else:
            result = 'losses'
        
        self.total_games += 1
        
        # Calculate and store win rate
        win_rate = (self.wins / self.total_games) * 100 if self.total_games > 0 else 0
        self.win_rates.append(win_rate)
        
        # Record game in history
        self.game_history.append({
            'datetime': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'player': player_choice,
            'computer': computer_choice,
            'result': result
        })
        
        return computer_choice, result

    def get_stats(self):
        win_rate = f"{(self.wins / self.total_games * 100):.1f}%" if self.total_games > 0 else "0.0%"
        return {
            'total_games': self.total_games,
            'wins': self.wins,
            'win_rate': win_rate
        }

    def get_move_distribution(self):
        return {k.capitalize(): v for k, v in self.move_counts.items()}

    def get_winrate_trend(self):
        return self.win_rates
