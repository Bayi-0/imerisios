import toga
from toga.style import Pack
from toga.constants import COLUMN, ROW
from datetime import date, timedelta
import sqlite3 as sql
from collections import defaultdict
from imerisios.mylib.tools import length_check, get_connection, close_connection, create_calendar_image, get_month_dicts

class Habits:
    def __init__(self, app, db_path, img_path):
        self.app = app 
        self.db_path = db_path
        self.img_path = img_path

        self.widgets = {}
        self.month_num_to_name, self.month_name_to_num = get_month_dicts()
        self.data = {}
        

    def get_habit_tracker_box(self):
        label = toga.Label(
            "Habit Tracker", 
            style=Pack(padding=14, text_align="center", font_weight="bold", font_size=20, color="#EBF6F7"))
        
        date_label = toga.Label(
            "Date:", 
            style=Pack(padding=(10,20), font_size=16, color="#EBF6F7"))
        self.habit_tracker_date = toga.DateInput(
            on_change=self.load_habits, 
            style=Pack(padding=(0,20), width=200, color="#EBF6F7"))
        date_input_box = toga.Box(
            children=[date_label, self.habit_tracker_date], 
            style=Pack(direction=ROW))
        
        today_button = toga.Button(
            "Today", on_press=self.habit_today, 
            style=Pack(flex=0.4, padding=(4,44,4), height=44, font_size=11, color="#EBF6F7", background_color="#27221F")
        )

        date_box = toga.Box(
            children=[date_input_box, today_button], 
            style=Pack(direction=COLUMN))

        self.habit_tracker_list_box = toga.Box(style=Pack(direction=COLUMN))
        habit_tracker_list_container = toga.ScrollContainer(
            content=self.habit_tracker_list_box, 
            horizontal=False, style=Pack(flex=0.8))

        habit_tracker_box = toga.Box(
            children=[
                label, toga.Divider(style=Pack(background_color="#27221F")), 
                date_box, toga.Divider(style=Pack(background_color="#27221F")), 
                habit_tracker_list_container
            ], 
            style=Pack(direction=COLUMN, background_color="#393432"))

        return habit_tracker_box
    
    
    def get_habit_details_box(self):
        label = toga.Label(
            "Habit Details", 
            style=Pack(padding=14, text_align="center", font_weight="bold", font_size=20, color="#EBF6F7"))
        
        self.habit_details_list_box = toga.Box(style=Pack(direction=COLUMN))
        habit_details_list_container = toga.ScrollContainer(
            content=self.habit_details_list_box, 
            horizontal=False, style=Pack(flex=0.8))
        
        habit_details_box = toga.Box(
            children=[label, toga.Divider(style=Pack(background_color="#27221F")), habit_details_list_container], 
            style=Pack(direction=COLUMN, background_color="#393432"))

        return habit_details_box


    def get_habit_manage_box(self):
        label = toga.Label(
            "Habit Manager", 
            style=Pack(flex=0.09, padding=14, text_align="center", font_weight="bold", font_size=20, color="#EBF6F7"))


        quotes_top = [
            "“A habit, if not resisted, soon becomes necessity.”", "— Haruki Murakami, The Wind-Up Bird Chronicle",
            "“A first sign of the beginning of understanding is the wish to die.”", "— Franz Kafka, The Zürau Aphorisms", 
            "“The scariest moment is always just before you start.”", "— Stephen King, On Writing: A Memoir of the Craft",
            "“If you only read the books that everyone else is reading, you can only think what everyone else\nis thinking.”", "— Toru Watanabe, Norwegian Wood by Haruki Murakami"
        ]
        quotes_box_top = toga.Box(style=Pack(direction=COLUMN, flex=0.3, padding=4))
        for i in range(0, len(quotes_top)-1, 2):
            quotes_box_top.add(toga.Label(quotes_top[i], style=Pack(padding=(4,4,0), font_size=7, color="#EBF6F7")))
            quotes_box_top.add(
                toga.Label(quotes_top[i+1], 
                style=Pack(padding=(0,4,4), text_align="right", font_size=7, font_style="italic", color="#EBF6F7")))
            
        quotes_middle = [
            "“Pain is inevitable. Suffering is optional.”", "— Haruki Murakami, What I Talk About When I Talk About Running",
            "“If you're going to do something that's going to slow down your work, just as well put off doing\nit as long as possible.”", "— John Wyndham, The Chrysalids",
            "“What we seek is some kind of compensation for what we put up with.”", "— Nakata, Kafka on the Shore by Haruki Murakami",
            "“It has long been an axiom of mine that the little things are infinitely the most important.”", "— Sherlock Holmes, by Arthur Conan Doyle"
        ]
        quotes_box_middle = toga.Box(style=Pack(direction=COLUMN, flex=0.3, padding=4))
        for i in range(0, len(quotes_middle)-1, 2):
            quotes_box_middle.add(toga.Label(quotes_middle[i], style=Pack(padding=(4,4,0), font_size=7, color="#EBF6F7")))
            quotes_box_middle.add(
                toga.Label(quotes_middle[i+1], 
                style=Pack(padding=(0,4,4), text_align="right", font_size=7, font_style="italic", color="#EBF6F7")))
        
        quotes_bottom = [
            "“The habit of hoping always for better things is actually an obstacle to success.”", "— Stendhal, The Red and the Black",
            "“The second half of a man's life is made up of nothing but the habits he has acquired during the\nfirst half.”", "— Alexei Ivanovich, The Gambler by Fyodor Dostoevsky",
            "“It is better to be lucky. But I would rather be exact. Then when luck comes you are ready.”", "— Santiago, The Old Man and the Sea by Ernest Hemingway",
            "“I'm not afraid of death; I just don't want to be there when it happens.”", "— Toru Watanabe, Norwegian Wood by Haruki Murakami (originally Woody Allen)"
        ]
        quotes_box_bottom = toga.Box(style=Pack(direction=COLUMN, flex=0.3, padding=4, background_color="#393432"))
        for i in range(0, len(quotes_bottom)-1, 2):
            quotes_box_bottom.add(toga.Label(quotes_bottom[i], style=Pack(padding=(4,4,0), font_size=7, color="#EBF6F7")))
            quotes_box_bottom.add(
                toga.Label(quotes_bottom[i+1], 
                style=Pack(padding=(0,4,4), text_align="right", font_size=7, font_style="italic", color="#EBF6F7")))
            

        create_label = toga.Label(
            "Pray inscribe the habit thou wishest\nto create(no more than 34 characters):", 
            style=Pack(padding=(18,18,0), font_size=14, color="#EBF6F7"))
        self.habit_manage_create_input = toga.TextInput(
            id="habit_create input 34",
            on_change=length_check, 
            style=Pack(padding=(0,18), height=44, font_size=12, color="#EBF6F7", background_color="#27221F"))
        create_button = toga.Button(
            "Create", on_press=self.create_habit, 
            style=Pack(flex=0.5, height=120, padding=(11,11,19), font_size=22, color="#EBF6F7", background_color="#27221F"))
        habit_manage_create_box = toga.Box(
            children=[create_label, self.habit_manage_create_input, create_button],
            style=Pack(direction=COLUMN, flex=0.23))

        select_label = toga.Label(
            "Pray choose the habit thou wishest\nto manage:", 
            style=Pack(padding=(18,18,0), font_size=14, color="#EBF6F7"))
        self.habit_manage_select = toga.Selection(
            on_change=self.manage_habit_change,
            style=Pack(padding=(10,18)))
        select_box = toga.Box(
            children=[select_label, self.habit_manage_select],
            style=Pack(direction=COLUMN, flex=0.08))
        
        self.habit_manage_delete_button = toga.Button(
            "Delete", on_press=self.delete_habit_dialog, 
            style=Pack(flex=0.5, height=120, padding=(11,4,11,11), font_size=22, color="#EBF6F7", background_color="#27221F"))
        self.habit_manage_complete_button = toga.Button(
            "Complete", on_press=self.tracking_habit_dialog, 
            id="habit complete button",
            style=Pack(flex=0.5, height=120, padding=(11,11,11,4), font_size=22, color="#EBF6F7", background_color="#27221F"))
        self.habit_manage_resume_button = toga.Button(
            "Resume", on_press=self.tracking_habit_dialog, 
            id="habit resume button",
            style=Pack(flex=0.5, height=120, padding=(11,11,11,4), font_size=22, color="#EBF6F7", background_color="#27221F"))
        
        self.habit_manage_button_box = toga.Box(
            style=Pack(direction=ROW, flex=0.16))
        
        self.habit_manage_rename_input = toga.TextInput(
            id="habit_rename input 34",
            on_change=length_check,
            placeholder="new name for the habit", 
            style=Pack(padding=(0,18), height=44, font_size=12, color="#EBF6F7", background_color="#27221F"))
        rename_button = toga.Button(
            "Rename", on_press=self.rename_habit_dialog, 
            style=Pack(flex=0.5, height=120, padding=11, font_size=22, color="#EBF6F7", background_color="#27221F"))
        rename_box = toga.Box(
            children=[self.habit_manage_rename_input, rename_button], 
            style=Pack(direction=COLUMN, flex=0.3))
        
        habit_manage_box = toga.Box(
            children=[
                label, toga.Divider(style=Pack(background_color="#27221F")), 
                quotes_box_top, toga.Divider(style=Pack(background_color="#27221F")), 
                habit_manage_create_box, toga.Divider(style=Pack(background_color="#27221F")), 
                quotes_box_middle, toga.Divider(style=Pack(background_color="#27221F")), 
                select_box, 
                self.habit_manage_button_box, 
                rename_box, toga.Divider(style=Pack(background_color="#27221F")), 
                quotes_box_bottom
            ], 
            style=Pack(direction=COLUMN, background_color="#393432"))
        habit_manage_container = toga.ScrollContainer(content=habit_manage_box, horizontal=False)

        return habit_manage_container
    

    def get_habit_more_box(self):
        self.habit_more_box = toga.Box(
            style=Pack(direction=COLUMN, background_color="#393432"))
        habit_more_container = toga.ScrollContainer(content=self.habit_more_box, horizontal=False)

        return habit_more_container
    

    def setup_habits(self):
        habit_tracker_box = self.get_habit_tracker_box()
        habit_details_box = self.get_habit_details_box()
        habit_manage_box = self.get_habit_manage_box()
        habit_more_box = self.get_habit_more_box()
    
        con, cur = get_connection(self.db_path)
        cur.executescript("""
            CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            longest_streak INTEGER DEFAULT 0,
            created_date DATE DEFAULT (date('now', 'localtime')),
            completed_date DATE
            );
            
            CREATE TABLE IF NOT EXISTS habit_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER NOT NULL,
            record_date DATE DEFAULT (date('now', 'localtime')),
            state TEXT CHECK(state IN ('success', 'failure', 'skip') OR state IS NULL),
            FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE ON UPDATE CASCADE
            );
                          
            CREATE INDEX IF NOT EXISTS idx_habit_records_state ON habit_records(state);

            CREATE INDEX IF NOT EXISTS idx_habit_records_date ON habit_records(record_date);    
        """)
        con.commit()

        self.update_habit((con, cur))

        con.close()

        return habit_tracker_box, habit_details_box, habit_manage_box, habit_more_box
    

    def update_habit(self, details=True, tracking=True, con_cur=None):
        con, cur = get_connection(self.db_path, con_cur)

        self.create_habit_records(False, (con, cur))
        self.habit_get_data(details=details, tracking=tracking, con_cur=(con, cur))
        
        self.load_habits(None, False, details, tracking)

        date_w = self.habit_tracker_date
        date_w.max = date_w.value = date.today()
        date_w.min = date.today() - timedelta(days=6)

        close_connection(con, con_cur)
    

    def habit_get_data(self, dates=None, details=False, tracking=False, con_cur=None):
        con, cur = get_connection(self.db_path, con_cur)
        if dates is None:
            dates = [date.today()-timedelta(days=i) for i in range(7)]
    
        for d in dates:
            iso = d.isoformat()
            cur.execute("SELECT id, record_date FROM habit_records")

            cur.execute("""
                SELECT habits.id, habits.name, habit_records.state
                FROM habits
                INNER JOIN habit_records
                ON habits.id = habit_records.habit_id
                WHERE habit_records.record_date = ?
                ORDER BY 
                    CASE WHEN habit_records.state IS NULL THEN 0 ELSE 1 END,
                    habit_records.state,
                    habits.name;
            """, (d,))
            self.data[iso] = cur.fetchall()
            
            for i in range(len(self.data[iso])):
                cur.execute("""
                    SELECT state FROM habit_records
                    WHERE habit_id = ?
                    AND record_date <= ?
                    AND state IS NOT NULL
                    ORDER BY record_date DESC;
                """, (self.data[iso][i][0], d,))
                states = cur.fetchall()

                streak = self.calculate_streak(states)

                self.data[iso][i] = self.data[iso][i] + (streak,)

        if details:
            cur.execute("""
                SELECT id, name, completed_date FROM habits
                ORDER BY 
                    CASE WHEN completed_date IS NULL THEN 0 ELSE 1 END,
                    completed_date,
                    id DESC;
            """)
            self.data["list"] = cur.fetchall()

        if tracking:
            cur.execute("SELECT name, completed_date FROM habits;")
            self.data["tracking"] = {h:c for (h, c) in cur.fetchall()}

        close_connection(con, con_cur)


    def load_habits(self, widget, tracker=True, details=False, tracking=False):
        if tracker:
            habit_box = self.habit_tracker_list_box
            habit_box.clear()

            data = self.data[self.habit_tracker_date.value.isoformat()]
            if len(data) == 0:
                    habit_box.add(toga.Label(
                        "No tracked habits on the day.",
                        style=Pack(padding=10, font_size=12, color="#EBF6F7")))
            else:
                states = ["success", "failure", "skip"]
                for h in data:
                    button_box = toga.Box(style=Pack(direction=ROW))
                    if h[2]:
                        img_boxes = [toga.Box(style=Pack(direction=COLUMN, flex=0.33)) for i in range(3)]
                        if h[2] == states[0]:
                            img_boxes[0].add(toga.ImageView(toga.Image("resources/habit/success.png"), style=Pack(flex=1, alignment="center", height=40)))
                        elif h[2] == states[1]:
                            img_boxes[1].add(toga.ImageView(toga.Image("resources/habit/failure.png"), style=Pack(flex=1, alignment="center", height=40)))
                        else:
                            img_boxes[2].add(toga.ImageView(toga.Image("resources/habit/skip.png"), style=Pack(flex=1, alignment="center", height=40)))
                        for i in range(3):
                            button_box.add(img_boxes[i])
                    else:
                        for s in states:
                            button_id = f"{h[0]} habit {s} button"
                            if button_id not in self.widgets:
                                self.widgets[button_id] = toga.Button(
                                    s.capitalize(), id=button_id, on_press=self.change_habit_state_dialog, 
                                    style=Pack(flex=0.33, height=42, font_size=12, color="#EBF6F7", background_color="#27221F"))
                            button_box.add(self.widgets[button_id])

                    habit_top = toga.Label(
                        f"[{h[0]:04d}] | Current streak: {h[3]}", 
                        style=Pack(padding=(14,4,4), flex=0.5, font_size=11, color="#EBF6F7"))
                    habit_bottom = toga.Label(
                        h[1], 
                        style=Pack(padding=(0,4,0), flex=0.5, font_size=11, color="#EBF6F7"))
                    habit_box.add(
                        toga.Box(
                            children=[
                                habit_top,
                                habit_bottom,
                                button_box], 
                            style=Pack(direction=COLUMN)),
                        toga.Divider(style=Pack(background_color="#27221F")))
                    
        if details:
            habit_box = self.habit_details_list_box
            habit_box.clear()

            data = self.data["list"]
            if len(data) == 0:
                    habit_box.add(toga.Label(
                        "All habits will appear here.",
                        style=Pack(padding=10, font_size=12, color="#EBF6F7")))
            for h in data:
                button_id = f"{h[0]} details button"
                tracked = "No" if h[2] else "Yes"
                if button_id not in self.widgets:
                    self.widgets[button_id] = toga.Button(
                                        "More", id=button_id, on_press=self.app.open_habit_more, 
                                        style=Pack(flex=0.14, height=72, font_size=12, color="#EBF6F7", background_color="#27221F"))
                habit_top = toga.Label(
                    f"[{h[0]:04d}] | Tracked: {tracked}", 
                    style=Pack(padding=(14,4,4), flex=0.5, font_size=11, color="#EBF6F7"))
                habit_bottom = toga.Label(
                    h[1], 
                    style=Pack(padding=(0,4,14), flex=0.5, font_size=11, color="#EBF6F7"))
                habit_label_box = toga.Box(children=[habit_top, habit_bottom], style=Pack(direction=COLUMN, flex=0.86))
                
                habit_box.add(toga.Box(
                            children=[
                                habit_label_box,
                                self.widgets[button_id]], 
                            style=Pack(direction=ROW)),
                        toga.Divider(style=Pack(background_color="#27221F")))
                
        if tracking:
            self.habit_manage_select.items = sorted([h for h in self.data["tracking"]])


    def load_habit_more(self, id):
        self.habit_more_box.clear()

        con, cur = get_connection(self.db_path)

        cur.execute("""
            SELECT name, created_date, completed_date, longest_streak FROM habits
            WHERE id = ?;
        """, (id,))
        name, created_date, completed_date, longest_streak = cur.fetchone()

        cur.execute("""
            SELECT COUNT(*) FROM habit_records
            WHERE habit_id = ?;
        """, (id,))
        total_records = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(*) FROM habit_records
            WHERE habit_id = ? AND state = 'success';
        """, (id,))
        total_success = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(*) FROM habit_records
            WHERE habit_id = ? AND state = 'failure';
        """, (id,))
        total_failure = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(*) FROM habit_records
            WHERE habit_id = ? AND state = 'skip';
        """, (id,))
        total_skip = cur.fetchone()[0]

        cur.execute("""
            WITH success_skip AS (
                SELECT COUNT(*) AS success_skip_count
                FROM habit_records
                WHERE habit_id = ? AND state IN ('success', 'skip')
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

        min_days = {"%W": 3, "%m": 12, "%Y": 60}  
        period_lengths = {"%W": 7, "%m": 30, "%Y": 365}

        average_rates = []

        for date_format in ["%W", "%m", "%Y"]:
            cur.execute("""
                SELECT strftime(?, record_date) as period, 
                    COUNT(*) as total_days, 
                    SUM(CASE WHEN state = 'success' THEN 1 ELSE 0 END) as successful_days
                FROM habit_records 
                WHERE habit_id = ? 
                GROUP BY period
                HAVING COUNT(*) > 0;
            """, (date_format, id,))
            records = cur.fetchall()

            total_periods = 0
            total_successful_days = 0
            total_scaled_successful_days = 0
            one_period_successful_days = 0

            for r in records:
                period_label, total_days, successful_days = r
                period_length = period_lengths[date_format]
                min_days_for_period = min_days[date_format]

                if total_days < min_days_for_period:
                    if not one_period_successful_days:
                        one_period_successful_days = successful_days / 1.0
                else:
                    scaling_factor = period_length / total_days
                    total_scaled_successful_days += successful_days * scaling_factor
                    total_successful_days += successful_days
                    total_periods += 1

            if total_periods == 0:
                if one_period_successful_days:
                    average_rates.append(one_period_successful_days)
                else:
                    average_rates.append(0.0)
            else:
                if total_periods > 1:
                    average_successful_days = round(total_scaled_successful_days / total_periods, 1)
                else:
                    average_successful_days = total_successful_days / 1.0
                average_rates.append(average_successful_days)

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

        habit_label = toga.Label(
            f"Habit [{id:04d}]\n{name}", 
            style=Pack(padding=14, text_align="center", font_weight="bold", font_size=15, color="#EBF6F7"))
        
        dates_label = toga.Label(
            "Dates", 
            style=Pack(padding=14, text_align="center", font_size=14, color="#EBF6F7"))
        created_label = toga.Label(
            f"Created: {created_date}", 
            style=Pack(padding=(14,20), font_size=14, color="#EBF6F7"))
        completed = completed_date if completed_date else '—'
        completed_label = toga.Label(
            f"Completed: {completed}", 
            style=Pack(padding=(0,20,14), font_size=14, color="#EBF6F7"))
        habit_dates_box = toga.Box(
            children=[
                dates_label, toga.Divider(style=Pack(padding=(0,80), background_color="#27221F")), 
                created_label, 
                completed_label
            ], 
            style=Pack(direction=COLUMN))

        total_label = toga.Label(
            "Total", 
            style=Pack(padding=14, text_align="center", font_size=14, color="#EBF6F7"))
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
        

        average_success_label = toga.Label(
            "Average Success Numbers", 
            style=Pack(padding=14, text_align="center", font_size=14, color="#EBF6F7"))
        
        weekly_success = toga.Label(
            f"Weekly: {average_rates[0]}", 
            style=Pack(flex=0.33, padding=14, text_align="center", font_size=14, color="#EBF6F7"))
        monthly_success = toga.Label(
            f"Monthly: {average_rates[1]}", 
            style=Pack(flex=0.33, padding=14, text_align="center", font_size=14, color="#EBF6F7"))
        yearly_success = toga.Label(
            f"Yearly: {average_rates[2]}", 
            style=Pack(flex=0.33, padding=14, text_align="center", font_size=14, color="#EBF6F7"))
        average_rates_box = toga.Box(children=[weekly_success, monthly_success, yearly_success], style=Pack(direction=ROW))

        average_success_box = toga.Box(
            children=[
                average_success_label, toga.Divider(style=Pack(padding=(0,80), background_color="#27221F")), 
                average_rates_box
            ], 
            style=Pack(direction=COLUMN))


        record_calendar_label = toga.Label(
            "Record Calendar", 
            style=Pack(padding=14, text_align="center", font_size=14, color="#EBF6F7"))
        
        year_select_label = toga.Label(
            "Year:", 
            style=Pack(flex=0.3, padding=(14,0,0,20), font_size=14, color="#EBF6F7"))
        year_select = toga.Selection(
            style=Pack(flex=0.7, padding=16))
        year_select_box = toga.Box(
            children=[year_select_label, year_select],
            style=Pack(direction=ROW))

        month_select_label = toga.Label(
            "Month:", 
            style=Pack(flex=0.3, padding=(0,0,0,20), font_size=14, color="#EBF6F7"))
        month_select = toga.Selection(style=Pack(flex=0.7, padding=(2,16,16)))
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

        
        self.habit_more_box.add(
            habit_label, toga.Divider(style=Pack(background_color="#27221F")), 
            habit_dates_box, toga.Divider(style=Pack(background_color="#27221F")), 
            total_box, toga.Divider(style=Pack(background_color="#27221F")), 
            completion_rate_label, toga.Divider(style=Pack(background_color="#27221F")), 
            longest_streak_label, toga.Divider(style=Pack(background_color="#27221F")), 
            average_success_box, toga.Divider(style=Pack(background_color="#27221F")), 
            record_calendar_box, 
            calendar_image_box
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


    async def change_habit_state_dialog(self, widget):
        splt = widget.id.split()
        result = await self.app.main_window.question_dialog("Confirmation", f"Art thou certain thou wishest to set [{int(splt[0]):04d}] habit's state to {splt[2]}?")
        if result:
            await self.change_habit_state(splt)


    async def change_habit_state(self, splt):
        habit_id = splt[0]
        state = splt[2]
        record_date = self.habit_tracker_date.value

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

        self.habit_get_data(dates=[record_date], con_cur=(con, cur))
        self.load_habits(None)

        con.close()


    def create_habit(self, widget):
        habit_name = self.habit_manage_create_input.value
        if habit_name:
            con, cur = get_connection(self.db_path)
            
            cur.execute("""
                INSERT INTO habits (name)
                VALUES (?);
                """, (habit_name,))

            con.commit()

            self.create_habit_records(load=False, con_cur=(con, cur))
            self.habit_get_data(dates=[date.today()], details=True, tracking=True, con_cur=(con, cur))

            con.close()

            self.habit_tracker_date.value = date.today()
            self.load_habits(widget, tracker=False, details=True, tracking=True)
            self.app.open_habit_tracker(widget)
    

    def create_habit_records(self, load=True, con_cur=None):
        con, cur = get_connection(self.db_path, con_cur)

        cur.execute("""
            SELECT habit_id FROM habit_records
            WHERE record_date IS ?;
        """, (date.today(),))
        created = cur.fetchall()

        cur.execute("""
            SELECT id FROM habits
            WHERE completed_date IS NULL;
        """)
        tracked = cur.fetchall()

        ids = set(tracked) - set(created)

        if ids:
            cur.executemany("""
                INSERT INTO habit_records (habit_id)
                VALUES (?);
            """, (ids))
            con.commit()
        
        if load:
            self.habit_get_data(dates=[date.today()], con_cur=(con, cur))
            self.load_habits(None)

        close_connection(con, con_cur)
    

    async def delete_habit_dialog(self, widget):
        result = await self.app.main_window.question_dialog("Confirmation", "Art thou certain thou wishest to delete the habit?")
        if result:
            await self.delete_habit()


    async def delete_habit(self):
        habit = self.habit_manage_select.value

        con, cur = get_connection(self.db_path)
        cur.execute("""
            SELECT id FROM habits
            WHERE name = ?;
        """, (habit,)) 
        habit_id = cur.fetchone()[0]

        cur.execute("""
            SELECT record_date FROM habit_records
            WHERE habit_id = ?
            AND record_date >= ?;
        """, (habit_id, date.today()-timedelta(days=6))) 
        dates = cur.fetchall()

        cur.execute("""
            DELETE FROM habits
            WHERE id = ?;
        """, (habit_id,))
        con.commit()

        self.habit_get_data(dates=[date.fromisoformat(d[0]) for d in dates], details=True, tracking=True, con_cur=(con, cur))
        self.load_habits(None, details=True, tracking=True)


    async def tracking_habit_dialog(self, widget):
        complete = widget.id.split()[1] == "complete"
        word = "complete" if complete else "resume"
        result = await self.app.main_window.question_dialog("Confirmation", f"Art thou certain thou wishest to {word} tracking the habit?")
        if result:
            await self.tracking_habit(complete)

    
    async def tracking_habit(self, complete):
        con, cur = get_connection(self.db_path)

        habit = self.habit_manage_select.value
        if complete:
            cur.execute("""
                UPDATE habits
                SET completed_date = ?
                WHERE name = ?;
            """, (date.today(), habit,))
        else:
            cur.execute("""
                UPDATE habits
                SET completed_date = NULL
                WHERE name = ?;
            """, (habit,))
        con.commit()

        self.habit_get_data(dates=[], tracking=True, con_cur=(con, cur))
        con.close()

        self.manage_habit_change(self.habit_manage_select)      


    def manage_habit_change(self, widget):
        box = self.habit_manage_button_box
        box.clear()
        if widget.value:
            completed = self.data["tracking"][widget.value]
            button = self.habit_manage_resume_button if completed else self.habit_manage_complete_button
            box.add(self.habit_manage_delete_button, button)
        else:
            label = toga.Label(
            "You have no created habits.", 
            style=Pack(padding=(0,18), font_size=14, color="#EBF6F7"))
            box.add(label)

    
    async def rename_habit_dialog(self, widget):
        if self.habit_manage_rename_input.value and self.habit_manage_select.value:
            result = await self.app.main_window.question_dialog("Confirmation", "Art thou certain thou wishest to rename the habit?")
            if result:
                await self.rename_habit()


    async def rename_habit(self):
        new_name = self.habit_manage_rename_input.value
        self.habit_manage_rename_input.value = ""

        con, cur = get_connection(self.db_path)
        
        cur.execute("""
            SELECT id FROM habits
            WHERE name = ?;
        """, (self.habit_manage_select.value,)) 
        habit_id = cur.fetchone()[0]

        cur.execute("""
            SELECT record_date FROM habit_records
            WHERE habit_id = ?
            AND record_date >= ?;
        """, (habit_id, date.today()-timedelta(days=6)))         
        dates = cur.fetchall()

        cur.execute("""
            UPDATE habits
            SET name = ?
            WHERE id = ?;
        """, (new_name, habit_id,))
        con.commit()

        self.habit_get_data(dates=[date.fromisoformat(d[0]) for d in dates], details=True, tracking=True, con_cur=(con, cur))
        con.close()

        self.load_habits(None, details=True, tracking=True)
        self.habit_manage_select.value = new_name


    def calculate_streak(self, states: list) -> int:
        streak = 0
        for s in states:
            if s[0] == "success":
                streak += 1
            elif s[0] == "failure":
                break
        return streak
    

    async def reset_habit_dialog(self, widget):
        result = await self.app.main_window.question_dialog("Confirmation", "Are you sure you wish to reset Habits database?")
        if result:
            await self.reset_habit()


    async def reset_habit(self):
        con, cur = get_connection(self.db_path)
        cur.execute("DROP TABLE habits;")
        cur.execute("DROP TABLE habit_records;")
        con.commit()

        cur.execute("""
            CREATE TABLE habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            longest_streak INTEGER DEFAULT 0,
            created_date DATE DEFAULT (date('now', 'localtime')),
            completed_date DATE
            );
        """)
        cur.execute("""
            CREATE TABLE habit_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER NOT NULL,
            record_date DATE DEFAULT (date('now', 'localtime')),
            state TEXT CHECK(state IN ('success', 'failure', 'skip')),
            FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE ON UPDATE CASCADE
            );
        """)
        cur.execute("CREATE INDEX idx_habit_records_state ON habit_records(state);")
        cur.execute("CREATE INDEX idx_habit_records_date ON habit_records(record_date);")
        con.commit()

        self.habit_get_data(details=True, con_cur=(con, cur))

        con.close()

        self.load_habits(None, details=True, tracking=True)

        await self.app.main_window.info_dialog("Success", "Habits database was successfully reset.")

    
    def reset_today_habit_records(self, widget):
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

    
    def habit_today(self, widget):
        self.habit_tracker_date.value = date.today()


    def clear_habit_manage_box(self):
        self.habit_manage_create_input.value = ""
        self.habit_manage_rename_input.value = ""