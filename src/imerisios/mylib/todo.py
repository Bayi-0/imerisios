import toga
from toga.style import Pack
from toga.constants import COLUMN, ROW, Direction
from datetime import date, timedelta
import sqlite3 as sql
from imerisios.mylib.tools import length_check, get_connection, close_connection

class ToDo:
    def __init__(self, app, db_path):
        self.app = app
        self.db_path = db_path

        self.widgets = {}
        self.data = {}
        self.type_dates_dict = {}
        self.task_history_load = {"routine", "challenging", "significant", "momentous"}
        self.tt_change = self.dd_change = True


    def get_create_task_box(self):
        label = toga.Label(
            "Create a New Task", 
            style=Pack(flex=0.09, padding=14, text_align="center", font_weight="bold", font_size=18, color="#EBF6F7"))
        
        input_label = toga.Label(
            "Pray inscribe thy task\n(no more than 48 characters):", 
            style=Pack(padding=(18,18,0), font_size=14, color="#EBF6F7"))
        self.create_input = toga.TextInput(
            id="task_create input 48",
            on_change=length_check, 
            style=Pack(padding=(0,18), height=44, font_size=12, color="#EBF6F7", background_color="#27221F"))
        
        tier_label = toga.Label(
            "Tier:", 
            style=Pack(padding=(18,18,0), font_size=14, color="#EBF6F7"))
        self.create_tier = toga.Selection(
            items=["Routine", "Challenging", "Significant", "Momentous"],
            style=Pack(padding=(0,18)))
        
        urgency_label = toga.Label(
            "Urgency:", 
            style=Pack(padding=(18,18,0), font_size=14, color="#EBF6F7"))
        self.create_urgency = toga.Selection(
            items=["Low", "Medium", "High"],
            style=Pack(padding=(0,18)))
        
        type_label = toga.Label(
            "Type:", 
            style=Pack(padding=(18,18,0), font_size=14, color="#EBF6F7"))
        self.create_type = toga.Selection(
            id="create task type", 
            items=["Daily", "Weekly", "Monthly", "Yearly"], 
            on_change=self.task_type_change,
            style=Pack(padding=(0,18)))
        self.widgets["create task type"] = self.create_type

        duedate_label = toga.Label(
            "Due:", 
            style=Pack(padding=(18,18,0), font_size=14, color="#EBF6F7"))
        self.create_duedate = toga.DateInput(
            id="create task duedate", 
            min=date.today(), 
            max=date.today(), 
            on_change=self.duedate_change,
            style=Pack(padding=(0,18), color="#EBF6F7"))
        self.widgets["create task duedate"] = self.create_duedate
        
        top_box = toga.Box(
            children=[
                input_label, self.create_input, 
                tier_label, self.create_tier, 
                urgency_label, self.create_urgency, 
                type_label, self.create_type, 
                duedate_label, self.create_duedate
            ], 
            style=Pack(direction=COLUMN, flex=0.7))
        
        button = toga.Button(
            "Create", on_press=self.create_task, 
            style=Pack(height=140, padding=11, font_size=28, color="#EBF6F7", background_color="#27221F"))
        bottom_box = toga.Box(children=[button], style=Pack(direction=COLUMN, flex=0.21))

        create_box = toga.Box(
            children=[
                label, toga.Divider(style=Pack(background_color="#27221F")), 
                top_box, 
                bottom_box
            ], 
            style=Pack(direction=COLUMN, background_color="#393432"))
        
        return create_box


    def get_edit_task_box(self):
        label = toga.Label(
            "Edit the Task", 
            style=Pack(flex=0.1, padding=14, text_align="center", font_weight="bold", font_size=18, color="#EBF6F7"))
        
        input_label = toga.Label(
            "Pray inscribe thy task\n(no more than 48 characters):", 
            style=Pack(padding=(18,18,0), font_size=14, color="#EBF6F7"))
        self.edit_input = toga.TextInput(
            id="task_edit input 48",
            on_change=length_check, 
            style=Pack(padding=(0,18), height=44, font_size=12, color="#EBF6F7", background_color="#27221F"))
        
        tier_label = toga.Label(
            "Tier:", 
            style=Pack(padding=(18,18,0), font_size=14, color="#EBF6F7"))
        self.edit_tier = toga.Selection(
            items=["Routine", "Challenging", "Significant", "Momentous"],
            style=Pack(padding=(0,18)))
            
        urgency_label = toga.Label(
            "Urgency:", 
            style=Pack(padding=(18,18,0), font_size=14, color="#EBF6F7"))
        self.edit_urgency = toga.Selection(
            items=["Low", "Medium", "High"],
            style=Pack(padding=(0,18)))
        
        type_label = toga.Label(
            "Type:", 
            style=Pack(padding=(18,18,0), font_size=14, color="#EBF6F7"))
        self.edit_type = toga.Selection(
            id="edit task type", 
            items=["Daily", "Weekly", "Monthly", "Yearly"], 
            on_change=self.task_type_change,
            style=Pack(padding=(0,18)))
        self.widgets["edit task type"] = self.edit_type

        duedate_label = toga.Label(
            "Due:", 
            style=Pack(padding=(18,18,0), font_size=14, color="#EBF6F7"))
        self.edit_duedate = toga.DateInput(
            id="edit task duedate", 
            on_change=self.duedate_change, 
            style=Pack(padding=(0,18), color="#EBF6F7"))
        self.widgets["edit task duedate"] = self.edit_duedate

        top_box = self.box = toga.Box(
            children=[
                input_label, self.edit_input, 
                tier_label, self.edit_tier, 
                urgency_label, self.edit_urgency, 
                type_label, self.edit_type, 
                duedate_label, self.edit_duedate], 
            style=Pack(direction=COLUMN, flex=0.7))

        delete_button = toga.Button(
            "Delete", on_press=self.delete_task_dialog, 
            style=Pack(flex=0.5, height=140, padding=(11,4,11,11), font_size=28, color="#EBF6F7", background_color="#27221F"))
        save_button = toga.Button(
            "Save", on_press=self.save_task, 
            style=Pack(flex=0.5, height=140, padding=(11,11,11,4), font_size=28, color="#EBF6F7", background_color="#27221F"))
        bottom_box = toga.Box(
            children=[delete_button, save_button], 
            style=Pack(direction=ROW, flex=0.21))
        
        edit_box = toga.Box(
            children=[
                label, toga.Divider(style=Pack(background_color="#27221F")), 
                top_box, 
                bottom_box
            ], 
            style=Pack(direction=COLUMN, background_color="#393432"))
        
        return edit_box

    def get_list_box(self):
        daily_label = toga.Label(
            "To-Do List", 
            style=Pack(padding=(14,20), text_align="center", font_weight="bold", font_size=20, color="#EBF6F7"))
        
        daily_count_box = toga.Box(id="daily count box", style=Pack(direction=ROW))
        self.widgets["daily count box"] = daily_count_box
        
        daily_task_box = toga.Box(id="daily task box", style=Pack(direction=COLUMN))
        self.widgets["daily task box"] = daily_task_box
        daily_task_container = toga.ScrollContainer(content=daily_task_box, horizontal=False, style=Pack(flex=0.9))

        daily_box = toga.Box(
            children=[
                daily_label, toga.Divider(style=Pack(background_color="#27221F")), 
                daily_count_box, toga.Divider(style=Pack(background_color="#27221F")), 
                daily_task_container
            ],
            style=Pack(direction=COLUMN, background_color="#393432"))
        
        ### weekly box
        weekly_label = toga.Label(
            "To-Do List", 
            style=Pack(padding=14, text_align="center", font_weight="bold", font_size=20, color="#EBF6F7"))
        
        weekly_count_box = toga.Box(id="weekly count box", style=Pack(direction=ROW))
        self.widgets["weekly count box"] = weekly_count_box

        weekly_task_box = toga.Box(id="weekly task box", style=Pack(direction=COLUMN))
        self.widgets["weekly task box"] = weekly_task_box
        weekly_task_container = toga.ScrollContainer(content=weekly_task_box, horizontal=False, style=Pack(flex=0.9))
        
        weekly_box = toga.Box(
            children=[
                weekly_label, toga.Divider(style=Pack(background_color="#27221F")), 
                weekly_count_box, toga.Divider(style=Pack(background_color="#27221F")), 
                weekly_task_container
            ],
            style=Pack(direction=COLUMN, background_color="#393432"))
        
        ### monthly box
        monthly_label = toga.Label(
            "To-Do List", 
            style=Pack(padding=14, text_align="center", font_weight="bold", font_size=20, color="#EBF6F7"))
        
        monthly_count_box = toga.Box(id="monthly count box", style=Pack(direction=ROW))
        self.widgets["monthly count box"] = monthly_count_box

        monthly_task_box = toga.Box(id="monthly task box", style=Pack(direction=COLUMN))
        self.widgets["monthly task box"] = monthly_task_box
        monthly_task_container = toga.ScrollContainer(content=monthly_task_box, horizontal=False, style=Pack(flex=0.9))

        monthly_box = toga.Box(
            children=[
                monthly_label, toga.Divider(style=Pack(background_color="#27221F")), 
                monthly_count_box, toga.Divider(style=Pack(background_color="#27221F")), 
                monthly_task_container
            ],
            style=Pack(direction=COLUMN, background_color="#393432"))
        
        ### yearly box
        yearly_label = toga.Label(
            "To-Do List", 
            style=Pack(padding=14, text_align="center", font_weight="bold", font_size=20, color="#EBF6F7"))
        
        yearly_count_box = toga.Box(id="yearly count box", style=Pack(direction=ROW))
        self.widgets["yearly count box"] = yearly_count_box

        yearly_task_box = toga.Box(id="yearly task box", style=Pack(direction=COLUMN))
        self.widgets["yearly task box"] = yearly_task_box
        yearly_task_container = toga.ScrollContainer(content=yearly_task_box, horizontal=False, style=Pack(flex=0.9))

        yearly_box = toga.Box(
            children=[
                yearly_label, toga.Divider(style=Pack(background_color="#27221F")), 
                yearly_count_box, toga.Divider(style=Pack(background_color="#27221F")), 
                yearly_task_container
            ],
            style=Pack(direction=COLUMN, background_color="#393432"))
        
        ## pending task boxes container 
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
        routine_label = toga.Label(
            "To-Do History", 
            style=Pack(padding=14, text_align="center", font_weight="bold", font_size=20, color="#EBF6F7"))
        
        routine_count_box = toga.Box(id="routine count box", style=Pack(direction=ROW))
        self.widgets["routine count box"] = routine_count_box

        routine_task_box = toga.Box(id="routine task box", style=Pack(direction=COLUMN))
        self.widgets["routine task box"] = routine_task_box
        routine_task_container = toga.ScrollContainer(content=routine_task_box, horizontal=False, style=Pack(flex=0.9))

        routine_box = toga.Box(
            children=[
                routine_label, toga.Divider(style=Pack(background_color="#27221F")), 
                routine_count_box, toga.Divider(style=Pack(background_color="#27221F")), 
                routine_task_container
            ],
            style=Pack(direction=COLUMN, background_color="#393432"))
        
        ### challenging box
        challenging_label = toga.Label(
            "To-Do History", 
            style=Pack(padding=14, text_align="center", font_weight="bold", font_size=20, color="#EBF6F7"))
        
        challenging_count_box = toga.Box(id="challenging count box", style=Pack(direction=ROW))
        self.widgets["challenging count box"] = challenging_count_box

        challenging_task_box = toga.Box(id="challenging task box", style=Pack(direction=COLUMN))
        self.widgets["challenging task box"] = challenging_task_box
        challenging_task_container = toga.ScrollContainer(content=challenging_task_box, horizontal=False, style=Pack(flex=0.9))
        
        challenging_box = toga.Box(
            children=[challenging_label, toga.Divider(style=Pack(background_color="#27221F")), challenging_count_box, toga.Divider(style=Pack(background_color="#27221F")), challenging_task_container],
            style=Pack(direction=COLUMN, background_color="#393432"))
        
        ### significant box
        significant_label = toga.Label(
            "To-Do History", 
            style=Pack(padding=14, text_align="center", font_weight="bold", font_size=20, color="#EBF6F7"))
        
        significant_count_box = toga.Box(id="significant count box", style=Pack(direction=ROW))
        self.widgets["significant count box"] = significant_count_box

        significant_task_box = toga.Box(id="significant task box", style=Pack(direction=COLUMN))
        self.widgets["significant task box"] = significant_task_box
        significant_task_container = toga.ScrollContainer(content=significant_task_box, horizontal=False, style=Pack(flex=0.9))

        significant_box = toga.Box(
            children=[significant_label, toga.Divider(style=Pack(background_color="#27221F")), significant_count_box, toga.Divider(style=Pack(background_color="#27221F")), significant_task_container],
            style=Pack(direction=COLUMN, background_color="#393432"))
        
        ### momentous box
        momentous_label = toga.Label(
            "To-Do History", 
            style=Pack(padding=14, text_align="center", font_weight="bold", font_size=20, color="#EBF6F7"))
        
        momentous_count_box = toga.Box(id="momentous count box", style=Pack(direction=ROW))
        self.widgets["momentous count box"] = momentous_count_box
        
        momentous_task_box = toga.Box(id="momentous task box", style=Pack(direction=COLUMN))
        self.widgets["momentous task box"] = momentous_task_box
        momentous_task_container = toga.ScrollContainer(content=momentous_task_box, horizontal=False, style=Pack(flex=0.9))

        momentous_box = toga.Box(
            children=[momentous_label, toga.Divider(style=Pack(background_color="#27221F")), momentous_count_box, toga.Divider(style=Pack(background_color="#27221F")), momentous_task_container],
            style=Pack(direction=COLUMN, background_color="#393432"))
        
        ## completed task boxes container
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
        create_box = self.get_create_task_box()
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

        self.update_todo(False, (con, cur))
        self.load_tasks(types=["daily", "weekly", "monthly", "yearly"], con_cur=(con, cur))

        con.close()

        return list_box, history_box, create_box, edit_box


    def update_todo(self, load=True, con_cur=None):
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
                ORDER BY
                    completed_date DESC,
                    id DESC;
            """, (t,))
            tasks = cur.fetchall()

            cur.execute("""
                SELECT COUNT(*) FROM tasks
                WHERE tier IS ? AND completed_date IS NOT NULL;
            """, (t,))
            count = cur.fetchone()[0]

            self.data[t] = (tasks, count)

        close_connection(con, con_cur)


    def create_task(self, widget):
        if self.create_input.value:
            task = self.create_input.value
            tier = self.create_tier.value.lower()
            urgency = self.create_urgency.value.lower()
            task_type = self.create_type.value.lower()
            due_date = self.create_duedate.value

            con, cur = get_connection(self.db_path)
            
            cur.execute("""
                INSERT INTO tasks (task_type, tier, task, urgency, due_date)
                VALUES (?, ?, ?, ?, ?);
            """, (task_type, tier, task, urgency, due_date))

            con.commit()

            self.load_tasks(types=[task_type], con_cur=(con, cur))
            con.close()
            self.app.open_todo(widget, task_type.capitalize())


    async def interact_task(self, widget):
        self.temp_task_id = int(widget.id.split()[0])
        result = await self.app.main_window.question_dialog("Confirmation", f"Hast thou completed Task [{self.temp_task_id:06d}] bestowed upon thee?")
        await self.done_task_dialog(result)


    async def done_task_dialog(self, result):
        if result:
            await self.done_task()
        else:
            result = await self.app.main_window.question_dialog("Edit", "Dost thou wish to amend the task?")
            await self.edit_task_dialog(result)


    async def edit_task_dialog(self, result):
        if result:
            await self.app.open_edit_task()


    async def done_task(self):
        con, cur = get_connection(self.db_path)

        cur.execute("""
            UPDATE tasks
            SET completed_date = date('now', 'localtime')
            WHERE id = ?;
        """, (self.temp_task_id,))
        
        con.commit()

        cur.execute("""
            SELECT task_type, tier FROM tasks
            WHERE id = ?;
        """, (self.temp_task_id,))
        task_type, tier = cur.fetchone()

        self.load_tasks(types=[task_type], con_cur=(con, cur))

        self.task_history_load.add(tier)

        con.close()


    def save_task(self, widget):
        if self.edit_input.value:
            con, cur = get_connection(self.db_path)

            cur.execute("""
                UPDATE tasks
                SET task_type = ?, tier = ?, task = ?, urgency = ?, due_date = ?
                WHERE id = ?;
            """, (self.edit_type.value.lower(), self.edit_tier.value.lower(), self.edit_input.value, self.edit_urgency.value.lower(), self.edit_duedate.value, self.temp_task_id,))
            con.commit()
            temp = [self.edit_type.value.lower()]
            task_types = temp if self.temp_task_type in temp else temp+[self.temp_task_type]
            self.load_tasks(types=task_types, con_cur=(con, cur))

            con.close()

            self.app.open_todo(widget, temp[0].capitalize())


    async def delete_task_dialog(self, widget):
        result = await self.app.main_window.question_dialog("Confirmation", "Art thou certain thou wishest to delete the task?")
        if result:
            await self.delete_task()


    async def delete_task(self):
        con, cur = get_connection(self.db_path)
        
        cur.execute("""
            SELECT task_type FROM tasks
            WHERE id = ?;
        """, (self.temp_task_id,))
        task_type = cur.fetchone()[0]

        cur.execute("""
            DELETE FROM tasks
            WHERE id = ?;
        """, (self.temp_task_id,))        
        con.commit()

        self.load_tasks(types=[task_type], con_cur=(con, cur))

        con.close()

        self.app.open_todo(None, tab=task_type.capitalize())


    def load_tasks(self, types: list=[], tiers: list=[], con_cur=None):
        self.todo_get_data(types, tiers, con_cur)

        for t in types:
            count_box = self.widgets[f"{t} count box"]
            task_box = self.widgets[f"{t} task box"]
            count_box.clear()
            task_box.clear()

            data = self.data[t]

            count_box.add(
                toga.Label(f"{t.capitalize()} tasks", style=Pack(flex=0.49, padding=10, font_size=16, color="#EBF6F7")),
                toga.Divider(direction=Direction.VERTICAL, style=Pack(height=49, background_color="#27221F")),
                toga.Label(f"Pending: {data[1]}", style=Pack(flex=0.51, padding=10, font_size=16, color="#EBF6F7")))

            if len(data[0]) == 0:
                task_box.add(toga.Label(
                    "Created tasks of the type will appear here.",
                    style=Pack(padding=10, font_size=12, color="#EBF6F7")))
            else:
                for task in data[0]:
                    if f"{task[0]} task button" not in self.widgets:
                        self.widgets[f"{task[0]} task button"] = toga.Button(
                            "Done", id=f"{task[0]} task button", on_press=self.interact_task, 
                            style=Pack(height=84, width=74, font_size=11, color="#EBF6F7", background_color="#27221F"))
                        
                    task_top = toga.Label(
                        f"[{task[0]:06d}] | Tier: {task[2].capitalize()} | Urgency: {task[3].capitalize()}\nCreated: {task[4]} | Due: {task[5]}", 
                        style=Pack(padding=(14,4,0), flex=0.66, font_size=10, color="#EBF6F7"))
                    task_bottom = toga.Label(
                        task[1], 
                        style=Pack(padding=(4,4,14), flex=0.33, font_size=10, color="#EBF6F7"))
                    task_label_box = toga.Box(children=[task_top, task_bottom], style=Pack(direction=COLUMN, flex=0.85))

                    task_box.add(
                        toga.Box(
                            children=[
                                task_label_box,
                                self.widgets[f"{task[0]} task button"]
                            ], 
                            style=Pack(direction=ROW)),
                        toga.Divider(style=Pack(background_color="#27221F")))
                
        if tiers:
            self.task_history_load.clear()
            for t in tiers:
                count_box = task_box = self.widgets[f"{t} count box"]
                task_box = self.widgets[f"{t} task box"]
                count_box.clear()
                task_box.clear()

                data = self.data[t]

                count_box.add(
                    toga.Label(f"{t.capitalize()} tasks", style=Pack(flex=0.49, padding=10, font_size=16, color="#EBF6F7")),
                    toga.Divider(direction=Direction.VERTICAL, style=Pack(height=49, background_color="#27221F")),
                    toga.Label(f"Completed: {data[1]}", style=Pack(flex=0.51, padding=10, font_size=16, color="#EBF6F7")))

                if len(data[0]) == 0:
                    task_box.add(toga.Label(
                        "Completed tasks of the tier will appear here.",
                        style=Pack(padding=10, font_size=12, color="#EBF6F7")))
                else:
                    for task in data[0]:
                        task_top = toga.Label(
                            f"[{task[0]:06d}]\nCreated: {task[2]} | Completed: {task[3]}", 
                            style=Pack(padding=(14,4,4), flex=0.66, font_size=10, color="#EBF6F7"))
                        task_bottom = toga.Label(
                            task[1], 
                            style=Pack(padding=(0,4,14), flex=0.33, font_size=10, color="#EBF6F7"))
                        task_box.add(
                            toga.Box(
                                children=[task_top, task_bottom],
                                style=Pack(direction=COLUMN)),
                            toga.Divider(style=Pack(background_color="#27221F")))


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
                    for t in ["daily", "weekly", "monthly"]:
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


    async def reset_todo_dialog(self, widget):
        result = await self.app.main_window.question_dialog("Confirmation", "Are you sure you wish to reset To-Do database?")
        if result:
            await self.reset_todo()


    async def reset_todo(self):
        con, cur = get_connection(self.db_path)
        cur.execute("DROP TABLE tasks;")
        con.commit()

        cur.execute("""
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
        """)
        cur.execute("CREATE INDEX idx_tasks_tier ON tasks(tier);")
        cur.execute("CREATE INDEX idx_tasks_completed_date ON tasks(completed_date);")
        con.commit()

        self.load_tasks(["daily", "weekly", "monthly", "yearly"], ["routine", "challenging", "significant", "momentous"], (con, cur))
        con.close()

        await self.app.main_window.info_dialog("Success", "To-Do database was successfully reset.")


    def task_type_change(self, widget):
        if self.tt_change:
            id = widget.id.split()[0]
            dd_widget = self.widgets[f"{id} task duedate"]
            self.dd_change = False
            dd_widget.min = dd_widget.max = self.type_dates_dict[widget.value.lower()][1]
            dd_widget.refresh()


    def duedate_change(self, widget):
        if self.dd_change:
            id = widget.id.split()[0]
            tt_widget = self.widgets[f"{id} task type"]
            tt_widget.enabled = False
            self.tt_change = False
            for t in self.type_dates_dict:
                dates = self.type_dates_dict[t]
                if dates[0] <= widget.value <= dates[1]: 
                    tt_widget.value = t.capitalize()
                    break


    def clear_create_box(self):
        self.tt_change = self.dd_change = False

        self.create_input.value = ""
        self.create_tier.value = "Routine"
        self.create_urgency.value = "Low"
        self.create_type.value = "Daily"
        self.create_duedate.min = self.create_duedate.value = date.today()
        self.create_duedate.max = self.type_dates_dict["yearly"][1]
        self.create_type.enabled = True

        self.tt_change = self.dd_change = True


    def clear_edit_box(self):
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