import toga
from toga.style import Pack
from toga.constants import COLUMN, ROW
from datetime import date, timedelta
import sqlite3 as sql
from collections import defaultdict
from imerisios.mylib.tools import length_check, get_connection, close_connection, get_month_dicts

class Journal:
    def __init__(self, app, db_path):
        self.app = app
        self.db_path = db_path

        self.widgets = {}
        self.journal_data = {}
        self.month_num_to_name, self.month_name_to_num = get_month_dicts()

    
    def get_journal_box(self):
        label = toga.Label(
            "Journal", 
            style=Pack(padding=14, text_align="center", font_weight="bold", font_size=20, color="#EBF6F7"))
        
        quotes_top = [
            "“So we beat on, boats against the current, borne back ceaselessly into the past.”", "— Nick Carraway, The Great Gatsby by F. Scott Fitzgerald",
            "“You cannot create experience. You must undergo it.”", "— Albert Camus, The Myth of Sisyphus", 
            "“We are cups, constantly and quietly being filled. The trick is knowing how to tip ourselves\nover and let the beautiful stuff out.”", "— Ray Bradbury, Dandelion Wine"
        ]
        quotes_box_top = toga.Box(style=Pack(direction=COLUMN, flex=0.2, padding=4))
        for i in range(0, len(quotes_top)-1, 2):
            quotes_box_top.add(toga.Label(quotes_top[i], style=Pack(padding=(4,4,0), font_size=7, color="#EBF6F7")))
            quotes_box_top.add(
                toga.Label(quotes_top[i+1], 
                style=Pack(padding=(0,4,4), text_align="right", font_size=7, font_style="italic", color="#EBF6F7")))

        quotes_middle = [
            "“Memories, I think, are a key to identity. And if our identity is formed by our memories, then\npreserving them is of the utmost importance.”", "— Kazuo Ishiguro, An Artist of the Floating World",
            "“We are a sum of our past. It's a mathematical fact, you see. All that we have experienced, all\nthat we have seen, heard, felt, tasted, and touched has made us who we are now.”", "— Harry Hole, by Jo Nesbø"
        ]
        quotes_box_middle = toga.Box(style=Pack(direction=COLUMN, flex=0.16, padding=4))
        for i in range(0, len(quotes_middle)-1, 2):
            quotes_box_middle.add(toga.Label(quotes_middle[i], style=Pack(padding=(4,4,0), font_size=7, color="#EBF6F7")))
            quotes_box_middle.add(
                toga.Label(quotes_middle[i+1], 
                style=Pack(padding=(0,4,4), text_align="right", font_size=7, font_style="italic", color="#EBF6F7")))
        
        quotes_bottom = [
            "“Maybe. But I know I exist. And I have to answer to me. And consider this: I'm not expecting any\npunishment or reward. I take my actions free of any eternal consequence.”", "— Martin Spencer, A Long Time Until Now by Michael Z. Williamson",
            "“The idea which makes a man's mind run like a squirrel in a cage is generally an idea that\nisn't quite right.”", "— Stendhal, The Red and the Black",
            "“If you're going to be arrogant, make sure you can back it up.”", "— Eithan Arelius, Cradle by Will Wight"
        ]
        quotes_box_bottom = toga.Box(style=Pack(direction=COLUMN, flex=0.24, padding=4))
        for i in range(0, len(quotes_bottom)-1, 2):
            quotes_box_bottom.add(toga.Label(quotes_bottom[i], style=Pack(padding=(4,4,0), font_size=7, color="#EBF6F7")))
            quotes_box_bottom.add(
                toga.Label(quotes_bottom[i+1], 
                style=Pack(padding=(0,4,4), text_align="right", font_size=7, font_style="italic", color="#EBF6F7")))


        entries_button = toga.Button(
            "Entries", on_press=self.app.open_journal_entries, 
            style=Pack(flex=0.2, height=140, padding=18, font_size=28, color="#EBF6F7", background_color="#27221F"))

        notes_button = toga.Button(
            "Notes", on_press=self.app.open_journal_notes, 
            style=Pack(flex=0.2, height=140, padding=18, font_size=28, color="#EBF6F7", background_color="#27221F"))
        
        journal_box = toga.Box(
            children=[
                label, toga.Divider(style=Pack(background_color="#27221F")),
                quotes_box_top,
                entries_button,
                quotes_box_middle,
                notes_button,
                quotes_box_bottom
            ],
            style=Pack(direction=COLUMN, background_color="#393432"))
        
        return journal_box
    

    def get_entries_box(self):
        label = toga.Label(
            "Entries", 
            style=Pack(padding=14, text_align="center", font_weight="bold", font_size=20, color="#EBF6F7"))

        year_label = toga.Label("Year:", style=Pack(padding=14, font_size=14, color="#EBF6F7"))
        self.journal_entries_year_select = toga.Selection(
            id="journal_entries date year", 
            on_change=self.load_entry,
            style=Pack(padding=(0,4,14))
        )
        year_box = toga.Box(children=[year_label, self.journal_entries_year_select], style=Pack(direction=COLUMN, flex=0.3))

        month_label = toga.Label("Month:", style=Pack(padding=14, font_size=14, color="#EBF6F7"))
        self.journal_entries_month_select = toga.Selection(
            id="journal_entries date month", 
            on_change=self.load_entry,
            style=Pack(padding=(0,4,14))
        )
        month_box = toga.Box(children=[month_label, self.journal_entries_month_select], style=Pack(direction=COLUMN, flex=0.45))

        day_label = toga.Label("Day:", style=Pack(padding=14, font_size=14, color="#EBF6F7"))
        self.journal_entries_day_select = toga.Selection(
            id="journal_entries date day", 
            on_change=self.load_entry,
            style=Pack(padding=(0,4,14))
        )
        day_box = toga.Box(children=[day_label, self.journal_entries_day_select], style=Pack(direction=COLUMN, flex=0.25))

        date_selection_box = toga.Box(
            children=[year_box, month_box, day_box],
            style=Pack(direction=ROW))
        
        today_button = toga.Button(
            "Today", on_press=self.entry_today, 
            style=Pack(flex=0.3, padding=(0,44,4), height=44, font_size=11, color="#EBF6F7", background_color="#27221F")
        )
        
        date_box = toga.Box(
            children=[date_selection_box, today_button],
            style=Pack(direction=COLUMN))


        self.journal_entries_input = toga.MultilineTextInput(placeholder="thy entry", style=Pack(flex=0.59, padding=(0,11), font_size=12, color="#EBF6F7", background_color="#27221F"))

        self.journal_entries_save_button = toga.Button(
            "Save", on_press=self.save_entry_dialog, 
            style=Pack(height=140, padding=(0,11,11), font_size=28, color="#EBF6F7", background_color="#27221F"))
        self.journal_entries_save_box = toga.Box(style=Pack(direction=COLUMN, flex=0.21))
        
        entries_box = toga.Box(
            children=[
            label, toga.Divider(style=Pack(background_color="#27221F")),
            date_box, toga.Divider(style=Pack(background_color="#27221F")),
            self.journal_entries_input,
            self.journal_entries_save_box
            ], 
            style=Pack(direction=COLUMN, background_color="#393432"))
        
        return entries_box
    
    def get_notes_box(self):
        label = toga.Label(
            "Notes", 
            style=Pack(padding=14, text_align="center", font_weight="bold", font_size=20, color="#EBF6F7"))

        self.journal_notes_list_box = toga.Box(style=Pack(direction=COLUMN))
        journal_notes_list_container = toga.ScrollContainer(content=self.journal_notes_list_box, horizontal=False, style=Pack(flex=0.9))

        notes_box = toga.Box(
            children=[
            label, toga.Divider(style=Pack(background_color="#27221F")),
            journal_notes_list_container
            ], 
            style=Pack(direction=COLUMN, background_color="#393432")
        )

        return notes_box


    def get_note_create_box(self):
        label = toga.Label(
            "Create a New Note", 
            style=Pack(flex=0.09, padding=14, text_align="center", font_weight="bold", font_size=18, color="#EBF6F7"))
        
        title_label = toga.Label(
            "Title (no more than 34 characters):", 
            style=Pack(padding=(18,18,0), font_size=14, color="#EBF6F7"))
        self.journal_notes_create_title_input = toga.TextInput(
            id="note_create_title input 34",
            on_change=length_check, 
            style=Pack(padding=(0,11), height=44, font_size=12, color="#EBF6F7", background_color="#27221F"))
        
        content_label = toga.Label(
            "Content:", 
            style=Pack(padding=(18,18,0), font_size=14, color="#EBF6F7"))
        self.journal_notes_create_content_input = toga.MultilineTextInput(style=Pack(flex=0.7, padding=(0,11), font_size=12, color="#EBF6F7", background_color="#27221F"))

        top_box = toga.Box(
            children=[
                title_label,
                self.journal_notes_create_title_input,
                content_label,
                self.journal_notes_create_content_input
            ],
            style=Pack(direction=COLUMN, flex=0.79))

        button = toga.Button(
            "Create", on_press=self.create_note, 
            style=Pack(height=140, padding=(0,11,11), font_size=28, color="#EBF6F7", background_color="#27221F"))
        bottom_box = toga.Box(children=[button], style=Pack(direction=COLUMN, flex=0.21))

        note_create_box = toga.Box(
            children=[
                label, toga.Divider(style=Pack(background_color="#27221F")), 
                top_box, 
                bottom_box
            ], 
            style=Pack(direction=COLUMN, background_color="#393432"))

        return note_create_box


    def get_note_edit_box(self):
        label = toga.Label(
            "Read/Edit the Note", 
            style=Pack(flex=0.09, padding=14, text_align="center", font_weight="bold", font_size=18, color="#EBF6F7"))
        
        title_label = toga.Label(
            "Title (no more than 34 characters):", 
            style=Pack(padding=(18,18,0), font_size=14, color="#EBF6F7"))
        self.journal_notes_edit_title_input = toga.TextInput(
            id="note_edit_title input 34",
            on_change=length_check, 
            style=Pack(padding=(0,11), height=44, font_size=12, color="#EBF6F7", background_color="#27221F"))
        
        content_label = toga.Label(
            "Content:", 
            style=Pack(padding=(18,18,0), font_size=14, color="#EBF6F7"))
        self.journal_notes_edit_content_input = toga.MultilineTextInput(style=Pack(flex=0.7, padding=(0,11), font_size=12, color="#EBF6F7", background_color="#27221F"))

        top_box = toga.Box(
            children=[
                title_label,
                self.journal_notes_edit_title_input,
                content_label,
                self.journal_notes_edit_content_input
            ],
            style=Pack(direction=COLUMN, flex=0.79))

        delete_button = toga.Button(
            "Delete", on_press=self.delete_note_dialog, 
            style=Pack(flex=0.5, height=140, padding=(0,4,11,11), font_size=28, color="#EBF6F7", background_color="#27221F"))
        save_button = toga.Button(
            "Save", on_press=self.save_note_dialog, 
            style=Pack(flex=0.5, height=140, padding=(0,11,11,4), font_size=28, color="#EBF6F7", background_color="#27221F"))
        bottom_box = toga.Box(
            children=[delete_button, save_button], 
            style=Pack(direction=ROW, flex=0.21))
        
        note_edit_box = toga.Box(
            children=[
                label, toga.Divider(style=Pack(background_color="#27221F")), 
                top_box, 
                bottom_box
            ], 
            style=Pack(direction=COLUMN, background_color="#393432"))
        
        return note_edit_box
    

    def setup_journal(self):
        journal_box = self.get_journal_box()
        entries_box = self.get_entries_box()
        notes_box = self.get_notes_box()
        note_create_box = self.get_note_create_box()
        note_edit_box = self.get_note_edit_box()

        con, cur = get_connection(self.db_path)
        cur.executescript("""
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE DEFAULT (date('now', 'localtime')),
                content TEXT NOT NULL
            );
                
            CREATE INDEX IF NOT EXISTS idx_entries_date ON entries(date);

            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                last_updated DEFAULT CURRENT_TIMESTAMP,
                title TEXT NOT NULL,
                content TEXT NOT NULL
            );
                          
            CREATE INDEX IF NOT EXISTS idx_notes_last_updated ON notes(last_updated);
                          
            CREATE TRIGGER IF NOT EXISTS update_last_updated
            AFTER UPDATE ON notes
            FOR EACH ROW
            BEGIN
                UPDATE notes
                SET last_updated = CURRENT_TIMESTAMP
                WHERE id = NEW.id;
            END;
        """)
        con.commit()

        self.update_journal(True, (con, cur))

        con.close()

        return journal_box, entries_box, notes_box, note_create_box, note_edit_box
        

    def update_journal(self, notes=False, con_cur=None):
        con, cur = get_connection(self.db_path, con_cur)

        self.journal_get_data(True, True, (con, cur))
        self.load_entry(None, (con, cur))
        if notes:
            self.load_notes(False, (con, cur))

        close_connection(con, con_cur)


    def journal_get_data(self, entries=False, notes=False, con_cur=None):
        con, cur = get_connection(self.db_path)

        if entries:
            cur.execute("""
                SELECT
                    strftime('%Y', date) AS year,
                    strftime('%m', date) AS month,
                    strftime('%d', date) AS day
                FROM entries
                ORDER BY year, month, day DESC;
            """)
            dates = cur.fetchall()
        
            if not con_cur:
                con.close()

            self.journal_data["entries dates"] = defaultdict(lambda: defaultdict(list))
            
            for year, month, day in dates:
                year = int(year)
                month = int(month)
                day = int(day)
                self.journal_data["entries dates"][year][month].append(day)

            today = date.today()
            year = today.year
            month = today.month
            day = today.day
            if day not in self.journal_data["entries dates"][year][month]:
                self.journal_data["entries dates"][year][month] = [day] + self.journal_data["entries dates"][year][month]

        if notes:
            cur.execute("""
                SELECT id, title
                FROM notes
                ORDER BY last_updated DESC;
            """)
            self.journal_data["notes"] = cur.fetchall()

        close_connection(con, con_cur)
                
    def entry_today(self, widget):
        year_widget = self.journal_entries_year_select
        month_widget = self.journal_entries_month_select
        day_widget = self.journal_entries_day_select

        today = date.today()

        if (
            year_widget.value != today.year 
            or self.month_name_to_num[month_widget.value] != today.month 
            or day_widget.value != today.day
        ):
            year_widget.value = today.year
            month_widget.value = self.month_num_to_name[today.month]
            day_widget.value = today.day
    

    def load_entry(self, widget, con_cur=None):
        if not widget:
            self.journal_entries_year_select.items = [y for y in sorted(self.journal_data["entries dates"], reverse=True)]
        else:
            date_type = widget.id.split()[2]
            value = widget.value

            if date_type == "year":
                self.journal_entries_month_select.items = [self.month_num_to_name[m] for m in sorted(self.journal_data["entries dates"][value], reverse=True)]
            else:
                year = self.journal_entries_year_select.value
                if date_type == "month":
                    self.journal_entries_day_select.items = self.journal_data["entries dates"][year][self.month_name_to_num[value]]
                else:
                    button_box = self.journal_entries_save_box
                    button_box.clear()

                    month = self.month_name_to_num[self.journal_entries_month_select.value]
                    day = widget.value
                    entry_date = date(year, month, day)
                    
                    con, cur = get_connection(self.db_path)

                    cur.execute("SELECT content FROM entries WHERE date = ?;", (entry_date,))
                    result = cur.fetchone()
                    
                    close_connection(con, con_cur)

                    input = self.journal_entries_input
                    if entry_date == date.today():
                        input.readonly = False
                        button_box.add(self.journal_entries_save_button)
                    else:
                        input.readonly = True

                        quotes = [
                            "“The world changes, and all that once was strong now proves unsure.”", "— Théoden, The Lord of the Rings by J.R.R. Tolkien", 
                            "“Memories warm you up from the inside. But they also tear you apart.”", "— Haruki Murakami, Kafka on the Shore",
                            "“The past always seems better when you look back on it than it did at the time.”", "— Robert Jordan, For Whom the Bell Tolls by Ernest Hemingway",
                            "“No matter how much suffering you went through, you never wanted to let go of those\nmemories.”", "— Toru Watanabe, Norwegian Wood by Haruki Murakami"
                        ]
                        for i in range(0, len(quotes)-1, 2):
                            button_box.add(toga.Label(quotes[i], style=Pack(padding=(4,4,0), font_size=7, color="#EBF6F7")))
                            button_box.add(
                                toga.Label(quotes[i+1], 
                                style=Pack(padding=(0,4,4), text_align="right", font_size=7, font_style="italic", color="#EBF6F7")))
                    
                    if result:
                        content = result[0]
                        input.value = content
                    else:
                        input.value = ""

    
    async def save_entry_dialog(self, widget):
        content = self.journal_entries_input.value
        if content:
            result = await self.app.main_window.question_dialog("Confirmation", "Art thou certain thou wishest to save the entry?")
            if result:
                await self.save_entry(content)


    async def save_entry(self, content):
        con, cur = get_connection(self.db_path)

        cur.execute("SELECT id FROM entries WHERE date = ?;", (date.today(),))
        id = cur.fetchone()
        if id:
            cur.execute("""
                UPDATE entries
                SET content = ?
                WHERE id = ?;
            """, (content, id[0],))
        else:
            cur.execute("""
                INSERT INTO entries (content)
                VALUES (?);
            """, (content,))
        con.commit()
        con.close()


    def load_notes(self, data=True, con_cur=None):
        if data:
            self.journal_get_data(notes=True, con_cur=con_cur)

        note_box = self.journal_notes_list_box
        note_box.clear()
        data = self.journal_data["notes"]
        if not data:
                note_box.add(toga.Label(
                    "Created notes will appear here.",
                    style=Pack(padding=10, font_size=12, color="#EBF6F7")))
        else:
            for n in self.journal_data["notes"]:
                b_id = f"{n[0]} note button"
                if b_id not in self.widgets:
                    self.widgets[b_id] = toga.Button(
                        f"{n[1]}", id=b_id, on_press=self.app.open_edit_note, 
                        style=Pack(flex=0.1, height=80, font_size=12, color="#EBF6F7", background_color="#27221F"))
                else: 
                    self.widgets[b_id].text = n[1]
                    
                note_box.add(
                    toga.Box(children=[self.widgets[b_id]], style=Pack(direction=COLUMN)),
                    toga.Divider(style=Pack(background_color="#27221F")))    
                

    def create_note(self, widget):
        title = self.journal_notes_create_title_input.value.strip()
        content = self.journal_notes_create_content_input.value 
        
        if title and content:
            con, cur = get_connection(self.db_path)

            cur.execute("""
                INSERT INTO notes (title, content) 
                VALUES (?, ?);
            """, (title, content,))
            con.commit()

            self.load_notes(con_cur=(con, cur))

            con.close()

            self.app.open_journal_notes(None)

    
    async def save_note_dialog(self, widget):
        title = self.journal_notes_edit_title_input.value.strip()
        content = self.journal_notes_edit_content_input.value

        if content and title:
            result = await self.app.main_window.question_dialog("Confirmation", "Art thou certain thou wishest to save the note?")
            if result:
                await self.save_note(title, content)


    async def save_note(self, title, content):
        con, cur = get_connection(self.db_path)

        cur.execute("""
            UPDATE notes
            SET title = ?, content = ?
            WHERE id = ?;
        """, (title, content, self.temp_note_id,))
        con.commit()

        self.load_notes(con_cur=(con, cur))
    
        con.close()


    async def delete_note_dialog(self, widget):
        result = await self.app.main_window.question_dialog("Confirmation", "Art thou certain thou wishest to delete the note?")
        if result:
            await self.delete_note()


    async def delete_note(self):
        con, cur = get_connection(self.db_path)

        cur.execute("""
            DELETE FROM notes
            WHERE id = ?;
        """, (self.temp_note_id,))
        con.commit()

        self.load_notes(con_cur=(con, cur))

        con.close()

        self.app.open_journal_notes(None)


    async def reset_journal_dialog(self, widget):
        result = await self.app.main_window.question_dialog("Confirmation", "Are you sure you wish to reset Journal database?")
        if result:
            await self.reset_journal()


    async def reset_journal(self):
        con, cur = get_connection(self.db_path)
        cur.execute("DROP TABLE entries;")
        cur.execute("DROP TABLE notes;")
        con.commit()

        cur.executescript("""
            CREATE TABLE entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE DEFAULT (date('now', 'localtime')),
                content TEXT NOT NULL
            );
                
            CREATE INDEX idx_entries_date ON entries(date);

            CREATE TABLE notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                last_updated DEFAULT CURRENT_TIMESTAMP,
                title TEXT NOT NULL,
                content TEXT NOT NULL
            );
                          
            CREATE INDEX idx_notes_last_updated ON notes(last_updated);
                          
            CREATE TRIGGER update_last_updated
            AFTER UPDATE ON notes
            FOR EACH ROW
            BEGIN
                UPDATE notes
                SET last_updated = CURRENT_TIMESTAMP
                WHERE id = NEW.id;
            END;
        """)
        con.commit()

        self.update_journal(True, (con, cur))

        con.close()

        await self.app.main_window.info_dialog("Success", "Journal database was successfully reset.")


    def clear_note_create_box(self):
        self.journal_notes_create_title_input.value = ""
        self.journal_notes_create_content_input.value = ""

    
    def load_edit_note_box(self, id):
        self.temp_note_id = id
        con, cur = get_connection(self.db_path)
        cur.execute("SELECT title, content FROM notes WHERE id = ?", (self.temp_note_id,))
        title, content = cur.fetchone()

        con.close()

        self.journal_notes_edit_title_input.value = title
        self.journal_notes_edit_content_input.value = content