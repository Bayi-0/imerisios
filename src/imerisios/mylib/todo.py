import toga
from toga.style import Pack
from toga.constants import COLUMN, ROW, Direction
from datetime import date, timedelta
import sqlite3 as sql
from imerisios.mylib.tools import length_check, get_connection, close_connection, get_ranges, change_range, set_range


class ToDo:
    def __init__(self, app, db_path):
        self.app = app
        self.db_path = db_path

        self.widgets_dict = {"tasks":{}}
        self.data = {"task types": ["daily", "weekly", "monthly", "yearly"], "task tiers": ["routine", "challenging", "significant", "momentous"]}
        self.type_dates_dict = {}
        self.task_history_load = {"routine", "challenging", "significant", "momentous"}
        self.tt_change = self.dd_change = True

    
    def get_add_task_box(self):
        label = toga.Label(
            "Add a New Task", 
            style=Pack(flex=0.09, padding=14, text_align="center", font_weight="bold", font_size=18, color="#EBF6F7"))
        
        input_label = toga.Label(
            "Task:", 
            style=Pack(padding=(18,18,0), font_size=14, color="#EBF6F7"))
        self.add_input = toga.TextInput(
            id="task_add input 80",
            placeholder="(no more than 80 characters)",
            on_change=length_check, 
            style=Pack(padding=(0,18,18), height=44, font_size=12, color="#EBF6F7", background_color="#27221F"))
        
        tier_label = toga.Label(
            "Tier:", 
            style=Pack(padding=(18,18,0), font_size=14, color="#EBF6F7"))
        self.add_tier = toga.Selection(
            items=["Routine", "Challenging", "Significant", "Momentous"],
            style=Pack(padding=(0,18,18), height=44))
        
        urgency_label = toga.Label(
            "Urgency:", 
            style=Pack(padding=(18,18,0), font_size=14, color="#EBF6F7"))
        self.add_urgency = toga.Selection(
            items=["Low", "Medium", "High"],
            style=Pack(padding=(0,18,18), height=44))
        
        type_label = toga.Label(
            "Type:", 
            style=Pack(padding=(18,18,0), font_size=14, color="#EBF6F7"))
        self.add_type = toga.Selection(
            id="add task type", 
            items=["Daily", "Weekly", "Monthly", "Yearly"], 
            on_change=self.task_type_change,
            style=Pack(padding=(0,18,18), height=44))
        self.widgets_dict["add task type"] = self.add_type

        duedate_label = toga.Label(
            "Due:", 
            style=Pack(padding=(18,18,0), font_size=14, color="#EBF6F7"))
        self.add_duedate = toga.DateInput(
            id="add task duedate", 
            min=date.today(), 
            max=date.today(), 
            on_change=self.duedate_change,
            style=Pack(padding=(0,18), color="#EBF6F7"))
        self.widgets_dict["add task duedate"] = self.add_duedate

        reset_button = toga.Button(
            "Reset type & date", 
            id="add task reset",
            on_press=self.reset_type_date, 
            style=Pack(padding=(4,4,14), height=44, font_size=13, color="#EBF6F7", background_color="#27221F"))
        
        top_box = toga.Box(
            children=[
                input_label, self.add_input, toga.Divider(style=Pack(padding=(0,80), background_color="#27221F")),
                tier_label, self.add_tier, toga.Divider(style=Pack(padding=(0,80), background_color="#27221F")),
                urgency_label, self.add_urgency, toga.Divider(style=Pack(padding=(0,80), background_color="#27221F")),
                type_label, self.add_type, toga.Divider(style=Pack(padding=(0,80), background_color="#27221F")),
                duedate_label, self.add_duedate, reset_button
            ], 
            style=Pack(direction=COLUMN, flex=0.73))
        top_container = toga.ScrollContainer(content=top_box, horizontal=False, vertical=False, style=Pack(flex=0.73))
        
        button = toga.Button(
            "Add", on_press=self.add_task, 
            style=Pack(height=120, padding=11, font_size=24, color="#EBF6F7", background_color="#27221F"))
        bottom_box = toga.Box(children=[button], style=Pack(direction=COLUMN, flex=0.18))

        add_box = toga.Box(
            children=[
                label, toga.Divider(style=Pack(background_color="#27221F")), 
                top_container, toga.Divider(style=Pack(background_color="#27221F")), 
                bottom_box
            ], 
            style=Pack(direction=COLUMN, background_color="#393432"))
        
        return add_box


    def get_edit_task_box(self):
        label = toga.Label(
            "Edit the Task", 
            style=Pack(flex=0.1, padding=14, text_align="center", font_weight="bold", font_size=18, color="#EBF6F7"))
        
        input_label = toga.Label(
            "Task:", 
            style=Pack(padding=(18,18,0), font_size=14, color="#EBF6F7"))
        self.edit_input = toga.TextInput(
            id="task_edit input 80",
            placeholder="(no more than 80 characters)",
            on_change=length_check, 
            style=Pack(padding=(0,18,18), height=44, font_size=12, color="#EBF6F7", background_color="#27221F"))
        
        tier_label = toga.Label(
            "Tier:", 
            style=Pack(padding=(18,18,0), font_size=14, color="#EBF6F7"))
        self.edit_tier = toga.Selection(
            items=["Routine", "Challenging", "Significant", "Momentous"],
            style=Pack(padding=(0,18,18), height=44))
            
        urgency_label = toga.Label(
            "Urgency:", 
            style=Pack(padding=(18,18,0), font_size=14, color="#EBF6F7"))
        self.edit_urgency = toga.Selection(
            items=["Low", "Medium", "High"],
            style=Pack(padding=(0,18,18), height=44))
        
        type_label = toga.Label(
            "Type:", 
            style=Pack(padding=(18,18,0), font_size=14, color="#EBF6F7"))
        self.edit_type = toga.Selection(
            id="edit task type", 
            items=["Daily", "Weekly", "Monthly", "Yearly"], 
            on_change=self.task_type_change,
            style=Pack(padding=(0,18,18), height=44))
        self.widgets_dict["edit task type"] = self.edit_type

        duedate_label = toga.Label(
            "Due:", 
            style=Pack(padding=(18,18,0), font_size=14, color="#EBF6F7"))
        self.edit_duedate = toga.DateInput(
            id="edit task duedate", 
            on_change=self.duedate_change, 
            style=Pack(padding=(0,18), color="#EBF6F7"))
        self.widgets_dict["edit task duedate"] = self.edit_duedate

        reset_button = toga.Button(
            "Reset type & date", 
            id="edit task reset", 
            on_press=self.reset_type_date, 
            style=Pack(padding=(4,4,14), height=44, font_size=13, color="#EBF6F7", background_color="#27221F"))

        top_box = self.box = toga.Box(
            children=[
                input_label, self.edit_input, toga.Divider(style=Pack(padding=(0,80), background_color="#27221F")), 
                tier_label, self.edit_tier, toga.Divider(style=Pack(padding=(0,80), background_color="#27221F")), 
                urgency_label, self.edit_urgency, toga.Divider(style=Pack(padding=(0,80), background_color="#27221F")), 
                type_label, self.edit_type, toga.Divider(style=Pack(padding=(0,80), background_color="#27221F")), 
                duedate_label, self.edit_duedate, reset_button
            ], 
            style=Pack(direction=COLUMN, flex=0.73))
        top_container = toga.ScrollContainer(content=top_box, horizontal=False, vertical=False, style=Pack(flex=0.73))

        remove_button = toga.Button(
            "Remove", on_press=self.remove_task_dialog, 
            style=Pack(flex=0.5, height=120, padding=(11,4,11,11), font_size=24, color="#EBF6F7", background_color="#27221F"))
        save_button = toga.Button(
            "Save", on_press=self.save_task, 
            style=Pack(flex=0.5, height=120, padding=(11,11,11,4), font_size=24, color="#EBF6F7", background_color="#27221F"))
        bottom_box = toga.Box(
            children=[remove_button, save_button], 
            style=Pack(direction=ROW, flex=0.18))
        
        edit_box = toga.Box(
            children=[
                label, toga.Divider(style=Pack(background_color="#27221F")), 
                top_container, toga.Divider(style=Pack(background_color="#27221F")), 
                bottom_box
            ], 
            style=Pack(direction=COLUMN, background_color="#393432"))
        
        return edit_box

    def get_list_box(self):
        # daily box
        daily_label = toga.Label(
            "To-Do List", 
            style=Pack(padding=(14,20), text_align="center", font_weight="bold", font_size=20, color="#EBF6F7"))
        
        daily_count_box = toga.Box(id="daily count box", style=Pack(direction=ROW))
        self.widgets_dict["daily count box"] = daily_count_box

        back_button = toga.Button(
            "<", id="daily back button",
            on_press=self.change_range, 
            style=Pack(flex=0.2, padding=4, height=44, font_size=13, color="#EBF6F7", background_color="#27221F")
        )
        next_button = toga.Button(
            ">", id="daily next button",
            on_press=self.change_range, 
            style=Pack(flex=0.2, padding=4, height=44, font_size=13, color="#EBF6F7", background_color="#27221F")
        )
        self.daily_range = toga.Selection(
            id="daily range", 
            on_change=self.load_tasks,
            style=Pack(flex=0.6, padding=4, height=44))
        self.widgets_dict["daily range"] = self.daily_range
        daily_range_box = toga.Box(
            children=[back_button, self.daily_range, next_button],
            style=Pack(direction=ROW))
        
        daily_task_box = toga.Box(id="daily task box", style=Pack(direction=COLUMN))
        self.widgets_dict["daily task box"] = daily_task_box
        daily_task_container = toga.ScrollContainer(content=daily_task_box, horizontal=False, style=Pack(flex=0.9))
        self.widgets_dict["daily task container"] = daily_task_container

        daily_box = toga.Box(
            children=[
                daily_label, toga.Divider(style=Pack(background_color="#27221F")), 
                daily_count_box, toga.Divider(style=Pack(background_color="#27221F")), 
                daily_range_box, toga.Divider(style=Pack(background_color="#27221F")),
                daily_task_container
            ],
            style=Pack(direction=COLUMN, background_color="#393432"))
        
        # weekly box
        weekly_label = toga.Label(
            "To-Do List", 
            style=Pack(padding=14, text_align="center", font_weight="bold", font_size=20, color="#EBF6F7"))
        
        weekly_count_box = toga.Box(id="weekly count box", style=Pack(direction=ROW))
        self.widgets_dict["weekly count box"] = weekly_count_box

        back_button = toga.Button(
            "<", id="weekly back button",
            on_press=self.change_range, 
            style=Pack(flex=0.2, padding=4, height=44, font_size=13, color="#EBF6F7", background_color="#27221F")
        )
        next_button = toga.Button(
            ">", id="weekly next button",
            on_press=self.change_range, 
            style=Pack(flex=0.2, padding=4, height=44, font_size=13, color="#EBF6F7", background_color="#27221F")
        )
        self.weekly_range = toga.Selection(
            id="weekly range", 
            on_change=self.load_tasks,
            style=Pack(flex=0.6, padding=4, height=44))
        self.widgets_dict["weekly range"] = self.weekly_range
        weekly_range_box = toga.Box(
            children=[back_button, self.weekly_range, next_button],
            style=Pack(direction=ROW))

        weekly_task_box = toga.Box(id="weekly task box", style=Pack(direction=COLUMN))
        self.widgets_dict["weekly task box"] = weekly_task_box
        weekly_task_container = toga.ScrollContainer(content=weekly_task_box, horizontal=False, style=Pack(flex=0.9))
        self.widgets_dict["weekly task container"] = weekly_task_container
        
        weekly_box = toga.Box(
            children=[
                weekly_label, toga.Divider(style=Pack(background_color="#27221F")), 
                weekly_count_box, toga.Divider(style=Pack(background_color="#27221F")), 
                weekly_range_box, toga.Divider(style=Pack(background_color="#27221F")),
                weekly_task_container
            ],
            style=Pack(direction=COLUMN, background_color="#393432"))
        
        # monthly box
        monthly_label = toga.Label(
            "To-Do List", 
            style=Pack(padding=14, text_align="center", font_weight="bold", font_size=20, color="#EBF6F7"))
        
        monthly_count_box = toga.Box(id="monthly count box", style=Pack(direction=ROW))
        self.widgets_dict["monthly count box"] = monthly_count_box

        back_button = toga.Button(
            "<", id="monthly back button",
            on_press=self.change_range, 
            style=Pack(flex=0.2, padding=4, height=44, font_size=13, color="#EBF6F7", background_color="#27221F")
        )
        next_button = toga.Button(
            ">", id="monthly next button",
            on_press=self.change_range, 
            style=Pack(flex=0.2, padding=4, height=44, font_size=13, color="#EBF6F7", background_color="#27221F")
        )
        self.monthly_range = toga.Selection(
            id="monthly range", 
            on_change=self.load_tasks,
            style=Pack(flex=0.6, padding=4, height=44))
        self.widgets_dict["monthly range"] = self.monthly_range
        monthly_range_box = toga.Box(
            children=[back_button, self.monthly_range, next_button],
            style=Pack(direction=ROW))        

        monthly_task_box = toga.Box(id="monthly task box", style=Pack(direction=COLUMN))
        self.widgets_dict["monthly task box"] = monthly_task_box
        monthly_task_container = toga.ScrollContainer(content=monthly_task_box, horizontal=False, style=Pack(flex=0.9))
        self.widgets_dict["monthly task container"] = monthly_task_container

        monthly_box = toga.Box(
            children=[
                monthly_label, toga.Divider(style=Pack(background_color="#27221F")), 
                monthly_count_box, toga.Divider(style=Pack(background_color="#27221F")), 
                monthly_range_box, toga.Divider(style=Pack(background_color="#27221F")),
                monthly_task_container
            ],
            style=Pack(direction=COLUMN, background_color="#393432"))
        
        # yearly box
        yearly_label = toga.Label(
            "To-Do List", 
            style=Pack(padding=14, text_align="center", font_weight="bold", font_size=20, color="#EBF6F7"))
        
        yearly_count_box = toga.Box(id="yearly count box", style=Pack(direction=ROW))
        self.widgets_dict["yearly count box"] = yearly_count_box

        back_button = toga.Button(
            "<", id="yearly back button",
            on_press=self.change_range, 
            style=Pack(flex=0.2, padding=4, height=44, font_size=13, color="#EBF6F7", background_color="#27221F")
        )
        next_button = toga.Button(
            ">", id="yearly next button",
            on_press=self.change_range, 
            style=Pack(flex=0.2, padding=4, height=44, font_size=13, color="#EBF6F7", background_color="#27221F")
        )
        self.yearly_range = toga.Selection(
            id="yearly range", 
            on_change=self.load_tasks,
            style=Pack(flex=0.6, padding=4, height=44))
        self.widgets_dict["yearly range"] = self.yearly_range
        yearly_range_box = toga.Box(
            children=[back_button, self.yearly_range, next_button],
            style=Pack(direction=ROW))

        yearly_task_box = toga.Box(id="yearly task box", style=Pack(direction=COLUMN))
        self.widgets_dict["yearly task box"] = yearly_task_box
        yearly_task_container = toga.ScrollContainer(content=yearly_task_box, horizontal=False, style=Pack(flex=0.9))
        self.widgets_dict["yearly task container"] = yearly_task_container

        yearly_box = toga.Box(
            children=[
                yearly_label, toga.Divider(style=Pack(background_color="#27221F")), 
                yearly_count_box, toga.Divider(style=Pack(background_color="#27221F")), 
                yearly_range_box, toga.Divider(style=Pack(background_color="#27221F")),
                yearly_task_container
            ],
            style=Pack(direction=COLUMN, background_color="#393432"))
        
        # pending task boxes container 
        daily_icon = toga.Icon("resources/todo/daily.png")
        weekly_icon = toga.Icon("resources/todo/weekly.png")
        monthly_icon = toga.Icon("resources/todo/monthly.png")
        yearly_icon = toga.Icon("resources/todo/yearly.png")

        list_box = toga.OptionContainer(content=[
            toga.OptionItem("Daily", daily_box, icon=daily_icon), 
            toga.OptionItem("Weekly", weekly_box, icon=weekly_icon), 
            toga.OptionItem("Monthly", monthly_box, icon=monthly_icon), 
            toga.OptionItem("Yearly", yearly_box, icon=yearly_icon)])

        return list_box

    def get_history_box(self):
        # routine box
        routine_label = toga.Label(
            "To-Do History", 
            style=Pack(padding=14, text_align="center", font_weight="bold", font_size=20, color="#EBF6F7"))
        
        routine_count_box = toga.Box(id="routine count box", style=Pack(direction=ROW))
        self.widgets_dict["routine count box"] = routine_count_box

        back_button = toga.Button(
            "<", id="routine back button",
            on_press=self.change_range, 
            style=Pack(flex=0.2, padding=4, height=44, font_size=13, color="#EBF6F7", background_color="#27221F")
        )
        next_button = toga.Button(
            ">", id="routine next button",
            on_press=self.change_range, 
            style=Pack(flex=0.2, padding=4, height=44, font_size=13, color="#EBF6F7", background_color="#27221F")
        )
        self.routine_range = toga.Selection(
            id="routine range", 
            on_change=self.load_tasks,
            style=Pack(flex=0.6, padding=4, height=44))
        self.widgets_dict["routine range"] = self.routine_range
        routine_range_box = toga.Box(
            children=[back_button, self.routine_range, next_button],
            style=Pack(direction=ROW))

        routine_task_box = toga.Box(id="routine task box", style=Pack(direction=COLUMN))
        self.widgets_dict["routine task box"] = routine_task_box
        routine_task_container = toga.ScrollContainer(content=routine_task_box, horizontal=False, style=Pack(flex=0.9))
        self.widgets_dict["routine task container"] = routine_task_container

        routine_box = toga.Box(
            children=[
                routine_label, toga.Divider(style=Pack(background_color="#27221F")), 
                routine_count_box, toga.Divider(style=Pack(background_color="#27221F")), 
                routine_range_box, toga.Divider(style=Pack(background_color="#27221F")),
                routine_task_container
            ],
            style=Pack(direction=COLUMN, background_color="#393432"))
        
        # challenging box
        challenging_label = toga.Label(
            "To-Do History", 
            style=Pack(padding=14, text_align="center", font_weight="bold", font_size=20, color="#EBF6F7"))
        
        challenging_count_box = toga.Box(id="challenging count box", style=Pack(direction=ROW))
        self.widgets_dict["challenging count box"] = challenging_count_box

        back_button = toga.Button(
            "<", id="challenging back button",
            on_press=self.change_range, 
            style=Pack(flex=0.2, padding=4, height=44, font_size=13, color="#EBF6F7", background_color="#27221F")
        )
        next_button = toga.Button(
            ">", id="challenging next button",
            on_press=self.change_range, 
            style=Pack(flex=0.2, padding=4, height=44, font_size=13, color="#EBF6F7", background_color="#27221F")
        )
        self.challenging_range = toga.Selection(
            id="challenging range", 
            on_change=self.load_tasks,
            style=Pack(flex=0.6, padding=4, height=44))
        self.widgets_dict["challenging range"] = self.challenging_range
        challenging_range_box = toga.Box(
            children=[back_button, self.challenging_range, next_button],
            style=Pack(direction=ROW))

        challenging_task_box = toga.Box(id="challenging task box", style=Pack(direction=COLUMN))
        self.widgets_dict["challenging task box"] = challenging_task_box
        challenging_task_container = toga.ScrollContainer(content=challenging_task_box, horizontal=False, style=Pack(flex=0.9))
        self.widgets_dict["challenging task container"] = challenging_task_container
        
        challenging_box = toga.Box(
            children=[
                challenging_label, toga.Divider(style=Pack(background_color="#27221F")), 
                challenging_count_box, toga.Divider(style=Pack(background_color="#27221F")), 
                challenging_range_box, toga.Divider(style=Pack(background_color="#27221F")), 
                challenging_task_container],
            style=Pack(direction=COLUMN, background_color="#393432"))
        
        # significant box
        significant_label = toga.Label(
            "To-Do History", 
            style=Pack(padding=14, text_align="center", font_weight="bold", font_size=20, color="#EBF6F7"))
        
        significant_count_box = toga.Box(id="significant count box", style=Pack(direction=ROW))
        self.widgets_dict["significant count box"] = significant_count_box

        back_button = toga.Button(
            "<", id="significant back button",
            on_press=self.change_range, 
            style=Pack(flex=0.2, padding=4, height=44, font_size=13, color="#EBF6F7", background_color="#27221F")
        )
        next_button = toga.Button(
            ">", id="significant next button",
            on_press=self.change_range, 
            style=Pack(flex=0.2, padding=4, height=44, font_size=13, color="#EBF6F7", background_color="#27221F")
        )
        self.significant_range = toga.Selection(
            id="significant range", 
            on_change=self.load_tasks,
            style=Pack(flex=0.6, padding=4, height=44))
        self.widgets_dict["significant range"] = self.significant_range
        significant_range_box = toga.Box(
            children=[back_button, self.significant_range, next_button],
            style=Pack(direction=ROW))

        significant_task_box = toga.Box(id="significant task box", style=Pack(direction=COLUMN))
        self.widgets_dict["significant task box"] = significant_task_box
        significant_task_container = toga.ScrollContainer(content=significant_task_box, horizontal=False, style=Pack(flex=0.9))
        self.widgets_dict["significant task container"] = significant_task_container

        significant_box = toga.Box(
            children=[
                significant_label, toga.Divider(style=Pack(background_color="#27221F")), 
                significant_count_box, toga.Divider(style=Pack(background_color="#27221F")),
                significant_range_box, toga.Divider(style=Pack(background_color="#27221F")), 
                significant_task_container],
            style=Pack(direction=COLUMN, background_color="#393432"))
        
        # momentous box
        momentous_label = toga.Label(
            "To-Do History", 
            style=Pack(padding=14, text_align="center", font_weight="bold", font_size=20, color="#EBF6F7"))
        
        momentous_count_box = toga.Box(id="momentous count box", style=Pack(direction=ROW))
        self.widgets_dict["momentous count box"] = momentous_count_box

        back_button = toga.Button(
            "<", id="momentous back button",
            on_press=self.change_range, 
            style=Pack(flex=0.2, padding=4, height=44, font_size=13, color="#EBF6F7", background_color="#27221F")
        )
        next_button = toga.Button(
            ">", id="momentous next button",
            on_press=self.change_range, 
            style=Pack(flex=0.2, padding=4, height=44, font_size=13, color="#EBF6F7", background_color="#27221F")
        )
        self.momentous_range = toga.Selection(
            id="momentous range", 
            on_change=self.load_tasks,
            style=Pack(flex=0.6, padding=4, height=44))
        self.widgets_dict["momentous range"] = self.momentous_range
        momentous_range_box = toga.Box(
            children=[back_button, self.momentous_range, next_button],
            style=Pack(direction=ROW))

        momentous_task_box = toga.Box(id="momentous task box", style=Pack(direction=COLUMN))
        self.widgets_dict["momentous task box"] = momentous_task_box
        momentous_task_container = toga.ScrollContainer(content=momentous_task_box, horizontal=False, style=Pack(flex=0.9))
        self.widgets_dict["momentous task container"] = momentous_task_container

        momentous_box = toga.Box(
            children=[
                momentous_label, toga.Divider(style=Pack(background_color="#27221F")), 
                momentous_count_box, toga.Divider(style=Pack(background_color="#27221F")),
                momentous_range_box, toga.Divider(style=Pack(background_color="#27221F")), 
                momentous_task_container],
            style=Pack(direction=COLUMN, background_color="#393432"))
        
        # completed task boxes container
        routine_icon = toga.Icon("resources/todo/routine.png")
        challenging_icon = toga.Icon("resources/todo/challenging.png")
        significant_icon = toga.Icon("resources/todo/significant.png")
        momentous_icon = toga.Icon("resources/todo/momentous.png")

        history_box = toga.OptionContainer(content=[
            toga.OptionItem("Routine", routine_box, icon=routine_icon), 
            toga.OptionItem("Challenging", challenging_box, icon=challenging_icon), 
            toga.OptionItem("Significant", significant_box, icon=significant_icon), 
            toga.OptionItem("Momentous", momentous_box, icon=momentous_icon)])
        
        return history_box

    def setup_todo(self):
        list_box = self.get_list_box()
        history_box = self.get_history_box()
        add_box = self.get_add_task_box()
        edit_box = self.get_edit_task_box()

        con, cur = get_connection(self.db_path)
        cur.executescript("""
            CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            tier TEXT CHECK(tier IN ('routine', 'challenging', 'significant', 'momentous')) NOT NULL,
            task_type TEXT CHECK(task_type IN ('daily', 'weekly', 'monthly', 'yearly')) NOT NULL,
            urgency TEXT CHECK(urgency IN ('low', 'medium', 'high')) NOT NULL,
            created_date DATE DEFAULT (date('now', 'localtime')),
            due_date DATE NOT NULL,
            completed_date DATE
            );

            CREATE INDEX IF NOT EXISTS idx_tasks_tier ON tasks(tier);
                       
            CREATE INDEX IF NOT EXISTS idx_tasks_completed_date ON tasks(completed_date);     
        """)
        con.commit()

        self.update_todo(load=False, con_cur=(con, cur))
        self.load_tasks(types=["daily", "weekly", "monthly", "yearly"], con_cur=(con, cur))

        con.close()

        return list_box, history_box, add_box, edit_box


    def update_todo(self, day_change=False, load=True, con_cur=None):
        weekdays_left = 7 - date.today().isocalendar().weekday if date.today().isocalendar().weekday != 7 else 7
        weekly_max_date = date.today()+timedelta(days=weekdays_left)
        monthly_max_date = (date((weekly_max_date+timedelta(days=1)).year, weekly_max_date.month+1, 1) - timedelta(days=1))
        if monthly_max_date == weekly_max_date:
            monthly_max_date = (date((weekly_max_date+timedelta(days=1)).year, weekly_max_date.month+2, 1) - timedelta(days=1))
        yearly_max_date = date((monthly_max_date+timedelta(days=1)).year, 12, 31)

        self.type_dates_dict = {
            "daily": (date.today(), date.today()), 
            "weekly": (date.today()+timedelta(days=1), weekly_max_date),
            "monthly": (weekly_max_date+timedelta(days=1), monthly_max_date),
            "yearly": (monthly_max_date+timedelta(days=1), yearly_max_date)}
        
        if day_change:
            self.app.setup_todo = True
            load = False

        self.update_task_types(load, con_cur)


    
    def todo_get_data(self, types: list=[], tiers: list=[], con_cur=None):
        con, cur = get_connection(self.db_path, con_cur)

        for t in types:
            cur.execute("""
                SELECT id, task, tier, urgency, created_date, due_date FROM tasks
                WHERE task_type IS ? AND completed_date IS NULL
                ORDER BY
                    due_date ASC,
                    CASE urgency
                        WHEN 'high' THEN 1
                        WHEN 'medium' THEN 2
                        WHEN 'low' THEN 3
                    END;
            """, (t,))
            tasks = cur.fetchall()

            cur.execute("""
                SELECT COUNT(*) FROM tasks
                WHERE task_type IS ? AND completed_date IS NULL;
            """, (t,))
            count = cur.fetchone()[0]

            self.data[t] = (tasks, count)

        for t in tiers:
            cur.execute("""
                SELECT id, task, created_date, completed_date FROM tasks
                WHERE tier IS ? AND completed_date IS NOT NULL
                ORDER BY completed_date DESC;
            """, (t,))
            tasks = cur.fetchall()

            cur.execute("""
                SELECT COUNT(*) FROM tasks
                WHERE tier IS ? AND completed_date IS NOT NULL;
            """, (t,))
            count = cur.fetchone()[0]

            self.data[t] = (tasks, count)

        close_connection(con, con_cur)


    async def add_task(self, widget):
        if task := self.add_input.value:
            task = task.strip()
            tier = self.add_tier.value.lower()
            urgency = self.add_urgency.value.lower()
            task_type = self.add_type.value.lower()
            due_date = self.add_duedate.value

            con, cur = get_connection(self.db_path)
            
            cur.execute("""
                INSERT INTO tasks (task_type, tier, task, urgency, due_date)
                VALUES (?, ?, ?, ?, ?);
            """, (task_type, tier, task, urgency, due_date))

            con.commit()

            self.load_tasks(types=[task_type], con_cur=(con, cur))
            con.close()
            self.app.open_todo(widget, task_type.capitalize())


    async def done_task_dialog(self, widget):
        self.temp_task_id = int(widget.id.split()[0])
        result = await self.app.dialog(toga.QuestionDialog("Confirmation", f"Have you completed [{self.temp_task_id:06d}] task?"))
        if result:
            await self.done_task()


    async def edit_task_dialog(self, widget):
        self.temp_task_id = int(widget.id.split()[0])
        result = await self.app.dialog(toga.QuestionDialog("Edit", "Do you want to edit the task?"))
        if result:
            await self.app.open_edit_task()


    async def done_task(self):
        id = self.temp_task_id
        con, cur = get_connection(self.db_path)

        cur.execute("""
            UPDATE tasks
            SET completed_date = date('now', 'localtime')
            WHERE id = ?;
        """, (id,))
        
        con.commit()

        cur.execute("""
            SELECT task_type, tier FROM tasks
            WHERE id = ?;
        """, (id,))
        task_type, tier = cur.fetchone()

        if id in self.widgets_dict["tasks"]:
            del self.widgets_dict["tasks"][id]
            del self.widgets_dict["tasks"][f"{id} task button"]

        self.load_tasks(types=[task_type], con_cur=(con, cur))

        self.task_history_load.add(tier)

        con.close()


    async def save_task(self, widget):
        if task := self.edit_input.value:
            task = task.strip()
            id = self.temp_task_id
            task_type = self.edit_type.value.lower()

            con, cur = get_connection(self.db_path)

            cur.execute("""
                UPDATE tasks
                SET task_type = ?, tier = ?, task = ?, urgency = ?, due_date = ?
                WHERE id = ?;
            """, (task_type, self.edit_tier.value.lower(), task, self.edit_urgency.value.lower(), self.edit_duedate.value, id,))
            con.commit()

            if id in self.widgets_dict["tasks"]:
                del self.widgets_dict["tasks"][id]
            temp = [self.edit_type.value.lower()]
            task_types = temp if self.temp_task_type in temp else temp+[self.temp_task_type]
            self.load_tasks(types=task_types, con_cur=(con, cur))

            con.close()

            self.app.open_todo(widget, temp[0].capitalize())


    async def remove_task_dialog(self, widget):
        result = await self.app.dialog(toga.QuestionDialog("Confirmation", "Are you sure you want to remove the task?"))
        if result:
            await self.remove_task()


    async def remove_task(self):
        id = self.temp_task_id

        con, cur = get_connection(self.db_path)
        
        cur.execute("""
            SELECT task_type FROM tasks
            WHERE id = ?;
        """, (id,))
        task_type = cur.fetchone()[0]

        cur.execute("""
            DELETE FROM tasks
            WHERE id = ?;
        """, (id,))        
        con.commit()

        if id in self.widgets_dict["tasks"]:
            del self.widgets_dict["tasks"][id]
            del self.widgets_dict["tasks"][f"{id} task button"]

        self.load_tasks(types=[task_type], con_cur=(con, cur))

        con.close()

        self.app.open_todo(None, tab=task_type.capitalize())


    def load_tasks(self, widget=None, types: list=[], tiers: list=[], con_cur=None):
        self.todo_get_data(types, tiers, con_cur)

        for t in types:
            data = self.data[t]

            items = get_ranges(data[0])
            set_range(self.widgets_dict[f"{t} range"], items)

            count_box = self.widgets_dict[f"{t} count box"]
            count_box.clear()

            count_box.add(
                toga.Label(f"{t.capitalize()} tasks", style=Pack(flex=0.49, padding=10, font_size=16, color="#EBF6F7")),
                toga.Divider(direction=Direction.VERTICAL, style=Pack(height=49, background_color="#27221F")),
                toga.Label(f"Pending: {data[1]}", style=Pack(flex=0.51, padding=10, font_size=16, color="#EBF6F7")))
                
        if tiers:
            self.task_history_load.clear()
            for t in tiers:
                data = self.data[t]

                items = get_ranges(data[0])
                self.widgets_dict[f"{t} range"].items = items

                count_box = self.widgets_dict[f"{t} count box"]
                count_box.clear()

                if f"{t} task label" not in self.widgets_dict:
                    self.widgets_dict[f"{t} task label"] = toga.Label(f"{t.capitalize()} tasks", style=Pack(flex=0.49, padding=10, font_size=16, color="#EBF6F7"))

                count_box.add(
                    self.widgets_dict[f"{t} task label"],
                    toga.Divider(direction=Direction.VERTICAL, style=Pack(height=49, background_color="#27221F")),
                    toga.Label(f"Completed: {data[1]}", style=Pack(flex=0.51, padding=10, font_size=16, color="#EBF6F7")))

        elif widget:
            widget_id = widget.id.split()

            t = widget_id[0]
            if t in self.data["task types"]:
                type_tier = ("Pending", "type")
                button = True
            else:
                type_tier = ("Completed", "tier")
                button = False

            data = self.data[t][0]
            list_box = self.widgets_dict[f"{t} task box"]
            list_box.clear()

            start, end = [int(i) for i in widget.value.split('–')]
            if start == 0 and end == 0:
                list_box.add(
                    toga.Label(
                        f"{type_tier[0]} tasks of the {type_tier[1]} will appear here.",
                        style=Pack(padding=10, font_size=12, color="#EBF6F7")))
            else:
                for i in range(start-1, end):
                    task = data[i]
                    id = task[0]
                    if id not in self.widgets_dict["tasks"]:
                        task_box = self.get_task_box(task, button=button)
                        self.widgets_dict["tasks"][id] = task_box
                    list_box.add(self.widgets_dict["tasks"][id])
            
            self.widgets_dict[f"{t} task container"].position = toga.Position(0,0)


    def update_task_types(self, load=True, con_cur=None):
        con, cur = get_connection(self.db_path, con_cur)

        cur.execute("""
            SELECT id, task_type, due_date FROM tasks
            WHERE completed_date IS NULL;
        """)
        tasks = cur.fetchall()

        task_types = set()
        updated_tasks = []

        for id, task_type, due_date in tasks:
            due_date = date.fromisoformat(due_date)
            if task_type != "daily":
                if self.type_dates_dict[task_type][0] <= due_date <= self.type_dates_dict[task_type][1]:
                    pass
                else:
                    task_types.add(task_type)
                    
                    t = "daily"
                    if due_date <= self.type_dates_dict[t][0]:
                        task_types.add(t)
                        updated_tasks.append((id, t))
                    else:
                        for t in ["weekly", "monthly"]:
                            if self.type_dates_dict[t][0] <= due_date <= self.type_dates_dict[t][1]:
                                task_types.add(t)
                                updated_tasks.append((id, t))
                                break
        
        if updated_tasks:
            cur.executemany(
                "UPDATE tasks SET task_type = ? WHERE id = ?;", 
                [(task_type, task_id,) for task_id, task_type in updated_tasks])
            con.commit()
            if load:
                self.load_tasks(types=list(task_types), con_cur=(con, cur))

        close_connection(con, con_cur)


    async def reset_todo_dialog(self):
        result = await self.app.dialog(toga.QuestionDialog("Confirmation", "Are you sure you want to reset To-Do database?"))
        if result:
            await self.reset_todo()


    async def reset_todo(self):
        con, cur = get_connection(self.db_path)
        cur.execute("DROP TABLE tasks;")
        con.commit()

        cur.executescript("""
            CREATE TABLE tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            tier TEXT CHECK(tier IN ('routine', 'challenging', 'significant', 'momentous')) NOT NULL,
            task_type TEXT CHECK(task_type IN ('daily', 'weekly', 'monthly', 'yearly')) NOT NULL,
            urgency TEXT CHECK(urgency IN ('low', 'medium', 'high')) NOT NULL,
            created_date DATE DEFAULT (date('now', 'localtime')),
            due_date DATE NOT NULL,
            completed_date DATE
            );    
            
            CREATE INDEX idx_tasks_tier ON tasks(tier);
            CREATE INDEX idx_tasks_completed_date ON tasks(completed_date);
        """)
        con.commit()
        con.close()

        self.app.setup_ui(todo=True)
        
        await self.app.dialog(toga.InfoDialog("Success", "To-Do database has been reset successfully."))


    def task_type_change(self, widget):
        if self.tt_change:
            id = widget.id.split()[0]
            dd_widget = self.widgets_dict[f"{id} task duedate"]
            self.dd_change = False
            dd_widget.min = dd_widget.max = self.type_dates_dict[widget.value.lower()][1]
            dd_widget.refresh()


    def duedate_change(self, widget):
        if self.dd_change:
            id = widget.id.split()[0]
            tt_widget = self.widgets_dict[f"{id} task type"]
            tt_widget.enabled = False
            self.tt_change = False
            for t in self.type_dates_dict:
                dates = self.type_dates_dict[t]
                if dates[0] <= widget.value <= dates[1]: 
                    tt_widget.value = t.capitalize()
                    break


    def clear_add_box(self):
        self.tt_change = self.dd_change = False

        self.add_input.value = ""
        self.add_tier.value = "Routine"
        self.add_urgency.value = "Low"
        self.add_type.value = "Daily"
        self.add_duedate.min = self.add_duedate.value = date.today()
        self.add_duedate.max = self.type_dates_dict["yearly"][1]
        self.add_type.enabled = True

        self.tt_change = self.dd_change = True


    def load_edit_box(self):
        con, cur = get_connection(self.db_path)

        cur.execute("""
            SELECT task, tier, urgency, task_type, due_date FROM tasks
            WHERE id = ?;
        """, (self.temp_task_id,))
        task, tier, urgency, task_type, due_date = cur.fetchone()
        
        con.close()
        
        self.tt_change = self.dd_change = False
        self.temp_task_type = task_type
        self.edit_input.value = task
        self.edit_tier.value = tier.capitalize()
        self.edit_urgency.value = urgency.capitalize()
        self.edit_type.value = task_type.capitalize()
        self.edit_duedate.min = date.today()
        self.edit_duedate.max = self.type_dates_dict["yearly"][1]
        self.edit_duedate.value = due_date
        self.edit_duedate.refresh()
        self.edit_type.enabled = True

        self.tt_change = self.dd_change = True


    def get_task_box(self, task, button=True):
        id = task[0]

        if button:
            if f"{id} task button" not in self.widgets_dict["tasks"]:
                done = toga.Button(
                    "Done", id=f"{task[0]} task done button", on_press=self.done_task_dialog, 
                    style=Pack(flex=0.5, height=55, font_size=12, color="#EBF6F7", background_color="#27221F"))
                edit = toga.Button(
                    "Edit", id=f"{task[0]} task edit button", on_press=self.edit_task_dialog, 
                    style=Pack(flex=0.5, height=55, font_size=12, color="#EBF6F7", background_color="#27221F"))
                self.widgets_dict["tasks"][f"{task[0]} task button"] = toga.Box(
                    children=[done, edit],
                    style=Pack(direction=COLUMN, padding=4, height=110, width=84))
                
            bottom_str = f"Tier: {task[2].capitalize()}  |  Urgency: {task[3].capitalize()}\nAdded: {task[4]}  |  Due: {task[5]}"
        else:
            bottom_str = f"Added: {task[2]}  |  Completed: {task[3]}"
            
        id_label = toga.Label(
            f"[{id:06d}]", 
            style=Pack(padding=4, font_size=11, color="#EBF6F7"))
        
        task_rows = self.format_task(task[1])
        main_label = toga.Label(
            f"{task_rows[0]}\n{task_rows[1]}", 
            style=Pack(padding=4, font_size=11, font_weight="bold", color="#EBF6F7"))
        
        bottom_label = toga.Label(
            bottom_str, 
            style=Pack(padding=4, font_size=11, color="#EBF6F7"))
        
        task_label_box = toga.Box(children=[id_label, main_label, bottom_label], style=Pack(direction=COLUMN, flex=0.85))

        children = [task_label_box,]
        children += [self.widgets_dict["tasks"][f"{id} task button"],] if button else []

        task_box = toga.Box(
            children=children,
            style=Pack(direction=ROW))
        task_box = toga.Box(
            children=[task_box, toga.Divider(style=Pack(background_color="#27221F"))],
            style=Pack(direction=COLUMN))
        
        return task_box


    def format_task(self, task, max_length=40):
        if len(task) > max_length:
            words = task.split()
            first_row = ""
            second_row = ""
            
            for word in words:
                if len(first_row) + len(word)<= max_length:
                    first_row += word + " "
                else:
                    break
            first_row = first_row.rstrip()

            for word in words[len(first_row.split()):]:
                if len(second_row) + len(word) <= max_length:
                    second_row += word + " "
            second_row = second_row.rstrip()

            return first_row, second_row
        
        else:
            return task, ""
        

    def change_range(self, widget):
        change_range(widget, self.widgets_dict)

            
    def reset_type_date(self, widget):
        tab = widget.id.split()[0]

        self.dd_change = self.tt_change = False

        w = self.widgets_dict[f"{tab} task type"]
        w.value = "Daily"
        w.enabled = True
        w.refresh()

        w = self.widgets_dict[f"{tab} task duedate"]
        w.min = w.value = date.today()
        w.max = self.type_dates_dict["yearly"][1]
        w.refresh()

        self.dd_change = self.tt_change = True