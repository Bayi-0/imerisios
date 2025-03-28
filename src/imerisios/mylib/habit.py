import toga
from toga.style import Pack
from toga.constants import COLUMN, ROW
from datetime import date, timedelta
import sqlite3 as sql
from collections import defaultdict
from imerisios.mylib.tools import length_check, get_connection, close_connection, create_calendar_image, get_month_dicts, get_ranges, change_range, set_range


class Habits:
    def __init__(self, app, db_path, img_path):
        self.app = app 
        self.db_path = db_path
        self.img_path = img_path

        self.widgets_dict = {"habits": {}}
        self.month_num_to_name, self.month_name_to_num = get_month_dicts()
        self.state_num_to_name = {3: "success", 1: "failure", 2: "skip"}
        self.state_name_to_num = {v: k for k, v in self.state_num_to_name.items()}
        self.phase_keys = ["AM", "PM", "N/A", "Completed"]
        self.phase_num_to_name = {1: "AM", 2: "PM", None: "N/A"}
        self.phase_name_to_num = {v: k for k, v in self.phase_num_to_name.items()}
        self.data = {"state images": [f"resources/habit/{s}.png" for s in ("success", "failure", "skip")]}
        self.details_setup = True
        self.more_setup = True
        

    def get_tracker_box(self):
        label = toga.Label(
            "Habit Tracker", 
            style=Pack(padding=14, text_align="center", font_weight="bold", font_size=20, color="#EBF6F7"))
        
        self.tracker_date = toga.DateInput(
            id="tracker date",
            on_change=self.load_habits, 
            style=Pack(flex=0.6, width=201, color="#EBF6F7"))
        back_button = toga.Button(
            "<", id="tracker back button",
            on_press=self.change_date, 
            style=Pack(flex=0.2, padding=4, height=44, font_size=13, color="#EBF6F7", background_color="#27221F")
        )
        next_button = toga.Button(
            ">", id="tracker next button",
            on_press=self.change_date, 
            style=Pack(flex=0.2, padding=4, height=44, font_size=13, color="#EBF6F7", background_color="#27221F")
        )
        date_input_box = toga.Box(
            children=[back_button, self.tracker_date, next_button], 
            style=Pack(direction=ROW))
        
        today_button = toga.Button(
            "Today", on_press=self.habit_today, 
            style=Pack(flex=0.4, padding=4, height=44, font_size=13, color="#EBF6F7", background_color="#27221F"))

        date_box = toga.Box(
            children=[date_input_box, today_button], 
            style=Pack(direction=COLUMN))

        self.tracker_list_box = toga.Box(style=Pack(direction=COLUMN))
        self.tracker_list_container = toga.ScrollContainer(
            content=self.tracker_list_box, 
            horizontal=False, style=Pack(flex=0.8))

        tracker_box = toga.Box(
            children=[
                label, toga.Divider(style=Pack(background_color="#27221F")), 
                date_box, toga.Divider(style=Pack(background_color="#27221F")), 
                self.tracker_list_container
            ], 
            style=Pack(direction=COLUMN, background_color="#393432"))
        
        # day phase labels
        am_label = toga.Label("AM", style=Pack(padding=10, font_size=16, text_align="center", color="#EBF6F7"))
        pm_label = toga.Label("PM", style=Pack(padding=10, font_size=16, text_align="center", color="#EBF6F7"))
        na_label = toga.Label("N/A", style=Pack(padding=10, font_size=16, text_align="center", color="#EBF6F7"))
        completed_label = toga.Label("Completed", style=Pack(padding=10, font_size=16, text_align="center", color="#EBF6F7"))

        self.widgets_dict["AM label"] = am_label
        self.widgets_dict["PM label"] = pm_label
        self.widgets_dict["N/A label"] = na_label
        self.widgets_dict["Completed label"] = completed_label

        return tracker_box
    
    
    def get_details_box(self):
        # tracked
        tracked_label = toga.Label(
            "Tracked Habit Details", 
            style=Pack(padding=14, text_align="center", font_weight="bold", font_size=20, color="#EBF6F7"))
        
        back_button = toga.Button(
            "<", id="tracked back button",
            on_press=self.change_range, 
            style=Pack(flex=0.2, padding=4, height=44, font_size=13, color="#EBF6F7", background_color="#27221F")
        )
        next_button = toga.Button(
            ">", id="tracked next button",
            on_press=self.change_range, 
            style=Pack(flex=0.2, padding=4, height=44, font_size=13, color="#EBF6F7", background_color="#27221F")
        )
        self.tracked_range = toga.Selection(
            id="tracked range", 
            on_change=self.load_habits,
            style=Pack(flex=0.6, padding=4, height=44))
        self.widgets_dict["tracked range"] = self.tracked_range
        tracked_range_box = toga.Box(
            children=[back_button, self.tracked_range, next_button],
            style=Pack(direction=ROW))

        self.details_tracked_box = toga.Box(style=Pack(direction=COLUMN))
        self.widgets_dict["details tracked box"] = self.details_tracked_box
        
        self.details_tracked_container = toga.ScrollContainer(
            content=self.details_tracked_box, 
            horizontal=False, style=Pack(flex=0.8))
        self.widgets_dict["details tracked container"] = self.details_tracked_container
        
        tracked_box = toga.Box(
            children=[tracked_label, toga.Divider(style=Pack(background_color="#27221F")), tracked_range_box, toga.Divider(style=Pack(background_color="#27221F")), self.details_tracked_container], 
            style=Pack(direction=COLUMN, background_color="#393432"))

        # untracked
        untracked_label = toga.Label(
            "Untracked Habit Details", 
            style=Pack(padding=14, text_align="center", font_weight="bold", font_size=20, color="#EBF6F7"))
        
        back_button = toga.Button(
            "<", id="untracked back button",
            on_press=self.change_range, 
            style=Pack(flex=0.2, padding=4, height=44, font_size=13, color="#EBF6F7", background_color="#27221F")
        )
        next_button = toga.Button(
            ">", id="untracked next button",
            on_press=self.change_range, 
            style=Pack(flex=0.2, padding=4, height=44, font_size=13, color="#EBF6F7", background_color="#27221F")
        )
        self.untracked_range = toga.Selection(
            id="untracked range", 
            on_change=self.load_habits,
            style=Pack(flex=0.6, padding=4, height=44))
        self.widgets_dict["untracked range"] = self.untracked_range
        untracked_range_box = toga.Box(
            children=[back_button, self.untracked_range, next_button],
            style=Pack(direction=ROW))

        self.details_untracked_box = toga.Box(style=Pack(direction=COLUMN))
        self.widgets_dict["details untracked box"] = self.details_untracked_box
        
        self.details_untracked_container = toga.ScrollContainer(
            content=self.details_untracked_box, 
            horizontal=False, style=Pack(flex=0.8))
        self.widgets_dict["details untracked container"] = self.details_untracked_container
        
        untracked_box = toga.Box(
            children=[untracked_label, toga.Divider(style=Pack(background_color="#27221F")), untracked_range_box, toga.Divider(style=Pack(background_color="#27221F")), self.details_untracked_container], 
            style=Pack(direction=COLUMN, background_color="#393432"))

        # details box
        details_box = toga.OptionContainer(content=[
            toga.OptionItem("Tracked", tracked_box, icon=toga.Icon(self.data["state images"][0])),
            toga.OptionItem("Untracked", untracked_box, icon=toga.Icon(self.data["state images"][1]))
        ])

        return details_box


    def get_add_habit_box(self):
        label = toga.Label(
            "Add a New Habit", 
            style=Pack(flex=0.9, padding=14, text_align="center", font_weight="bold", font_size=18, color="#EBF6F7"))

        quotes_top = [
            "“A habit, if not resisted, soon becomes necessity.”", "— Haruki Murakami, The Wind-Up Bird Chronicle",
            "“A first sign of the beginning of understanding is the wish to die.”", "— Franz Kafka, The Zürau Aphorisms", 
            "“The scariest moment is always just before you start.”", "— Stephen King, On Writing: A Memoir of the Craft",
            "“If you only read the books that everyone else is reading, you can only think what everyone else\nis thinking.”", "— Toru Watanabe, Norwegian Wood by Haruki Murakami",
            "“Pain is inevitable. Suffering is optional.”", "— Haruki Murakami, What I Talk About When I Talk About Running",
            "“The world doesn't give you what you want. It gives you what you take.”", "— Eithan Arelius, Cradle by Will Wight",
            "“When the soul suffers too much, it develops a taste for misfortune.”", "— Albert Camus, The First Man"
        ]
        quotes_box_top = toga.Box(style=Pack(direction=COLUMN, flex=0.26, padding=4))
        for i in range(0, len(quotes_top)-1, 2):
            quotes_box_top.add(toga.Label(quotes_top[i], style=Pack(padding=(4,4,0), font_size=7, color="#EBF6F7")))
            quotes_box_top.add(
                toga.Label(quotes_top[i+1], 
                style=Pack(padding=(0,4,4), text_align="right", font_size=7, font_style="italic", color="#EBF6F7")))
        quotes_bottom = [
            "“What we seek is some kind of compensation for what we put up with.”", "— Narrator, The Rat by Haruki Murakami",
            "“It has long been an axiom of mine that the little things are infinitely the most important.”", "— Sherlock Holmes, by Arthur Conan Doyle",
            "“The habit of hoping always for better things is actually an obstacle to success.”", "— Stendhal, The Red and the Black",
            "“There is always a philosophy for lack of courage.”", "— Albert Camus, Notebooks (1942-1951)",
            "“If you're going to do something that's going to slow down your work, just as well put off doing\nit as long as possible.”", "— John Wyndham, The Chrysalids",
            "“You have to decide who you want to be. Before someone else does it for you.”", "— Eithan Arelius, Cradle by Will Wight",
            "“I'm not afraid of death; I just don't want to be there when it happens.”", "— Toru Watanabe, Norwegian Wood by Haruki Murakami (originally Woody Allen)"
        ]
        quotes_box_bottom = toga.Box(style=Pack(direction=COLUMN, flex=0.26, padding=4, background_color="#393432"))
        for i in range(0, len(quotes_bottom)-1, 2):
            quotes_box_bottom.add(toga.Label(quotes_bottom[i], style=Pack(padding=(4,4,0), font_size=7, color="#EBF6F7")))
            quotes_box_bottom.add(
                toga.Label(quotes_bottom[i+1], 
                style=Pack(padding=(0,4,4), text_align="right", font_size=7, font_style="italic", color="#EBF6F7")))

        self.add_input = toga.TextInput(
            id="add input 34",
            placeholder="(no more than 34 characters)",
            on_change=length_check, 
            style=Pack(padding=(11,18,0), height=44, font_size=12, color="#EBF6F7", background_color="#27221F"))
        add_button = toga.Button(
            "Add", on_press=self.add_habit, 
            style=Pack(flex=0.5, height=120, padding=(8,11,18), font_size=24, color="#EBF6F7", background_color="#27221F"))
        add_box = toga.Box(
            children=[self.add_input, add_button],
            style=Pack(direction=COLUMN, flex=0.2))

        add_habit_box = toga.Box(
            children=[
                label, toga.Divider(style=Pack(background_color="#27221F")), 
                quotes_box_top, toga.Divider(style=Pack(background_color="#27221F")), 
                add_box, toga.Divider(style=Pack(background_color="#27221F")),
                quotes_box_bottom
            ], 
            style=Pack(direction=COLUMN, background_color="#393432"))

        return add_habit_box
    

    def get_more_box(self):
        self.more_box = toga.Box(
            style=Pack(direction=COLUMN, background_color="#393432"))
        more_container = toga.ScrollContainer(content=self.more_box, horizontal=False)

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
            
            self.load_habits(None, False, details)

            date_w = self.tracker_date
            date_w.max = date_w.value = date.today()
            date_w.min = date.today() - timedelta(days=6)

        close_connection(con, con_cur)
    

    def habit_get_data(self, dates=None, details=False, tracking=False, con_cur=None):
        con, cur = get_connection(self.db_path, con_cur)
        if dates is None:
            dates = [date.today()-timedelta(days=i) for i in range(7)]
    
        for d in dates:
            iso = d.isoformat()
            self.data[iso] = {"AM": [], "PM": [], "N/A": [], "Completed": []}

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
                self.data[iso][self.phase_num_to_name[day_phase]].append(row)
            
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

            self.data[iso]["Completed"].extend(rows)
            
            for key in self.phase_keys:
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


    def load_habits(self, widget, tracker=True, details=False):
        if tracker:
            list_box = self.tracker_list_box
            list_box.clear()

            d = self.tracker_date.value.isoformat()
            data = self.data[self.tracker_date.value.isoformat()]
            if len(data) == 0:
                    list_box.add(toga.Label(
                        "No tracked habits on the day.",
                        style=Pack(padding=10, font_size=12, color="#EBF6F7")))
            else:
                for key in self.phase_keys:
                    if data[key]:
                        list_box.add(self.widgets_dict[f"{key} label"], toga.Divider(style=Pack(background_color="#27221F")))

                        for h in data[key]:
                            id = h[0]
                            if d not in self.widgets_dict["habits"]:
                                self.widgets_dict["habits"][d] = {}
                            if id not in self.widgets_dict["habits"][d]:
                                self.widgets_dict["habits"][d][id] = self.get_habit_box(h, d)
                            list_box.add(self.widgets_dict["habits"][d][id])
                    
        if details:
            for t in ["tracked", "untracked"]:
                data = self.data[t]

                items = get_ranges(data)
                set_range(self.widgets_dict[f"{t} range"], items)

        elif widget and widget.id.split()[0] in ["tracked", "untracked"]:
            t = widget.id.split()[0]

            data = self.data[t]
            box = self.widgets_dict[f"details {t} box"]
            box.clear()

            start, end = [int(i) for i in widget.value.split('–')]
            if start == 0 and end == 0:
                box.add(toga.Label(
                    f"{t.capitalize()} habits will appear here.",
                    style=Pack(padding=10, font_size=12, color="#EBF6F7")
                ))
            else:
                for i in range(start-1, end):
                    habit = data[i]
                    id = habit[0]
                    if id not in self.widgets_dict["habits"]:
                        self.widgets_dict["habits"][id] = self.get_habit_box(habit)
                    box.add(self.widgets_dict["habits"][id])
            
            self.widgets_dict[f"details {t} container"].position = toga.Position(0,0)
                    


    def load_habit_more(self, id):
        self.temp_habit_id = id

        self.more_box.clear()

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
            f"Habit [{id:06d}]\n{name}", 
            style=Pack(padding=14, text_align="center", font_weight="bold", font_size=15, color="#EBF6F7"))
        self.habit_more_label_box = toga.Box(
            children=[habit_more_label],
            style=Pack(direction=COLUMN))
        
        if self.more_setup:
            self.widgets_dict["habit_more day_phase label"] = toga.Label(
                "Day phase:", 
                style=Pack(flex=0.4, padding=(14,0,14,20), font_size=14, color="#EBF6F7"))
            self.widgets_dict["habit_more day_phase select"] = toga.Selection(items=["N/A", "AM", "PM"], on_change=self.day_phase_change, style=Pack(flex=0.6, padding=(6,16,0), height=44))
        
            self.widgets_dict["habit_more dates label"] = toga.Label(
                "Dates", 
                style=Pack(padding=14, text_align="center", font_size=14, color="#EBF6F7"))
            
        self.widgets_dict["habit_more day_phase select"].value = self.phase_num_to_name[day_phase]

        day_phase_box = toga.Box(
            children=[self.widgets_dict["habit_more day_phase label"], self.widgets_dict["habit_more day_phase select"]],
            style=Pack(direction=ROW))    
        
        self.dates_label = self.widgets_dict["habit_more dates label"]
        self.added_label = toga.Label(
            f"Added: {added_date}", 
            style=Pack(padding=(14,20), font_size=14, color="#EBF6F7"))
        stopped = stopped_date if stopped_date else '—'
        stopped_label = toga.Label(
            f"Stopped: {stopped}", 
            style=Pack(padding=(0,20,14), font_size=14, color="#EBF6F7"))
        self.habit_dates_box = toga.Box(
            children=[
                self.dates_label, toga.Divider(style=Pack(padding=(0,80), background_color="#27221F")), 
                self.added_label, 
                stopped_label
            ], 
            style=Pack(direction=COLUMN))
        if self.more_setup:
            self.widgets_dict["habit_more total label"] = toga.Label(
                "Total", 
                style=Pack(padding=14, text_align="center", font_size=14, color="#EBF6F7"))
        total_label = self.widgets_dict["habit_more total label"]
        total_records_label = toga.Label(
            f"Records: {total_records}", 
            style=Pack(flex=0.5, padding=14, text_align="center", font_size=14, color="#EBF6F7"))
        total_success_label = toga.Label(
            f"Successes: {total_success}", 
            style=Pack(flex=0.5, padding=14, text_align="center", font_size=14, color="#EBF6F7"))
        total_top_box = toga.Box(children=[total_records_label, total_success_label], style=Pack(direction=ROW))

        total_failure_label = toga.Label(
            f"Failures: {total_failure}", 
            style=Pack(flex=0.5, padding=(0,14,14), text_align="center", font_size=14, color="#EBF6F7"))
        total_skip_label = toga.Label(
            f"Skips: {total_skip}", 
            style=Pack(flex=0.5, padding=(0,14,14), text_align="center", font_size=14, color="#EBF6F7"))
        total_bottom_box = toga.Box(children=[total_failure_label, total_skip_label], style=Pack(direction=ROW))
        
        total_box = toga.Box(
            children=[
                total_label, toga.Divider(style=Pack(padding=(0,80), background_color="#27221F")), 
                total_top_box, total_bottom_box
            ], 
            style=Pack(direction=COLUMN))
        
        completion_rate_label = toga.Label(
            f"Completion Rate: {round(total_success_skip_percent, 1)}%", 
            style=Pack(padding=(14,20), font_size=14, color="#EBF6F7"))
        longest_streak_label = toga.Label(
            f"Longest Success Streak: {longest_streak}", 
            style=Pack(padding=(14,20), font_size=14, color="#EBF6F7"))

        if self.more_setup:
            self.widgets_dict["habit_more average label"] = toga.Label(
                "Average Success Numbers", 
                style=Pack(padding=14, text_align="center", font_size=14, color="#EBF6F7"))
        average_success_label = self.widgets_dict["habit_more average label"]
        
        weekly_success = toga.Label(
            f"Weekly: {average_rates[0]}", 
            style=Pack(flex=0.33, padding=8, text_align="center", font_size=14, color="#EBF6F7"))
        monthly_success = toga.Label(
            f"Monthly: {average_rates[1]}", 
            style=Pack(flex=0.33, padding=8, text_align="center", font_size=14, color="#EBF6F7"))
        yearly_success = toga.Label(
            f"Yearly: {average_rates[2]}", 
            style=Pack(flex=0.33, padding=8, text_align="center", font_size=14, color="#EBF6F7"))
        average_rates_box = toga.Box(children=[weekly_success, monthly_success, yearly_success], style=Pack(direction=ROW))

        average_success_box = toga.Box(
            children=[
                average_success_label, toga.Divider(style=Pack(padding=(0,80), background_color="#27221F")), 
                average_rates_box
            ], 
            style=Pack(direction=COLUMN))
        
        if self.more_setup:
            self.widgets_dict["habit_more calendar label"] = toga.Label(
                "Record Calendar", 
                style=Pack(padding=14, text_align="center", font_size=14, color="#EBF6F7"))
            self.widgets_dict["habit_more year label"] = toga.Label(
                "Year:", 
                style=Pack(flex=0.3, padding=(14,0,0,20), font_size=14, color="#EBF6F7"))
            self.widgets_dict["habit_more year select"] = toga.Selection(style=Pack(flex=0.7, padding=(6,16,0), height=44))
            self.widgets_dict["habit_more month label"] = toga.Label(
                "Month:", 
                style=Pack(flex=0.3, padding=(14,0,0,20), font_size=14, color="#EBF6F7"))
            self.widgets_dict["habit_more month select"] = toga.Selection(style=Pack(flex=0.7, padding=(6,16,0), height=44))
        record_calendar_label = self.widgets_dict["habit_more calendar label"]
        year_select_label = self.widgets_dict["habit_more year label"]
        year_select = self.widgets_dict["habit_more year select"]
        year_select_box = toga.Box(
            children=[year_select_label, year_select],
            style=Pack(direction=ROW))
        month_select_label = self.widgets_dict["habit_more month label"]
        month_select = self.widgets_dict["habit_more month select"]
        month_select_box = toga.Box(
            children=[month_select_label, month_select],
            style=Pack(direction=ROW))
        record_calendar_box = toga.Box(
            children=[
                record_calendar_label, toga.Divider(style=Pack(padding=(0,80), background_color="#27221F")), 
                year_select_box, 
                month_select_box],
            style=Pack(direction=COLUMN))
        calendar_image_box = toga.Box(style=Pack(flex=1, padding=(4), height=280))
        
        if self.more_setup:
            self.widgets_dict["habit_more manage label"] = toga.Label(
                "Manage", 
                style=Pack(padding=14, text_align="center", font_size=14, color="#EBF6F7"))
            self.widgets_dict["habit_more rename input"] = toga.TextInput(
                id="habit_rename input 34",
                on_change=length_check,
                placeholder="new name for the habit", 
                style=Pack(padding=(8,11,0), height=44, font_size=12, color="#EBF6F7", background_color="#27221F"))
            self.widgets_dict["habit_more rename button"] =toga.Button(
                "Rename", on_press=self.rename_habit_dialog, 
                style=Pack(flex=0.5, height=120, padding=(0,11), font_size=24, color="#EBF6F7", background_color="#27221F"))
            self.widgets_dict["habit_more remove button"] = toga.Button(
                "Remove", on_press=self.remove_habit_dialog, 
                style=Pack(flex=0.5, height=120, padding=(4,4,11,11), font_size=24, color="#EBF6F7", background_color="#27221F"))
            self.widgets_dict["habit_more stop button"] = toga.Button(
                "Stop", on_press=self.tracking_habit_dialog, 
                id="habit stop button",
                style=Pack(flex=0.5, height=120, padding=(4,11,11,4), font_size=24, color="#EBF6F7", background_color="#27221F"))
            self.widgets_dict["habit_more resume button"] = toga.Button(
                "Resume", on_press=self.tracking_habit_dialog, 
                id="habit resume button",
                style=Pack(flex=0.5, height=120, padding=(4,11,11,4), font_size=24, color="#EBF6F7", background_color="#27221F"))
        habit_more_manage_label = self.widgets_dict["habit_more manage label"]    
        self.habit_more_rename_input = self.widgets_dict["habit_more rename input"]
        self.habit_more_rename_input.value = ""
        rename_button = self.widgets_dict["habit_more rename button"]
        rename_box = toga.Box(
            children=[self.habit_more_rename_input, rename_button], 
            style=Pack(direction=COLUMN, flex=0.3))
        self.habit_more_remove_button = self.widgets_dict["habit_more remove button"]
        self.habit_more_stop_button = self.widgets_dict["habit_more stop button"]
        self.habit_more_resume_button = self.widgets_dict["habit_more resume button"]
        button = self.habit_more_resume_button if self.data["tracking"][id] else self.habit_more_stop_button
        self.habit_more_button_box = toga.Box(
            children=[self.habit_more_remove_button, button],
            style=Pack(direction=ROW, flex=0.16))
        habit_more_manage_box = toga.Box(
            children=[
                habit_more_manage_label, toga.Divider(style=Pack(padding=(0,80), background_color="#27221F")), 
                rename_box, 
                self.habit_more_button_box
            ], 
            style=Pack(direction=COLUMN))
        
        self.more_box.add(
            self.habit_more_label_box, toga.Divider(style=Pack(background_color="#27221F")), 
            day_phase_box, toga.Divider(style=Pack(background_color="#27221F")),
            self.habit_dates_box, toga.Divider(style=Pack(background_color="#27221F")), 
            total_box, toga.Divider(style=Pack(background_color="#27221F")), 
            completion_rate_label, toga.Divider(style=Pack(background_color="#27221F")), 
            longest_streak_label, toga.Divider(style=Pack(background_color="#27221F")), 
            average_success_box, toga.Divider(style=Pack(background_color="#27221F")), 
            record_calendar_box, 
            calendar_image_box, toga.Divider(style=Pack(background_color="#27221F")),
            habit_more_manage_box
        )

        def year_change(widget):
            year = int(widget.value)
            month_select.year = year
            month_select.items = [self.month_num_to_name[m] for m in sorted(habit_records[year], reverse=True)]

        def month_change(widget):
            calendar_image_box.clear()

            year = widget.year
            month = self.month_name_to_num[widget.value]
            create_calendar_image(year, month, self.img_path, habit_records[year][month])
            img = toga.ImageView(toga.Image(self.img_path), style=Pack(flex=1))

            calendar_image_box.add(img)
        
        year_select.on_change=year_change
        month_select.on_change=month_change

        year_select.items = sorted([y for y in habit_records], reverse=True)

        self.more_setup = False


    async def change_habit_state_dialog(self, widget):
        splt = widget.id.split()
        result = await self.app.dialog(toga.QuestionDialog("Confirmation", f"Are you sure you want to set [{int(splt[0]):06d}] habit's state to {splt[2]}?"))
        if result:
            await self.change_habit_state(splt)


    async def change_habit_state(self, splt):
        habit_id = int(splt[0])
        state = self.state_name_to_num[splt[2]]
        record_date = self.tracker_date.value

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
        """, (habit_id, date.today(),))
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
        if record_date != date.today():
            difference = (date.today()-record_date).days
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
        self.load_habits(None)

        con.close()


    async def add_habit(self, widget):
        if habit_name := self.add_input.value.strip():
            con, cur = get_connection(self.db_path)
            
            cur.execute("""
                SELECT id FROM habits
                WHERE name = ?;
                """, (habit_name,))
            if result := cur.fetchone():
                await self.app.dialog(toga.InfonDialog("Habit Already Exists", f"Habit [{result[0]:04d}] already uses this name."))
                self.add_input.value = ""
            else:
                cur.execute("""
                    INSERT INTO habits (name)
                    VALUES (?);
                    """, (habit_name,))
                con.commit()

                today = date.today()

                self.add_habit_records(load=False, con_cur=(con, cur))
                self.habit_get_data(dates=[today], details=True, tracking=True, con_cur=(con, cur))

                self.tracker_date.value = today
                self.load_habits(widget, tracker=False, details=True)
                self.app.open_habit_tracker(widget)

            con.close()
    

    def add_habit_records(self, dates=[date.today()], load=True, con_cur=None):
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
            self.load_habits(None)

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
        result = await self.app.dialog(toga.QuestionDialog("Confirmation", "Are you sure you want to remove the habit?"))
        if result:
            await self.remove_habit()


    async def remove_habit(self):
        id = self.temp_habit_id

        con, cur = get_connection(self.db_path)
        cur.execute("""
            SELECT record_date FROM habit_records
            WHERE habit_id = ?
            AND record_date >= ?;
        """, (id, date.today()-timedelta(days=6))) 
        dates = cur.fetchall()

        cur.execute("""
            DELETE FROM habits
            WHERE id = ?;
        """, (id,))
        con.commit()

        self.habit_get_data(dates=[date.fromisoformat(d[0]) for d in dates], details=True, con_cur=(con, cur))

        con.close()

        for d in dates:
            if d in self.widgets_dict["habits"]:
                if id in self.widgets_dict["habits"][d]:
                    del self.widgets_dict["habits"][d][id]
                    del self.widgets_dict["habits"][d][f"{id} habit state button"]
        if id in self.widgets_dict["habits"]:
            del self.widgets_dict["habits"][id]

        self.load_habits(None, details=True)
        self.app.open_habit_details(None)


    async def tracking_habit_dialog(self, widget):
        stop = widget.id.split()[1] == "stop"
        word = "stop" if stop else "resume"
        result = await self.app.dialog(toga.QuestionDialog("Confirmation", f"Are you sure you want to {word} tracking the habit?"))
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
            """, (date.today(), id,))
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
            f"Stopped: {stopped}", 
            style=Pack(padding=(0,20,14), font_size=14, color="#EBF6F7"))
        self.habit_dates_box.clear()
        self.habit_dates_box.add(
                self.dates_label, toga.Divider(style=Pack(padding=(0,80), background_color="#27221F")), 
                self.added_label, 
                stopped_label)
        box = self.habit_more_button_box
        box.clear()
        stopped = self.data["tracking"][id]
        button = self.habit_more_resume_button if stopped else self.habit_more_stop_button
        box.add(self.habit_more_remove_button, button)

        if id in self.widgets_dict["habits"]:
            del self.widgets_dict["habits"][id]

        self.load_habits(None, tracker=False, details=True)

    
    async def rename_habit_dialog(self, widget):
        if self.habit_more_rename_input.value:
            result = await self.app.dialog(toga.QuestionDialog("Confirmation", "Are you sure you want to rename the habit?"))
            if result:
                await self.rename_habit()


    async def rename_habit(self):
        new_name = self.habit_more_rename_input.value.strip()
        self.habit_more_rename_input.value = ""
        id = self.temp_habit_id

        con, cur = get_connection(self.db_path)

        cur.execute("""
                SELECT id FROM habits
                WHERE name = ?;
                """, (new_name,))
        if result := cur.fetchone():
            await self.app.dialog(toga.InfoDialog("Habit Already Exists", f"Habit [{result[0]:04d}] already uses this name."))
            self.habit_more_rename_input.value = ""
        else:
            cur.execute("""
                SELECT record_date FROM habit_records
                WHERE habit_id = ?
                AND record_date >= ?;
            """, (id, date.today()-timedelta(days=6)))         
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

            self.load_habits(None, details=True)
            habit_more_label = toga.Label(
                f"Habit [{id:04d}]\n{new_name}", 
                style=Pack(padding=14, text_align="center", font_weight="bold", font_size=15, color="#EBF6F7"))
            self.habit_more_label_box.clear()
            self.habit_more_label_box.add(habit_more_label)
            
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
        result = await self.app.dialog(toga.QuestionDialog("Confirmation", "Are you sure you want to reset Habits database?"))
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

        await self.app.dialog(toga.InfoDialog("Success", "Habits database has been reset successfully."))

    
    async def reset_habit_records_dialog(self):
        result = await self.app.dialog(toga.QuestionDialog("Confirmation", "Are you sure you want to reset today's habit records?"))
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
            """, (id, date.today(),))
        con.commit()
        con.close()

        self.app.setup_ui(habits=True)

        await self.app.dialog(toga.InfoDialog("Success", "Today's habit records have been reset successfully."))

    
    def habit_today(self, widget):
        self.tracker_date.value = date.today()


    def clear_add_habit(self):
        self.add_input.value = ""

    
    def get_habit_box(self, habit, tracker_date=None):
        id = habit[0]

        if tracker_date:
            button_id = f"{id} habit state button"
            if button_id not in self.widgets_dict["habits"][tracker_date]:
                states = ["success", "failure", "skip"]
                button_box = toga.Box(style=Pack(direction=ROW))
                if habit[2]:
                    img_boxes = [toga.Box(style=Pack(direction=COLUMN, flex=0.33)) for i in range(3)]
                    for i in range(3):
                        if self.state_num_to_name[habit[2]] == states[i]:
                            img_boxes[i].add(toga.ImageView(toga.Image(self.data["state images"][i]), style=Pack(flex=1, alignment="center", height=40)))
                            break
                    for i in range(3):
                        button_box.add(img_boxes[i])

                else:
                    for s in states:
                        state_button_id = f"{id} habit {s} button"
                        button = toga.Button(
                            s, id=state_button_id, on_press=self.change_habit_state_dialog, 
                            style=Pack(flex=0.33, height=42, font_size=12, color="#EBF6F7", background_color="#27221F"))
                        button_box.add(button)

                self.widgets_dict["habits"][tracker_date][button_id] = button_box
            button = self.widgets_dict["habits"][tracker_date][button_id]
            
            temp_label = f"Current streak: {habit[-1]}"
            temp_label += f"  |  Day phase: {self.phase_num_to_name[habit[3]]}" if habit[2] else ""
            bottom_label = toga.Label(
                temp_label,
                style=Pack(padding=(4,4,0), font_size=11, color="#EBF6F7"))
            
        else:
            button_id = f"{id} habit more button"
            if button_id not in self.widgets_dict["habits"]:
                self.widgets_dict["habits"][button_id] = toga.Button(
                    "More", id=button_id, on_press=self.app.open_habit_more, 
                    style=Pack(flex=0.14, height=56, font_size=12, color="#EBF6F7", background_color="#27221F"))
            button = self.widgets_dict["habits"][button_id]

        id_label = toga.Label(
            f"[{id:06d}]", 
            style=Pack(padding=4, font_size=11, color="#EBF6F7"))
        
        main_label = toga.Label(
            habit[1], 
            style=Pack(padding=4, font_size=11, font_weight="bold", color="#EBF6F7"))
        
        children = [id_label, main_label]
        children += [bottom_label] if tracker_date else []
        habit_label_box = toga.Box(children=children, style=Pack(direction=COLUMN, flex=0.85))

        children = [habit_label_box, button]
        direction = COLUMN if tracker_date else ROW

        habit_box = toga.Box(
            children=children,
            style=Pack(direction=direction))
        
        habit_box = toga.Box(
            children=[habit_box, toga.Divider(style=Pack(background_color="#27221F"))],
            style=Pack(direction=COLUMN))
    
        return habit_box


    async def add_last_week_records_dialog(self):
        result = await self.app.dialog(toga.QuestionDialog("Confirmation", "Are you sure you want to add last week's habit records?"))
        if result:
            await self.add_last_week_records()

    
    async def add_last_week_records(self):
        self.add_habit_records(dates=[date.today()-timedelta(i) for i in range(1, 7)])

        await self.app.dialog(toga.InfoDialog("Success", "Habit records have been added successfully."))

    
    def change_range(self, widget):
        change_range(widget, self.widgets_dict)


    def change_date(self, widget):
        w = self.tracker_date
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
        day_phase = self.phase_name_to_num[widget.value]
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
            """, (id, date.today()-timedelta(days=6)))         
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

            self.load_habits(None, details=False)
        
        con.close()