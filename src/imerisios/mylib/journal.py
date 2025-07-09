import toga
from toga.style import Pack
from toga.constants import COLUMN, ROW
from datetime import date, timedelta
import sqlite3 as sql
import calendar
from collections import defaultdict
from imerisios.mylib.tools import get_back_next_buttons, reverse_dict, length_check, get_connection, close_connection, get_ranges, set_range, change_range


class Journal:
    def __init__(self, app, db_path):
        self.app = app
        self.db_path = db_path

        self.strings = self.app.strings["journal"]
        self.strings_c = self.app.strings["common"]

        self.widgets_dict = {}
        self.data = {"entries": {}}
        self.data["entries quotes"] = [
            "“The world changes, and all that once was strong now proves unsure.”", "— Théoden, The Lord of the Rings by J.R.R. Tolkien", 
            "“Memories warm you up from the inside. But they also tear you apart.”", "— Haruki Murakami, Kafka on the Shore",
            "“The past always seems better when you look back on it than it did at the time.”", "— Robert Jordan, For Whom the Bell Tolls by Ernest Hemingway",
            "“No matter how much suffering you went through, you never wanted to let go of those\nmemories.”", "— Toru Watanabe, Norwegian Wood by Haruki Murakami"
        ]
        self.maps = {"num_to_name": {i: calendar.month_name[i] for i in range(1, 13)}}
        self.maps["name_to_num"] = reverse_dict(self.maps["num_to_name"])
        self.maps["localized_to_system"] = {k: v for k, v in zip(self.strings_c["months"], calendar.month_name[1:])}


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


    def get_quotes_box(self, quotes, flex):
        box = toga.Box(style=Pack(direction=COLUMN, flex=flex, padding=4))
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
    

    def get_journal_box(self):
        label = toga.Label(
            self.strings["journal"], 
            style=Pack(padding=14, text_align="center", font_weight="bold", font_size=18, color=self.clrs[2])
        )
        
        quotes_top = [
            "“So we beat on, boats against the current, borne back ceaselessly into the past.”", "— Nick Carraway, The Great Gatsby by F. Scott Fitzgerald",
            "“You cannot create experience. You must undergo it.”", "— Albert Camus, The Myth of Sisyphus", 
            "“We are cups, constantly and quietly being filled. The trick is knowing how to tip ourselves\nover and let the beautiful stuff out.”", "— Ray Bradbury, Dandelion Wine"
        ]
        quotes_middle = [
            "“Memories, I think, are a key to identity. And if our identity is formed by our memories, then\npreserving them is of the utmost importance.”", "— Kazuo Ishiguro, An Artist of the Floating World",
            "“We are a sum of our past. It's a mathematical fact, you see. All that we have experienced, all\nthat we have seen, heard, felt, tasted, and touched has made us who we are now.”", "— Harry Hole, by Jo Nesbø"
        ]
        quotes_bottom = [
            "“Maybe. But I know I exist. And I have to answer to me. And consider this: I'm not expecting any\npunishment or reward. I take my actions free of any eternal consequence.”", "— Martin Spencer, A Long Time Until Now by Michael Z. Williamson",
            "“The idea which makes a man's mind run like a squirrel in a cage is generally an idea that\nisn't quite right.”", "— Stendhal, The Red and the Black",
            "“If you're going to be arrogant, make sure you can back it up.”", "— Eithan Arelius, Cradle by Will Wight"
        ]
        quotes_box_top = self.get_quotes_box(quotes_top, 0.2)
        quotes_box_middle = self.get_quotes_box(quotes_middle, 0.16)
        quotes_box_bottom = self.get_quotes_box(quotes_bottom, 0.24)

        entries_button = toga.Button(
            self.strings["entries"], on_press=self.app.open_journal_entries, 
            style=Pack(flex=0.2, height=140, padding=18, font_size=18, color=self.clrs[2], background_color=self.clrs[1])
        )

        notes_button = toga.Button(
            self.strings["notes"], on_press=self.app.open_journal_notes, 
            style=Pack(flex=0.2, height=140, padding=18, font_size=18, color=self.clrs[2], background_color=self.clrs[1])
        )
        
        chld = [
            label, self.get_div(),
            quotes_box_top,
            entries_button,
            quotes_box_middle,
            notes_button,
            quotes_box_bottom
        ]
        
        journal_box = toga.Box(children=chld, style=Pack(direction=COLUMN, background_color=self.clrs[0]))
        
        self.reg(chld + [journal_box])

        return journal_box
    

    def get_entries_box(self):
        label = toga.Label(
            self.strings["entries"], 
            style=Pack(padding=14, text_align="center", font_weight="bold", font_size=18, color=self.clrs[2])
        )

        boxes = []
        for s, flex in (("year", 0.3), ("month", 0.45), ("day", 0.25)):
            l = toga.Label(f"{self.strings_c[s]}:", style=Pack(padding=14, font_size=14, color=self.clrs[2]))

            self.widgets_dict[f"entries {s} selection"] = toga.Selection(
                id=f"journal_entries date {s}", 
                on_change=self.load_entry,
                style=Pack(padding=(0,4), height=44)
            )

            boxes.append(toga.Box(children=[l, self.widgets_dict[f"entries {s} selection"]], style=Pack(direction=COLUMN, flex=flex)))

            self.reg([l])

        date_selection_box = toga.Box(children=boxes, style=Pack(direction=ROW))
        
        today_button = toga.Button(
            self.strings_c["today"], on_press=self.entry_today, 
            style=Pack(flex=0.3, padding=4, height=44, font_size=13, color=self.clrs[2], background_color=self.clrs[1])
        )
        
        date_box = toga.Box(
            children=[date_selection_box, today_button],
            style=Pack(direction=COLUMN))

        self.widgets_dict["entries input"] = toga.MultilineTextInput(
            placeholder=self.strings["entries_input_placeholder"], 
            style=Pack(flex=0.6, padding=(0,11), font_size=12, color=self.clrs[2], background_color=self.clrs[1])
        )

        self.widgets_dict["entries save button"] = toga.Button(
            self.strings_c["save"], on_press=self.save_entry_dialog, 
            style=Pack(height=120, padding=11, font_size=18, color=self.clrs[2], background_color=self.clrs[1])
        )
        self.widgets_dict["entries button box"] = toga.Box(style=Pack(direction=COLUMN))
        
        
        quotes = self.data["entries quotes"]
        self.widgets_dict["entries quotes box"] = self.get_quotes_box(quotes, flex=0.2)

        chld = [
            label, self.get_div(),
            date_box, self.get_div(),
            self.widgets_dict["entries input"], self.get_div(),
            self.widgets_dict["entries button box"]
        ]
        
        entries_box = toga.Box(children=chld, style=Pack(direction=COLUMN, background_color=self.clrs[0]))
        
        self.reg(chld + [entries_box, self.widgets_dict["entries save button"], today_button])

        return entries_box
    
    def get_notes_box(self):
        label = toga.Label(
            self.strings["notes"], 
            style=Pack(padding=14, text_align="center", font_weight="bold", font_size=18, color=self.clrs[2])
        )

        back_next_buttons = get_back_next_buttons(id="notes", func=lambda button: change_range(button, widgets=self.widgets_dict), color=self.clrs[2], background_color=self.clrs[1])
    
        self.widgets_dict["notes range"] = toga.Selection(
            id="notes range", 
            on_change=self.load_notes,
            style=Pack(flex=0.6, padding=4, height=44)
        )
        notes_range_box = toga.Box(
            children=[back_next_buttons[0], self.widgets_dict["notes range"], back_next_buttons[1]],
            style=Pack(direction=ROW)
        )

        self.widgets_dict["notes list box"] = toga.Box(style=Pack(direction=COLUMN))
        self.widgets_dict["notes list container"] = toga.ScrollContainer(
            content=self.widgets_dict["notes list box"], 
            horizontal=False, 
            style=Pack(flex=0.9)
        )

        self.widgets_dict["no_notes label"] = toga.Label(
            self.strings["no_notes_label"], 
            style=Pack(padding=10, font_size=12, color=self.clrs[2])
        )

        chld = [
            label, self.get_div(),
            notes_range_box, self.get_div(),
            self.widgets_dict["notes list container"]
        ]
        notes_box = toga.Box(children=chld, style=Pack(direction=COLUMN, background_color=self.clrs[0]))

        self.reg(chld + back_next_buttons + [notes_box, self.widgets_dict["no_notes label"]])

        return notes_box


    def get_notes_add_edit_boxes(self):
        boxes = []
        for t in ("add", "edit"):
            label = toga.Label(
                self.strings[f"{t}_note_label"], 
                style=Pack(flex=0.09, padding=14, text_align="center", font_weight="bold", font_size=18, color=self.clrs[2])
            )
            
            title_label = toga.Label(
                f"{self.strings['title']}:", 
                style=Pack(padding=(18,18,0), font_size=14, color=self.clrs[2])
            )
            self.widgets_dict[f"notes {t} title input"] = toga.TextInput(
                placeholder=self.strings["title_input_placeholder"],
                id=f"notes_{t}_title input 34",
                on_change=length_check, 
                style=Pack(padding=(0,11,18), height=44, font_size=12, color=self.clrs[2], background_color=self.clrs[1])
            )
            
            content_label = toga.Label(
                f"{self.strings['content']}:", 
                style=Pack(padding=(18,18,0), font_size=14, color=self.clrs[2])
            )
            self.widgets_dict[f"notes {t} content input"] = toga.MultilineTextInput(
                placeholder=self.strings["content_input_placeholder"],
                style=Pack(flex=0.72, padding=(0,11), font_size=12, color=self.clrs[2], background_color=self.clrs[1])
            )

            top_chld = [
                title_label, self.widgets_dict[f"notes {t} title input"], self.get_div((0,80)), 
                content_label, self.widgets_dict[f"notes {t} content input"] 
            ]
            top_box = toga.Box(children=top_chld, style=Pack(direction=COLUMN, flex=0.8))
            top_container = toga.ScrollContainer(content=top_box, horizontal=False, vertical=False, style=Pack(flex=0.8))

            if t == "add":
                direction = COLUMN
                button = toga.Button(
                    self.strings_c["add"], on_press=self.add_note, 
                    style=Pack(height=120, padding=11, font_size=18, color=self.clrs[2], background_color=self.clrs[1])
                )
                bottom_chld = [button]
            else:
                direction = ROW
                remove_button = toga.Button(
                    self.strings_c["remove"], on_press=self.remove_note_dialog, 
                    style=Pack(flex=0.5, height=120, padding=(11,4,11,11), font_size=18, color=self.clrs[2], background_color=self.clrs[1])
                )
                save_button = toga.Button(
                    self.strings_c["save"], on_press=self.save_note_dialog, 
                    style=Pack(flex=0.5, height=120, padding=(11,11,11,4), font_size=18, color=self.clrs[2], background_color=self.clrs[1])
                )
                bottom_chld = [remove_button, save_button]
            bottom_box = toga.Box(children=bottom_chld, style=Pack(direction=direction))

            chld = [
                label, self.get_div(), 
                top_container, self.get_div(),
                bottom_box
            ]
            box = toga.Box(children=chld, style=Pack(direction=COLUMN, background_color=self.clrs[0]))
            boxes.append(box)

            self.reg(top_chld + bottom_chld + chld + [box])

        return boxes


    def setup_journal(self):
        journal_box = self.get_journal_box()
        entries_box = self.get_entries_box()
        notes_box = self.get_notes_box()
        notes_add_box, notes_edit_box = self.get_notes_add_edit_boxes()

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

        self.update_journal(notes=True, con_cur=(con, cur))

        con.close()

        return journal_box, entries_box, notes_box, notes_add_box, notes_edit_box
        

    def update_journal(self, day_change=False, notes=False, con_cur=None):
        if day_change:
            self.app.setup_journal = True
        else:
            con, cur = get_connection(self.db_path, con_cur)

            self.journal_get_data(True, True, (con, cur))
            self.load_entry(None, (con, cur))
            if notes:
                self.load_notes(data=False, con_cur=(con, cur))

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

            self.data["entries dates"] = defaultdict(lambda: defaultdict(list))
            
            for year, month, day in dates:
                year = int(year)
                month = int(month)
                day = int(day)
                self.data["entries dates"][year][month].append(day)

            today = self.today
            year = today.year
            month = today.month
            day = today.day
            if day not in self.data["entries dates"][year][month]:
                self.data["entries dates"][year][month] = [day] + self.data["entries dates"][year][month]

        if notes:
            cur.execute("""
                SELECT id, title
                FROM notes
                ORDER BY last_updated DESC;
            """)
            self.data["notes"] = cur.fetchall()

        close_connection(con, con_cur)
                
    def entry_today(self, widget):
        year_widget = self.widgets_dict["entries year selection"]
        month_widget = self.widgets_dict["entries month selection"]
        day_widget = self.widgets_dict["entries day selection"]

        today = self.today

        month = self.maps["name_to_num"][self.maps["localized_to_system"][month_widget.value]]
        if (
            year_widget.value != today.year 
            or month != today.month 
            or day_widget.value != today.day
        ):
            year_widget.value = today.year
            month_widget.value = self.strings_c["months"][today.month - 1]
            day_widget.value = today.day
    

    def load_entry(self, widget, con_cur=None):
        if not widget:
            self.widgets_dict["entries year selection"].items = [y for y in sorted(self.data["entries dates"], reverse=True)]
        else:
            date_type = widget.id.split()[2]
            value = widget.value

            if date_type == "year":
                self.widgets_dict["entries month selection"].items = [self.strings_c["months"][m - 1] for m in sorted(self.data["entries dates"][value], reverse=True)]
            else:
                year = self.widgets_dict["entries year selection"].value
                if date_type == "month":
                    month = self.maps["name_to_num"][self.maps["localized_to_system"][value]]
                    self.widgets_dict["entries day selection"].items = self.data["entries dates"][year][month]
                else:
                    month = self.maps["name_to_num"][self.maps["localized_to_system"][self.widgets_dict["entries month selection"].value]]
                    entry_date = date(year, month, value)
                    iso = entry_date.isoformat()
                    if iso not in self.data["entries"]:
                        con, cur = get_connection(self.db_path, con_cur)

                        cur.execute("SELECT content FROM entries WHERE date = ?;", (entry_date,))
                        result = cur.fetchone()
                        
                        close_connection(con, con_cur)

                        if entry_date != self.today:
                            self.data["entries"][iso] = result
                    content = self.data["entries"][iso] if entry_date != self.today else result

                    input = self.widgets_dict["entries input"]
                    button_box = self.widgets_dict["entries button box"]
                    button_box.clear()
                    if entry_date == self.today:
                        input.readonly = False
                        button_box.add(self.widgets_dict["entries save button"])
                    else:
                        input.readonly = True
                        button_box.add(self.widgets_dict["entries quotes box"])
                    
                    if content:
                        input.value = content[0]
                    else:
                        input.value = ""

    
    async def save_entry_dialog(self, widget):
        content = self.widgets_dict["entries input"].value.strip()
        if content:
            result = await self.app.dialog(toga.QuestionDialog(self.strings_c["confirmation"], self.strings["save_entry_question"]))
            if result:
                await self.save_entry(content)


    async def save_entry(self, content):
        con, cur = get_connection(self.db_path)

        cur.execute("SELECT id FROM entries WHERE date = ?;", (self.today,))
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


    def load_notes(self, widget=None, data=False, con_cur=None):
        if data:
            self.journal_get_data(notes=True, con_cur=con_cur)
        
        data = self.data["notes"]

        if not widget:
            items = get_ranges(data)
            set_range(self.widgets_dict["notes range"], items)

        else: 
            box = self.widgets_dict["notes list box"]
            box.clear()

            start, end = [int(i) for i in widget.value.split('–')]

            if start == 0 and end == 0:
                box.add(self.widgets_dict["no_notes label"])
            else:
                for i in range(start-1, end):
                    n = data[i]
                    b_id = f"{n[0]} note button"
                    if b_id not in self.widgets_dict:
                        self.widgets_dict[b_id] = toga.Button(
                            f"{n[1]}", id=b_id, on_press=self.app.open_edit_note, 
                            style=Pack(flex=0.1, height=80, font_size=11, color=self.clrs[2], background_color=self.clrs[1])
                        )
                        self.reg([self.widgets_dict[b_id]])
                    else: 
                        self.widgets_dict[b_id].text = n[1]
                    
                    div = self.get_div()
                    box.add(self.widgets_dict[b_id], div) 

                    self.reg([div]) 
                self.prepare_notes_container()
                

    def add_note(self, widget):
        title = self.widgets_dict["notes add title input"].value.strip()
        content = self.widgets_dict["notes add content input"].value.strip() 
        
        if title and content:
            con, cur = get_connection(self.db_path)

            cur.execute("""
                INSERT INTO notes (title, content) 
                VALUES (?, ?);
            """, (title, content,))
            con.commit()

            self.load_notes(data=True, con_cur=(con, cur))

            con.close()

            self.app.open_journal_notes(None)

    
    async def save_note_dialog(self, widget):
        title = self.widgets_dict["notes edit title input"].value.strip()
        content = self.widgets_dict["notes edit content input"].value.strip()

        if content and title:
            result = await self.app.dialog(toga.QuestionDialog(self.strings_c["confirmation"], self.strings["save_note_question"]))
            if result:
                await self.save_note(title, content)


    async def save_note(self, title, content):
        id = self.temp_note_id

        con, cur = get_connection(self.db_path)

        cur.execute("""
            UPDATE notes
            SET title = ?, content = ?
            WHERE id = ?;
        """, (title, content, id,))
        con.commit()

        button_id = f"{id} note button"
        if button_id in self.widgets_dict:
            del self.widgets_dict[button_id]

        self.load_notes(data=True, con_cur=(con, cur))
    
        con.close()


    async def remove_note_dialog(self, widget):
        result = await self.app.dialog(toga.QuestionDialog(self.strings_c["confirmation"], self.strings["remove_note_question"]))
        if result:
            await self.remove_note()


    async def remove_note(self):
        con, cur = get_connection(self.db_path)

        cur.execute("""
            DELETE FROM notes
            WHERE id = ?;
        """, (self.temp_note_id,))
        con.commit()

        button_id = f"{id} note button"
        if button_id in self.widgets_dict:
            del self.widgets_dict[button_id]

        self.load_notes(data=True, con_cur=(con, cur))

        con.close()

        self.app.open_journal_notes(None)


    async def reset_journal_dialog(self):
        result = await self.app.dialog(toga.QuestionDialog(self.strings_c["confirmation"], self.strings["reset_db_question"]))
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
        con.close()

        self.app.setup_ui(journal=True)

        await self.app.dialog(toga.InfoDialog(self.strings_c["success"], self.strings["reset_db_success"]))


    def clear_note_add_box(self):
        self.widgets_dict["notes add title input"].value = ""
        self.widgets_dict["notes add content input"].value = ""

    
    def load_edit_note_box(self, id):
        self.temp_note_id = id
        con, cur = get_connection(self.db_path)
        cur.execute("SELECT title, content FROM notes WHERE id = ?", (self.temp_note_id,))
        title, content = cur.fetchone()

        con.close()

        self.widgets_dict["notes edit title input"].value = title
        self.widgets_dict["notes edit content input"].value = content
    
    
    async def remove_entry_dialog(self, entry_date):
        result = await self.app.dialog(toga.QuestionDialog(self.strings_c["confirmation"], self.strings["remove_entry_question"].format(date=entry_date.isoformat())))
        if result:
            await self.remove_entry(entry_date)

    
    async def remove_entry(self, entry_date):
        con, cur = get_connection(self.db_path)

        cur.execute("SELECT id FROM entries WHERE date = ?", (entry_date,))

        if id := cur.fetchone():
            cur.execute("DELETE FROM entries WHERE id = ?", id)
            con.commit()

            self.entry_today(None)  
            self.widgets_dict["entries input"].value = ""

            await self.app.dialog(toga.InfoDialog(self.strings_c["success"], self.strings["remove_entry_success"]))
        else:
            await self.app.dialog(toga.InfoDialog(self.strings_c["error"], self.strings["no_entry_found"]))


    def prepare_notes_container(self):
        self.widgets_dict["notes list container"].position = toga.Position(0,0)