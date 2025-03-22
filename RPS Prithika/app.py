import customtkinter as ctk
from datetime import datetime
from data_utils import create_charts
from game_utils import RPSGame

# Set appearance mode and default color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Create the main application window
app = ctk.CTk()
app.title("Prithika's Dashboard")

# Set the window size
app.geometry("1000x600")

# Center the window on the screen
screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()
x = (screen_width - 1000) // 2
y = (screen_height - 600) // 2
app.geometry(f"1000x600+{x}+{y}")

# Configure grid layout
app.grid_rowconfigure(0, weight=1)
app.grid_columnconfigure(1, weight=1)

# Create frames dictionary to store different views
frames = {}

# Create sidebar frame with gradient effect
sidebar_frame = ctk.CTkFrame(app, width=200, corner_radius=0, fg_color=("#2B2B2B", "#2B2B2B"))
sidebar_frame.grid(row=0, column=0, sticky="nsew")
sidebar_frame.grid_rowconfigure(4, weight=1)

# Create main content frame
main_frame = ctk.CTkFrame(app, fg_color="transparent")
main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
main_frame.grid_columnconfigure(0, weight=1)

# Add logo/title to sidebar with accent color
logo_label = ctk.CTkLabel(sidebar_frame, text="Prithika", 
                         font=ctk.CTkFont(family="Helvetica", size=26, weight="bold"),
                         text_color=("#1F538D", "#3B8ED0"))
logo_label.grid(row=0, column=0, padx=20, pady=(30, 30))

# Initialize game
game = RPSGame()

# Update navigation buttons
button_style = {
    "height": 40, 
    "corner_radius": 8, 
    "hover_color": ("#1F538D", "#3B8ED0"),
    "font": ctk.CTkFont(family="Roboto", size=14)
}

nav_buttons = [
    ("🏠 Dashboard", "dashboard"),
    ("🎮 Game", "game"),
    ("📋 History", "history")
]

# Create frames dictionary to store different views
frames = {}

def show_frame(frame_name):
    for frame in frames.values():
        frame.grid_remove()
    if frame_name == 'dashboard':
        update_stats_display()
    elif frame_name == 'history':
        update_history_display()
    frames[frame_name].grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

# Create and configure navigation buttons
for i, (text, frame_name) in enumerate(nav_buttons, 1):
    btn = ctk.CTkButton(sidebar_frame, text=text, command=lambda n=frame_name: show_frame(n), **button_style)
    btn.grid(row=i, column=0, padx=20, pady=10, sticky="ew")

# Create main dashboard frame
dashboard_frame = ctk.CTkFrame(app, fg_color="transparent")
frames['dashboard'] = dashboard_frame
dashboard_frame.grid_columnconfigure(0, weight=1)

# Create other frames
for frame_name in ['game', 'history', 'settings']:
    frame = ctk.CTkFrame(app, fg_color="transparent")
    frames[frame_name] = frame
    frame.grid_columnconfigure(0, weight=1)
    
    # Add title to each frame
    title = ctk.CTkLabel(frame, text=frame_name.title(),
                        font=ctk.CTkFont(family="Helvetica", size=32, weight="bold"))
    title.grid(row=0, column=0, padx=20, pady=(20,30), sticky="w")

# Dashboard content
# Header with date
header_frame = ctk.CTkFrame(dashboard_frame, height=100)
header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
header_frame.grid_columnconfigure(1, weight=1)

current_time = datetime.now().strftime("%B %d, 2023")
time_label = ctk.CTkLabel(header_frame, text=current_time, 
                         font=ctk.CTkFont(family="Arial", size=15, weight="bold"))
time_label.grid(row=0, column=2, padx=20, pady=20)

# Welcome section
welcome_frame = ctk.CTkFrame(dashboard_frame)
welcome_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
welcome_frame.grid_columnconfigure(0, weight=1)

welcome_label = ctk.CTkLabel(welcome_frame, 
                            text="👋 Welcome back, Prithika!",
                            font=ctk.CTkFont(family="Helvetica", size=32, weight="bold"))
welcome_label.grid(row=0, column=0, padx=20, pady=(20,10), sticky="w")

# Statistics cards with reduced height
stats_frame = ctk.CTkFrame(dashboard_frame)
stats_frame.grid(row=2, column=0, sticky="ew", pady=(0, 15))
stats_frame.grid_columnconfigure((0,1,2), weight=1)

# Create three statistics cards
stats_data = [
    ("Total Projects", "125", "📁"),
    ("Active Tasks", "42", "✔️"),
    ("Completed", "83", "🎯")
]

for idx, (title, value, icon) in enumerate(stats_data):
    card = ctk.CTkFrame(stats_frame)
    card.grid(row=0, column=idx, padx=10, pady=5, sticky="ew")
    
    icon_label = ctk.CTkLabel(card, text=icon, 
                             font=ctk.CTkFont(family="Segoe UI", size=24))
    icon_label.grid(row=0, column=0, padx=20, pady=(10,2))
    
    value_label = ctk.CTkLabel(card, text=value, 
                              font=ctk.CTkFont(family="Helvetica", size=24, weight="bold"))
    value_label.grid(row=1, column=0, padx=20, pady=2)
    
    title_label = ctk.CTkLabel(card, text=title, 
                              font=ctk.CTkFont(family="Arial", size=14))
    title_label.grid(row=2, column=0, padx=20, pady=(2,10))

# Analytics charts
charts_frame = ctk.CTkFrame(dashboard_frame)
charts_frame.grid(row=3, column=0, sticky="nsew", padx=20, pady=(0,20))

# Create and add charts
charts_widget = create_charts(charts_frame)
charts_widget.pack(fill="both", expand=True)

# Modify dashboard to show game stats
def update_stats_display():
    stats = game.get_stats()
    stats_data = [
        ("Total Games", str(stats['total_games']), "🎮"),
        ("Wins", str(stats['wins']), "🏆"),
        ("Win Rate", stats['win_rate'], "📈")
    ]
    
    for idx, (title, value, icon) in enumerate(stats_data):
        card = ctk.CTkFrame(stats_frame)
        card.grid(row=0, column=idx, padx=10, pady=5, sticky="ew")
        
        icon_label = ctk.CTkLabel(card, text=icon, 
                                font=ctk.CTkFont(family="Segoe UI", size=24))
        icon_label.grid(row=0, column=0, padx=20, pady=(10,2))
        
        value_label = ctk.CTkLabel(card, text=value, 
                                font=ctk.CTkFont(family="Helvetica", size=24, weight="bold"))
        value_label.grid(row=1, column=0, padx=20, pady=2)
        
        title_label = ctk.CTkLabel(card, text=title, 
                                font=ctk.CTkFont(family="Arial", size=14))
        title_label.grid(row=2, column=0, padx=20, pady=(2,10))

# Add back history display function
def update_history_display():
    history_frame = frames['history']
    
    # Clear existing content
    for widget in history_frame.winfo_children():
        widget.destroy()
    
    # Title
    title = ctk.CTkLabel(history_frame, text="Game History",
                        font=ctk.CTkFont(family="Helvetica", size=32, weight="bold"))
    title.grid(row=0, column=0, padx=20, pady=(20,30))
    
    # Create scrollable frame
    scroll_frame = ctk.CTkScrollableFrame(history_frame, width=800, height=400)
    scroll_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
    
    # Add history entries
    for i, record in enumerate(reversed(game.game_history[-50:])):  # Show last 50 games
        entry = f"{record['datetime']} - Player: {record['player'].title()} vs Computer: {record['computer'].title()} - "
        entry += "Win 🎉" if record['result'] == 'wins' else "Loss 😢" if record['result'] == 'losses' else "Tie 🤝"
        
        label = ctk.CTkLabel(scroll_frame, text=entry, anchor="w")
        label.grid(row=i, column=0, padx=10, pady=5, sticky="w")

# Create game interface
def create_game_interface():
    game_frame = frames['game']
    
    # Game container with custom styling
    game_container = ctk.CTkFrame(game_frame, fg_color=("#E3E3E3", "#2B2B2B"))
    game_container.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
    
    # Title with enhanced styling
    title = ctk.CTkLabel(game_container, 
                        text="✨ Rock, Paper, Scissors ✨",
                        font=ctk.CTkFont(family="Helvetica", size=36, weight="bold"),
                        text_color=("#1F538D", "#3B8ED0"))
    title.grid(row=0, column=0, columnspan=3, padx=20, pady=(30,20))
    
    # Score display
    score_frame = ctk.CTkFrame(game_container, fg_color="transparent")
    score_frame.grid(row=1, column=0, columnspan=3, pady=(0,20))
    
    stats = game.get_stats()
    score_text = f"Wins: {stats['wins']} | Total Games: {stats['total_games']} | Win Rate: {stats['win_rate']}"
    score_label = ctk.CTkLabel(score_frame, 
                              text=score_text,
                              font=ctk.CTkFont(family="Arial", size=16),
                              text_color=("#666666", "#999999"))
    score_label.pack(pady=10)
    
    # Result display with custom styling
    result_frame = ctk.CTkFrame(game_container, 
                               fg_color=("#FFFFFF", "#1E1E1E"),
                               corner_radius=15)
    result_frame.grid(row=2, column=0, columnspan=3, pady=20, padx=40, sticky="ew")
    
    result_label = ctk.CTkLabel(result_frame, 
                               text="Make your choice!",
                               font=ctk.CTkFont(family="Arial", size=24, weight="bold"),
                               text_color=("#2B2B2B", "#E0E0E0"))
    result_label.pack(pady=20)
    
    # Choice buttons with enhanced styling
    def play_game(choice):
        computer_choice, result = game.play(choice)
        
        # Animated result display
        result_text = f"You chose {choice}\nComputer chose {computer_choice}\n"
        if result == 'wins':
            result_text += "🎉 You win! 🎉"
            result_label.configure(text_color=("#28A745", "#28A745"))
        elif result == 'losses':
            result_text += "😢 You lose! 😢"
            result_label.configure(text_color=("#DC3545", "#DC3545"))
        else:
            result_text += "🤝 It's a tie! 🤝"
            result_label.configure(text_color=("#FFC107", "#FFC107"))
            
        result_label.configure(text=result_text)
        
        # Update score display
        stats = game.get_stats()
        score_text = f"Wins: {stats['wins']} | Total Games: {stats['total_games']} | Win Rate: {stats['win_rate']}"
        score_label.configure(text=score_text)
        
        # Get game analytics data
        analytics_data = {
            'moves': game.get_move_distribution(),
            'trend': game.get_winrate_trend()
        }
        
        # Update charts if on dashboard
        if 'dashboard' in frames:
            charts_widget = charts_frame.winfo_children()[0]
            charts_widget.update_charts(analytics_data)
        
        update_stats_display()
    
    button_frame = ctk.CTkFrame(game_container, fg_color="transparent")
    button_frame.grid(row=3, column=0, columnspan=3, pady=(20,30))
    
    button_style = {
        "width": 160,
        "height": 160,
        "corner_radius": 20,
        "border_width": 2,
        "border_color": ("#1F538D", "#3B8ED0"),
        "hover_color": ("#1F538D", "#3B8ED0"),
        "fg_color": ("white", "#2B2B2B"),
        "text_color": ("#1F538D", "#3B8ED0"),
        "font": ctk.CTkFont(family="Arial", size=24, weight="bold")
    }
    
    choices = [
        ("🪨\nRock", "rock"),
        ("📄\nPaper", "paper"),
        ("✂️\nScissors", "scissors")
    ]
    
    for i, (text, choice) in enumerate(choices):
        btn = ctk.CTkButton(button_frame, 
                           text=text,
                           command=lambda c=choice: play_game(c),
                           **button_style)
        btn.grid(row=0, column=i, padx=15)
        
        # Add hover animation
        def on_enter(e, button=btn):
            button.configure(fg_color=("#1F538D", "#3B8ED0"),
                           text_color=("white", "white"))
        
        def on_leave(e, button=btn):
            button.configure(fg_color=("white", "#2B2B2B"),
                           text_color=("#1F538D", "#3B8ED0"))
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

# Initialize game interface
create_game_interface()

# Show dashboard initially
show_frame('dashboard')

# Add appearance mode switcher at bottom of sidebar
appearance_mode_menu = ctk.CTkOptionMenu(sidebar_frame, 
                                       values=["Dark", "Light", "System"],
                                       command=lambda x: ctk.set_appearance_mode(x.lower()),
                                       font=ctk.CTkFont(family="Arial", size=13))
appearance_mode_menu.grid(row=5, column=0, padx=20, pady=20, sticky="s")

# Run the application
app.mainloop()

# Update the color scheme and styling constants
COLORS = {
    'primary': ("#1F538D", "#3B8ED0"),
    'secondary': ("#E3E3E3", "#2B2B2B"),
    'accent': ("#28A745", "#28A745"),
    'warning': ("#FFC107", "#FFC107"),
    'danger': ("#DC3545", "#DC3545"),
    'text': ("#2B2B2B", "#E0E0E0"),
    'text_secondary': ("#666666", "#999999"),
    'gradient_start': ("#1F538D", "#2B2B2B"),
    'gradient_end': ("#3B8ED0", "#1E1E1E")
}

# Add custom card styling
class StylizedCard(ctk.CTkFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.configure(
            fg_color=COLORS['secondary'],
            corner_radius=15,
            border_width=2,
            border_color=COLORS['primary']
        )

# Update the create_game_interface function
def create_game_interface():
    game_frame = frames['game']
    
    # Stylized container with gradient effect
    game_container = StylizedCard(game_frame)
    game_container.grid(row=0, column=0, padx=30, pady=30, sticky="nsew")
    
    # Enhanced title with glow effect
    title = ctk.CTkLabel(game_container, 
                        text="⚡ Rock, Paper, Scissors ⚡",
                        font=ctk.CTkFont(family="Helvetica", size=42, weight="bold"),
                        text_color=COLORS['primary'])
    title.grid(row=0, column=0, columnspan=3, padx=20, pady=(40,30))
    
    # Animated score display
    score_frame = StylizedCard(game_container)
    score_frame.grid(row=1, column=0, columnspan=3, pady=(0,30), padx=40, sticky="ew")
    
    stats = game.get_stats()
    score_text = f"🎮 Games: {stats['total_games']} | 🏆 Wins: {stats['wins']} | 📈 Win Rate: {stats['win_rate']}"
    score_label = ctk.CTkLabel(score_frame, 
                              text=score_text,
                              font=ctk.CTkFont(family="Arial", size=18, weight="bold"),
                              text_color=COLORS['text'])
    score_label.pack(pady=15)
    
    # Enhanced result display
    result_frame = StylizedCard(game_container)
    result_frame.grid(row=2, column=0, columnspan=3, pady=20, padx=40, sticky="ew")
    
    result_label = ctk.CTkLabel(result_frame, 
                               text="✨ Choose Your Move! ✨",
                               font=ctk.CTkFont(family="Arial", size=28, weight="bold"),
                               text_color=COLORS['text'])
    result_label.pack(pady=25)
    
    # Enhanced game logic with animations
    def play_game(choice):
        computer_choice, result = game.play(choice)
        
        if result == 'wins':
            result_color = COLORS['accent']
            emoji = "🎉"
        elif result == 'losses':
            result_color = COLORS['danger']
            emoji = "💫"
        else:
            result_color = COLORS['warning']
            emoji = "🤝"
            
        result_text = f"{emoji} You chose {choice.upper()} | Computer chose {computer_choice.upper()} {emoji}"
        result_label.configure(text=result_text, text_color=result_color)
        
        # Animated score update
        stats = game.get_stats()
        score_text = f"🎮 Games: {stats['total_games']} | 🏆 Wins: {stats['wins']} | 📈 Win Rate: {stats['win_rate']}"
        score_label.configure(text=score_text)
        
        # Get game analytics data
        analytics_data = {
            'moves': game.get_move_distribution(),
            'trend': game.get_winrate_trend()
        }
        
        # Update charts if on dashboard
        if 'dashboard' in frames:
            charts_widget = charts_frame.winfo_children()[0]
            charts_widget.update_charts(analytics_data)
        
        update_stats_display()
    
    # Enhanced button styling
    button_frame = ctk.CTkFrame(game_container, fg_color="transparent")
    button_frame.grid(row=3, column=0, columnspan=3, pady=(30,40))
    
    button_style = {
        "width": 180,
        "height": 180,
        "corner_radius": 25,
        "border_width": 3,
        "border_color": COLORS['primary'],
        "hover_color": COLORS['primary'],
        "fg_color": COLORS['secondary'],
        "text_color": COLORS['primary'],
        "font": ctk.CTkFont(family="Arial", size=28, weight="bold")
    }
    
    choices = [
        ("🪨\nROCK", "rock"),
        ("📄\nPAPER", "paper"),
        ("✂️\nSCISSORS", "scissors")
    ]
    
    for i, (text, choice) in enumerate(choices):
        btn = ctk.CTkButton(button_frame, 
                           text=text,
                           command=lambda c=choice: play_game(c),
                           **button_style)
        btn.grid(row=0, column=i, padx=20)
        
        # Enhanced hover animations
        def on_enter(e, button=btn):
            button.configure(
                fg_color=COLORS['primary'],
                text_color=("white", "white"),
                border_width=0,
                scale_factor=1.1
            )
        
        def on_leave(e, button=btn):
            button.configure(
                fg_color=COLORS['secondary'],
                text_color=COLORS['primary'],
                border_width=3,
                scale_factor=1.0
            )
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

# Update the sidebar styling
sidebar_frame.configure(
    fg_color=COLORS['gradient_start'],
    corner_radius=0
)

# Update the appearance mode menu styling
appearance_mode_menu.configure(
    font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
    button_color=COLORS['primary'],
    button_hover_color=COLORS['accent'],
    corner_radius=10
)