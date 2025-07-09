import toga
from toga.style import Pack
from toga.constants import COLUMN, ROW
import sqlite3 as sql
from imerisios.mylib.tools import get_back_next_buttons, reverse_dict, length_check, get_connection, close_connection, get_ranges, change_range, set_range
from datetime import date
from titlecase import titlecase
from nameparser import HumanName


class Rankings:
    def __init__(self, app, db_path):
        self.app = app
        self.db_path = db_path

        self.strings = self.app.strings["ranking"]
        self.strings_c = self.app.strings["common"]

        self.tab_on = ""
        self.widgets_load_lists = {}

        crt = (["—", self.strings["grade"], self.strings["title"]], [self.strings_c["year"], self.strings["added_date"]])
        self.data = {
            "rankings": {}, 
            "filters": {},
            "categories": ["book", "movie", "series", "music"],
            "criteria": {
                "book": crt[0] + [self.strings["author"]] + crt[1],
                "movie": crt[0] + [self.strings["director"]] + crt[1],
                "series": crt[0] + [self.strings["creator"]] + crt[1],
                "music": crt[0][:2] + [self.strings["artist"]] + crt[1][-1:]
            },
            "grades": ["E", "D", "C", "B", "A", "S"]
        }
        self.widgets_dict = {"entries": {t:{} for t in self.data["categories"]}}

        self.maps = {
            "category_to_person": {"book": "author", "movie": "director", "series": "creator", "music": "artist"},
            "num_to_name": {i + 1: self.data["grades"][i] for i in range(len(self.data["grades"]))},
            "localized_to_system": 
                {self.strings[k]: k for k in ["grade", "title", "added_date"]} | 
                {k: v for k, v in zip(self.strings["categories"], self.data["categories"])}
        }
        self.maps["name_to_num"] = reverse_dict(self.maps["num_to_name"])
        self.maps["localized_to_system"]["year"] = self.strings_c["year"]


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
    

    def get_label(self, txt, padding=(18,18,0)):
        return toga.Label(
            txt, 
            style=Pack(padding=padding, font_size=14, color=self.clrs[2])
        )
    

    def get_list_box(self):
        boxes = []
        for i in range(len(self.data["categories"])):
            t = self.data["categories"][i]
            label = toga.Label(
                self.strings["rankings_labels"][i], 
                style=Pack(flex=0.09, padding=(14,20), text_align="center", font_weight="bold", font_size=18, color=self.clrs[2])
            )
            
            sort_button = toga.Button(
                self.strings["sort_filter_label"], id=f"{t} sort button", 
                on_press=self.app.open_ranking_sort, 
                style=Pack(flex=0.08, padding=4, height=44, font_size=13, color=self.clrs[2], background_color=self.clrs[1])
            )
            sort_box = toga.Box(children=[sort_button], style=Pack(direction=COLUMN))

            back_next_buttons = get_back_next_buttons(id=t, func=lambda button: change_range(button, widgets=self.widgets_dict), color=self.clrs[2], background_color=self.clrs[1])

            self.widgets_dict[f"{t} range"] = toga.Selection(
                id=f"{t} range", 
                on_change=self.load_rankings,
                style=Pack(flex=0.6, padding=4, height=44)
            )
            
            range_box = toga.Box(
                children=[back_next_buttons[0], self.widgets_dict[f"{t} range"], back_next_buttons[1]],
                style=Pack(direction=ROW)
            )
            
            self.widgets_dict[f"{t} box"] = toga.Box(id=f"{t} box", style=Pack(direction=COLUMN))
            self.widgets_dict[f"{t} container"] = toga.ScrollContainer(content=self.widgets_dict[f"{t} box"], horizontal=False, style=Pack(flex=0.75))

            self.widgets_dict[f"{t} no_entries label"] = toga.Label(
                self.strings["no_entries_label"],
                style=Pack(padding=10, font_size=12, color=self.clrs[2])
            )

            chld = [
                label, self.get_div(), 
                sort_box, self.get_div(), 
                range_box, self.get_div(),
                self.widgets_dict[f"{t} container"]
            ]
            box = toga.Box(children=chld, style=Pack(direction=COLUMN, background_color=self.clrs[0]))
            boxes.append(box)

            self.reg(chld + back_next_buttons + [sort_button, box, self.widgets_dict[f"{t} no_entries label"]])

        # return container
        icons = [toga.Icon(f"resources/images/ranking/{t}.png") for t in self.data["categories"]]

        list_container = toga.OptionContainer(content=[toga.OptionItem(self.strings["categories"][i], boxes[i], icon=icons[i]) for i in range(4)])

        return list_container
        
    
    def get_add_edit_entry_box(self):
        # box label
        add_label = toga.Label(
            self.strings["add_entry_label"], 
            style=Pack(padding=14, text_align="center", font_weight="bold", font_size=18, color=self.clrs[2])
        )
        edit_label = toga.Label(
            self.strings["edit_entry_label"], 
            style=Pack(padding=14, text_align="center", font_weight="bold", font_size=18, color=self.clrs[2])
        )
        
        # category box
        category_label = toga.Label(
            f"{self.strings['category']}:", 
            style=Pack(padding=(10,18), font_size=14, color=self.clrs[2])
        )
        self.widgets_dict["category selection"] = toga.Selection(
            items=[t for t in self.strings["categories"]],
            id=f"category selection",
            on_change=self.type_change,
            style=Pack(padding=(3,18,0), height=44, flex=0.66)
        )
        self.widgets_dict["category box"] = toga.Box(
            children=[category_label, self.widgets_dict["category selection"]],
            style=Pack(direction=ROW)
        )

        # entry box
        ## title
        title_label = self.get_label(f"{self.strings['title']}:")
        self.widgets_dict["add_edit title input"] = toga.TextInput(
            style=Pack(padding=(0,18), height=44, font_size=12, color=self.clrs[2], background_color=self.clrs[1])
        )

        self.widgets_dict["add_edit title_person switch"] = toga.Switch(
            text=self.strings["autoformat"],
            id="title_person switch",
            value=True, 
            style=Pack(padding=(8,18,18), font_size=12, color=self.clrs[2])
        )
        
        ## author/director/creator (person)
        for c in self.data["categories"]:
            self.widgets_dict[f"{c}_person label"] = self.get_label(f"{self.strings[self.maps['category_to_person'][c]]}:")
            self.reg([self.widgets_dict[f"{c}_person label"]])
        
        self.widgets_dict["person input"] = toga.TextInput(
            style=Pack(padding=(0,18,18), height=44, font_size=12, color=self.clrs[2], background_color=self.clrs[1])
        )

        ## years
        def start_year_change(widget):
            self.widgets_dict["add_edit end_year input"].min = widget.value  

        self.widgets_dict["start_year label"] = self.get_label(f"{self.strings['start_year']}:")
        self.widgets_dict["add_edit start_year input"] = toga.NumberInput(
            id="add_edit start_year input",
            step=1, 
            min=-2601, max=self.today.year,
            on_change=start_year_change, 
            style=Pack(padding=(0,18), height=44, font_size=12, color=self.clrs[2], background_color=self.clrs[1])
        )
        
        end_year_label = self.get_label(f"{self.strings['end_year']}:", (10,18,0))
        self.widgets_dict["add_edit end_year input"] = toga.NumberInput(
            step=1, max=self.today.year,
            style=Pack(padding=(0,18,18), height=44, font_size=12, color=self.clrs[2], background_color=self.clrs[1])
        )
        
        ## tags
        self.widgets_dict["tags label"] = self.get_label(f"{self.strings['tags']}:")
        self.widgets_dict["add_edit tags input"] = toga.TextInput(
            style=Pack(padding=(0,18,18), height=44, font_size=12, color=self.clrs[2], background_color=self.clrs[1])
        )
        
        ## note
        note_label = self.get_label(f"{self.strings['note']}:")
        
        self.widgets_dict["add_edit note input"] = toga.MultilineTextInput(
            placeholder=self.strings["note_input_placeholder"], 
            style=Pack(padding=(0,18,18), height=200, font_size=12, color=self.clrs[2], background_color=self.clrs[1])
        )

        ## grade
        self.widgets_dict["grade label"] = self.get_label(f"{self.strings['grade']}:")
        
        self.widgets_dict["add_edit grade selection"] = toga.Selection(
            items=[self.maps["num_to_name"][i] for i in range(len(self.maps["num_to_name"]), 0, -1)],
            style=Pack(padding=(0,18), height=44)
        )
        
        self.widgets_dict["add_edit top_box"] = toga.Box(style=Pack(direction=COLUMN, flex=0.8))
        self.widgets_dict["add_edit top_container"] = toga.ScrollContainer(
            content=self.widgets_dict["add_edit top_box"], 
            horizontal=False, 
            style=Pack(flex=0.7)
        )
        
        button = toga.Button(
            self.strings_c["add"], on_press=self.add_save_entry, 
            style=Pack(height=120, padding=11, font_size=18, color=self.clrs[2], background_color=self.clrs[1])
        )
        add_bottom_box = toga.Box(children=[button], style=Pack(direction=COLUMN))

        remove_button = toga.Button(
            self.strings_c["remove"], on_press=self.remove_entry_dialog, 
            style=Pack(flex=0.5, height=120, padding=(11,4,11,11), font_size=18, color=self.clrs[2], background_color=self.clrs[1])
        )
        save_button = toga.Button(
            self.strings_c["save"], on_press=self.save_entry_dialog, 
            style=Pack(flex=0.5, height=120, padding=(11,11,11,4), font_size=18, color=self.clrs[2], background_color=self.clrs[1])
        )
        bottom_chld = [remove_button, save_button]
        edit_bottom_box = toga.Box(children=bottom_chld, style=Pack(direction=ROW))

        # return box
        self.widgets_dict["full_divs"] = full_divs = [self.get_div() for _ in range(4)]
        add_chld = [
            add_label, full_divs[0],
            self.widgets_dict["category box"], full_divs[1],
            self.widgets_dict["add_edit top_container"], full_divs[2],
            add_bottom_box
        ]
        edit_chld = [edit_label] + add_chld[1:-1] + [edit_bottom_box]
        self.widgets_load_lists["add box"] = add_chld
        self.widgets_load_lists["edit box"] = edit_chld

        self.widgets_load_lists["add_edit top_boxes"] = {}
        for t in self.data["categories"]:
            l = []
            if t != "music":
                l.extend([title_label, self.widgets_dict["add_edit title input"], self.widgets_dict["add_edit title_person switch"], "partial div"])
            l.extend([self.widgets_dict[f"{t}_person label"], self.widgets_dict["person input"]])
            if t == "music":
                l.append(self.widgets_dict["add_edit title_person switch"])
            l.append("partial div")
            if t != "music":
                l.extend([
                    self.widgets_dict["start_year label"], self.widgets_dict["add_edit start_year input"], 
                    end_year_label, self.widgets_dict["add_edit end_year input"], "partial div"
                ])
            l.extend([
                self.widgets_dict["tags label"], self.widgets_dict["add_edit tags input"], "partial div",
                note_label, self.widgets_dict["add_edit note input"], "partial div",
                self.widgets_dict["grade label"], self.widgets_dict["add_edit grade selection"]
            ])

            self.widgets_load_lists["add_edit top_boxes"][t] = l

            self.reg(l)
        
        self.widgets_dict["add_edit box"] = box = toga.Box(style=Pack(direction=COLUMN, background_color=self.clrs[0]))

        self.reg(add_chld + edit_chld + bottom_chld + [
            self.widgets_dict["start_year label"], self.widgets_dict["add_edit start_year input"],
            end_year_label, self.widgets_dict["add_edit end_year input"], 
            button, category_label, box
        ])

        return box
    

    def get_sort_box(self):
        self.data["sorting"] = {t: [("—", "↑") for _ in range(3)] for t in self.data["categories"]}

        self.data["filtering"] = {
            t: {"grade": ("E", "S"), "person": "", "tags_include": "", "tags_exclude": "", "start_year": ("", ""), "added_date": (date(year=2024, month=7, day=25), self.today)}
            for t in self.data["categories"]
        }
        del self.data["filtering"]["music"]["person"]
        del self.data["filtering"]["music"]["start_year"]

        self.data["load sorting"] = {t: [] for t in self.data["categories"]}
        self.data["load filtering"] = {t: [] for t in self.data["categories"]}
        
        # category box
        category_box = self.widgets_dict["category box"]
        
        # sort
        ## label
        sort_label = toga.Label(
            self.strings["sort"], 
            style=Pack(padding=14, text_align="center", font_weight="bold", font_size=18, color=self.clrs[2])
        )
        
        ## number+criterion+order boxes
        labels = [
            toga.Label(f"{i}.", style=Pack(padding=18, font_size=14, color=self.clrs[2])) 
            for i in range(1,4)
        ]
        self.widgets_dict["sort criterion selections"] = [
            toga.Selection(
                id=f"sort criterion selection {i}",
                on_change=self.criterion_change,
                style=Pack(flex=0.8, padding=(8,18,8,2), height=44)
            )
            for i in range(1,4)
        ]
        self.widgets_dict["sort order selections"] = [
            toga.Selection(items=["↑", "↓"], id=f"sort order selection {i}", style=Pack(flex=0.15, padding=(8,18,8,8), height=44))
            for i in range(1,4)
        ]
        
        sort_boxes = []
        for i in range(3):
            chld = [labels[i], self.widgets_dict["sort criterion selections"][i], self.widgets_dict["sort order selections"][i]]
            sort_boxes.append(toga.Box(children=chld,style=Pack(direction=ROW)))

            self.reg([labels[i]])

        ## reset button
        sort_reset_button = toga.Button(
            self.strings_c["reset"], on_press=self.reset_sort, 
            style=Pack(padding=4, height=44, font_size=13, color=self.clrs[2], background_color=self.clrs[1])
        )
        
        ## sort box
        sort_chld = [
            sort_label, self.get_div(), 
            sort_boxes[0], self.get_div((0,80)),
            sort_boxes[1], self.get_div((0,80)), 
            sort_boxes[2], self.get_div((0,80)),
            sort_reset_button, self.get_div()
        ]
        sort_box = toga.Box(children=sort_chld, style=Pack(direction=COLUMN))
        
        # filter box
        ## label
        filter_label = toga.Label(
            self.strings["filter"], 
            style=Pack(padding=14, text_align="center", font_weight="bold", font_size=18, color=self.clrs[2])
        )
        
        ## grade
        grade_label = self.widgets_dict["grade label"]
        
        items = [self.maps["num_to_name"][i] for i in range(1, len(self.maps["num_to_name"]) + 1)]
        self.widgets_dict["sort grade selections"] = [toga.Selection(items=items,style=Pack(flex=0.5, padding=(0,18,18), height=44)) for _ in range(2)]

        grade_box = toga.Box(children=self.widgets_dict["sort grade selections"], style=Pack(direction=ROW))

        def adjust_grade(widget):
            w = self.widgets_dict["sort grade selections"][1]
            val = w.value

            idx = self.data["grades"].index(widget.value)
            items = self.data["grades"][idx:]
            w.items = items
            if w.value != val and val in items:
                w.value = val
            
        self.widgets_dict["sort grade selections"][0].on_change = adjust_grade

        ## author/director/creator/artist (person)
        person_input = self.widgets_dict["person input"]

        ## tags
        tags_label = self.widgets_dict["tags label"]
        
        self.widgets_dict["sort tags_include input"] = toga.TextInput(
            placeholder=self.strings["include_tags_placeholder"],
            style=Pack(padding=(0,18,0), height=44, font_size=12, color=self.clrs[2], background_color=self.clrs[1])
        )

        self.widgets_dict["sort tags_exclude input"] = toga.TextInput(
            placeholder=self.strings["exclude_tags_placeholder"],
            style=Pack(padding=(0,18,18), height=44, font_size=12, color=self.clrs[2], background_color=self.clrs[1])
        )

        ## start year between
        start_year_label = self.widgets_dict["start_year label"]
        self.widgets_dict["sort start_year inputs"] = [
            toga.NumberInput(
                step=1, 
                min=-2601, max=self.today.year,
                style=Pack(flex=0.5, padding=(0,18,18), height=44, font_size=12, color=self.clrs[2], background_color=self.clrs[1])
            )
            for _ in range(2)]
        
        def adjust_year(widget):
            self.widgets_dict["sort start_year inputs"][1].min = widget.value

        self.widgets_dict["sort start_year inputs"][0].on_change = adjust_year

        start_year_box = toga.Box(children=self.widgets_dict["sort start_year inputs"], style=Pack(direction=ROW))
        
        ## added date between
        added_date_label = self.get_label(f"{self.strings['added_date']}:")

        self.widgets_dict["sort added_date dates"] = [
            toga.DateInput(max=self.today, style=Pack(flex=0.5, padding=(0,18,18), width=160, color=self.clrs[2]))
            for _ in range(2)
        ]
        added_date_boxes = [
            toga.Box(children=[self.widgets_dict["sort added_date dates"][i]], style=Pack(direction=COLUMN, flex=0.5))
            for i in range(2)
        ]

        def adjust_date(widget):
            w = self.widgets_dict["sort added_date dates"][1]
            if widget.value > w.value:
                w.value = widget.value

        self.widgets_dict["sort added_date dates"][0].on_change = adjust_date

        added_date_box  = toga.Box(children=added_date_boxes, style=Pack(direction=ROW))

        ## filter reset button
        reset_button = toga.Button(
            self.strings_c["reset"], on_press=self.reset_filter, 
            style=Pack(padding=4, height=44, font_size=13, color=self.clrs[2], background_color=self.clrs[1])
        )

        ## filter box
        self.widgets_dict["filter box"] = toga.Box(style=Pack(direction=COLUMN))

        ## filter load lists
        self.widgets_load_lists["filter box"] = {}
        for t in self.data["categories"]:
            l = [
                filter_label, self.widgets_dict["full_divs"][0], 
                grade_label, grade_box, "partial div",
            ]
            if t != "music":
                l.extend([self.widgets_dict[f"{t}_person label"], person_input, "partial div"])
            l.extend([tags_label, self.widgets_dict["sort tags_include input"], self.widgets_dict["sort tags_exclude input"], "partial div"])
            if t != "music":
                l.extend([start_year_label, start_year_box, "partial div"])
            l.extend([added_date_label, added_date_box, "partial div", reset_button])

            self.widgets_load_lists["filter box"][t] = l

            self.reg(l)

        # sort & filter button
        button = toga.Button(
            self.strings_c["apply"], id="sort button", 
            on_press=self.check_sort_inputs, 
            style=Pack(height=120, padding=11, font_size=18, color=self.clrs[2], background_color=self.clrs[1])
        )
        
        # return box
        sort_filter_box = toga.Box(
            children=[
                sort_box, self.widgets_dict["full_divs"][1],
                self.widgets_dict["filter box"]
            ],
            style=Pack(direction=COLUMN)
        )
        self.widgets_dict["sort container"] = toga.ScrollContainer(content=sort_filter_box, horizontal=False, style=Pack(flex=0.8))

        chld = [
            category_box, self.widgets_dict["full_divs"][2],
            self.widgets_dict["sort container"], self.widgets_dict["full_divs"][3],
            button
        ]
        self.widgets_load_lists["sort box"] = chld
        self.widgets_dict["sort box"] = toga.Box(
            children=chld, 
            style=Pack(direction=COLUMN, background_color=self.clrs[0])
        )
        
        self.reg(
            sort_chld + self.widgets_dict["sort start_year inputs"] + self.widgets_dict["sort added_date dates"] + 
            [sort_label, added_date_label, button, self.widgets_dict["sort box"]]
        )

        return self.widgets_dict["sort box"]


    def get_search_box(self):
        # label
        label = toga.Label(
            self.strings["search_label"], 
            style=Pack(padding=(14,20), text_align="center", font_weight="bold", font_size=18, color=self.clrs[2])
        )
        
        # type
        self.widgets_dict["search category box"] = toga.Box(children=[self.widgets_dict["category box"]], style=Pack(direction=COLUMN))

        # search
        self.widgets_dict["search input"] = toga.TextInput(
            style=Pack(padding=(4,4,0), height=44, font_size=12, color=self.clrs[2], background_color=self.clrs[1])
        )
        search_button = toga.Button(
            self.strings["search"], id="search button",
            on_press=self.load_rankings, 
            style=Pack(padding=4, height=44, font_size=13, color=self.clrs[2], background_color=self.clrs[1])
        )
        search_chld = [self.widgets_dict["search input"], search_button]
        search_box = toga.Box(children=search_chld, style=Pack(direction=COLUMN))
        
        self.widgets_dict["search no_entries label"] = toga.Label(
            self.strings["no_entries_found"],
            style=Pack(padding=10, font_size=12, color=self.clrs[2])
        )
        
        # result box
        self.widgets_dict["search result box"] = toga.Box(style=Pack(direction=COLUMN))
        result_container = toga.ScrollContainer(content=self.widgets_dict["search result box"], horizontal=False, style=Pack(flex=0.75))

        # return box
        chld = [
            label, self.get_div(),
            self.widgets_dict["search category box"], self.get_div(),
            search_box, self.get_div(),
            result_container
        ]
        box = toga.Box(
            children=chld, 
            style=Pack(direction=COLUMN, background_color=self.clrs[0])
        )
        
        self.reg(chld + search_chld + [box])

        return box
    

    def setup_rankings(self):
        list_box = self.get_list_box()
        add_edit_box = self.get_add_edit_entry_box()
        sort_box = self.get_sort_box()
        search_box = self.get_search_box()

        self.setup_db_script = """
            CREATE TABLE IF NOT EXISTS book_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                added_date DATE DEFAULT (date('now', 'localtime')),
                title TEXT NOT NULL,
                author TEXT,
                start_year INTEGER,
                end_year INTEGER,
                tags TEXT,
                grade INTEGER NOT NULL,
                note TEXT
            );
                          
            CREATE TABLE IF NOT EXISTS movie_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                added_date DATE DEFAULT (date('now', 'localtime')),
                title TEXT NOT NULL,
                director TEXT,
                start_year INTEGER,
                end_year INTEGER,
                tags TEXT,
                grade INTEGER NOT NULL,
                note TEXT
            );

            CREATE TABLE IF NOT EXISTS series_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                added_date DATE DEFAULT (date('now', 'localtime')),
                title TEXT NOT NULL,
                creator TEXT,
                start_year INTEGER,
                end_year INTEGER,
                tags TEXT,
                grade INTEGER NOT NULL,  
                note TEXT       
            );

            CREATE TABLE IF NOT EXISTS music_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                added_date DATE DEFAULT (date('now', 'localtime')),
                artist TEXT NOT NULL,
                tags TEXT,
                grade INTEGER NOT NULL,
                note TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_book_added_date ON book_entries (added_date);
            CREATE INDEX IF NOT EXISTS idx_book_title ON book_entries (title);
            CREATE INDEX IF NOT EXISTS idx_book_author ON book_entries (author);
            CREATE INDEX IF NOT EXISTS idx_book_start_year ON book_entries (start_year);
            CREATE INDEX IF NOT EXISTS idx_book_end_year ON book_entries (end_year);
            CREATE INDEX IF NOT EXISTS idx_book_tags ON book_entries (tags);
            CREATE INDEX IF NOT EXISTS idx_book_grade ON book_entries (grade);

            CREATE INDEX IF NOT EXISTS idx_movie_added_date ON movie_entries (added_date);
            CREATE INDEX IF NOT EXISTS idx_movie_title ON movie_entries (title);
            CREATE INDEX IF NOT EXISTS idx_movie_director ON movie_entries (director);
            CREATE INDEX IF NOT EXISTS idx_movie_start_year ON movie_entries (start_year);
            CREATE INDEX IF NOT EXISTS idx_movie_end_year ON movie_entries (end_year);
            CREATE INDEX IF NOT EXISTS idx_movie_tags ON movie_entries (tags);
            CREATE INDEX IF NOT EXISTS idx_movie_grade ON movie_entries (grade);

            CREATE INDEX IF NOT EXISTS idx_series_added_date ON series_entries (added_date);
            CREATE INDEX IF NOT EXISTS idx_series_title ON series_entries (title);
            CREATE INDEX IF NOT EXISTS idx_series_creator ON series_entries (creator);
            CREATE INDEX IF NOT EXISTS idx_series_start_year ON series_entries (start_year);
            CREATE INDEX IF NOT EXISTS idx_series_end_year ON series_entries (end_year);
            CREATE INDEX IF NOT EXISTS idx_series_tags ON series_entries (tags);
            CREATE INDEX IF NOT EXISTS idx_series_grade ON series_entries (grade);
          
            CREATE INDEX IF NOT EXISTS idx_music_added_date ON music_entries (added_date);
            CREATE INDEX IF NOT EXISTS idx_music_artist ON music_entries (artist);
            CREATE INDEX IF NOT EXISTS idx_music_tags ON music_entries (tags);
            CREATE INDEX IF NOT EXISTS idx_music_grade ON music_entries (grade);
        """

        con, cur = get_connection(self.db_path)
        cur.executescript(self.setup_db_script)
        con.commit()

        self.update_rankings(load=True, con_cur=(con, cur))
        con.close()

        return list_box, sort_box, add_edit_box, search_box


    def update_rankings(self, load=False, con_cur=None):
        self.widgets_dict["sort added_date dates"][1].max = self.today
        if load:
            self.load_rankings(None, con_cur=con_cur)
        

    def ranking_get_data(self, rankings={}, search=None, con_cur=None):
        con, cur = get_connection(self.db_path, con_cur)

        # rankings
        for t in rankings:
            sort, filters = rankings[t]

            ## sorting criteria
            sort_criteria = []
            for c_o in sort:
                criterion, order = c_o
                string = f"{criterion} {order}" if criterion not in self.maps["category_to_person"].values() and criterion != "title" else f"LOWER({criterion}) {order}"
                sort_criteria.append(string)
            sorting = "ORDER BY " + (", ".join(sort_criteria + ["RANDOM()"]) if sort_criteria else "RANDOM()")

            ## filter criterion
            filter_criteria = []
            filter_values = []
            
            for c_v in filters:
                criterion, value = c_v
                if criterion == "grade":
                    from_grade, to_grade = value
                    filter_criteria.append("grade >= ? AND grade <= ?")
                    filter_values.append(from_grade)
                    filter_values.append(to_grade)
                elif criterion == self.maps["category_to_person"][t]:
                    for person in value:
                        filter_criteria.append(f"LOWER({person}) LIKE LOWER(?)")
                        filter_values.append(f"%{value}%")
                elif criterion == "tags_include":
                    for tag in value:
                        filter_criteria.append("LOWER(tags) LIKE LOWER(?)")
                        filter_values.append(f"%{tag}%")
                elif criterion == "tags_exclude":
                    for tag in value:
                        filter_criteria.append("LOWER(tags) NOT LIKE LOWER(?)")
                        filter_values.append(f"%{tag}%")
                elif criterion == "start_year":
                    from_year, to_year = value
                    filter_criteria.append("start_year >= ? AND start_year <= ?")
                    filter_values.append(from_year)
                    filter_values.append(to_year)
                elif criterion == "added_date":
                    from_date, to_date = value
                    filter_criteria.append("added_date >= ? AND added_date <= ?")
                    filter_values.append(from_date)
                    filter_values.append(to_date)

            filtering = "WHERE " + " AND ".join(filter_criteria) if filter_criteria else ""

            ## query
            query = f"PRAGMA table_info({t}_entries);"
            cur.execute(query)
            columns = [row[1] for row in cur.fetchall()]  
            columns = [col for col in columns if col != 'note']

            query = f"""
                SELECT {', '.join(columns)} FROM {t}_entries
                {filtering}
                {sorting};
            """
            cur.execute(query, filter_values)
            self.data["rankings"][t] = cur.fetchall()

        # search
        if search:
            t, s = search

            # base query string
            query = f"""
                SELECT * FROM {t}_entries
                WHERE id = CAST(? AS INTEGER)
                OR LOWER({self.maps["category_to_person"][t]}) LIKE LOWER(?)
            """
            
            # add title search if needed and execute
            if t != "music":
                query += " OR LOWER(title) LIKE LOWER(?)"
                query += " ORDER BY LOWER(title) ASC;"
                cur.execute(query, (s, f"%{s}%", f"%{s}%",))
            else:
                query += " ORDER BY LOWER(artist) ASC;"
                cur.execute(query, (s, f"%{s}%",))

            self.data["search"] = cur.fetchall()

        close_connection(con, con_cur)  
    

    def load_rankings(self, widget, con_cur=None):
        # setup 
        if not widget:
            self.ranking_get_data({t:([],[]) for t in self.data["categories"]}, con_cur=con_cur)

            for t in self.data["categories"]:
                data = self.data["rankings"][t]
                items = get_ranges(data)
                set_range(self.widgets_dict[f"{t} range"], items)

        else:  
            widget_id = widget.id.split()

            if widget_id[-1] == "range":
                t = widget_id[0]
                data = self.data["rankings"][t]
                box = self.widgets_dict[f"{t} box"]
                box.clear()

                start, end = [int(i) for i in widget.value.split('–')]
                if start == 0 and end == 0:
                    box.add(self.widgets_dict[f"{t} no_entries label"])
                else:
                    for i in range(start-1, end):
                        e = data[i]
                        id = e[0]
                        if id not in self.widgets_dict["entries"][t]:
                            entry_box = self.get_entry_box(t, e)
                            self.widgets_dict["entries"][t][id] = entry_box
                        box.add(self.widgets_dict["entries"][t][id])

                self.widgets_dict[f"{t} container"].position = toga.Position(0,0)

            elif widget_id[0] == "sort":
                t = self.data["load type"]
                self.ranking_get_data({t:(self.data["load sorting"][t], self.data["load filtering"][t])})
                items = get_ranges(self.data["rankings"][t])
                self.widgets_dict[f"{t} range"].items = items

            elif widget_id[0] == "search":
                if input := self.widgets_dict["search input"].value.strip():
                    t = self.maps["localized_to_system"][self.widgets_dict["category selection"].value]

                    self.ranking_get_data(search=(t, input))
                    box = self.widgets_dict["search result box"]
                    box.clear()

                    if data := self.data["search"]:
                        for e in data:
                            box.add(self.get_entry_box(t, e, True))
                    else:
                        box.add(self.widgets_dict["search no_entries label"])


    def type_change(self, widget):
        t = self.maps["localized_to_system"][widget.value]
        tab = self.tab_on
        if tab == "sort":
            self.widgets_dict["sort criterion selections"][0].items = self.data["criteria"][t]
            for i in range(3):
                self.widgets_dict["sort criterion selections"][i].value = self.data["sorting"][t][i][0]
                self.widgets_dict["sort order selections"][i].value = self.data["sorting"][t][i][1]
            box = self.widgets_dict["filter box"]
            box.clear()
            for w in self.widgets_load_lists["filter box"][t]:
                w = self.check_widget(w)
                box.add(w)
            data = self.data["filtering"][t]
            for c in data:
                w_id = f"sort {c}" if c != "person" else c
                if c not in ("grade", "start_year", "added_date"):
                    self.widgets_dict[w_id + " input"].value = data[c]
                else: 
                    w_id += " " + {"grade": "selections", "start_year": "inputs", "added_date": "dates"}[c]
                    self.widgets_dict[w_id][0].value, self.widgets_dict[w_id][1].value = data[c]

        elif tab == "search":
            self.widgets_dict["search input"].value = ""
            self.widgets_dict["search result box"].clear()
            self.widgets_dict["search input"].placeholder = self.strings[f"search_{t}_placeholder"]

        else:    
            box = self.widgets_dict["add_edit top_box"]
            box.clear()
            for w in self.widgets_load_lists["add_edit top_boxes"][t]:
                w = self.check_widget(w)
                box.add(w)
            if t == "music":
                padd = 0
            else:
                padd = 18
            self.widgets_dict["person input"].style.padding_bottom = padd
            
        self.type_change_check = False

    async def remove_entry_dialog(self, widget):
        result = await self.app.dialog(toga.QuestionDialog(self.strings_c["confirmation"], "Are you sure you want to remove the entry?"))
        if result:
            await self.remove_entry()


    async def remove_entry(self):
        category = self.widgets_dict["category selection"].value
        t = self.maps["localized_to_system"][category]
        id = self.temp_edit_id
        query = f"""
            DELETE FROM {t}_entries
            WHERE id = ?;         
        """

        con, cur = get_connection(self.db_path)

        cur.execute(query, (id,))
        con.commit()

        self.ranking_get_data(rankings={t: (self.data["load sorting"][t], self.data["load filtering"][t])}, con_cur=(con, cur))

        con.close()

        for w in (id, f"{id} edit_button"):
            if w in self.widgets_dict["entries"][t]:
                del self.widgets_dict["entries"][t][w]


        items = get_ranges(self.data["rankings"][t])
        set_range(self.widgets_dict[f"{t} range"], items)

        self.app.open_ranking(widget=None, tab=category)
        

    async def save_entry_dialog(self, widget):
        result = await self.app.dialog(toga.QuestionDialog(self.strings_c["confirmation"], self.strings["save_entry_question"]))
        if result:
            await self.add_save_entry(widget, id=self.temp_edit_id)


    def criterion_change(self, widget): 
        value = widget.value
        items = widget.items
        n = int(widget.id.split()[-1])
        s_c = self.widgets_dict["sort criterion selections"]
        s_o = self.widgets_dict["sort order selections"]
        if value == "—":
            if n != 3:
                s_c[n].items = [c.value for c in items]
                s_c[n].enabled = False
                s_o[n].value = "↑"
                s_o[n].enabled = False
        else:
            if n != 3:
                s_c[n].items = [c.value for c in items if c.value != value]
                s_c[n].enabled = True
                s_o[n].enabled = True
                

    def reset_sort(self, widget):
        self.widgets_dict["sort criterion selections"][0].value = "—"
        self.widgets_dict["sort order selections"][0].value = "↑"


    def reset_filter(self, widget):
        self.widgets_dict["sort grade selections"][0].value, self.widgets_dict["sort grade selections"][1].value = "E", "S"
        self.widgets_dict["sort tags_include input"].value = ""
        self.widgets_dict["sort tags_exclude input"].value = ""
        self.widgets_dict["sort added_date dates"][0].value, self.widgets_dict["sort added_date dates"][1].value = date(2024, 7, 25), self.today
        self.widgets_dict["person input"].value = ""
        self.widgets_dict["sort start_year inputs"][0].value, self.widgets_dict["sort start_year inputs"][1].value = "", ""


    def format_title(self, title, max_length=52):
        if len(title) > max_length:
            words = title.split()
            result = ""
            
            for word in words:
                if len(result) + len(word) <= max_length:
                    result += word + " "
                else:
                    result = result.rstrip() + "..."
                    break

            return result
        
        else:
            return title

    def format_items(self, items, first_max_length=42, second_max_length=None):
        def fit_text(text, max_length):
            """Helper to fit text within max_length, breaking at word/item boundaries."""
            if len(text) <= max_length:
                return text
            
            # Try to break at ", " (item boundary)
            last_comma = text.rfind(", ", 0, max_length)
            if last_comma > 0:
                return text[:last_comma]
            
            # Fall back to word boundary
            last_space = text.rfind(" ", 0, max_length)
            if last_space > 0:
                return text[:last_space]
            
            # Last resort: hard cut
            return text[:max_length-1]

        if not items:
            return "—\n" if second_max_length else "—"
        
        if len(items) <= first_max_length:
            return items + ("\n" if second_max_length else "")
        
        # Find the best split point for first row
        first_row = fit_text(items, first_max_length)
        
        if not second_max_length:
            return first_row + ", ..."
        
        # Extract remaining items for second row
        remaining = items[len(first_row):].lstrip(", ")
        second_row = fit_text(remaining, second_max_length)
        
        # Add ellipsis if there's more content
        if len(remaining) > len(second_row):
            second_row += ", ..." if second_row else "..."
        
        return first_row + "\n" + second_row


    def get_entry_box(self, category, entry, edit_button=False):
        id = entry[0]
        added_date = entry[1]
        tags_idx = 3 if category == "music" else 6
        grade_idx = 4 if category == "music" else 7
        grade = self.maps["num_to_name"][entry[grade_idx]]

        tags = self.format_items(entry[tags_idx], first_max_length=46, second_max_length=52)
        middle_txt = f"{self.strings_c['added']}: {added_date}\n{self.strings['tags']}: {tags}"
        not_music_middle = None
        if category != "music":
            main = self.format_title(entry[2])
            person = self.format_items(entry[3], first_max_length=42) if entry[3] else "—"
            if entry[4]:
                if entry[4] == entry[5]:
                    year = entry[4]
                else:
                    year = f"{entry[4]}–{entry[5]}"
            else:
                year = "—"
            not_music_middle = f"{self.strings[self.maps['category_to_person'][category]]}: {person}\n{self.strings_c['year']}: {year}  |  "      
        else:
            main = entry[2]
            
        if not_music_middle:
            middle_txt = not_music_middle + middle_txt

        id_label = toga.Label(
            f"[{id:06d}]", 
            style=Pack(padding=4, font_size=11, color=self.clrs[2])
        )
        main_label = toga.Label(
            main, 
            style=Pack(padding=4, font_size=11, font_weight="bold", color=self.clrs[2])
        )
        middle_label = toga.Label(
            middle_txt, 
            style=Pack(padding=4, font_size=11, color=self.clrs[2])
        )
        grade_label = toga.Label(
            f"{self.strings['grade']}: {grade}", 
            style=Pack(padding=4, font_size=11, color=self.clrs[2])
        )

        children = [id_label, main_label, middle_label, grade_label]
        if edit_button:
            if (button_id := f"{id} edit_button") not in self.widgets_dict["entries"][category]:
                self.widgets_dict["entries"][category][button_id] = toga.Button(
                    self.strings["edit_button_label"], id=button_id, on_press=self.app.open_ranking_edit_entry, 
                    style=Pack(padding=4, height=42, font_size=12, color=self.clrs[2], background_color=self.clrs[1])
                )
                self.reg([self.widgets_dict["entries"][category][button_id]])
            children.append(self.widgets_dict["entries"][category][button_id])
        children.append(self.get_div())

        entry_box = toga.Box(children=children, style=Pack(direction=COLUMN))
        
        self.reg(children)

        return entry_box
    

    async def check_sort_inputs(self, widget):
        category = self.widgets_dict["category selection"].value
        t = self.maps["localized_to_system"][category]

        # filter 
        filtering = []       
        grades = [self.maps["name_to_num"][self.widgets_dict["sort grade selections"][i].value] for i in range(2)]
        filtering.append(("grade", grades))
        
        tags = [self.widgets_dict[f"sort tags_{s}clude input"].value.strip() for s in ("in", "ex")]
        tags_include, tags_exclude = tags
        temp_include, temp_exclude = [set(tag.strip().lower() for tag in t.split(",") if tag.strip()) for t in tags]
        
        if tags_include and tags_exclude:
            if temp_include & temp_exclude:
                await self.app.dialog(toga.InfoDialog(self.strings_c["error"], self.strings["tag_overlap_error"]))
                return 0
            else:
                filtering.append(("tags_include", temp_include))
                filtering.append(("tags_exclude", temp_exclude))
        elif tags_include:
            filtering.append(("tags_include", temp_include))
        elif tags_exclude:
            filtering.append(("tags_exclude", temp_exclude))

        dates = [w.value for w in self.widgets_dict["sort added_date dates"]]
        if dates[0] > dates[1]:
            await self.app.dialog(toga.InfoDialog(self.strings_c["error"], self.strings["sort_date_error"]))
            return 0
        filtering.append(("added_date", dates))

        if t != "music":
            if (person := self.widgets_dict["person input"].value):
                filtering.append((self.maps["category_to_person"][t], set(p.strip().lower() for p in person.split(",") if p.strip())))
            
            start_year, end_year = [int(w.value) if w.value else None for w in self.widgets_dict["sort start_year inputs"]]
            years = [-2601, self.today.year]
            if start_year:
                years[0] = start_year
            if end_year:
                years[1] = end_year
            filtering.append(("start_year", years))
            
            self.data["filtering"][t]["person"] = person
            self.data["filtering"][t]["start_year"] = (start_year, end_year)

        self.data["filtering"][t]["tags_include"] = tags_include
        self.data["filtering"][t]["tags_exclude"] = tags_exclude
        self.data["filtering"][t]["grade"] = [self.maps["num_to_name"][grades[i]] for i in range(2)]
        self.data["filtering"][t]["added_date"] = [self.widgets_dict["sort added_date dates"][i].value for i in range(2)]

        self.data["load filtering"][t] = filtering

        # sort
        sort = [(self.widgets_dict["sort criterion selections"][i].value, self.widgets_dict["sort order selections"][i].value) for i in range(3)]
        self.data["sorting"][t] = sort
        sorting = []
        for i in sort:
            if i[0] != "—":
                c = self.maps["localized_to_system"][i[0]].replace("year", "start_year")
                o = "ASC" if i[1] == "↑" else "DESC"
                sorting.append((c, o))

        self.data["load sorting"][t] = sorting

        # type
        self.data["load type"] = t

        self.load_rankings(widget)

        self.app.open_ranking(widget=None, tab=self.strings[t])

    
    def load_edit_box(self, widget):
        id = int(widget.id.split()[0])
        self.temp_edit_id = id
        t = self.maps["localized_to_system"][self.widgets_dict["category selection"].value]

        values = f"{self.maps['category_to_person'][t]}, tags, grade, note"
        widgets = ["person", "tags", "grade", "note"]
        if t != "music":
            values += ", title, start_year, end_year"
            widgets.extend(["title", "start_year", "end_year"])

        query = f"""
            SELECT {values} FROM {t}_entries
            WHERE id = ?
        """
        con, cur = get_connection(self.db_path)
        cur.execute(query, (id,))
        entry = cur.fetchone()

        con.close()

        for i in range(len(widgets)):
            id = widgets[i]
            id += " input" if widgets[i] != "grade" else " selection"
            id = "add_edit " + id if widgets[i] != "person" else id
            self.widgets_dict[id].value = entry[i] if i != 2 else self.maps["num_to_name"][entry[i]]

        self.widgets_dict["add_edit title_person switch"].value = False


    def clear_add_box(self, widget=None):
        for w in ["title", "person", "tags", "start_year", "end_year", "grade", "note", "title_person switch"]:
            if w == "grade":
                self.widgets_dict[f"add_edit {w} selection"].value = "S"
            elif w == "title_person switch":
                self.widgets_dict[f"add_edit {w}"].value = True
            else:
                id = f"{w} input"
                id = "add_edit " + id if w != "person" else id
                self.widgets_dict[id].value = ""


    async def reset_ranking_dialog(self):
        result = await self.app.dialog(toga.QuestionDialog(self.strings_c["confirmation"], self.strings["reset_db_question"]))
        if result:
            await self.reset_ranking()


    async def reset_ranking(self):
        con, cur = get_connection(self.db_path)
        
        for t in self.maps["category_to_person"]:
            query = f"DROP TABLE {t}_entries;"
            cur.execute(query)
            con.commit()

        cur.executescript(self.setup_db_script)
        con.commit()
        con.close()

        self.app.setup_ui(rankings=True)

        await self.app.dialog(toga.InfoDialog(self.strings_c["success"], self.strings["reset_db_success"]))

    
    def get_tags(self, value):
        values = value.split(",")
        added = set()
        tags = list()

        for tag in values:
            t = tag.strip()
            if t:
                if t.lower() not in added:
                    added.add(t.lower())
                    tags.append(t)

        tags = titlecase(", ".join(sorted(tags, key=lambda tag: tag.lower())))
        
        return tags


    async def replace_entries_tag_dialog(self, category, old, new):
        result = await self.app.dialog(toga.QuestionDialog(self.strings_c["confirmation"], self.strings["replace_tag_question"]))
        if result:
            await self.replace_entries_tag(category, old, new)


    async def replace_entries_tag(self, category, old, new):
        category = self.maps["localized_to_system"][category]

        query = f"""
            SELECT id, tags FROM {category}_entries
            WHERE LOWER(tags) LIKE LOWER(?);
        """

        con, cur = get_connection(self.db_path)
        cur.execute(query, (f"%{old}%",))

        entries = cur.fetchall()
        if entries:
            new_entries = []
            for e in entries:
                id = e[0]
                old_tags = e[1].split(", ")

                new_tags = [tag for tag in old_tags if tag.lower() != old.lower()]
                if new and new not in new_tags:
                    new_tags = sorted(new_tags + [new,])
                new_tags = ", ".join(new_tags)

                new_entries.append((id, new_tags))
            
            query_start = f"UPDATE {category}_entries"
            for id, tags in new_entries:
                cur.execute(query_start + " SET tags = ? WHERE id = ?", (tags, id,))
            con.commit()

            if len(new_entries) == 1:
                txt = self.strings["replace_tag_success"][0]
            else:
                txt = self.strings["replace_tag_success"][1].format(count=len(new_entries))
            await self.app.dialog(toga.InfoDialog(self.strings_c["success"], txt))

            self.app.setup_rankings = True

        else:
            await self.app.dialog(toga.InfoDialog(self.strings_c["error"], self.strings["replace_tag_no_entries"]))
        
        con.close()

    
    def set_tab_on(self, tab, widget=None, category=None):
        if tab == "add":
            self.clear_add_box()

        if self.tab_on != tab:
            self.tab_on = tab
            selection = self.widgets_dict["category selection"]
            if tab == "add" or tab == "edit":
                box = self.widgets_dict["add_edit box"]
                box.clear()
                for w in self.widgets_load_lists[f"{tab} box"]:
                    w = self.check_widget(w)
                    box.add(w)
                    
                if tab == "edit":
                    self.load_edit_box(widget)
                
            elif tab == "search":
                box = self.widgets_dict["search category box"]
                box.clear()
                box.add(self.widgets_dict["category box"])
            elif tab == "sort":
                self.widgets_dict["person input"].style.padding_bottom = 18
                box = self.widgets_dict["sort box"]
                box.clear()
                for w in self.widgets_load_lists["sort box"]:
                    w = self.check_widget(w)
                    box.add(w)

            selection.enabled = True if tab in ["add", "search"] else False
            if category:
                self.type_change_check = True
                selection.value = category

            if not category or self.type_change_check:
                self.type_change(selection)


    def get_add_edit_values(self):
        return {
            "category": self.widgets_dict["category selection"].value,
            "title": self.widgets_dict["add_edit title input"].value,
            "person": self.widgets_dict["person input"].value,
            "autoformat": self.widgets_dict["add_edit title_person switch"].value,
            "start_year": self.widgets_dict["add_edit start_year input"].value,
            "end_year": self.widgets_dict["add_edit end_year input"].value,
            "tags": self.widgets_dict["add_edit tags input"].value,
            "grade": self.widgets_dict["add_edit grade selection"].value,
            "note": self.widgets_dict["add_edit note input"].value
        }
    

    async def add_save_entry(self, widget, id=None):
        values = self.get_add_edit_values()

        t = self.maps["localized_to_system"][values["category"]]
        if t != "music":
            start_year, end_year = values["start_year"], values["end_year"]
            if not start_year and end_year:
                await self.app.dialog(toga.InfoDialog(self.strings_c["error"], self.strings["no_start_year_error"]))
                return 0
            
            elif start_year and not end_year:
                end_year = start_year

            title = values["title"].strip()
            if not title:
                await self.app.dialog(toga.InfoDialog(self.strings_c["error"], self.strings["no_title_error"]))
                return 0
            title = titlecase(title) if values["autoformat"] else title

        person = values["person"].strip()
        if t == "music":   
            if not person:
                await self.app.dialog(toga.InfoDialog(self.strings_c["error"], self.strings["no_artist_error"]))
                return 0
            if values["autoformat"]:
                person = titlecase(person)

        else:
            person = [p.strip() for p in person.split(",") if p.strip()] if person else None
            if person:
                for i in range(len(person)):
                    person[i] = HumanName(person[i])
                    person[i].capitalize(force=True)
                    person[i] = str(person[i])

                person = ", ".join(sorted(person))
        
        tags = self.get_tags(values["tags"])

        note = values["note"].strip()

        grade = self.maps["name_to_num"][values["grade"]]

        if t != "music":
            check_str, check_value = "title", title

            years = [int(y) if y else None for y in (start_year, end_year)]
            
            query_values = (title, person, years[0], years[1], tags, grade, note)
            if not id:
                query = f"""
                    INSERT INTO {t}_entries (title, {self.maps["category_to_person"][t]}, start_year, end_year, tags, grade, note)
                    VALUES (?, ?, ?, ?, ?, ?, ?);
                """
            else:
                query_values += (id,)
                query = f"""
                    UPDATE {t}_entries
                    SET title = ?, {self.maps["category_to_person"][t]} = ?, start_year = ?, end_year = ?, tags = ?, grade = ?, note = ?
                    WHERE id = ?;
                """
        else:
            check_str, check_value = "artist", person

            query_values = (person, tags, grade, note)
            if not id:
                query = """
                    INSERT INTO music_entries (artist, tags, grade, note)
                    VALUES (?, ?, ?, ?);
                """
            else:
                query_values += (id,)
                query = """
                    UPDATE music_entries
                    SET artist = ?, tags = ?, grade = ?, note = ?
                    WHERE id = ?;
                """
        
        check_query = f"""
            SELECT id FROM {t}_entries 
            WHERE LOWER({check_str}) = LOWER(?)
        """

        con, cur = get_connection(self.db_path)

        cur.execute(check_query, (check_value,))
        if (check_id := cur.fetchone()):
            if not id or check_id[0] != id:
                # If id is None, it means we are adding a new entry, so we should not allow duplicates.
                # If id is not None, we are editing an existing entry, so we can allow the same id.
                con.close()

                error_msg = self.strings[f"{check_str}_already_used"].format(id=check_id[0])
                await self.app.dialog(toga.InfoDialog(self.strings_c["error"], error_msg))
                return 0
        
        cur.execute(query, query_values)
        con.commit()

        self.ranking_get_data(rankings={t: (self.data["load sorting"][t], self.data["load filtering"][t])}, con_cur=(con, cur))

        if id and id in self.widgets_dict["entries"][t]:
            del self.widgets_dict["entries"][t][id]

        con.close()

        items = get_ranges(self.data["rankings"][t])
        set_range(self.widgets_dict[f"{t} range"], items)

        self.app.open_ranking(widget=None, tab=values["category"])

    
    def check_widget(self, widget):
        if widget == "partial div":
            widget = self.get_div((0,80))
            self.reg([widget])
        return widget