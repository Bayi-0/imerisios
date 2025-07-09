import toga
from toga.style import Pack
from toga.constants import COLUMN, ROW, Direction
from datetime import date, timedelta
import sqlite3 as sql
from imerisios.mylib.tools import get_back_next_buttons, length_check, get_connection, close_connection, get_ranges, change_range, set_range, reverse_dict


class ToDo:
    def __init__(self, app, db_path):
        self.app = app
        self.db_path = db_path

        self.tab_on = ""

        self.strings = self.app.strings["todo"]
        self.strings_c = self.app.strings["common"]

        self.widgets_load_dicts = {}
        self.data = {
            "system": {
                "types": ["daily", "weekly", "monthly", "yearly"], 
                "tiers": ["routine", "challenging", "significant", "momentous"],
                "urgencies": ["low", "medium", "high"],
            },
            "localized": {
                "types": self.strings["types"],
                "tiers": self.strings["tiers"],
                "urgencies": self.strings["urgencies"],
            }
        }
        self.maps = {
            "localized_to_system": 
                {self.data["localized"]["types"][i]: self.data["system"]["types"][i] for i in range(len(self.data["localized"]["types"]))} |
                {self.data["localized"]["tiers"][i]: self.data["system"]["tiers"][i] for i in range(len(self.data["localized"]["tiers"]))} |
                {self.data["localized"]["urgencies"][i]: self.data["system"]["urgencies"][i] for i in range(len(self.data["localized"]["urgencies"]))},
            "num_to_name": {
                "tiers": {i + 1: self.data["system"]["tiers"][i] for i in range(len(self.data["system"]["tiers"]))},
                "urgencies": {i + 1: self.data["system"]["urgencies"][i] for i in range(len(self.data["system"]["urgencies"]))}
            }
        }
        self.maps["system_to_localized"] = reverse_dict(self.maps["localized_to_system"])
        self.maps["name_to_num"] = reverse_dict(self.maps["num_to_name"]["tiers"]) | reverse_dict(self.maps["num_to_name"]["urgencies"])
        self.widgets_dict = {"tasks":{}}
        
        self.type_dates_dict = {}
        self.task_history_load = set(self.data["system"]["tiers"])
        self.tt_change = self.dd_change = True


    @property
    def clrs(self):
        return self.app.clrs
    
    
    @property
    def today(self):
        return self.app.today
    

    def reg(self, widgets=[]):
        self.app.reg(widgets)
    

    def get_div(self, padding=0):
        return self.app.get_div(padding=padding)
    
    
    def get_add_edit_box(self):
        def get_label(txt):
            return toga.Label(
                txt, 
                style=Pack(padding=(18,18,0), font_size=14, color=self.clrs[2])
            )
        
        main_labels = []
        for t in ("add", "edit"):
            
            main_labels.append(
                toga.Label(
                    self.strings[f"{t}_label"], 
                    style=Pack(flex=0.09, padding=14, text_align="center", font_weight="bold", font_size=18, color=self.clrs[2])
                )
            )

        input_label = get_label(f"{self.strings['task']}:")
        self.widgets_dict["add_edit task input"] = toga.TextInput(
            id=f"add_edit input 80",
            placeholder=self.strings["task_input_placeholder"],
            on_change=length_check, 
            style=Pack(padding=(0,18,18), height=44, font_size=12, color=self.clrs[2], background_color=self.clrs[1])
        )
        
        tier_label = get_label(f"{self.strings['tier']}:")
        self.widgets_dict["add_edit tier selection"] = toga.Selection(
            items=self.data["localized"]["tiers"],
            style=Pack(padding=(0,18,18), height=44)
        )
        
        urgency_label = get_label(f"{self.strings['urgency']}:")
        self.widgets_dict["add_edit urgency selection"] = toga.Selection(
            items=self.data["localized"]["urgencies"],
            style=Pack(padding=(0,18,18), height=44)
        )
        
        type_label = get_label(f"{self.strings['type']}:")
        self.widgets_dict["add_edit type selection"] = toga.Selection(
            id="add_edit type", 
            items=self.data["localized"]["types"], 
            on_change=self.task_type_change,
            style=Pack(padding=(0,18,18), height=44)
        )

        duedate_label = get_label(f"{self.strings['due']}:")
        self.widgets_dict["add_edit duedate date"] = toga.DateInput(
            id="add_edit duedate date", 
            min=self.today, 
            max=self.today, 
            on_change=self.duedate_change,
            style=Pack(padding=(0,18), color=self.clrs[2])
        )

        reset_button = toga.Button(
            self.strings["reset_type_date"], 
            id="add_edit reset button",
            on_press=self.reset_type_date, 
            style=Pack(padding=(4,4,14), height=44, font_size=13, color=self.clrs[2], background_color=self.clrs[1])
        )
        
        top_chld = [
            input_label, self.widgets_dict["add_edit task input"], self.get_div((0,80)),
            tier_label, self.widgets_dict["add_edit tier selection"], self.get_div((0,80)),
            urgency_label, self.widgets_dict["add_edit urgency selection"], self.get_div((0,80)),
            type_label, self.widgets_dict["add_edit type selection"], self.get_div((0,80)),
            duedate_label, self.widgets_dict["add_edit duedate date"], reset_button
        ]
        top_box = toga.Box(
            children=top_chld, 
            style=Pack(direction=COLUMN, flex=0.73)
        )
        top_container = toga.ScrollContainer(content=top_box, horizontal=False, style=Pack(flex=0.73))
        
        
        add_button = toga.Button(
            self.strings_c["add"], on_press=self.add_task, 
            style=Pack(height=120, padding=11, font_size=18, color=self.clrs[2], background_color=self.clrs[1])
        )
        add_bottom_box = toga.Box(children=[add_button], style=Pack(direction=COLUMN))

        remove_button = toga.Button(
            self.strings_c["remove"], on_press=self.remove_task_dialog, 
            style=Pack(flex=0.5, height=120, padding=(11,4,11,11), font_size=18, color=self.clrs[2], background_color=self.clrs[1])
        )
        save_button = toga.Button(
            self.strings_c["save"], on_press=self.save_task, 
            style=Pack(flex=0.5, height=120, padding=(11,11,11,4), font_size=18, color=self.clrs[2], background_color=self.clrs[1])
        )
        edit_bottom_box = toga.Box(children=[remove_button, save_button], style=Pack(direction=ROW))

        self.widgets_load_dicts["add box"] = add_chld = [
            main_labels[0], self.get_div(), 
            top_container, self.get_div(), 
            add_bottom_box
        ]
        self.widgets_load_dicts["edit box"] = edit_chld = [
            main_labels[1], self.get_div(), 
            top_container, self.get_div(), 
            edit_bottom_box
        ]

        self.widgets_dict["add_edit box"] = toga.Box(
            style=Pack(direction=COLUMN, background_color=self.clrs[0])
        )

        self.reg(top_chld + add_chld + edit_chld + [self.widgets_dict["add_edit box"], add_button, remove_button, save_button])
        
        return self.widgets_dict["add_edit box"]


    def get_list_history_box(self):
        def get_container(todo):
            if todo:
                string = "todo"
                value_type = "types"
                value_type_singular = "type"
            else:
                string = "history"
                value_type = "tiers"
                value_type_singular = "tier"
            boxes = []
            for i in range(len(self.data["system"][value_type])):
                t = self.data["system"][value_type][i]
                count_label_txt = self.strings[f"{value_type_singular}_labels"][i]

                main_label = toga.Label(
                    self.strings[f"{string}_list"], 
                    style=Pack(padding=(14,20), text_align="center", font_weight="bold", font_size=18, color=self.clrs[2])
                )

                self.widgets_dict[f"{t} count label"] = toga.Label(count_label_txt, style=Pack(flex=0.5, padding=10, font_size=14, color=self.clrs[2]))
                self.widgets_dict[f"{t} count divider"] = toga.Divider(direction=Direction.VERTICAL, style=Pack(height=49, background_color=self.clrs[1]))
                self.widgets_dict[f"{t} count box"] = toga.Box(id=f"{t} count box", style=Pack(direction=ROW))
                
                back_next_buttons = get_back_next_buttons(id=t, func=lambda button: change_range(button, widgets=self.widgets_dict), color=self.clrs[2], background_color=self.clrs[1])

                self.widgets_dict[f"{t} range"] = toga.Selection(
                    id=f"{t} range", 
                    on_change=self.load_tasks,
                    style=Pack(flex=0.6, padding=4, height=44)
                )

                range_box = toga.Box(
                    children=[back_next_buttons[0], self.widgets_dict[f"{t} range"], back_next_buttons[1]],
                    style=Pack(direction=ROW)
                )
                
                self.widgets_dict[f"{t} no_tasks label"] = toga.Label(
                    self.strings["no_tasks_message"],
                    style=Pack(padding=10, font_size=12, color=self.clrs[2])
                )

                self.widgets_dict[f"{t} box"] = toga.Box(id=f"{t} box", style=Pack(direction=COLUMN))
                self.widgets_dict[f"{t} container"] = toga.ScrollContainer(
                    content=self.widgets_dict[f"{t} box"], 
                    horizontal=False, style=Pack(flex=0.9)
                )

                chld = [
                    main_label, self.get_div(), 
                    self.widgets_dict[f"{t} count box"], self.get_div(), 
                    range_box, self.get_div(),
                    self.widgets_dict[f"{t} container"]
                ]
                box = toga.Box(
                    children=chld,
                    style=Pack(direction=COLUMN, background_color=self.clrs[0])
                )

                self.reg(back_next_buttons + chld + [box, self.widgets_dict[f"{t} count label"], self.widgets_dict[f"{t} count divider"]])

                boxes.append(box)

            # final container 
            icons = [toga.Icon(f"resources/images/todo/{t}.png") for t in self.data["system"][value_type]]

            container = toga.OptionContainer(
                content=[toga.OptionItem(self.data["localized"][value_type][i], boxes[i], icon=icons[i]) for i in range(len(self.data["localized"][value_type]))]
            )

            return container

        list_container = get_container(True)
        history_container = get_container(False)

        return (list_container, history_container)

    def setup_todo(self):
        list_box, history_box = self.get_list_history_box()
        add_edit_box = self.get_add_edit_box()

        con, cur = get_connection(self.db_path)
        cur.executescript("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL,
                tier INTEGER CHECK(tier IN (1, 2, 3, 4)) NOT NULL,  -- 1=routine, 2=challenging, 3=significant, 4=momentous
                urgency INTEGER CHECK(urgency IN (1, 2, 3)),  -- 1=low, 2=medium, 3=high
                created_date DATE DEFAULT (date('now', 'localtime')),
                due_date DATE,
                completed_date DATE
            );

            CREATE INDEX IF NOT EXISTS idx_tasks_tier ON tasks(tier);
            CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);
            CREATE INDEX IF NOT EXISTS idx_tasks_completed_date ON tasks(completed_date);    
        """)
        con.commit()

        self.update_todo()
        self.load_tasks(types=self.data["system"]["types"], con_cur=(con, cur))

        con.close()

        return list_box, history_box, add_edit_box


    def update_todo(self, day_change=False):
        weekdays_left = 7 - self.today.isocalendar().weekday if self.today.isocalendar().weekday != 7 else 7
        weekly_max_date = self.today + timedelta(days=weekdays_left)

        temp = weekly_max_date + timedelta(days=1)
        monthly_month = temp.month + 1 if temp.month != 12 else 1
        monthly_year = temp.year if monthly_month != 1 else temp.year + 1
        monthly_max_date = date(monthly_year, monthly_month, 1) - timedelta(days=1)

        yearly_max_date = date((monthly_max_date+timedelta(days=1)).year, 12, 31)

        self.type_dates_dict = {
            "daily": (self.today, self.today), 
            "weekly": (self.today+timedelta(days=1), weekly_max_date),
            "monthly": (weekly_max_date+timedelta(days=1), monthly_max_date),
            "yearly": (monthly_max_date+timedelta(days=1), yearly_max_date)
        }
        
        if day_change:
            self.app.setup_todo = True

    
    def todo_get_data(self, types: list=[], tiers: list=[], con_cur=None):
        con, cur = get_connection(self.db_path, con_cur)

        for t in types:
            dates = self.type_dates_dict[t]
            if t == "daily":
                dates = ("0001-01-01", dates[1])

            cur.execute("""
                SELECT id, task, tier, urgency, created_date, due_date FROM tasks
                WHERE due_date >= ? AND due_date <= ?
                    AND completed_date IS NULL
                ORDER BY
                    due_date ASC,
                    URGENCY DESC;
            """, dates)
            tasks = cur.fetchall()

            cur.execute("""
                SELECT COUNT(*) FROM tasks
                WHERE due_date >= ? AND due_date <= ?
                    AND completed_date IS NULL;
            """, dates)
            count = cur.fetchone()[0]

            self.data[t] = (tasks, count)

        for t in tiers:
            cur.execute("""
                SELECT id, task, created_date, completed_date FROM tasks
                WHERE tier IS ? AND completed_date IS NOT NULL
                ORDER BY completed_date DESC;
            """, (self.maps["name_to_num"][t],))
            tasks = cur.fetchall()

            cur.execute("""
                SELECT COUNT(*) FROM tasks
                WHERE tier IS ? AND completed_date IS NOT NULL;
            """, (self.maps["name_to_num"][t],))
            count = cur.fetchone()[0]

            self.data[t] = (tasks, count)

        close_connection(con, con_cur)


    async def add_task(self, widget):
        if inputs := self.get_add_edit_values():
            con, cur = get_connection(self.db_path)
            
            cur.execute("""
                INSERT INTO tasks (task, tier, urgency, due_date)
                VALUES (?, ?, ?, ?);
            """, (inputs[0], inputs[1], inputs[2], inputs[3]))

            con.commit()

            self.load_tasks(types=[inputs[5]], con_cur=(con, cur))
            con.close()

            self.app.open_todo(widget, inputs[4])


    async def done_task_dialog(self, widget):
        self.temp_task_id = int(widget.id.split()[0])
        result = await self.app.dialog(
            toga.QuestionDialog(
                self.strings_c["confirmation"], 
                self.strings["complete_question"].format(id=self.temp_task_id)
            )
        )
        if result:
            await self.done_task()


    async def edit_task_dialog(self, widget):
        self.temp_task_id = int(widget.id.split()[0])
        result = await self.app.dialog(
            toga.QuestionDialog(
                self.strings_c["edit"], 
                self.strings["edit_question"]
            )
        )
        if result:
            await self.app.open_edit_task()


    async def done_task(self):
        id = self.temp_task_id
        con, cur = get_connection(self.db_path)

        cur.execute("""
            SELECT due_date, tier FROM tasks
            WHERE id = ?;
        """, (id,))
        due_date, tier = cur.fetchone()
        task_type = self.determine_type(due_date)

        cur.execute("""
            UPDATE tasks
            SET completed_date = date('now', 'localtime'), urgency = NULL, due_date = NULL
            WHERE id = ?;
        """, (id,))
        
        con.commit()

        if id in self.widgets_dict["tasks"]:
            del self.widgets_dict["tasks"][id]
            del self.widgets_dict["tasks"][f"{id} task button"]

        self.load_tasks(types=[task_type], con_cur=(con, cur))

        self.task_history_load.add(self.maps["num_to_name"]["tiers"][tier])

        con.close()


    async def save_task(self, widget):
        if inputs := self.get_add_edit_values():
            id = self.temp_task_id

            con, cur = get_connection(self.db_path)

            cur.execute("""
                UPDATE tasks
                SET task = ?, tier = ?, urgency = ?, due_date = ?
                WHERE id = ?;
            """, (inputs[0], inputs[1], inputs[2], inputs[3], id,))
            con.commit()

            if id in self.widgets_dict["tasks"]:
                del self.widgets_dict["tasks"][id]

            temp = [inputs[5]]
            task_types = temp if self.temp_task_type in temp else temp+[self.temp_task_type]
            self.load_tasks(types=task_types, con_cur=(con, cur))

            con.close()

            self.app.open_todo(widget, inputs[4])


    async def remove_task_dialog(self, widget):
        result = await self.app.dialog(
            toga.QuestionDialog(
                self.strings_c["confirmation"], 
                self.strings["remove_question"]
            )
        )
        if result:
            await self.remove_task()


    async def remove_task(self):
        id = self.temp_task_id

        con, cur = get_connection(self.db_path)
        
        cur.execute("""
            SELECT due_date FROM tasks
            WHERE id = ?;
        """, (id,))
        due_date = cur.fetchone()[0]
        task_type = self.determine_type(due_date)

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

        self.app.open_todo(None, tab=self.maps["system_to_localized"][task_type])


    def load_tasks(self, widget=None, types: list=[], tiers: list=[], con_cur=None):
        self.todo_get_data(types, tiers, con_cur)

        for t in types + tiers:
            data = self.data[t]

            todo = t in self.data["system"]["types"]
            number_str = "pending" if todo else "completed"
            if not todo:
                self.task_history_load.clear()

            items = get_ranges(data[0])
            set_range(self.widgets_dict[f"{t} range"], items)

            count_box = self.widgets_dict[f"{t} count box"]
            count_box.clear()
            
            number_label = toga.Label(f"{self.strings[number_str]}: {data[1]}", style=Pack(flex=0.5, padding=10, font_size=14, color=self.clrs[2]))
            chld = [
                self.widgets_dict[f"{t} count label"],
                self.widgets_dict[f"{t} count divider"],
                number_label
            ]
            for c in chld:
                count_box.add(c)

            self.reg([number_label])

        if widget:
            widget_id = widget.id.split()

            t = widget_id[0]
            button = t in self.data["system"]["types"]

            data = self.data[t][0]
            list_box = self.widgets_dict[f"{t} box"]
            list_box.clear()

            start, end = [int(i) for i in widget.value.split('–')]
            if start == 0 and end == 0:
                list_box.add(self.widgets_dict[f"{t} no_tasks label"])
            else:
                for i in range(start-1, end):
                    task = data[i]
                    id = task[0]
                    if id not in self.widgets_dict["tasks"]:
                        task_box = self.get_task_box(task, button=button)
                        self.widgets_dict["tasks"][id] = task_box
                    list_box.add(self.widgets_dict["tasks"][id])
            
            self.widgets_dict[f"{t} container"].position = toga.Position(0,0)


    async def reset_todo_dialog(self):
        result = await self.app.dialog(
            toga.QuestionDialog(
                self.strings_c["confirmation"], self.strings["reset_question"]
            )
        )
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
                tier INTEGER CHECK(tier IN (1, 2, 3, 4)) NOT NULL,  -- 1=routine, 2=challenging, 3=significant, 4=momentous
                urgency INTEGER CHECK(urgency IN (1, 2, 3)),  -- 1=low, 2=medium, 3=high
                created_date DATE DEFAULT (date('now', 'localtime')),
                due_date DATE,
                completed_date DATE
            );

            CREATE INDEX idx_tasks_tier ON tasks(tier);
            CREATE INDEX idx_tasks_due_date ON tasks(due_date);
            CREATE INDEX idx_tasks_completed_date ON tasks(completed_date);    
        """)
        con.commit()
        con.close()

        self.app.setup_ui(todo=True)
        
        await self.app.dialog(
            toga.InfoDialog(
                self.strings_c["success"], self.strings["reset_success"]
            )
        )


    def task_type_change(self, widget):
        if self.tt_change:
            task_type = self.maps["localized_to_system"][widget.value]
            dd_widget = self.widgets_dict["add_edit duedate date"]
            self.dd_change = False
            dd_widget.min = dd_widget.max = self.type_dates_dict[task_type][1]
            dd_widget.refresh()


    def duedate_change(self, widget):
        if self.dd_change:
            tt_widget = self.widgets_dict["add_edit type selection"]
            tt_widget.enabled = False
            self.tt_change = False
            for t in self.type_dates_dict:
                dates = self.type_dates_dict[t]
                if dates[0] <= widget.value <= dates[1]: 
                    tt_widget.value = self.maps["system_to_localized"][t]
                    break


    def clear_add_box(self):
        self.tt_change = self.dd_change = False

        data = self.data["localized"]
        self.widgets_dict["add_edit task input"].value = ""
        self.widgets_dict["add_edit tier selection"].value = data["tiers"][0]
        self.widgets_dict["add_edit urgency selection"].value = data["urgencies"][0]
        self.widgets_dict["add_edit type selection"].value = data["types"][0]
        self.widgets_dict["add_edit duedate date"].min = self.widgets_dict["add_edit duedate date"].value = self.today
        self.widgets_dict["add_edit duedate date"].max = self.type_dates_dict["yearly"][1]
        self.widgets_dict["add_edit type selection"].enabled = True

        self.tt_change = self.dd_change = True


    def load_edit_box(self):
        con, cur = get_connection(self.db_path)

        cur.execute("""
            SELECT task, tier, urgency, due_date FROM tasks
            WHERE id = ?;
        """, (self.temp_task_id,))
        task, tier, urgency, due_date = cur.fetchone()
        
        con.close()
        
        task_type = self.determine_type(due_date)

        self.tt_change = self.dd_change = False
        self.temp_task_type = task_type
        self.widgets_dict["add_edit task input"].value = task
        self.widgets_dict["add_edit tier selection"].value = self.data["localized"]["tiers"][tier - 1]
        self.widgets_dict["add_edit urgency selection"].value = self.data["localized"]["urgencies"][urgency - 1]
        self.widgets_dict["add_edit type selection"].value = self.maps["system_to_localized"][task_type]
        self.widgets_dict["add_edit duedate date"].min = self.today
        self.widgets_dict["add_edit duedate date"].max = self.type_dates_dict["yearly"][1]
        self.widgets_dict["add_edit duedate date"].value = due_date

        self.widgets_dict["add_edit type selection"].enabled = True

        self.tt_change = self.dd_change = True


    def get_task_box(self, task, button=True):
        id = task[0]

        if button:
            if f"{id} task button" not in self.widgets_dict["tasks"]:
                done = toga.Button(
                    self.strings["done"], id=f"{task[0]} task done button", on_press=self.done_task_dialog, 
                    style=Pack(flex=0.5, height=55, font_size=9, color=self.clrs[2], background_color=self.clrs[1])
                )
                edit = toga.Button(
                    self.strings["edit"], id=f"{task[0]} task edit button", on_press=self.edit_task_dialog, 
                    style=Pack(flex=0.5, height=55, font_size=9, color=self.clrs[2], background_color=self.clrs[1])
                )
                self.widgets_dict["tasks"][f"{task[0]} task button"] = toga.Box(
                    children=[done, edit],
                    style=Pack(direction=COLUMN, padding=(4,0), height=110, width=104)
                )
                22
                self.reg([done, edit])
            bottom_str = f"{self.strings['tier']}: {self.data['localized']['tiers'][task[2] - 1]}  |  {self.strings['urgency']}: {self.data['localized']['urgencies'][task[3] - 1]}\n{self.strings_c['added']}: {task[4]}  |  {self.strings['due']}: {task[5]}"
        else:
            bottom_str = f"{self.strings_c['added']}: {task[2]}  |  {self.strings['completed']}: {task[3]}"
            
        id_label = toga.Label(
            f"[{id:06d}]", 
            style=Pack(padding=4, font_size=10, color=self.clrs[2])
        )
        
        task_rows = self.format_task(task[1])
        main_label = toga.Label(
            f"{task_rows[0]}\n{task_rows[1]}", 
            style=Pack(padding=4, font_size=11, font_weight="bold", color=self.clrs[2])
        )
        
        bottom_label = toga.Label(
            bottom_str, 
            style=Pack(padding=4, font_size=10, color=self.clrs[2])
        )
        
        task_label_chld = [id_label, main_label, bottom_label]
        task_label_box = toga.Box(children=task_label_chld, style=Pack(direction=COLUMN, flex=0.85))

        children = [task_label_box,]
        children += [self.widgets_dict["tasks"][f"{id} task button"],] if button else []

        div = self.get_div()
        task_box = toga.Box(children=children, style=Pack(direction=ROW))
        task_box = toga.Box(children=[task_box, div], style=Pack(direction=COLUMN))
        
        self.reg(task_label_chld + [div])

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

            
    def reset_type_date(self, widget):
        self.dd_change = self.tt_change = False

        w = self.widgets_dict["add_edit type selection"]
        w.value = self.data["localized"]["types"][0]
        w.enabled = True

        w = self.widgets_dict["add_edit duedate date"]
        w.min = w.value = self.today
        w.max = self.type_dates_dict["yearly"][1]

        self.dd_change = self.tt_change = True

    
    def determine_type(self, due_date):
        due_date = date.fromisoformat(due_date)
        if due_date <= self.today:
            task_type = self.data["system"]["types"][0]
        else:
            for t in self.data["system"]["types"][1:]:
                if self.type_dates_dict[t][0] <= due_date <= self.type_dates_dict[t][1]:
                    task_type = t
                    break
        
        return task_type
    

    def get_add_edit_values(self):
        if task := self.widgets_dict["add_edit task input"].value.strip():
            tier = self.maps["name_to_num"][self.maps["localized_to_system"][self.widgets_dict["add_edit tier selection"].value]]
            urgency = self.maps["name_to_num"][self.maps["localized_to_system"][self.widgets_dict["add_edit urgency selection"].value]]
            due_date = self.widgets_dict["add_edit duedate date"].value
            task_type = self.widgets_dict["add_edit type selection"].value
            task_type_system = self.maps["localized_to_system"][task_type]

            return (task, tier, urgency, due_date, task_type, task_type_system)
        else:
            return None
    

    def set_tab_on(self, tab):
        if tab == "add":
            self.clear_add_box()
        else:
            self.load_edit_box()
        if self.tab_on != tab:
            self.tab_on = tab
            box = self.widgets_dict["add_edit box"]
            box.clear()
            for w in self.widgets_load_dicts[f"{tab} box"]:
                box.add(w)