import io
import matplotlib.pyplot as plt
import matplotlib as mpl
from aiogram.types import BufferedInputFile

# Set global dark theme styling for premium look
plt.style.use('dark_background')
mpl.rcParams.update({
    'axes.facecolor': '#1E1E2E',       # Catppuccin Mocha Base
    'figure.facecolor': '#1E1E2E',
    'axes.edgecolor': '#313244',
    'axes.grid': True,
    'grid.color': '#313244',
    'grid.alpha': 0.5,
    'text.color': '#CDD6F4',
    'axes.labelcolor': '#CDD6F4',
    'xtick.color': '#CDD6F4',
    'ytick.color': '#CDD6F4',
    'font.size': 10,
    'font.family': 'sans-serif'
})

COLORS = ['#89B4FA', '#F38BA8', '#A6E3A1', '#F9E2AF', '#CBA6F7', '#94E2D5', '#FAB387']

def _save_to_buffer() -> BufferedInputFile:
    """Helper to save the current matplotlib figure to a bytes buffer."""
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=120)
    plt.close()
    buf.seek(0)
    return BufferedInputFile(buf.getvalue(), filename="chart.png")

def generate_pie_chart(data: dict, title: str) -> BufferedInputFile:
    """Generates a pie chart for categorical data (e.g. expenses)."""
    labels = list(data.keys())
    values = list(data.values())
    
    fig, ax = plt.subplots(figsize=(6, 6))
    wedges, texts, autotexts = ax.pie(
        values, labels=labels, autopct='%1.1f%%',
        colors=COLORS, startangle=140, 
        wedgeprops=dict(width=0.4, edgecolor='#1E1E2E')
    )
    
    plt.setp(autotexts, size=9, weight="bold", color="#11111B")
    plt.setp(texts, size=11)
    
    ax.set_title(title, size=14, weight="bold", pad=20)
    return _save_to_buffer()

def generate_line_chart(dates: list, income: list, expenses: list, title: str) -> BufferedInputFile:
    """Generates a line chart tracking income vs expenses over time."""
    fig, ax = plt.subplots(figsize=(8, 4))
    
    ax.plot(dates, income, marker='o', linestyle='-', color='#A6E3A1', linewidth=2, label='Income')
    ax.plot(dates, expenses, marker='o', linestyle='-', color='#F38BA8', linewidth=2, label='Expenses')
    
    ax.fill_between(dates, income, color='#A6E3A1', alpha=0.1)
    ax.fill_between(dates, expenses, color='#F38BA8', alpha=0.1)
    
    ax.set_title(title, size=14, weight="bold", pad=15)
    ax.legend(facecolor='#1E1E2E', edgecolor='#313244')
    plt.xticks(rotation=45)
    return _save_to_buffer()

def generate_bar_chart(labels: list, values: list, title: str, horizontal: bool = False, color: str = '#89B4FA') -> BufferedInputFile:
    """Generates a generic bar chart."""
    fig, ax = plt.subplots(figsize=(8, 5))
    
    if horizontal:
        bars = ax.barh(labels, values, color=color, edgecolor='#1E1E2E')
        ax.invert_yaxis()  # top-down
    else:
        bars = ax.bar(labels, values, color=color, edgecolor='#1E1E2E')
        
    ax.set_title(title, size=14, weight="bold", pad=15)
    return _save_to_buffer()

def generate_gauge_dashboard(cpu: float, ram: float, disk: float) -> BufferedInputFile:
    """Generates a triple bar dashboard for system stats."""
    labels = ['CPU Usage', 'RAM Usage', 'Disk Space']
    values = [cpu, ram, disk]
    
    fig, ax = plt.subplots(figsize=(7, 3))
    
    # Background bars (100%)
    ax.barh(labels, [100, 100, 100], color='#313244', height=0.5)
    
    # Foreground bars based on usage
    colors = []
    for v in values:
        if v < 60: colors.append('#A6E3A1') # Green
        elif v < 85: colors.append('#F9E2AF') # Yellow
        else: colors.append('#F38BA8') # Red
        
    bars = ax.barh(labels, values, color=colors, height=0.5)
    ax.set_xlim(0, 100)
    ax.invert_yaxis()
    
    # Add text labels on bars
    for idx, rect in enumerate(bars):
        width = rect.get_width()
        ax.text(width + 2, rect.get_y() + rect.get_height()/2.0, f"{values[idx]:.1f}%", 
                ha='left', va='center', weight='bold')
                
    ax.set_title("System Resource Utilization", size=14, weight="bold", pad=15)
    ax.grid(False) # Turn off grid for gauges
    ax.set_xticks([]) # Remove x-axis
    
    return _save_to_buffer()

def generate_podium_chart(users: list, points: list) -> BufferedInputFile:
    """Generates a gamification podium chart."""
    fig, ax = plt.subplots(figsize=(8, 5))
    
    bars = ax.bar(users, points, color=['#F9E2AF', '#CBA6F7', '#89B4FA', '#94E2D5', '#A6E3A1'][:len(users)], edgecolor='#1E1E2E')
    
    # Add points on top of bars
    for rect in bars:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2.0, height + (max(points)*0.02), f"{int(height)} PTS", 
                ha='center', va='bottom', weight='bold')
                
    ax.set_title("Top 5 Gamification Leaderboard", size=14, weight="bold", pad=15)
    ax.grid(axis='x') # Only horizontal grid
    
    return _save_to_buffer()
