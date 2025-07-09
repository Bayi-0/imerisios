import toga
from toga.style import Pack
from toga.constants import COLUMN, ROW
from datetime import date, timedelta
import sqlite3 as sql
from collections import defaultdict
import calendar
from imerisios.mylib.tools import get_back_next_buttons, reverse_dict, length_check, get_connection, close_connection, create_calendar_image, get_ranges, change_range, set_range


class Habits:
    def __init__(self, app, db_path, img_path):
        self.app = app 
        self.db_path = db_path
        self.img_path = img_path

        self.strings = self.app.strings["habit"]
        self.strings_c = self.app.strings["common"]

        self.widgets_dict = {"habits": {}}

        self.data = {
            "states": ["success", "failure", "skip"],
            "phases": ["before_noon", "after_noon", "not_specified", "completed"],
            "track": ["tracked", "untracked"],
            "state images": [f"resources/images/habit/{s}.png" for s in ("success", "failure", "skip")]
        }

        self.maps = {
            "num_to_name": {
                "month": {i: calendar.month_name[i] for i in range(1, 13)},
                "state": {3: "success", 1: "failure", 2: "skip"},
                "phase": {1: "before_noon", 2: "after_noon", None: "not_specified"}
            },
            "localized_to_system": {k: v for k, v in zip(self.strings_c["months"], calendar.month_name[1:])} | {self.strings[self.data["phases"][i]]: self.data["phases"][i] for i in range(3)},
            "name_to_num": {}
        }
        for key in self.maps["num_to_name"].keys():
            self.maps["name_to_num"] |= reverse_dict(self.maps["num_to_name"][key])

        self.details_setup = True
        self.more_setup = True
        

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


    def get_tracker_box(self):
        label = toga.Label(
            self.strings["tracker_label"], 
            style=Pack(padding=14, text_align="center", font_weight="bold", font_size=18, color=self.clrs[2])
        )
        
        self.widgets_dict["tracker date"] = toga.DateInput(
            id="tracker date",
            on_change=self.load_habits, 
            style=Pack(flex=0.6, width=201, color=self.clrs[2])
        )
        
        back_next_buttons = get_back_next_buttons(id="tracker", func=self.change_date, color=self.clrs[2], background_color=self.clrs[1])
        
        date_chld = [back_next_buttons[0], self.widgets_dict["tracker date"], back_next_buttons[1]]
        date_input_box = toga.Box(
            children=date_chld, 
            style=Pack(direction=ROW)
        )
        
        today_button = toga.Button(
            self.strings_c["today"], on_press=self.habit_today, 
            style=Pack(flex=0.4, padding=4, height=44, font_size=13, color=self.clrs[2], background_color=self.clrs[1])
        )

        date_box = toga.Box(
            children=[date_input_box, today_button], 
            style=Pack(direction=COLUMN)
        )

        self.widgets_dict["tracker list box"] = toga.Box(style=Pack(direction=COLUMN))
        self.widgets_dict["tracker list container"] = toga.ScrollContainer(
            content=self.widgets_dict["tracker list box"], 
            horizontal=False, style=Pack(flex=0.8)
        )

        chld = [
            label, self.get_div(), 
            date_box, self.get_div(), 
            self.widgets_dict["tracker list container"]
        ]
        tracker_box = toga.Box(
            children=chld, 
            style=Pack(direction=COLUMN, background_color=self.clrs[0])
        )
        
        # day phase labels
        phase_labels = []
        for phase in self.data["phases"]:
            self.widgets_dict[f"{phase} label"] = l = toga.Label(
                self.strings[phase], 
                style=Pack(padding=10, font_size=14, text_align="center", color=self.clrs[2])
            )
            self.widgets_dict[f"{phase} divider"] = d = self.get_div()
            phase_labels.extend([l,d])

        # no habits label
        self.widgets_dict["tracker no_habits label"] = toga.Label(
            self.strings["tracker_no_habits"],
            style=Pack(padding=10, font_size=12, color=self.clrs[2])
        )

        self.reg(date_chld + chld + phase_labels + [today_button, tracker_box, self.widgets_dict["tracker no_habits label"]])

        return tracker_box

    
    def get_details_box(self):
        for t in ("tracked", "untracked"):
            label = toga.Label(
                self.strings["details_label"][0 if t == "tracked" else 1], 
                style=Pack(padding=14, text_align="center", font_weight="bold", font_size=18, color=self.clrs[2])
            )

            back_next_buttons = get_back_next_buttons(id=t, func=lambda button: change_range(button, widgets=self.widgets_dict), color=self.clrs[2], background_color=self.clrs[1])
            
            self.widgets_dict[f"{t} range"] = toga.Selection(
                id=f"{t} range", 
                on_change=self.load_habits,
                style=Pack(flex=0.6, padding=4, height=44)
            )
            self.widgets_dict[f"details {t} range box"] = toga.Box(
                children=[back_next_buttons[0], self.widgets_dict[f"{t} range"], back_next_buttons[1]],
                style=Pack(direction=ROW)
            )
            
            self.widgets_dict[f"details {t} list box"] = toga.Box(style=Pack(direction=COLUMN))
            self.widgets_dict[f"details {t} list container"] = toga.ScrollContainer(
                content=self.widgets_dict[f"details {t} list box"], 
                horizontal=False, style=Pack(flex=0.8)
            )

            chld = [
                label, self.get_div(), 
                self.widgets_dict[f"details {t} range box"], self.get_div(),
                self.widgets_dict[f"details {t} list container"]
            ]
            self.widgets_dict[f"details {t} box"] = toga.Box(
                children=chld, 
                style=Pack(direction=COLUMN, background_color=self.clrs[0])
            )
            
            self.widgets_dict[f"details {t} no_habits label"] = toga.Label(
                self.strings["details_no_habits"],
                style=Pack(padding=10, font_size=12, color=self.clrs[2])
            )

            self.reg(chld + back_next_buttons + [self.widgets_dict[f"details {t} box"], self.widgets_dict[f"details {t} no_habits label"]])

        # details box
        details_box = toga.OptionContainer(
            content=[
                toga.OptionItem(self.strings["tracked"], self.widgets_dict["details tracked box"], icon=toga.Icon(self.data["state images"][0])),
                toga.OptionItem(self.strings["untracked"], self.widgets_dict["details untracked box"], icon=toga.Icon(self.data["state images"][1]))
            ]
        )

        return details_box


    def get_add_habit_box(self):
        def get_quotes_box(quotes):
            box = toga.Box(style=Pack(direction=COLUMN, flex=0.26, padding=4))
            for i in range(0, len(quotes)-1, 2):
                l1 = toga.Label(quotes[i], style=Pack(padding=(4,4,0), font_size=7, color=self.clrs[2]))
                l2 = toga.Label(
                    quotes[i+1], 
                    style=Pack(padding=(0,4,4), text_align="right", font_size=7, font_style="italic", color=self.clrs[2])
                )
                box.add(l1)
                box.add(l2)
                self.reg([l1, l2])
            return box
        
        
        label = toga.Label(
            self.strings["add_label"], 
            style=Pack(flex=0.9, padding=14, text_align="center", font_weight="bold", font_size=18, color=self.clrs[2]))

        quotes_top = [
            "“A habit, if not resisted, soon becomes necessity.”", "— Haruki Murakami, The Wind-Up Bird Chronicle",
            "“A first sign of the beginning of understanding is the wish to die.”", "— Franz Kafka, The Zürau Aphorisms", 
            "“The scariest moment is always just before you start.”", "— Stephen King, On Writing: A Memoir of the Craft",
            "“If you only read the books that everyone else is reading, you can only think what everyone else\nis thinking.”", "— Toru Watanabe, Norwegian Wood by Haruki Murakami",
            "“Pain is inevitable. Suffering is optional.”", "— Haruki Murakami, What I Talk About When I Talk About Running",
            "“The world doesn't give you what you want. It gives you what you take.”", "— Eithan Arelius, Cradle by Will Wight",
            "“When the soul suffers too much, it develops a taste for misfortune.”", "— Albert Camus, The First Man"
        ]
        quotes_bottom = [
            "“What we seek is some kind of compensation for what we put up with.”", "— Narrator, The Rat by Haruki Murakami",
            "“It has long been an axiom of mine that the little things are infinitely the most important.”", "— Sherlock Holmes, by Arthur Conan Doyle",
            "“The habit of hoping always for better things is actually an obstacle to success.”", "— Stendhal, The Red and the Black",
            "“There is always a philosophy for lack of courage.”", "— Albert Camus, Notebooks (1942-1951)",
            "“If you're going to do something that's going to slow down your work, just as well put off doing\nit as long as possible.”", "— John Wyndham, The Chrysalids",
            "“You have to decide who you want to be. Before someone else does it for you.”", "— Eithan Arelius, Cradle by Will Wight",
            "“I'm not afraid of death; I just don't want to be there when it happens.”", "— Toru Watanabe, Norwegian Wood by Haruki Murakami (originally Woody Allen)"
        ]
        quotes_box_top = get_quotes_box(quotes_top)
        quotes_box_bottom = get_quotes_box(quotes_bottom)

        self.widgets_dict["add input"] = toga.TextInput(
            id="add input 34",
            placeholder=self.strings["add_input_placeholder"],
            on_change=length_check, 
            style=Pack(padding=(11,18,0), height=44, font_size=12, color=self.clrs[2], background_color=self.clrs[1])
        )
        add_button = toga.Button(
            self.strings_c["add"], on_press=self.add_habit, 
            style=Pack(flex=0.5, height=120, padding=(8,11,18), font_size=18, color=self.clrs[2], background_color=self.clrs[1])
        )
        add_chld = [self.widgets_dict["add input"], add_button]
        add_box = toga.Box(
            children=add_chld,
            style=Pack(direction=COLUMN, flex=0.2)
        )

        chld = [
            label, self.get_div(), 
            quotes_box_top, self.get_div(), 
            add_box, self.get_div(),
            quotes_box_bottom
        ]
        add_habit_box = toga.Box(
            children=chld, 
            style=Pack(direction=COLUMN, background_color=self.clrs[0])
        )

        self.reg(chld + add_chld + [add_habit_box])

        return add_habit_box
    

    def get_more_box(self):
        self.widgets_dict["more box"] = toga.Box(
            style=Pack(direction=COLUMN, background_color=self.clrs[0])
        )
        more_container = toga.ScrollContainer(content=self.widgets_dict["more box"], horizontal=False)

        self.reg([self.widgets_dict["more box"]])

        return more_container
    

    def setup_habits(self):
        tracker_box = self.get_tracker_box()
        details_box = self.get_details_box()
        add_habit_box = self.get_add_habit_box()
        more_box = self.get_more_box()
    
        con, cur = get_connection(self.db_path)
        cur.executescript("""
            CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            longest_streak INTEGER DEFAULT 0,
            created_date DATE DEFAULT (date('now', 'localtime')),
            completed_date DATE,
            day_phase INTEGER CHECK(day_phase IN (1, 2) OR day_phase IS NULL) -- 1=am, 2=pm
            );
            
            CREATE TABLE IF NOT EXISTS habit_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER NOT NULL,
            record_date DATE DEFAULT (date('now', 'localtime')),
            state INTEGER CHECK(state IN (1, 2, 3) OR state IS NULL), -- 1=failure, 2=skip, 3=success
            FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE ON UPDATE CASCADE
            );
                          
            CREATE INDEX IF NOT EXISTS idx_habit_records_state ON habit_records(state);
            CREATE INDEX IF NOT EXISTS idx_habit_records_date ON habit_records(record_date);    
        """)
        con.commit()

        self.update_habit(con_cur=(con, cur))

        con.close()

        return tracker_box, details_box, add_habit_box, more_box
    

    def update_habit(self, day_change=False, details=False, tracking=True, con_cur=None):
        con, cur = get_connection(self.db_path, con_cur)

        self.add_habit_records(load=False, con_cur=(con, cur))
        self.remove_habit_records((con, cur))
        if day_change:
            self.app.setup_habits = True
        else:
            self.habit_get_data(details=details, tracking=tracking, con_cur=(con, cur))
            
            self.load_habits(None, tracker=False, details=details)

            date_w = self.widgets_dict["tracker date"]
            date_w.max = date_w.value = self.today
            date_w.min = self.today - timedelta(days=6)

        close_connection(con, con_cur)
    

    def habit_get_data(self, dates=None, details=False, tracking=False, con_cur=None):
        con, cur = get_connection(self.db_path, con_cur)
        if dates is None:
            dates = [self.today - timedelta(days=i) for i in range(7)]
    
        for d in dates:
            iso = d.isoformat()
            self.data[iso] = {phase: [] for phase in self.data["phases"]}

            cur.execute("""
                SELECT habits.id, habits.name, habit_records.state, habits.day_phase
                FROM habits
                INNER JOIN habit_records ON habits.id = habit_records.habit_id
                WHERE habit_records.record_date = ? AND habit_records.state IS NULL
                ORDER BY LOWER(habits.name);   
            """, (d,))

            rows = cur.fetchall()

            for row in rows:
                day_phase = row[-1]
                self.data[iso][self.maps["num_to_name"]["phase"][day_phase]].append(row)
            
            cur.execute("""
                SELECT habits.id, habits.name, habit_records.state, habits.day_phase
                FROM habits
                INNER JOIN habit_records ON habits.id = habit_records.habit_id
                WHERE habit_records.record_date = ? AND habit_records.state IS NOT NULL
                ORDER BY 
                    habit_records.state,
                    LOWER(habits.name);   
            """, (d,))

            rows = cur.fetchall()

            self.data[iso]["completed"].extend(rows)
            
            for key in self.data["phases"]:
                for i in range(len(self.data[iso][key])):
                    cur.execute("""
                        SELECT state FROM habit_records
                        WHERE habit_id = ?
                        AND record_date <= ?
                        AND state IS NOT NULL
                        ORDER BY record_date DESC;
                    """, (self.data[iso][key][i][0], d,))
                    states = cur.fetchall()

                    streak = self.calculate_streak(states)

                    self.data[iso][key][i] = self.data[iso][key][i] + (streak,)

        if details:
            cur.execute("""
                SELECT id, name FROM habits
                WHERE completed_date IS NULL
                ORDER BY LOWER(name);
            """)
            self.data["tracked"] = cur.fetchall()

            cur.execute("""
                SELECT id, name FROM habits
                WHERE completed_date IS NOT NULL
                ORDER BY LOWER(name);
            """)
            self.data["untracked"] = cur.fetchall()

        if tracking:
            cur.execute("SELECT id, completed_date FROM habits;")
            self.data["tracking"] = {id:c for (id, c) in cur.fetchall()}

        close_connection(con, con_cur)


    def load_habits(self, widget, tracker=False, details=False):
        if tracker or (widget and widget.id == "tracker date"):
            list_box = self.widgets_dict["tracker list box"]
            list_box.clear()

            d = self.widgets_dict["tracker date"].value.isoformat()
            data = self.data[self.widgets_dict["tracker date"].value.isoformat()]
            any_habits = False
            if data:
                for key in self.data["phases"]:
                    if data[key]:
                        any_habits = True
                        list_box.add(self.widgets_dict[f"{key} label"], self.widgets_dict[f"{key} divider"])

                        for h in data[key]:
                            id = h[0]
                            if d not in self.widgets_dict["habits"]:
                                self.widgets_dict["habits"][d] = {}
                            if id not in self.widgets_dict["habits"][d]:
                                self.widgets_dict["habits"][d][id] = self.get_habit_box(h, d)
                            list_box.add(self.widgets_dict["habits"][d][id])
            if not any_habits:
                list_box.add(self.widgets_dict["tracker no_habits label"])
                
        if details:
            for t in self.data["track"]:
                data = self.data[t]

                items = get_ranges(data)
                set_range(self.widgets_dict[f"{t} range"], items)

        elif widget and widget.id.split()[0] in self.data["track"]:
            t = widget.id.split()[0]

            data = self.data[t]
            box = self.widgets_dict[f"details {t} list box"]
            box.clear()

            start, end = [int(i) for i in widget.value.split('–')]
            if start == 0 and end == 0:
                box.add(self.widgets_dict[f"details {t} no_habits label"])
            else:
                for i in range(start-1, end):
                    habit = data[i]
                    id = habit[0]
                    if id not in self.widgets_dict["habits"]:
                        self.widgets_dict["habits"][id] = self.get_habit_box(habit)
                    box.add(self.widgets_dict["habits"][id])
            
            self.widgets_dict[f"details {t} list container"].position = toga.Position(0,0)
                    

    def load_habit_more(self, id):
        f_size = 13

        def get_label(txt, padding=14, center=False):
            return toga.Label(
                txt, 
                style=Pack(padding=padding, text_align="center" if center else "left", font_size=f_size, color=self.clrs[2])
            )

        self.temp_habit_id = id

        self.widgets_dict["more box"].clear()

        con, cur = get_connection(self.db_path)

        cur.execute("""
            SELECT name, created_date, completed_date, longest_streak, day_phase FROM habits
            WHERE id = ?;
        """, (id,))
        name, added_date, stopped_date, longest_streak, day_phase = cur.fetchone()

        cur.execute("""
            SELECT COUNT(*) FROM habit_records
            WHERE habit_id = ? AND state IS NOT NULL;
        """, (id,))
        total_records = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(*) FROM habit_records
            WHERE habit_id = ? AND state = 3;
        """, (id,))
        total_success = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(*) FROM habit_records
            WHERE habit_id = ? AND state = 1;
        """, (id,))
        total_failure = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(*) FROM habit_records
            WHERE habit_id = ? AND state = 2;
        """, (id,))
        total_skip = cur.fetchone()[0]

        cur.execute("""
            WITH success_skip AS (
                SELECT COUNT(*) AS success_skip_count
                FROM habit_records
                WHERE habit_id = ? AND state IN (3, 2)
            ), 
            total AS (
                SELECT COUNT(*) AS total_count
                FROM habit_records
                WHERE habit_id = ?
            )
            SELECT 
                (success_skip.success_skip_count * 1.0 / total.total_count) * 100 AS success_skip_percent
            FROM success_skip, total;
        """, (id, id,))
        total_success_skip_percent = cur.fetchone()[0]

        min_days = {7: 3, 30: 12, 365: 60}  
        average_rates = []
        for period_length in [7, 30, 365]:
            if total_records >= min_days[period_length]:
                average_rates.append(round(total_success/total_records*period_length, 1))
            else:
                average_rates.append("N/A")

        cur.execute("""
            SELECT 
                strftime('%Y', record_date) AS year,
                strftime('%m', record_date) AS month,
                strftime('%d', record_date) AS day,
                state
            FROM habit_records
            WHERE habit_id = ?
            ORDER BY record_date;
        """, (id,))
        records = cur.fetchall()

        con.close()

        habit_records = defaultdict(lambda: defaultdict(dict))
        
        for year, month, day, state in records:
            year = int(year)
            month = int(month)
            day = int(day)
            habit_records[year][month][day] = state

        habit_more_label = toga.Label(
            f"{self.strings['habit']} [{id:06d}]\n{name}",
            style=Pack(padding=14, text_align="center", font_weight="bold", font_size=f_size+1, color=self.clrs[2])
        )
        self.widgets_dict["more label box"] = toga.Box(
            children=[habit_more_label],
            style=Pack(direction=COLUMN)
        )
        
        if self.more_setup:
            self.widgets_dict["more day_phase label"] = toga.Label(
                f"{self.strings['day_phase']}:", 
                style=Pack(flex=0.35, padding=(14,0,14,20), font_size=f_size, color=self.clrs[2])
            )
            self.widgets_dict["more day_phase select"] = toga.Selection(
                items=[self.strings["not_specified"], self.strings["before_noon"], self.strings["after_noon"]], 
                on_change=self.day_phase_change, 
                style=Pack(flex=0.65, padding=(4,14,0,8), height=44)
            )
        
            self.widgets_dict["more dates label"] = get_label(self.strings["dates"], center=True)

            self.widgets_dict["more total label"] = get_label(self.strings["total"], center=True)

            self.widgets_dict["more average label"] = get_label(self.strings["average_success_numbers"], center=True)
            
            self.widgets_dict["more calendar label"] = get_label(self.strings["record_calendar"], center=True)
            self.widgets_dict["more year label"] = toga.Label(
                f"{self.strings_c['year']}:", 
                style=Pack(flex=0.3, padding=(14,0,0,20), font_size=f_size, color=self.clrs[2])
            )
            self.widgets_dict["more year select"] = toga.Selection(style=Pack(flex=0.7, padding=(4,16,0), height=44))
            self.widgets_dict["more month label"] = toga.Label(
                f"{self.strings_c['month']}:", 
                style=Pack(flex=0.3, padding=(14,0,0,20), font_size=f_size, color=self.clrs[2])
            )
            self.widgets_dict["more month select"] = toga.Selection(style=Pack(flex=0.7, padding=(4,16,0), height=44))

            self.widgets_dict["more manage label"] = get_label(self.strings["manage"], center=True)
            self.widgets_dict["more rename input"] = toga.TextInput(
                id="rename input 34",
                on_change=length_check,
                placeholder=self.strings["rename_input_placeholder"], 
                style=Pack(padding=(8,11,0), height=44, font_size=12, color=self.clrs[2], background_color=self.clrs[1])
            )
            

            def get_button(txt, func, padding=(4,11,11,4), id=None):
                button = toga.Button(
                    txt, on_press=func, id=id,
                    style=Pack(flex=0.5, height=120, padding=padding, font_size=18, color=self.clrs[2], background_color=self.clrs[1])
                )

                return button
            
            self.widgets_dict["more rename button"] = get_button(self.strings["rename"], self.rename_habit_dialog, (0,11))
            self.widgets_dict["more remove button"] = get_button(self.strings_c["remove"], self.remove_habit_dialog, (4,4,11,11))
            self.widgets_dict["more stop button"] = get_button(self.strings["stop"], self.tracking_habit_dialog, id="habit stop button")
            self.widgets_dict["more resume button"] = get_button(self.strings["resume"], self.tracking_habit_dialog, id="habit resume button")

            self.reg(
                [self.widgets_dict[f"more {k} label"] for k in ("day_phase", "dates", "total", "average", "calendar", "year", "month", "manage")] +
                [self.widgets_dict["more rename input"]] +
                [self.widgets_dict[f"more {k} button"] for k in ("rename", "remove", "stop", "resume")]
            )

        self.widgets_dict["more day_phase select"].value = self.strings[self.maps["num_to_name"]["phase"][day_phase]]

        day_phase_box = toga.Box(
            children=[self.widgets_dict["more day_phase label"], self.widgets_dict["more day_phase select"]],
            style=Pack(direction=ROW)
        )    
        
        self.widgets_dict["more added label"] = get_label(f"{self.strings_c['added']}: {added_date}", padding=(14,20))
        stopped_label = get_label(f"{self.strings['stopped']}: {stopped_date or '—'}", padding=(0,20,14))

        self.widgets_dict["more dates box"] = toga.Box(
            children=[
                self.widgets_dict["more dates label"], self.get_div(padding=(0,80)), 
                self.widgets_dict["more added label"], 
                stopped_label
            ], 
            style=Pack(direction=COLUMN)
        )

        total_label = self.widgets_dict["more total label"]

        strs = self.strings["total_number_strs"]
        vals = [total_records, total_success, total_failure, total_skip]
        chld_top, chld_bottom = [], []
        for i in range(4):
            if i < 2:
                label = toga.Label(
                    f"{strs[i]}: {vals[i]}", 
                    style=Pack(flex=0.5, padding=14, text_align="center", font_size=f_size, color=self.clrs[2])
                )
                chld_top.append(label)
            else:
                label = toga.Label(
                    f"{strs[i]}: {vals[i]}", 
                    style=Pack(flex=0.5, padding=(0,14,14), text_align="center", font_size=f_size, color=self.clrs[2])
                )
                chld_bottom.append(label)

        total_top_box = toga.Box(children=chld_top, style=Pack(direction=ROW))
        total_bottom_box = toga.Box(children=chld_bottom, style=Pack(direction=ROW))
        
        total_box = toga.Box(
            children=[
                total_label, self.get_div(padding=(0,80)), 
                total_top_box, total_bottom_box
            ], 
            style=Pack(direction=COLUMN)
        )
        
        completion_rate_label = get_label(f"{self.strings['completion_rate']}: {round(total_success_skip_percent, 1)}%", padding=(14,20))
        longest_streak_label = get_label(f"{self.strings['longest_success']}: {longest_streak}", padding=(14,20))

        average_success_label = self.widgets_dict["more average label"]
        
        successes = []
        periods = [self.strings_c[s] for s in ("week", "month", "year")]
        for i in range(3):
            label = toga.Label(
                f"{periods[i]}: {average_rates[i]}", 
                style=Pack(flex=0.33, padding=8, text_align="center", font_size=f_size, color=self.clrs[2])
            )
            successes.append(label)
        average_rates_box = toga.Box(children=successes, style=Pack(direction=ROW))

        average_success_box = toga.Box(
            children=[
                average_success_label, self.get_div(padding=(0,80)),
                average_rates_box
            ], 
            style=Pack(direction=COLUMN)
        )
        
        record_calendar_label = self.widgets_dict["more calendar label"]
        year_select_label = self.widgets_dict["more year label"]
        year_select = self.widgets_dict["more year select"]
        year_select_box = toga.Box(
            children=[year_select_label, year_select],
            style=Pack(direction=ROW)
        )
        month_select_label = self.widgets_dict["more month label"]
        month_select = self.widgets_dict["more month select"]
        month_select_box = toga.Box(
            children=[month_select_label, month_select],
            style=Pack(direction=ROW)
        )
        record_calendar_box = toga.Box(
            children=[
                record_calendar_label, self.get_div(padding=(0,80)), 
                year_select_box, 
                month_select_box
            ],
            style=Pack(direction=COLUMN)
        )
        calendar_image_box = toga.Box(style=Pack(flex=1, padding=(4), height=280))
        
        habit_more_manage_label = self.widgets_dict["more manage label"] 

        self.widgets_dict["more rename input"].value = ""
        rename_button = self.widgets_dict["more rename button"]
        rename_box = toga.Box(
            children=[self.widgets_dict["more rename input"], rename_button], 
            style=Pack(direction=COLUMN, flex=0.3)
        )

        button = self.widgets_dict["more resume button"] if self.data["tracking"][id] else self.widgets_dict["more stop button"]
        self.widgets_dict["more button box"] = toga.Box(
            children=[self.widgets_dict["more remove button"], button],
            style=Pack(direction=ROW, flex=0.16)
        )
        habit_more_manage_box = toga.Box(
            children=[
                habit_more_manage_label, self.get_div(padding=(0,80)),
                rename_box, 
                self.widgets_dict["more button box"]
            ], 
            style=Pack(direction=COLUMN)
        )
        
        self.widgets_dict["more box"].add(
            self.widgets_dict["more label box"], self.get_div(), 
            day_phase_box, self.get_div(),
            self.widgets_dict["more dates box"], self.get_div(), 
            total_box, self.get_div(), 
            completion_rate_label, self.get_div(), 
            longest_streak_label, self.get_div(), 
            average_success_box, self.get_div(), 
            record_calendar_box, 
            calendar_image_box, self.get_div(),
            habit_more_manage_box
        )

        def year_change(widget):
            year = int(widget.value)
            month_select.year = year
            month_select.items = [self.strings_c["months"][m - 1] for m in sorted(habit_records[year], reverse=True)]

        def month_change(widget):
            calendar_image_box.clear()

            year = widget.year
            month = self.maps["name_to_num"][self.maps["localized_to_system"][widget.value]]
            create_calendar_image(year, month, self.img_path, habit_records[year][month])
            img = toga.ImageView(toga.Image(self.img_path), style=Pack(flex=1))

            calendar_image_box.add(img)
        
        year_select.on_change=year_change
        month_select.on_change=month_change

        year_select.items = sorted([y for y in habit_records], reverse=True)

        self.more_setup = False


    async def change_habit_state_dialog(self, widget):
        splt = widget.id.split()
        result = await self.app.dialog(
            toga.QuestionDialog(
                self.strings_c["confirmation"], 
                self.strings["change_state_question"].format(id=int(splt[0]), state=self.strings[splt[2]])
            )
        )
        if result:
            await self.change_habit_state(splt)


    async def change_habit_state(self, splt):
        habit_id = int(splt[0])
        state = self.maps["name_to_num"][splt[2]]
        record_date = self.widgets_dict["tracker date"].value

        con, cur = get_connection(self.db_path)
        
        cur.execute("""
            UPDATE habit_records
            SET state = ?
            WHERE habit_id = ? 
            AND record_date = ?;
        """, (state, habit_id, record_date,))
        con.commit()

        cur.execute("""
            SELECT state FROM habit_records
            WHERE habit_id = ?
            AND record_date <= ?
            AND state IS NOT NULL
            ORDER BY record_date DESC;
        """, (habit_id, self.today,))
        states = cur.fetchall()

        current_streak = self.calculate_streak(states)

        cur.execute("""
            SELECT longest_streak FROM habits
            WHERE id = ?;
        """, (habit_id,))
        longest_streak = cur.fetchone()[0]

        if current_streak > longest_streak:
            cur.execute("""
                UPDATE habits
                SET longest_streak = ?
                WHERE id = ?;
            """, (current_streak, habit_id,))
            con.commit()

        record_iso = record_date.isoformat()

        dates = [record_date,]
        if record_date != self.today:
            difference = (self.today-record_date).days
            for i in range(1, difference+1):
                dates.append(record_date+timedelta(days=i))
        for d in dates:
            d = d.isoformat()
            if d in self.widgets_dict["habits"]:
                if habit_id in self.widgets_dict["habits"][d]:
                    del self.widgets_dict["habits"][d][habit_id]
                    if d == record_iso:
                        del self.widgets_dict["habits"][d][f"{habit_id} habit state button"]

        self.habit_get_data(dates=dates, con_cur=(con, cur))
        self.load_habits(None, tracker=True)

        con.close()


    async def add_habit(self, widget):
        if habit_name := self.widgets_dict["add input"].value.strip():
            con, cur = get_connection(self.db_path)
            
            cur.execute("""
                SELECT id FROM habits
                WHERE name = ?;
                """, (habit_name,))
            if result := cur.fetchone():
                await self.app.dialog(toga.InfonDialog(self.strings["habit_already_exists"], self.strings["habit_already_uses"].format(id=result[0])))
                self.widgets_dict["add input"].value = ""
            else:
                cur.execute("""
                    INSERT INTO habits (name)
                    VALUES (?);
                    """, (habit_name,))
                con.commit()

                today = self.today

                self.add_habit_records(load=False, con_cur=(con, cur))
                self.habit_get_data(dates=[today], details=True, tracking=True, con_cur=(con, cur))

                self.widgets_dict["tracker date"].value = today
                self.load_habits(widget, tracker=False, details=True)
                self.app.open_habit_tracker(widget)

            con.close()
    

    def add_habit_records(self, dates=[], load=True, con_cur=None):
        dates += [self.today] if not dates else []

        con, cur = get_connection(self.db_path, con_cur)

        update_dates = []
        for d in dates:
            cur.execute("""
                SELECT habit_id FROM habit_records
                WHERE record_date IS ?;
            """, (d,))
            added = cur.fetchall()

            cur.execute("""
                SELECT id FROM habits
                WHERE completed_date IS NULL;
            """)
            tracked = cur.fetchall()

            ids = set(tracked) - set(added)

            if ids:
                values = [(id[0], d) for id in ids]
                cur.executemany("""
                    INSERT INTO habit_records (habit_id, record_date)
                    VALUES (?, ?);
                """, values)
                con.commit()

                update_dates.append(d)
            
        if load and update_dates:
            self.habit_get_data(dates=update_dates, con_cur=(con, cur))
            self.load_habits(None, tracker=True)

        close_connection(con, con_cur)


    def remove_habit_records(self, con_cur):
        con, cur = get_connection(self.db_path, con_cur)
        
        cur.execute("""
            DELETE FROM habit_records 
            WHERE state IS NULL 
            AND record_date <= date('now', '-7 days', 'localtime');
            """)
        con.commit()

        close_connection(con, con_cur)

    async def remove_habit_dialog(self, widget):
        result = await self.app.dialog(
            toga.QuestionDialog(
                self.strings_c["confirmation"], 
                self.strings["remove_habit_question"]
            )
        )
        if result:
            await self.remove_habit(self.temp_habit_id)


    async def remove_habit(self, id, open_details=True, con_cur=None):
        con, cur = get_connection(self.db_path, con_cur)
        cur.execute("""
            SELECT record_date FROM habit_records
            WHERE habit_id = ?
            AND record_date >= ?;
        """, (id, self.today-timedelta(days=6))) 
        dates = cur.fetchall()

        cur.execute("""
            DELETE FROM habits
            WHERE id = ?;
        """, (id,))
        con.commit()

        self.habit_get_data(dates=[date.fromisoformat(d[0]) for d in dates], details=True, con_cur=(con, cur))

        close_connection(con, con_cur)

        for d in dates:
            if d in self.widgets_dict["habits"]:
                if id in self.widgets_dict["habits"][d]:
                    del self.widgets_dict["habits"][d][id]
                    del self.widgets_dict["habits"][d][f"{id} habit state button"]
        if id in self.widgets_dict["habits"]:
            del self.widgets_dict["habits"][id]

        self.load_habits(None, tracker=True, details=True)

        if open_details:
            self.app.open_habit_details(None)


    async def tracking_habit_dialog(self, widget):
        stop = widget.id.split()[1] == "stop"
        word = 0 if stop else 1
        result = await self.app.dialog(
            toga.QuestionDialog(
                self.strings_c["confirmation"], 
                self.strings["tracking_habit_question"][word]
            )
        )
        if result:
            await self.tracking_habit(stop)

    
    async def tracking_habit(self, stop):
        con, cur = get_connection(self.db_path)

        id = self.temp_habit_id
        if stop:
            cur.execute("""
                UPDATE habits
                SET completed_date = ?
                WHERE id = ?;
            """, (self.today, id,))
        else:
            cur.execute("""
                UPDATE habits
                SET completed_date = NULL
                WHERE id = ?;
            """, (id,))

            self.add_habit_records(con_cur=(con, cur))
            
        con.commit()

        self.habit_get_data(dates=[], details=True, tracking=True, con_cur=(con, cur))
        con.close()     

        stopped_date = self.data["tracking"][id]
        stopped = stopped_date if stopped_date else '—'
        stopped_label = toga.Label(
            f"{self.strings['stopped']}: {stopped}", 
            style=Pack(padding=(0,20,14), font_size=14, color=self.clrs[2])
        )
        self.widgets_dict["more dates box"].clear()
        self.widgets_dict["more dates box"].add(
            self.widgets_dict["more dates label"], self.get_div(padding=(0,80)),
            self.widgets_dict["more added label"], 
            stopped_label
        )
        box = self.widgets_dict["more button box"]
        box.clear()
        stopped = self.data["tracking"][id]
        button = self.widgets_dict["more resume button"] if stopped else self.widgets_dict["more stop button"]
        box.add(self.widgets_dict["more remove button"], button)

        if id in self.widgets_dict["habits"]:
            del self.widgets_dict["habits"][id]

        self.load_habits(None, tracker=False, details=True)

    
    async def rename_habit_dialog(self, widget):
        if self.widgets_dict["more rename input"].value:
            result = await self.app.dialog(
                toga.QuestionDialog(
                    self.strings_c["confirmation"], 
                    self.strings["rename_habit_question"]
                )
            )
            if result:
                await self.rename_habit()


    async def rename_habit(self):
        new_name = self.widgets_dict["more rename input"].value.strip()
        self.widgets_dict["more rename input"].value = ""
        id = self.temp_habit_id

        con, cur = get_connection(self.db_path)

        cur.execute("""
                SELECT id FROM habits
                WHERE name = ?;
                """, (new_name,))
        if result := cur.fetchone():
            await self.app.dialog(
                toga.InfoDialog(
                    self.strings["habit_already_exists"], 
                    self.strings["habit_already_uses"].format(id=result[0])
                )
            )
            self.widgets_dict["more rename input"].value = ""
        else:
            cur.execute("""
                SELECT record_date FROM habit_records
                WHERE habit_id = ?
                AND record_date >= ?;
            """, (id, self.today-timedelta(days=6)))         
            dates = cur.fetchall()

            cur.execute("""
                UPDATE habits
                SET name = ?
                WHERE id = ?;
            """, (new_name, id,))
            con.commit()

            self.habit_get_data(dates=[date.fromisoformat(d[0]) for d in dates], details=True, tracking=True, con_cur=(con, cur))

            for d in dates:
                d = d[0]
                if d in self.widgets_dict["habits"]:
                    if id in self.widgets_dict["habits"][d]:
                        del self.widgets_dict["habits"][d][id]
            if id in self.widgets_dict["habits"]:
                del self.widgets_dict["habits"][id]

            self.load_habits(None, tracker=True, details=True)
            habit_more_label = toga.Label(
                f"{self.strings['habit']} [{id:06d}]\n{new_name}", 
                style=Pack(padding=14, text_align="center", font_weight="bold", font_size=15, color=self.clrs[2])
            )
            self.widgets_dict["more label box"].clear()
            self.widgets_dict["more label box"].add(habit_more_label)
            
        con.close()


    def calculate_streak(self, states: list) -> int:
        streak = 0
        for s in states:
            if s[0] == 3:
                streak += 1
            elif s[0] == 1:
                break
        return streak
    

    async def reset_habit_dialog(self):
        result = await self.app.dialog(toga.QuestionDialog(self.strings_c["confirmation"], self.strings["reset_db_question"]))
        if result:
            await self.reset_habit()


    async def reset_habit(self):
        con, cur = get_connection(self.db_path)
        cur.execute("DROP TABLE habits;")
        cur.execute("DROP TABLE habit_records;")
        con.commit()

        cur.executescript("""
            CREATE TABLE habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            longest_streak INTEGER DEFAULT 0,
            created_date DATE DEFAULT (date('now', 'localtime')),
            completed_date DATE,
            day_phase INTEGER CHECK(day_phase IN (1, 2) OR day_phase IS NULL) -- 1=am, 2=pm
            );
                          
            CREATE TABLE habit_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER NOT NULL,
            record_date DATE DEFAULT (date('now', 'localtime')),
            state INTEGER CHECK(state IN (1, 2, 3) OR state IS NULL),
            FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE ON UPDATE CASCADE
            );
                          
            CREATE INDEX idx_habit_records_state ON habit_records(state);
            CREATE INDEX idx_habit_records_date ON habit_records(record_date);       
        """)
        con.commit()
        con.close()
        
        self.app.setup_ui(habits=True)

        await self.app.dialog(toga.InfoDialog(self.strings_c["success"], self.strings["reset_db_success"]))

    
    async def reset_habit_records_dialog(self):
        result = await self.app.dialog(toga.QuestionDialog(self.strings_c["confirmation"], self.strings["reset_records_question"]))
        if result:
            await self.reset_habit_records()


    async def reset_habit_records(self):
        con, cur = get_connection(self.db_path)

        cur.execute("""
            SELECT id FROM habits
            WHERE completed_date IS NULL;
        """)
        ids = [id[0] for id in cur.fetchall()]
        for id in ids:
            cur.execute("""
                UPDATE habit_records
                SET state = NULL
                WHERE habit_id = ? 
                AND record_date = ?;
            """, (id, self.today,))
        con.commit()
        con.close()

        self.app.setup_ui(habits=True)

        await self.app.dialog(toga.InfoDialog(self.strings_c["success"], self.strings["reset_records_success"]))

    
    def habit_today(self, widget):
        self.widgets_dict["tracker date"].value = self.today


    def clear_add_habit(self):
        self.widgets_dict["add input"].value = ""

    
    def get_habit_box(self, habit, tracker_date=None):
        id = habit[0]

        if tracker_date:
            button_id = f"{id} habit state button"
            if button_id not in self.widgets_dict["habits"][tracker_date]:
                states = self.data["states"]
                button_box = toga.Box(style=Pack(direction=ROW))
                if habit[2]:
                    img_boxes = [toga.Box(style=Pack(direction=COLUMN, flex=0.33)) for _ in range(3)]
                    for i in range(3):
                        if self.maps["num_to_name"]["state"][habit[2]] == states[i]:
                            img_boxes[i].add(toga.ImageView(toga.Image(
                                self.data["state images"][i]), 
                                style=Pack(flex=1, alignment="center", height=40)
                            ))
                            break
                    for i in range(3):
                        button_box.add(img_boxes[i])

                else:
                    for s in states:
                        state_button_id = f"{id} habit {s} button"
                        button = toga.Button(
                            self.strings[s], id=state_button_id, on_press=self.change_habit_state_dialog, 
                            style=Pack(flex=0.33, height=42, font_size=12, color=self.clrs[2], background_color=self.clrs[1])
                        )
                        button_box.add(button)

                        self.reg([button])

                self.widgets_dict["habits"][tracker_date][button_id] = button_box
            button = self.widgets_dict["habits"][tracker_date][button_id]
            
            temp_label = f"{self.strings['current_streak']}: {habit[-1]}"
            temp_label += f"  |  {self.strings['day_phase']}: {self.strings[self.maps['num_to_name']['phase'][habit[3]]]}" if habit[2] else ""
            bottom_label = toga.Label(
                temp_label,
                style=Pack(padding=(4,4,0), font_size=10, color=self.clrs[2])
            )
            
        else:
            button_id = f"{id} habit more button"
            if button_id not in self.widgets_dict["habits"]:
                self.widgets_dict["habits"][button_id] = toga.Button(
                    self.strings["more"], id=button_id, on_press=self.check_if_any_records, 
                    style=Pack(flex=0.1, height=56, font_size=9, color=self.clrs[2], background_color=self.clrs[1])
                )
            button = self.widgets_dict["habits"][button_id]

            self.reg([button])

        id_label = toga.Label(
            f"[{id:06d}]", 
            style=Pack(padding=4, font_size=10, color=self.clrs[2])
        )
        
        main_label = toga.Label(
            habit[1], 
            style=Pack(padding=4, font_size=11, font_weight="bold", color=self.clrs[2])
        )
        
        chld = [id_label, main_label]
        chld += [bottom_label] if tracker_date else []
        habit_label_box = toga.Box(children=chld, style=Pack(direction=COLUMN, flex=0.8))

        children = [habit_label_box, button]
        direction = COLUMN if tracker_date else ROW

        habit_box = toga.Box(children=children, style=Pack(direction=direction))
        
        div = self.get_div()
        habit_box = toga.Box(children=[habit_box, div], style=Pack(direction=COLUMN))

        self.reg(chld + [div])

        return habit_box


    async def add_last_week_records_dialog(self):
        result = await self.app.dialog(toga.QuestionDialog(self.strings_c["confirmation"], self.strings["add_records_question"]))
        if result:
            await self.add_last_week_records()

    
    async def add_last_week_records(self):
        self.add_habit_records(dates=[self.today-timedelta(i) for i in range(1, 7)])

        await self.app.dialog(toga.InfoDialog(self.strings_c["success"], self.strings["add_records_success"]))

    
    def change_range(self, widget):
        change_range(widget, self.widgets_dict)


    def change_date(self, widget):
        w = self.widgets_dict["tracker date"]
        val = w.value
        mn, mx = w.min, w.max
        t = widget.id.split()[1]
        if t == "back":
            if val != mn:
                w.value = val - timedelta(1)
        else:
            if val != mx:
                w.value = val + timedelta(1)
                

    def day_phase_change(self, widget):
        id = self.temp_habit_id
        day_phase = self.maps["name_to_num"][self.maps["localized_to_system"][widget.value]]
        con, cur = get_connection(self.db_path)

        cur.execute("SELECT day_phase FROM habits WHERE id = ?;", (id,))
        old_day_phase = cur.fetchone()[0]
        if old_day_phase == day_phase:
            pass
        else:
            cur.execute("""
                SELECT record_date FROM habit_records
                WHERE habit_id = ?
                AND record_date >= ?;
            """, (id, self.today-timedelta(days=6)))         
            dates = cur.fetchall()

            cur.execute("""
                UPDATE habits
                SET day_phase = ?
                WHERE id = ?;
            """, (day_phase, id,))
            con.commit()

            self.habit_get_data(dates=[date.fromisoformat(d[0]) for d in dates], details=False, tracking=False, con_cur=(con, cur))

            con.close()

            for d in dates:
                d = d[0]
                if d in self.widgets_dict["habits"]:
                    if id in self.widgets_dict["habits"][d]:
                        del self.widgets_dict["habits"][d][id]
            if id in self.widgets_dict["habits"]:
                del self.widgets_dict["habits"][id]

            self.load_habits(None, tracker=True, details=False)
        
        con.close()

    
    def prepare_tracker_container(self):
        self.widgets_dict["tracker list container"].position = toga.Position(0,0)


    def prepare_details_containers(self):
        for t in self.data["track"]:
            self.widgets_dict[f"details {t} list container"].position = toga.Position(0,0)


    async def remove_habit_by_id(self, id):
        con, cur = get_connection(self.db_path)

        cur.execute("SELECT id FROM habits WHERE id = ?", (id,))
        if cur.fetchone():
            await self.remove_habit(id=id, open_details=False, con_cur=(con, cur))
            
            con.close()

            await self.app.dialog(toga.InfoDialog(self.strings_c["success"], self.strings["remove_habit_success"]))
        else:
            con.close()

            await self.app.dialog(toga.InfoDialog(self.strings_c["error"], self.strings["remove_habit_error"]))


    async def check_if_any_records(self, widget):
        habit_id = int(widget.id.split()[0])

        con, cur = get_connection(self.db_path)
        cur.execute("SELECT COUNT(*) FROM habit_records WHERE habit_id = ?", (habit_id,))

        res = cur.fetchone()[0]
        
        con.close()

        if res:
            self.app.open_habit_more(habit_id)
        else:
            await self.app.dialog(toga.InfoDialog(self.strings_c["error"], self.strings["no_records_error"]))