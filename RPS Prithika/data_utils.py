import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def create_charts(parent_frame):
    # Create a figure with a dark background
    fig = plt.figure(figsize=(12, 4), facecolor='#2B2B2B')
    
    # Add subplots
    moves_ax = plt.subplot(121)
    trend_ax = plt.subplot(122)
    
    # Sample data (will be replaced by actual game data)
    moves_data = {'Rock': 0, 'Paper': 0, 'Scissors': 0}
    trend_data = [0]  # Win rate over time
    
    def update_charts(game_data):
        # Clear previous plots
        moves_ax.clear()
        trend_ax.clear()
        
        # Update moves distribution chart
        moves = game_data['moves']
        moves_ax.pie(moves.values(), labels=moves.keys(), autopct='%1.1f%%',
                    colors=['#1F538D', '#3B8ED0', '#28A745'])
        moves_ax.set_title('Move Distribution', color='white', pad=20)
        
        # Update win rate trend
        trend = game_data['trend']
        trend_ax.plot(trend, color='#3B8ED0', linewidth=2)
        trend_ax.set_title('Win Rate Trend', color='white', pad=20)
        trend_ax.set_ylim(0, 100)
        trend_ax.grid(True, alpha=0.2)
        trend_ax.set_facecolor('#2B2B2B')
        
        # Style adjustments
        for ax in [moves_ax, trend_ax]:
            ax.set_facecolor('#2B2B2B')
            
        fig.tight_layout()
        canvas.draw()
    
    # Create canvas
    canvas = FigureCanvasTkAgg(fig, master=parent_frame)
    widget = canvas.get_tk_widget()
    
    # Store update function as attribute
    widget.update_charts = update_charts
    
    return widget
