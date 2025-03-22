import customtkinter as ctk
from datetime import datetime, timedelta
import json
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv
from tkinter import filedialog, messagebox
import threading
import time
from plyer import notification
import calendar

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Modern UI color scheme
        self.colors = {
            "primary": "#2d60e8",
            "secondary": "#00a8e8",
            "accent": "#7289da",
            "background": "#1a1a1a",
            "surface": "#2b2b2b",
            "card": "#333333",
            "text": "#ffffff",
            "text_secondary": "#a0a0a0",  # Added missing color
            "warning": "#FFA500",
            "danger": "#ff4d4d"
        }
        
        # Update category styles with modern colors
        self.category_styles = {
            "Work": {"color": "#4e54c8", "icon": "💼"},
            "Personal": {"color": "#00b4d8", "icon": "👤"},
            "Shopping": {"color": "#48cae4", "icon": "🛒"},
            "Study": {"color": "#8338ec", "icon": "📚"},
            "Health": {"color": "#06d6a0", "icon": "🏥"},
            "Fitness": {"color": "#ff006e", "icon": "💪"}
        }
        
        # Configure window
        self.title("TaskMaster Pro")
        self.minsize(1000, 600)
        self.geometry("1200x800")
        
        # Make window resizable
        self.resizable(True, True)
        
        # Configure grid weights for responsiveness
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Initialize size variables with default values
        self.sidebar_width = 250
        self.window_width = 1000
        self.window_height = 800
        self.main_width = self.window_width - self.sidebar_width
        
        # Bind resize event
        self.bind("<Configure>", self.on_resize)
        
        # Set window title
        self.title("TaskMaster Pro")
        
        # Set window size
        self.geometry("1000x800")
        
        # Center window on screen
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 1000) // 2
        y = (screen_height - 800) // 2
        self.geometry(f"1000x600+{x}+{y}")
        
        # Prevent window resizing
        self.resizable(False, False)
        
        # Set the default color theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Initialize task data with priorities
        self.tasks = {category: [] for category in self.category_styles.keys()}
        self.priority_colors = {
            "High": "#ff4d4d",
            "Medium": "#ffd700",
            "Low": "#90EE90"
        }
        
        # Add sorting options
        self.sort_by = "date"  # default sort
        self.sort_reverse = False
        
        # Add reminder thread
        self.reminder_thread = threading.Thread(target=self.check_reminders, daemon=True)
        self.reminder_thread.start()
        
        # Create main frames first
        self.create_main_frames()
        
        # Then create other components
        self.create_sidebar()
        self.create_task_management_frame()
        self.create_content_frames()
        
        # Show default frame and start updates
        self.show_frame("home")
        self.after(1000, self.update_datetime)

    def update_dimensions(self):
        """Update dimensions based on window size"""
        self.window_width = self.winfo_width()
        self.window_height = self.winfo_height()
        self.main_width = self.window_width - self.sidebar_width

    def on_resize(self, event):
        """Handle window resize"""
        if event.widget == self:
            self.update_dimensions()
            self.update_layout()

    def update_layout(self):
        """Update layout based on new dimensions"""
        # Update main content frame size
        self.main_content.configure(width=self.main_width)
        
        # Update task display width
        if "tasks" in self.frames:
            self.frames["tasks"].configure(width=self.main_width - 40)  # 40 for padding
        
        # Update statistics panel
        if hasattr(self, 'canvas'):
            new_width = min(700, self.main_width - 60)
            self.canvas.get_tk_widget().configure(width=new_width)
            # Adjust figure size
            if hasattr(self, 'fig'):
                self.fig.set_size_inches(new_width/100, 4)
                self.fig.tight_layout()
                self.canvas.draw()

    def create_main_frames(self):
        # Configure grid weights for responsiveness
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create sidebar frame
        self.sidebar = ctk.CTkFrame(
            self,
            width=self.sidebar_width,
            height=self.window_height,
            corner_radius=0,
            fg_color="#1a1a1a"
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        
        # Create main content frame
        self.main_content = ctk.CTkFrame(
            self,
            width=self.main_width,
            height=self.window_height,
            fg_color="#2b2b2b"
        )
        self.main_content.grid(row=0, column=1, sticky="nsew")
        self.main_content.grid_columnconfigure(0, weight=1)
        self.main_content.grid_rowconfigure(1, weight=1)

    def create_sidebar(self):
        # Create modernized sidebar
        self.sidebar = ctk.CTkFrame(
            self,
            fg_color=self.colors["background"],
            corner_radius=0,
            width=250
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew", rowspan=2)
        self.sidebar.grid_propagate(False)
        
        # Modern logo design
        logo_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent"
        )
        logo_frame.grid(row=0, column=0, padx=20, pady=(30, 20), sticky="ew")
        
        ctk.CTkLabel(
            logo_frame,
            text="TaskMaster",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=self.colors["secondary"]
        ).grid(row=0, column=0)
        
        ctk.CTkLabel(
            logo_frame,
            text="Pro",
            font=ctk.CTkFont(size=16),
            text_color=self.colors["text_secondary"]
        ).grid(row=1, column=0)
        
        # Modern navigation buttons
        nav_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        nav_frame.grid(row=1, column=0, sticky="nsew", pady=(20, 0))
        
        self.nav_buttons = [
            {"text": "📊 Dashboard", "command": lambda: self.show_frame("home")},
            {"text": "📝 Tasks", "command": lambda: self.show_frame("tasks")},
            {"text": "📅 Calendar", "command": lambda: self.show_frame("calendar")},
            {"text": "⚙️ Settings", "command": lambda: self.show_frame("settings")}
        ]
        
        for i, btn in enumerate(self.nav_buttons):
            button = ctk.CTkButton(
                nav_frame,
                text=btn["text"],
                command=btn["command"],
                font=ctk.CTkFont(size=14),
                fg_color="transparent",
                text_color=self.colors["text"],
                hover_color=self.colors["surface"],
                anchor="w",
                height=45
            )
            button.grid(row=i, column=0, padx=10, pady=5, sticky="ew")
        
        # Bottom section
        bottom_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        bottom_frame.grid(row=2, column=0, sticky="ews", pady=20)
        
        self.theme_switch = ctk.CTkSwitch(
            bottom_frame,
            text="Dark Mode",
            command=self.toggle_theme,
            button_color=self.colors["secondary"],
            button_hover_color=self.colors["primary"]
        )
        self.theme_switch.grid(row=0, column=0, padx=20, pady=10)
        self.theme_switch.select()

    def create_task_management_frame(self):
        # Create modern task input area
        container = ctk.CTkFrame(
            self.main_content,
            fg_color=self.colors["surface"],
            corner_radius=15
        )
        container.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        container.grid_columnconfigure(0, weight=1)
        
        # Modern task input with icon
        input_frame = ctk.CTkFrame(container, fg_color="transparent")
        input_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=15)
        input_frame.grid_columnconfigure(1, weight=1)
        
        # Task input
        self.task_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="✍️ What needs to be done?",
            height=45,
            font=ctk.CTkFont(size=14)
        )
        self.task_entry.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        
        # Modern control panel
        control_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        control_frame.grid(row=1, column=1, sticky="ew", pady=(15, 0))
        control_frame.grid_columnconfigure(4, weight=1)
        
        # Category selection with icons
        categories = [f"{self.category_styles[cat]['icon']} {cat}" 
                     for cat in self.category_styles.keys()]
        self.category_combobox = ctk.CTkComboBox(
            control_frame,
            values=categories,
            width=150,
            height=40
        )
        self.category_combobox.grid(row=0, column=0, padx=10, pady=10)
        
        # Priority selection
        self.priority_combobox = ctk.CTkComboBox(
            control_frame,
            values=["High", "Medium", "Low"],
            width=100,
            height=40
        )
        self.priority_combobox.grid(row=0, column=1, padx=10, pady=10)
        
        # Custom date selection frame
        date_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        date_frame.grid(row=0, column=2, padx=10, pady=10)
        
        # Day selection
        self.day_combo = ctk.CTkComboBox(
            date_frame,
            values=[str(i).zfill(2) for i in range(1, 32)],
            width=60,
            height=40
        )
        self.day_combo.grid(row=0, column=0, padx=2)
        self.day_combo.set(datetime.now().strftime("%d"))
        
        # Month selection
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                 "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        self.month_combo = ctk.CTkComboBox(
            date_frame,
            values=months,
            width=70,
            height=40
        )
        self.month_combo.grid(row=0, column=1, padx=2)
        self.month_combo.set(datetime.now().strftime("%b"))
        
        # Year selection
        current_year = datetime.now().year
        years = [str(i) for i in range(current_year, current_year + 5)]
        self.year_combo = ctk.CTkComboBox(
            date_frame,
            values=years,
            width=70,
            height=40
        )
        self.year_combo.grid(row=0, column=2, padx=2)
        self.year_combo.set(str(current_year))
        
        # Add button
        add_button = ctk.CTkButton(
            control_frame,
            text="Add Task",
            command=self.add_task,
            width=100,
            height=40,
            fg_color="#00a8e8",
            hover_color="#0086ba"
        )
        add_button.grid(row=0, column=3, padx=10, pady=10)
        
        # Add sort options
        sort_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        sort_frame.grid(row=1, column=0, columnspan=4, pady=5)
        
        ctk.CTkLabel(sort_frame, text="Sort by:").grid(row=0, column=0, padx=5)
        
        self.sort_combobox = ctk.CTkComboBox(
            sort_frame,
            values=["Date", "Priority", "Due Date"],
            command=self.sort_tasks,
            width=100
        )
        self.sort_combobox.grid(row=0, column=1, padx=5)
        
        # Add export/import buttons
        ctk.CTkButton(
            sort_frame,
            text="Export Tasks",
            command=self.export_tasks,
            width=100
        ).grid(row=0, column=2, padx=5)
        
        ctk.CTkButton(
            sort_frame,
            text="Import Tasks",
            command=self.import_tasks,
            width=100
        ).grid(row=0, column=3, padx=5)

    def create_content_frames(self):
        """Create and store all main content frames"""
        self.frames = {}
        
        # Create frames
        self.frames["home"] = self.create_home_frame()
        self.frames["tasks"] = self.create_tasks_frame()
        self.frames["calendar"] = self.create_calendar_frame()
        self.frames["settings"] = self.create_settings_frame()

    def create_tasks_frame(self):
        """Create the tasks view frame"""
        frame = ctk.CTkScrollableFrame(
            self.main_content,
            fg_color="#2b2b2b",
            width=700,
            height=500
        )
        frame.grid_columnconfigure(0, weight=1)
        
        # Add task management controls
        self.create_task_management_frame()
        
        return frame

    def create_home_frame(self):
        frame = ctk.CTkFrame(self.main_content)
        frame.grid_columnconfigure(0, weight=1)
        
        # Welcome section
        welcome_frame = ctk.CTkFrame(frame, fg_color="transparent")
        welcome_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        
        ctk.CTkLabel(
            welcome_frame,
            text="Welcome to TaskMaster Pro",
            font=ctk.CTkFont(size=24, weight="bold")
        ).grid(row=0, column=0, sticky="w")
        
        # Quick Actions
        quick_actions = ctk.CTkFrame(frame)
        quick_actions.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        ctk.CTkLabel(
            quick_actions,
            text="Quick Actions",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        actions = [
            ("Add New Task", lambda: self.show_frame("tasks")),
            ("View Calendar", lambda: self.show_frame("calendar")),
            ("Export Tasks", self.export_tasks)
        ]
        
        for i, (text, command) in enumerate(actions):
            ctk.CTkButton(
                quick_actions,
                text=text,
                command=command,
                width=150
            ).grid(row=1, column=i, padx=10, pady=10)
        
        # Statistics Panel
        self.create_statistics_panel(frame)
        
        return frame

    def create_calendar_frame(self):
        frame = ctk.CTkScrollableFrame(self.main_content)
        frame.grid_columnconfigure(0, weight=1)
        
        # Navigation buttons for months
        nav_frame = ctk.CTkFrame(frame)
        nav_frame.grid(row=0, column=0, padx=20, pady=(10, 0), sticky="ew")
        
        prev_month = ctk.CTkButton(
            nav_frame,
            text="◀",
            width=30,
            command=self.prev_month
        )
        prev_month.grid(row=0, column=0, padx=5)
        
        self.current_date = datetime.now()
        self.month_label = ctk.CTkLabel(
            nav_frame,
            text=self.current_date.strftime("%B %Y"),
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.month_label.grid(row=0, column=1, padx=20)
        
        next_month = ctk.CTkButton(
            nav_frame,
            text="▶",
            width=30,
            command=self.next_month
        )
        next_month.grid(row=0, column=2, padx=5)
        
        # Calendar grid
        self.calendar_grid = ctk.CTkFrame(frame)
        self.calendar_grid.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        # Initialize calendar
        self.update_calendar()
        
        return frame

    def update_calendar(self):
        # Clear existing calendar grid
        for widget in self.calendar_grid.winfo_children():
            widget.destroy()
        
        # Update month label
        self.month_label.configure(text=self.current_date.strftime("%B %Y"))
        
        # Days of week header
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for i, day in enumerate(days):
            ctk.CTkLabel(
                self.calendar_grid,
                text=day,
                font=ctk.CTkFont(weight="bold")
            ).grid(row=0, column=i, padx=5, pady=5)
        
        # Get calendar for current month
        cal = calendar.monthcalendar(self.current_date.year, self.current_date.month)
        
        # Add calendar days
        for week_num, week in enumerate(cal, 1):
            for day_num, day in enumerate(week):
                if day != 0:
                    day_frame = ctk.CTkFrame(self.calendar_grid)
                    day_frame.grid(row=week_num, column=day_num, padx=2, pady=2, sticky="nsew")
                    day_frame.grid_columnconfigure(0, weight=1)
                    day_frame.grid_rowconfigure(1, weight=1)
                    
                    # Day number
                    ctk.CTkLabel(
                        day_frame,
                        text=str(day),
                        font=("Helvetica", 12)
                    ).grid(row=0, column=0, padx=5, pady=2)
                    
                    # Check for tasks
                    date_str = f"{self.current_date.year}-{str(self.current_date.month).zfill(2)}-{str(day).zfill(2)}"
                    tasks_today = self.get_tasks_for_date(date_str)
                    
                    if tasks_today:
                        task_label = ctk.CTkLabel(
                            day_frame,
                            text=f"{len(tasks_today)} tasks",
                            text_color="#00a8e8",
                            font=("Helvetica", 10)
                        )
                        task_label.grid(row=1, column=0, padx=5, pady=2)
                        
                        # Make the day frame clickable to show tasks
                        day_frame.bind("<Button-1>", lambda e, d=date_str: self.show_day_tasks(d))

    def next_month(self):
        if self.current_date.month == 12:
            self.current_date = self.current_date.replace(year=self.current_date.year + 1, month=1)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month + 1)
        self.update_calendar()

    def prev_month(self):
        if self.current_date.month == 1:
            self.current_date = self.current_date.replace(year=self.current_date.year - 1, month=12)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month - 1)
        self.update_calendar()

    def show_day_tasks(self, date_str):
        tasks = self.get_tasks_for_date(date_str)
        if not tasks:
            return
        
        task_window = ctk.CTkToplevel(self)
        task_window.title(f"Tasks for {date_str}")
        task_window.geometry("400x300")
        
        # Create scrollable frame for tasks
        task_frame = ctk.CTkScrollableFrame(task_window, width=380, height=250)
        task_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        for task in tasks:
            task_item = ctk.CTkFrame(task_frame)
            task_item.pack(pady=5, padx=5, fill="x")
            
            ctk.CTkLabel(
                task_item,
                text=f"{task['text']} ({task['priority']})",
                font=("Helvetica", 12)
            ).pack(side="left", padx=5)
            
            status = "✓" if task["completed"] else "○"
            ctk.CTkLabel(
                task_item,
                text=status,
                text_color="#00ff00" if task["completed"] else "#ff0000"
            ).pack(side="right", padx=5)

    def create_settings_frame(self):
        frame = ctk.CTkFrame(self.main_content)
        frame.grid_columnconfigure(0, weight=1)
        
        # Settings header
        ctk.CTkLabel(
            frame,
            text="Settings",
            font=ctk.CTkFont(size=24, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=20, sticky="w")
        
        # Settings sections
        sections = [
            ("Appearance", [
                ("Theme Mode", self.theme_switch),
                ("Color Theme", self.create_color_theme_selector())
            ]),
            ("Notifications", [
                ("Enable Reminders", self.create_reminder_toggle()),
                ("Reminder Time", self.create_reminder_time_selector())
            ]),
            ("Data Management", [
                ("Export Data", self.create_export_button),
                ("Import Data", self.create_import_button),
                ("Clear All Data", self.create_clear_button)
            ])
        ]
        
        for i, (section_name, settings) in enumerate(sections):
            section_frame = ctk.CTkFrame(frame)
            section_frame.grid(row=i+1, column=0, padx=20, pady=10, sticky="ew")
            
            ctk.CTkLabel(
                section_frame,
                text=section_name,
                font=ctk.CTkFont(size=16, weight="bold")
            ).grid(row=0, column=0, padx=10, pady=5, sticky="w")
            
            for j, (setting_name, widget) in enumerate(settings):
                ctk.CTkLabel(
                    section_frame,
                    text=setting_name
                ).grid(row=j+1, column=0, padx=10, pady=5, sticky="w")
                
                if callable(widget):
                    widget(section_frame).grid(row=j+1, column=1, padx=10, pady=5)
                else:
                    widget.grid(row=j+1, column=1, padx=10, pady=5)
        
        return frame

    def create_export_button(self, master):
        return ctk.CTkButton(
            master=master,
            text="Export",
            command=self.export_tasks,
            width=100
        )

    def create_import_button(self, master):
        return ctk.CTkButton(
            master=master,
            text="Import",
            command=self.import_tasks,
            width=100
        )

    def create_clear_button(self, master):
        return ctk.CTkButton(
            master=master,
            text="Clear Data",
            command=self.clear_all_data,
            width=100,
            fg_color="#ff4d4d",
            hover_color="#ff3333"
        )

    def update_calendar_grid(self, calendar_grid):
        # Get current month's calendar
        now = datetime.now()
        cal = calendar.monthcalendar(now.year, now.month)
        
        # Add calendar days with task indicators
        for week_num, week in enumerate(cal):
            for day_num, day in enumerate(week):
                if day != 0:
                    day_frame = ctk.CTkFrame(calendar_grid)
                    day_frame.grid(row=week_num+1, column=day_num, padx=2, pady=2, sticky="nsew")
                    
                    # Day number
                    ctk.CTkLabel(
                        day_frame,
                        text=str(day)
                    ).grid(row=0, column=0, padx=5, pady=2)
                    
                    # Check for tasks on this day
                    date_str = f"{now.year}-{str(now.month).zfill(2)}-{str(day).zfill(2)}"
                    tasks_today = self.get_tasks_for_date(date_str)
                    
                    if tasks_today:
                        ctk.CTkLabel(
                            day_frame,
                            text=f"{len(tasks_today)} tasks",
                            text_color="#00a8e8"
                        ).grid(row=1, column=0, padx=5, pady=2)

    def get_tasks_for_date(self, date_str):
        tasks_on_date = []
        for category in self.tasks:
            tasks_on_date.extend([
                task for task in self.tasks[category]
                if task["due_date"] == date_str
            ])
        return tasks_on_date

    def create_color_theme_selector(self):
        return ctk.CTkComboBox(
            master=None,
            values=["Blue", "Dark-Blue", "Green"],
            command=self.change_color_theme
        )

    def create_reminder_toggle(self):
        return ctk.CTkSwitch(
            master=None,
            text="",
            command=self.toggle_reminders
        )

    def create_reminder_time_selector(self):
        return ctk.CTkComboBox(
            master=None,
            values=["1 hour", "3 hours", "6 hours", "12 hours", "24 hours"]
        )

    def change_color_theme(self, theme):
        ctk.set_default_color_theme(theme.lower())

    def toggle_reminders(self):
        # Toggle reminder functionality
        pass

    def clear_all_data(self):
        if self.show_confirmation("Are you sure you want to clear all data?"):
            self.tasks = {category: [] for category in self.category_styles.keys()}
            self.update_task_display()
            self.update_statistics()
            self.update_statistics_charts(self.ax1, self.ax2)

    def show_confirmation(self, message):
        return messagebox.askyesno("Confirm", message)

    def create_statistics_panel(self, parent_frame):
        stats_frame = ctk.CTkFrame(parent_frame, fg_color="#333333")
        stats_frame.grid(row=1, column=0, padx=20, pady=20, sticky="ew")
        stats_frame.grid_columnconfigure(0, weight=1)
        
        # Create figure with safe default size
        plt.style.use('dark_background')
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4), dpi=100)
        fig.patch.set_facecolor('#333333')
        
        # Add padding to prevent text cutoff
        fig.set_tight_layout(True)
        
        self.canvas = FigureCanvasTkAgg(fig, master=stats_frame)
        canvas_widget = self.canvas.get_tk_widget()
        canvas_widget.configure(width=min(700, self.main_width - 60))
        canvas_widget.grid(row=1, column=0, columnspan=3, padx=10, pady=10)
        
        # Add text statistics
        stats_text = ctk.CTkFrame(stats_frame, fg_color="transparent")
        stats_text.grid(row=0, column=0, columnspan=3, padx=10, pady=10)
        
        self.stats_labels = {
            "total": ctk.CTkLabel(stats_text, text="Total Tasks: 0"),
            "completed": ctk.CTkLabel(stats_text, text="Completed: 0"),
            "pending": ctk.CTkLabel(stats_text, text="Pending: 0")
        }
        
        for i, label in enumerate(self.stats_labels.values()):
            label.grid(row=0, column=i, padx=20)
        
        # Store figure and axes references
        self.fig = fig
        self.ax1 = ax1
        self.ax2 = ax2
        
        # Initialize charts
        self.update_statistics_charts(ax1, ax2)

    def update_statistics_charts(self, ax1, ax2):
        # Clear previous charts
        ax1.clear()
        ax2.clear()
        
        # Task distribution by category
        categories = list(self.tasks.keys())
        task_counts = [len(self.tasks[cat]) for cat in categories]
        
        # Bar chart
        if sum(task_counts) > 0:
            ax1.bar(categories, task_counts, color=[self.category_styles[cat]["color"] for cat in categories])
        else:
            ax1.text(0.5, 0.5, "No tasks yet", ha='center', va='center')
            
        ax1.set_title("Tasks by Category")
        ax1.tick_params(axis='x', rotation=45)
        
        # Pie chart
        completed = sum(task["completed"] for tasks in self.tasks.values() for task in tasks)
        total = sum(len(tasks) for tasks in self.tasks.values())
        pending = total - completed
        
        if total > 0:
            ax2.pie([completed, pending], 
                   labels=['Completed', 'Pending'],
                   colors=['#4CAF50', '#FFA500'],
                   autopct='%1.1f%%')
        else:
            ax2.text(0.5, 0.5, "No tasks yet", ha='center', va='center')
            
        ax2.set_title("Task Completion Status")
        
        # Adjust layout to prevent text cutoff
        plt.tight_layout()
        self.canvas.draw()

    def add_task(self):
        task_text = self.task_entry.get().strip()
        category = self.category_combobox.get().split()[1]
        priority = self.priority_combobox.get()
        
        if not task_text:
            self.show_error("Task text cannot be empty!")
            return
        
        try:
            # Convert month abbreviation to number
            months = {
                "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
                "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
                "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
            }
            
            due_date = f"{self.year_combo.get()}-{months[self.month_combo.get()]}-{self.day_combo.get()}"
            
            task = {
                "text": task_text,
                "completed": False,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "priority": priority,
                "due_date": due_date,
                "category": category,
                "id": datetime.now().strftime("%Y%m%d%H%M%S")
            }
            self.tasks[category].append(task)
            self.task_entry.delete(0, 'end')
            self.update_task_display()
            self.update_statistics_charts(self.canvas.figure.axes[0], self.canvas.figure.axes[1])
            self.update_statistics()
        except Exception as e:
            self.show_error(f"Error adding task: {str(e)}")

    def show_error(self, message):
        error_window = ctk.CTkToplevel(self)
        error_window.title("Error")
        error_window.geometry("300x150")
        
        ctk.CTkLabel(
            error_window,
            text=message,
            wraplength=250
        ).pack(pady=20)
        
        ctk.CTkButton(
            error_window,
            text="OK",
            command=error_window.destroy
        ).pack(pady=10)

    def toggle_task(self, task_id):
        for category in self.tasks:
            for task in self.tasks[category]:
                if task.get('id') == task_id:
                    task['completed'] = not task.get('completed', False)
                    self.update_task_display()
                    self.update_statistics()
                    self.update_statistics_charts(self.canvas.figure.axes[0], self.canvas.figure.axes[1])
                    return

    def update_datetime(self):
        current_time = datetime.now().strftime("%B %d, %Y\n%H:%M:%S")
        self.datetime_label.configure(text=current_time)
        self.after(1000, self.update_datetime)
    
    def update_statistics(self):
        total = sum(len(tasks) for tasks in self.tasks.values())
        completed = sum(
            sum(1 for task in tasks if task["completed"])
            for tasks in self.tasks.values()
        )
        
        self.stats_labels["total"].configure(text=f"Total Tasks: {total}")
        self.stats_labels["completed"].configure(text=f"Completed: {completed}")
        self.stats_labels["pending"].configure(text=f"Pending: {total - completed}")
    
    def update_task_display(self, search_term=""):
        # Modern task card design
        for widget in self.frames["tasks"].winfo_children():
            widget.destroy()
        
        container = ctk.CTkFrame(
            self.frames["tasks"],
            fg_color="transparent"
        )
        container.grid(row=0, column=0, sticky="nsew")
        container.grid_columnconfigure(0, weight=1)
        
        for category, task_list in self.tasks.items():
            if not task_list and not search_term:
                continue
            
            # Modern category header
            header = ctk.CTkFrame(
                container,
                fg_color=self.colors["surface"],
                corner_radius=10
            )
            header.grid(row=len(header.winfo_children()), 
                       column=0, padx=10, pady=5, sticky="ew")
            
            ctk.CTkLabel(
                header,
                text=f"{self.category_styles[category]['icon']} {category}",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=self.category_styles[category]["color"]
            ).grid(row=0, column=0, padx=15, pady=10, sticky="w")
            
            # Modern task cards
            for task in task_list:
                if search_term and search_term not in task["text"].lower():
                    continue
                
                self.create_task_card(container, task)

    def create_task_card(self, parent, task):
        # Modern task card design
        card = ctk.CTkFrame(
            parent,
            fg_color=self.colors["surface"],
            corner_radius=10
        )
        card.grid(row=len(parent.winfo_children()), 
                 column=0, padx=10, pady=5, sticky="ew")
        card.grid_columnconfigure(1, weight=1)
        
        # Task checkbox and text
        ctk.CTkCheckBox(
            card,
            text=task["text"],
            command=lambda t=task["id"]: self.toggle_task(t),
            checkbox_height=22,
            checkbox_width=22,
            corner_radius=5,
            border_width=2,
            checkbox_color=self.colors["secondary"],
            hover_color=self.colors["primary"],
            font=ctk.CTkFont(size=13)
        ).grid(row=0, column=0, padx=15, pady=12, sticky="w")
        
        # Task metadata with modern design
        meta_frame = ctk.CTkFrame(card, fg_color="transparent")
        meta_frame.grid(row=0, column=2, padx=15, pady=10, sticky="e")
        
        # Add modern metadata display and action buttons
        # ...rest of task card implementation...

    def show_frame(self, frame_name):
        """Show the selected frame and hide others"""
        # Hide all frames
        for frame in self.frames.values():
            if frame:  # Check if frame exists
                frame.grid_remove()
        
        # Show selected frame
        if frame_name in self.frames and self.frames[frame_name]:
            self.frames[frame_name].grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
            
            # Update task display if showing tasks frame
            if frame_name == "tasks":
                self.update_task_display()
    
    def toggle_theme(self):
        current_theme = ctk.get_appearance_mode()
        new_theme = "light" if current_theme == "dark" else "dark"
        ctk.set_appearance_mode(new_theme)

    def search_tasks(self, *args):
        search_term = self.search_var.get().lower()
        self.update_task_display(search_term)

    def edit_task(self, task):
        edit_window = ctk.CTkToplevel(self)
        edit_window.title("Edit Task")
        edit_window.geometry("400x500")
        
        # Task text
        ctk.CTkLabel(edit_window, text="Task:").pack(pady=5)
        text_entry = ctk.CTkEntry(edit_window, width=300)
        text_entry.insert(0, task["text"])
        text_entry.pack(pady=5)
        
        # Notes
        ctk.CTkLabel(edit_window, text="Notes:").pack(pady=5)
        notes_text = ctk.CTkTextbox(edit_window, width=300, height=100)
        notes_text.insert("1.0", task.get("notes", ""))
        notes_text.pack(pady=5)
        
        def save_changes():
            task["text"] = text_entry.get()
            task["notes"] = notes_text.get("1.0", "end-1c")
            self.update_task_display()
            edit_window.destroy()
        
        ctk.CTkButton(
            edit_window,
            text="Save Changes",
            command=save_changes
        ).pack(pady=10)

    def delete_task(self, task):
        for category in self.tasks:
            if task in self.tasks[category]:
                self.tasks[category].remove(task)
                self.update_task_display()
                self.update_statistics()
                self.update_statistics_charts(self.ax1, self.ax2)
                return

    def show_notes(self, task):
        notes_window = ctk.CTkToplevel(self)
        notes_window.title("Task Notes")
        notes_window.geometry("400x300")
        
        notes_text = ctk.CTkTextbox(notes_window, width=380, height=250)
        notes_text.insert("1.0", task.get("notes", ""))
        notes_text.pack(pady=10, padx=10)
        
        def save_notes():
            task["notes"] = notes_text.get("1.0", "end-1c")
            notes_window.destroy()
        
        ctk.CTkButton(
            notes_window,
            text="Save Notes",
            command=save_notes
        ).pack(pady=5)

    def sort_tasks(self, option=None):
        self.sort_by = option.lower() if option else self.sort_by
        
        for category in self.tasks:
            if self.sort_by == "date":
                self.tasks[category].sort(key=lambda x: x["date"], reverse=self.sort_reverse)
            elif self.sort_by == "priority":
                priority_order = {"High": 0, "Medium": 1, "Low": 2}
                self.tasks[category].sort(
                    key=lambda x: priority_order[x["priority"]],
                    reverse=self.sort_reverse
                )
            elif self.sort_by == "due date":
                self.tasks[category].sort(key=lambda x: x["due_date"], reverse=self.sort_reverse)
        
        self.update_task_display()

    def export_tasks(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            with open(filename, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Category", "Text", "Priority", "Due Date", "Notes", "Completed"])
                for category, tasks in self.tasks.items():
                    for task in tasks:
                        writer.writerow([
                            category,
                            task["text"],
                            task["priority"],
                            task["due_date"],
                            task.get("notes", ""),
                            task["completed"]
                        ])

    def import_tasks(self):
        filename = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            with open(filename, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    task = {
                        "text": row["Text"],
                        "completed": row["Completed"].lower() == "true",
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "priority": row["Priority"],
                        "due_date": row["Due Date"],
                        "notes": row["Notes"],
                        "id": datetime.now().strftime("%Y%m%d%H%M%S")
                    }
                    self.tasks[row["Category"]].append(task)
            self.update_task_display()
            self.update_statistics()
            self.update_statistics_charts(self.ax1, self.ax2)

    def check_reminders(self):
        while True:
            current_date = datetime.now().strftime("%Y-%m-%d")
            for category, tasks in self.tasks.items():
                for task in tasks:
                    if (not task["completed"] and 
                        task["due_date"] == current_date):
                        notification.notify(
                            title="Task Due Today!",
                            message=f"{task['text']} is due today!",
                            timeout=10
                        )
            time.sleep(3600)  # Check every hour

if __name__ == "__main__":
    app = App()
    app.mainloop()
