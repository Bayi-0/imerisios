import toga
from toga.style import Pack
from toga.constants import COLUMN, ROW
import sqlite3 as sql
from imerisios.mylib.tools import length_check, get_connection, close_connection
from datetime import date
from titlecase import titlecase
from nameparser import HumanName

class Rankings:
    def __init__(self, app, db_path):
        self.app = app
        self.db_path = db_path

        self.ranking_types = ["book", "movie", "series", "music"]
        self.data = {"rankings": {}}
        self.widgets = {"entries": {t:{} for t in self.ranking_types}}
        self.type_to_person = {"book": "author", "movie": "director", "series": "creator", "music": "artist"}
        self.int_to_grade = {6: 'S', 5: 'A', 4: 'B', 3: 'C', 2: 'D', 1: 'E'}
        self.grade_to_int = {v: k for k, v in self.int_to_grade.items()}

    def get_list_box(self):
        # book ranking
        book_label = toga.Label(
            "Book Ranking", 
            style=Pack(flex=0.09, padding=(14,20), text_align="center", font_weight="bold", font_size=20, color="#EBF6F7"))
        
        sort_button = toga.Button(
            "Sort & Filter", id="book sort button", 
            on_press=self.app.open_ranking_sort, 
            style=Pack(flex=0.08, padding=4, height=44, font_size=13, color="#EBF6F7", background_color="#27221F")
        )
        book_sort_box = toga.Box(children=[sort_button], style=Pack(direction=COLUMN))

        back_button = toga.Button(
            "<", id="book back button",
            on_press=self.change_range, 
            style=Pack(flex=0.2, padding=4, height=44, font_size=13, color="#EBF6F7", background_color="#27221F")
        )
        next_button = toga.Button(
            ">", id="book next button",
            on_press=self.change_range, 
            style=Pack(flex=0.2, padding=4, height=44, font_size=13, color="#EBF6F7", background_color="#27221F")
        )
        self.book_range = toga.Selection(
            id="book range", 
            on_change=self.load_rankings,
            style=Pack(flex=0.6, padding=4, height=44))
        self.widgets["book range"] = self.book_range
        book_range_box = toga.Box(
            children=[back_button, self.book_range, next_button],
            style=Pack(direction=ROW))
        
        book_ranking_box = toga.Box(id="book ranking box", style=Pack(direction=COLUMN))
        self.widgets["book ranking box"] = book_ranking_box
        book_ranking_container = toga.ScrollContainer(content=book_ranking_box, horizontal=False, style=Pack(flex=0.75))

        book_box = toga.Box(
            children=[
                book_label, toga.Divider(style=Pack(background_color="#27221F")), 
                book_sort_box, toga.Divider(style=Pack(background_color="#27221F")), 
                book_range_box, toga.Divider(style=Pack(background_color="#27221F")),
                book_ranking_container
            ],
            style=Pack(direction=COLUMN, background_color="#393432"))
        
        # movie ranking
        movie_label = toga.Label(
            "Movie Ranking", 
            style=Pack(flex=0.09, padding=(14,20), text_align="center", font_weight="bold", font_size=20, color="#EBF6F7"))
        
        sort_button = toga.Button(
            "Sort & Filter", id="movie sort button", 
            on_press=self.app.open_ranking_sort, 
            style=Pack(flex=0.08, padding=4, height=44, font_size=13, color="#EBF6F7", background_color="#27221F")
        )
        movie_sort_box = toga.Box(children=[sort_button], style=Pack(direction=COLUMN))

        back_button = toga.Button(
            "<", id="movie back button",
            on_press=self.change_range, 
            style=Pack(flex=0.2, padding=4, height=44, font_size=13, color="#EBF6F7", background_color="#27221F")
        )
        next_button = toga.Button(
            ">", id="movie next button",
            on_press=self.change_range, 
            style=Pack(flex=0.2, padding=4, height=44, font_size=13, color="#EBF6F7", background_color="#27221F")
        )
        self.movie_range = toga.Selection(
            id="movie range", 
            on_change=self.load_rankings,
            style=Pack(flex=0.6, padding=4, height=44))
        self.widgets["movie range"] = self.movie_range
        movie_range_box = toga.Box(
            children=[back_button, self.movie_range, next_button],
            style=Pack(direction=ROW))
        
        movie_ranking_box = toga.Box(id="movie ranking box", style=Pack(direction=COLUMN))
        self.widgets["movie ranking box"] = movie_ranking_box
        movie_ranking_container = toga.ScrollContainer(content=movie_ranking_box, horizontal=False, style=Pack(flex=0.75))

        movie_box = toga.Box(
            children=[
                movie_label, toga.Divider(style=Pack(background_color="#27221F")), 
                movie_sort_box, toga.Divider(style=Pack(background_color="#27221F")), 
                movie_range_box, toga.Divider(style=Pack(background_color="#27221F")),
                movie_ranking_container
            ],
            style=Pack(direction=COLUMN, background_color="#393432"))
        
        # series ranking
        series_label = toga.Label(
            "Series Ranking", 
            style=Pack(flex=0.09, padding=(14,20), text_align="center", font_weight="bold", font_size=20, color="#EBF6F7"))
        
        sort_button = toga.Button(
            "Sort & Filter", id="series sort button", 
            on_press=self.app.open_ranking_sort, 
            style=Pack(flex=0.08, padding=4, height=44, font_size=13, color="#EBF6F7", background_color="#27221F")
        )
        series_sort_box = toga.Box(children=[sort_button], style=Pack(direction=COLUMN))

        back_button = toga.Button(
            "<", id="series back button",
            on_press=self.change_range, 
            style=Pack(flex=0.2, padding=4, height=44, font_size=13, color="#EBF6F7", background_color="#27221F")
        )
        next_button = toga.Button(
            ">", id="series next button",
            on_press=self.change_range, 
            style=Pack(flex=0.2, padding=4, height=44, font_size=13, color="#EBF6F7", background_color="#27221F")
        )
        self.series_range = toga.Selection(
            id="series range", 
            on_change=self.load_rankings,
            style=Pack(flex=0.6, padding=4, height=44))
        self.widgets["series range"] = self.series_range
        series_range_box = toga.Box(
            children=[back_button, self.series_range, next_button],
            style=Pack(direction=ROW))
        
        series_ranking_box = toga.Box(id="series ranking box", style=Pack(direction=COLUMN))
        self.widgets["series ranking box"] = series_ranking_box
        series_ranking_container = toga.ScrollContainer(content=series_ranking_box, horizontal=False, style=Pack(flex=0.75))

        series_box = toga.Box(
            children=[
                series_label, toga.Divider(style=Pack(background_color="#27221F")), 
                series_sort_box, toga.Divider(style=Pack(background_color="#27221F")), 
                series_range_box, toga.Divider(style=Pack(background_color="#27221F")),
                series_ranking_container
            ],
            style=Pack(direction=COLUMN, background_color="#393432"))
        
        # music ranking
        music_label = toga.Label(
            "Music Ranking", 
            style=Pack(flex=0.09, padding=(14,20), text_align="center", font_weight="bold", font_size=20, color="#EBF6F7"))
        
        sort_button = toga.Button(
            "Sort & Filter", id="music sort button", 
            on_press=self.app.open_ranking_sort, 
            style=Pack(flex=0.08, padding=4, height=44, font_size=13, color="#EBF6F7", background_color="#27221F")
        )
        music_sort_box = toga.Box(children=[sort_button], style=Pack(direction=COLUMN))

        back_button = toga.Button(
            "<", id="music back button",
            on_press=self.change_range, 
            style=Pack(flex=0.2, padding=4, height=44, font_size=13, color="#EBF6F7", background_color="#27221F")
        )
        next_button = toga.Button(
            ">", id="music next button",
            on_press=self.change_range, 
            style=Pack(flex=0.2, padding=4, height=44, font_size=13, color="#EBF6F7", background_color="#27221F")
        )
        self.music_range = toga.Selection(
            id="music range", 
            on_change=self.load_rankings,
            style=Pack(flex=0.6, padding=4, height=44))
        self.widgets["music range"] = self.music_range
        music_range_box = toga.Box(
            children=[back_button, self.music_range, next_button],
            style=Pack(direction=ROW))
        
        music_ranking_box = toga.Box(id="music ranking box", style=Pack(direction=COLUMN))
        self.widgets["music ranking box"] = music_ranking_box
        music_ranking_container = toga.ScrollContainer(content=music_ranking_box, horizontal=False, style=Pack(flex=0.75))

        music_box = toga.Box(
            children=[
                music_label, toga.Divider(style=Pack(background_color="#27221F")), 
                music_sort_box, toga.Divider(style=Pack(background_color="#27221F")), 
                music_range_box, toga.Divider(style=Pack(background_color="#27221F")),
                music_ranking_container
            ],
            style=Pack(direction=COLUMN, background_color="#393432"))
        
        # return container
        book_icon = toga.Icon("resources/ranking/book.png")
        movie_icon = toga.Icon("resources/ranking/movie.png")
        series_icon = toga.Icon("resources/ranking/series.png")
        music_icon = toga.Icon("resources/ranking/music.png")

        list_box = toga.OptionContainer(content=[
            toga.OptionItem("Book", book_box, icon=book_icon), 
            toga.OptionItem("Movie", movie_box, icon=movie_icon), 
            toga.OptionItem("Series", series_box, icon=series_icon), 
            toga.OptionItem("Music", music_box, icon=music_icon)])

        return list_box
        
    
    def get_add_entry_box(self):
        # add box label
        label = toga.Label(
            "Add a New Entry", 
            style=Pack(padding=14, text_align="center", font_weight="bold", font_size=18, color="#EBF6F7"))
        
        # type box
        type_label = toga.Label(
            "Type:", 
            style=Pack(padding=(10,18), font_size=16, color="#EBF6F7"))
        self.add_type = toga.Selection(
            items=[t.capitalize() for t in self.ranking_types],
            id="add type",
            on_change=self.type_change,
            style=Pack(padding=(3,18,0), height=44, flex=0.8))
        type_box = toga.Box(
            children=[type_label, self.add_type],
            style=Pack(direction=ROW))
        
        # entry box
        ## title
        title_label = toga.Label(
            "Title:", 
            style=Pack(padding=(18,18,0), font_size=14, color="#EBF6F7"))
        self.widgets["add title label"] = title_label
        self.add_title = toga.TextInput(style=Pack(padding=(0,18), height=44, font_size=12, color="#EBF6F7", background_color="#27221F"))
        self.widgets["add title"] = self.add_title

        self.add_switch = toga.Switch(
            text="Autoformat",
            id="add switch",
            value=True, 
            style=Pack(padding=(8,18,18), font_size=12, color="#EBF6F7"))
        self.widgets["add switch"] = self.add_switch
        
        ## author/director/creator/artist (person)
        author_label = toga.Label(
            "Author:", 
            style=Pack(padding=(18,18,0), font_size=14, color="#EBF6F7"))
        self.widgets["add book_person label"] = author_label
        director_label = toga.Label(
            "Director:", 
            style=Pack(padding=(18,18,0), font_size=14, color="#EBF6F7"))
        self.widgets["add movie_person label"] = director_label
        creator_label = toga.Label(
            "Creator:", 
            style=Pack(padding=(18,18,0), font_size=14, color="#EBF6F7"))
        self.widgets["add series_person label"] = creator_label
        artist_label = toga.Label(
            "Artist:", 
            style=Pack(padding=(18,18,0), font_size=14, color="#EBF6F7"))
        self.widgets["add music_person label"] = artist_label
        
        self.add_person = toga.TextInput(style=Pack(padding=(0,18,18), height=44, font_size=12, color="#EBF6F7", background_color="#27221F"))
        self.widgets["add person"] = self.add_person

        ## years
        start_year_label = toga.Label(
            "Start Year:", 
            style=Pack(padding=(18,18,0), font_size=14, color="#EBF6F7"))
        self.add_start_year = toga.NumberInput(
            id="add start_year input",
            step=1, 
            min=-2601, max=date.today().year,
            on_change=self.start_year_change, 
            style=Pack(padding=(0,18), height=44, font_size=12, color="#EBF6F7", background_color="#27221F"))
        self.widgets["add start_year"] = self.add_start_year
        
        end_year_label = toga.Label(
            "End Year:", 
            style=Pack(padding=(10,18,0), font_size=14, color="#EBF6F7"))
        self.add_end_year = toga.NumberInput(
            step=1, max=date.today().year,
            style=Pack(padding=(0,18,18), height=44, font_size=12, color="#EBF6F7", background_color="#27221F"))
        self.widgets["add end_year"] = self.add_end_year
        
        self.widgets["add year box"] = toga.Box(
            children=[start_year_label, self.add_start_year, end_year_label, self.add_end_year],
            style=Pack(direction=COLUMN))
        
        ## tags
        tags_label = toga.Label(
            "Tags:", 
            style=Pack(padding=(18,0,0,18), font_size=14, color="#EBF6F7"))
        self.widgets["add tags label"] = tags_label
        self.add_tags = toga.TextInput(style=Pack(padding=(0,18,18), height=44, font_size=12, color="#EBF6F7", background_color="#27221F"))
        self.widgets["add tags"] = self.add_tags
        
        ## grade
        grade_label = toga.Label(
            "Grade:", 
            style=Pack(padding=(18,0,0,18), font_size=14, color="#EBF6F7"))
        self.widgets["add grade label"] = grade_label
        self.add_grade = toga.Selection(
            items=[self.int_to_grade[i] for i in range(len(self.int_to_grade), 0, -1)],
            style=Pack(padding=(0,18), height=44))
        self.widgets["add grade"] = self.add_grade
        
        self.add_top_box = toga.Box(style=Pack(direction=COLUMN, flex=0.8))
        self.add_entry_container = toga.ScrollContainer(content=self.add_top_box, horizontal=False, style=Pack(flex=0.7))
        self.widgets["add top_box"] = self.add_top_box
        
        # button box
        button = toga.Button(
            "Add", on_press=self.add_entry, 
            style=Pack(height=120, padding=11, font_size=24, color="#EBF6F7", background_color="#27221F"))
        bottom_box = toga.Box(children=[button], style=Pack(direction=COLUMN, flex=0.19))

        # return box
        add_box = toga.Box(
            children=[
                label, toga.Divider(style=Pack(background_color="#27221F")),
                type_box, toga.Divider(style=Pack(background_color="#27221F")),
                self.add_entry_container, toga.Divider(style=Pack(background_color="#27221F")),
                bottom_box
            ], 
            style=Pack(direction=COLUMN, background_color="#393432"))
        
        return add_box


    def get_edit_entry_box(self):
        # edit box label
        label = toga.Label(
            "Edit the Entry", 
            style=Pack(padding=14, text_align="center", font_weight="bold", font_size=18, color="#EBF6F7"))
        
        # type box
        type_label = toga.Label(
            "Type:", 
            style=Pack(padding=(10,18), font_size=16, color="#EBF6F7"))
        self.edit_type = toga.Selection(
            items=[t.capitalize() for t in self.ranking_types],
            id="edit type",
            on_change=self.type_change,
            enabled=False,
            style=Pack(padding=(3,18), height=44, flex=0.8))
        type_box = toga.Box(
            children=[type_label, self.edit_type],
            style=Pack(direction=ROW))
        
        # entry box
        ## title
        title_label = toga.Label(
            "Title:", 
            style=Pack(padding=(18,18,0), font_size=14, color="#EBF6F7"))
        self.widgets["edit title label"] = title_label
        self.edit_title = toga.TextInput(style=Pack(padding=(0,18), height=44, font_size=12, color="#EBF6F7", background_color="#27221F"))
        self.widgets["edit title"] = self.edit_title

        self.edit_switch = toga.Switch(
            text="Autoformat",
            id="edit switch",
            value=True, 
            style=Pack(padding=(8,18,18), font_size=12, color="#EBF6F7"))
        self.widgets["edit switch"] = self.edit_switch
        
        ## author/director/creator/artist (person)
        author_label = toga.Label(
            "Author:", 
            style=Pack(padding=(18,18,0), font_size=14, color="#EBF6F7"))
        self.widgets["edit book_person label"] = author_label
        director_label = toga.Label(
            "Director:", 
            style=Pack(padding=(18,18,0), font_size=14, color="#EBF6F7"))
        self.widgets["edit movie_person label"] = director_label
        creator_label = toga.Label(
            "Creator:", 
            style=Pack(padding=(18,18,0), font_size=14, color="#EBF6F7"))
        self.widgets["edit series_person label"] = creator_label
        artist_label = toga.Label(
            "Artist:", 
            style=Pack(padding=(18,18,0), font_size=14, color="#EBF6F7"))
        self.widgets["edit music_person label"] = artist_label
        
        self.edit_person = toga.TextInput(style=Pack(padding=(0,18,18), height=44, font_size=12, color="#EBF6F7", background_color="#27221F"))
        self.widgets["edit person"] = self.edit_person

        ## years
        start_year_label = toga.Label(
            "Start Year:", 
            style=Pack(padding=(18,18,0), font_size=14, color="#EBF6F7"))
        self.edit_start_year = toga.NumberInput(
            id="edit start_year input",
            step=1, 
            min=-2601, max=date.today().year,
            on_change=self.start_year_change, 
            style=Pack(padding=(0,18), height=44, font_size=12, color="#EBF6F7", background_color="#27221F"))
        self.widgets["edit start_year"] = self.edit_start_year
        
        end_year_label = toga.Label(
            "End Year:", 
            style=Pack(padding=(10,18,0), font_size=14, color="#EBF6F7"))
        self.edit_end_year = toga.NumberInput(
            step=1, max=date.today().year,
            style=Pack(padding=(0,18,18), height=44, font_size=12, color="#EBF6F7", background_color="#27221F"))
        self.widgets["edit end_year"] = self.edit_end_year
        
        self.widgets["edit year box"] = toga.Box(
            children=[start_year_label, self.edit_start_year, end_year_label, self.edit_end_year],
            style=Pack(direction=COLUMN))
        
        ## tags
        tags_label = toga.Label(
            "Tags:", 
            style=Pack(padding=(18,18,0), font_size=14, color="#EBF6F7"))
        self.widgets["edit tags label"] = tags_label
        self.edit_tags = toga.TextInput(style=Pack(padding=(0,18,18), height=44, font_size=12, color="#EBF6F7", background_color="#27221F"))
        self.widgets["edit tags"] = self.edit_tags
        
        ## grade
        grade_label = toga.Label(
            "Grade:", 
            style=Pack(padding=(18,18,0), font_size=14, color="#EBF6F7"))
        self.widgets["edit grade label"] = grade_label
        self.edit_grade = toga.Selection(
            items=[self.int_to_grade[i] for i in range(len(self.int_to_grade), 0, -1)],
            style=Pack(padding=(0,18), height=44, flex=0.8))
        self.widgets["edit grade"] = self.edit_grade
        
        self.edit_top_box = toga.Box(style=Pack(direction=COLUMN, flex=0.8))
        self.edit_entry_container = toga.ScrollContainer(content=self.edit_top_box, horizontal=False, style=Pack(flex=0.7))
        self.widgets["edit top_box"] = self.edit_top_box
        
        # button box
        remove_button = toga.Button(
                "Remove", on_press=self.remove_entry_dialog, 
                style=Pack(flex=0.5, height=120, padding=(4,4,11,11), font_size=24, color="#EBF6F7", background_color="#27221F"))
        save_button = toga.Button(
                "Save", on_press=self.save_entry_dialog, 
                style=Pack(flex=0.5, height=120, padding=(4,11,11,4), font_size=24, color="#EBF6F7", background_color="#27221F"))
        bottom_box = toga.Box(children=[remove_button, save_button], style=Pack(direction=ROW, flex=0.19))

        # return box
        edit_box = toga.Box(
            children=[
                label, toga.Divider(style=Pack(background_color="#27221F")),
                type_box, toga.Divider(style=Pack(background_color="#27221F")),
                self.edit_entry_container, toga.Divider(style=Pack(background_color="#27221F")),
                bottom_box
            ], 
            style=Pack(direction=COLUMN, background_color="#393432"))
        
        return edit_box
    

    def get_sort_box(self):
        self.criterias = {
            "book": ["—", "Grade", "Title", "Author", "Year", "Added Date"], 
            "movie": ["—", "Grade", "Title", "Director", "Year", "Added Date"], 
            "series": ["—", "Grade", "Title", "Creator", "Year", "Added Date"],
            "music": ["—", "Grade", "Artist", "Added Date"]}
        self.data["sorting"] = {t:[("—", "Asc") for _ in range(3)] for t in self.ranking_types}
        self.data["filtering"] = {
            t:{"grade": ("E", "S"), "person": "", "start_year": ("", ""), "added_date": (date(year=2024, month=7, day=25), date.today())}
            for t in self.ranking_types if t != "music"}
        self.data["filtering"]["music"] = {"grade": ("E", "S"), "added_date": [date(year=2024, month=7, day=25), date.today()]}
        self.data["load sorting"] = {t:[] for t in self.ranking_types}
        self.data["load filtering"] = {t:[] for t in self.ranking_types}
        
        # type box
        type_label = toga.Label(
            "Type:", 
            style=Pack(padding=(10,18), font_size=16, color="#EBF6F7"))
        self.sort_type = toga.Selection(
            items=[t.capitalize() for t in self.ranking_types],
            id="sort type",
            on_change=self.type_change,
            enabled=False,
            style=Pack(padding=(3,18), height=44, flex=0.8))
        self.widgets["sort type"] = self.sort_type
        type_box = toga.Box(
            children=[type_label, self.sort_type],
            style=Pack(direction=ROW))
        
        # sort
        ## label
        sort_label = toga.Label(
            "Sort", 
            style=Pack(padding=14, text_align="center", font_weight="bold", font_size=18, color="#EBF6F7"))
        
        ## number+criteria+order boxes
        labels = [
            toga.Label(f"{i}.", style=Pack(padding=18, font_size=14, color="#EBF6F7")) 
            for i in range(1,4)]
        self.sort_criterias = [
            toga.Selection(
                id=f"sort criteria {i}",
                on_change=self.criteria_change,
                style=Pack(flex=0.55, padding=(8,18), height=44))
            for i in range(1,4)]
        self.sort_orders = [
            toga.Selection(items=["Asc", "Desc"], id=f"sort order {i}", style=Pack(flex=0.45, padding=(8,18), height=44))
            for i in range(1,4)]
        
        sort_boxes = [
            toga.Box(
            children=[labels[i], self.sort_criterias[i], self.sort_orders[i]],
            style=Pack(direction=ROW))
            for i in range(3)]
        
        ## reset button
        sort_reset_button = toga.Button(
            "Reset", on_press=self.reset_sort, 
            style=Pack(padding=4, height=44, font_size=13, color="#EBF6F7", background_color="#27221F"))
        
        ## sort box
        sort_box = toga.Box(
            children=[
                sort_label, toga.Divider(style=Pack(background_color="#27221F")), 
                sort_boxes[0], toga.Divider(style=Pack(padding=(0,80), background_color="#27221F")),
                sort_boxes[1], toga.Divider(style=Pack(padding=(0,80), background_color="#27221F")), 
                sort_boxes[2], toga.Divider(style=Pack(padding=(0,80), background_color="#27221F")),
                sort_reset_button],
            style=Pack(direction=COLUMN))
        
        # filter box
        ## label
        filter_label = toga.Label(
            "Filter", 
            style=Pack(padding=14, text_align="center", font_weight="bold", font_size=18, color="#EBF6F7"))
        
        ## grade
        grade_label = toga.Label(
            "Grade:", 
            style=Pack(padding=(18,18,0), font_size=14, color="#EBF6F7"))
        self.widgets["sort grade label"] = grade_label
        self.sort_grades = [toga.Selection(style=Pack(flex=0.5, padding=(0,18,18), height=44)) for _ in range(2)]
        self.sort_grades[0].items = [self.int_to_grade[i] for i in range(1, len(self.int_to_grade)+1)]
        self.sort_grades[1].items = [self.int_to_grade[i] for i in range(len(self.int_to_grade), 0, -1)]
        grade_box = toga.Box(children=self.sort_grades, style=Pack(direction=ROW))
        self.widgets["sort grade"] = self.sort_grades

        ## author/director/creator/artist (person)
        author_label = toga.Label(
            "Author:", 
            style=Pack(padding=(18,18,0), font_size=14, color="#EBF6F7"))
        self.widgets["sort book_person label"] = author_label
        director_label = toga.Label(
            "Director:", 
            style=Pack(padding=(18,18,0), font_size=14, color="#EBF6F7"))
        self.widgets["sort movie_person label"] = director_label
        creator_label = toga.Label(
            "Creator:", 
            style=Pack(padding=(18,18,0), font_size=14, color="#EBF6F7"))
        self.widgets["sort series_person label"] = creator_label
        artist_label = toga.Label(
            "Artist:", 
            style=Pack(padding=(18,18,0), font_size=14, color="#EBF6F7"))
        self.widgets["sort music_person label"] = artist_label
        
        self.sort_person = toga.TextInput(style=Pack(padding=(0,18,18), height=44, font_size=12, color="#EBF6F7", background_color="#27221F"))
        self.widgets["sort person"] = self.sort_person

        ## tags
        tags_label = toga.Label(
            "Tags:", 
            style=Pack(padding=(18,18,0), font_size=14, color="#EBF6F7"))
        self.widgets["sort tags label"] = tags_label
        self.sort_tags = toga.TextInput(style=Pack(padding=(0,18,18), height=44, font_size=12, color="#EBF6F7", background_color="#27221F"))
        self.widgets["sort tags"] = self.sort_tags

        ## start year between
        start_year_label = toga.Label(
            "Start Year:", 
            style=Pack(padding=(18,0,0,18), font_size=14, color="#EBF6F7"))
        self.widgets["sort start_year label"] = start_year_label
        self.sort_start_years = [
            toga.NumberInput(
                step=1, 
                min=-2601, max=date.today().year,
                style=Pack(flex=0.5, padding=(0,18,18), height=44, font_size=12, color="#EBF6F7", background_color="#27221F"))
            for _ in range(2)]
        self.widgets["sort start_year"] = self.sort_start_years
        start_year_box = toga.Box(children=self.sort_start_years, style=Pack(direction=ROW))
        self.widgets["sort start_year box"] = start_year_box
        
        ## added date between
        added_date_label = toga.Label(
            "Added Date:", 
            style=Pack(padding=(18,18,0), font_size=14, color="#EBF6F7"))
        self.widgets["sort added_date label"] = added_date_label
        self.sort_added_dates = [
            toga.DateInput(max=date.today(), style=Pack(flex=0.5, padding=(0,18,18), width=160, color="#EBF6F7"))
            for _ in range(2)]
        added_date_boxes = [
            toga.Box(children=[self.sort_added_dates[i],], style=Pack(direction=COLUMN, flex=0.5))
            for i in range(2)
        ]
        self.widgets["sort added_date"] = self.sort_added_dates
        added_date_box = toga.Box(children=added_date_boxes, style=Pack(direction=ROW))
        self.widgets["sort added_date box"] = added_date_box

        ## filter reset button
        filter_reset_button = toga.Button(
            "Reset", on_press=self.reset_filter, 
            style=Pack(padding=4, height=44, font_size=13, color="#EBF6F7", background_color="#27221F"))
        self.widgets["sort filter_reset button"] = filter_reset_button

        ## filter box
        self.filter_box = toga.Box(style=Pack(direction=COLUMN))

        ## filter load lists
        full_divider = toga.Divider(style=Pack(background_color="#27221F"))
        small_dividers = [toga.Divider(style=Pack(padding=(0,80), background_color="#27221F")) for i in range(5)]
        self.filters = {}
        for t in self.ranking_types:
            if t != "music":
                self.filters[t] = [
                    filter_label, full_divider,
                    grade_label, grade_box, small_dividers[0],
                    self.widgets[f"sort {t}_person label"], self.sort_person, small_dividers[1],
                    tags_label, self.sort_tags, small_dividers[2],
                    start_year_label, start_year_box, small_dividers[3],
                    added_date_label, added_date_box, small_dividers[4], 
                    filter_reset_button
                ]
            else:
                self.filters[t] = [
                    filter_label, full_divider,
                    grade_label, grade_box, small_dividers[0],
                    tags_label, self.sort_tags, small_dividers[1],
                    added_date_label, added_date_box, small_dividers[2], 
                    filter_reset_button
                ]
        
        # sort & filter button
        button = toga.Button(
            "Sort & Filter", id="sort button", 
            on_press=self.check_sort_inputs, 
            style=Pack(height=120, padding=11, font_size=24, color="#EBF6F7", background_color="#27221F"))
        
        # return box
        sort_filter_box = toga.Box(
            children=[
                sort_box, toga.Divider(style=Pack(background_color="#27221F")),
                self.filter_box
            ],
            style=Pack(direction=COLUMN))
        self.sort_filter_container = toga.ScrollContainer(content=sort_filter_box, horizontal=False, style=Pack(flex=0.8))

        box = toga.Box(
            children=[
                type_box, toga.Divider(style=Pack(background_color="#27221F")),
                self.sort_filter_container, toga.Divider(style=Pack(background_color="#27221F")),
                button
            ], 
            style=Pack(direction=COLUMN, background_color="#393432"))
        
        return box


    def get_search_box(self):
        # label
        label = toga.Label(
            "Search Entry", 
            style=Pack(padding=(14,20), text_align="center", font_weight="bold", font_size=20, color="#EBF6F7"))
        
        # type
        type_label = toga.Label(
            "Type:", 
            style=Pack(padding=(10,18), font_size=16, color="#EBF6F7"))
        self.search_type = toga.Selection(
            items=[t.capitalize() for t in self.ranking_types],
            id="search type",
            on_change=self.type_change,
            style=Pack(padding=(3,18), height=44, flex=0.8))
        type_box = toga.Box(
            children=[type_label, self.search_type],
            style=Pack(direction=ROW))

        # search
        self.search_input = toga.TextInput(style=Pack(padding=(4,4,0), height=44, font_size=12, color="#EBF6F7", background_color="#27221F"))
        search_button = toga.Button(
            "Search", id="search button",
            on_press=self.load_rankings, 
            style=Pack(padding=4, height=44, font_size=13, color="#EBF6F7", background_color="#27221F"))
        search_box = toga.Box(
            children=[self.search_input, search_button],
            style=Pack(direction=COLUMN))
        
        # result box
        self.search_result_box = toga.Box(style=Pack(direction=COLUMN))
        result_container = toga.ScrollContainer(content=self.search_result_box, horizontal=False, style=Pack(flex=0.75))

        # return box
        box = toga.Box(
            children=[
                label, toga.Divider(style=Pack(background_color="#27221F")),
                type_box, toga.Divider(style=Pack(background_color="#27221F")),
                search_box, toga.Divider(style=Pack(background_color="#27221F")),
                result_container
            ], 
            style=Pack(direction=COLUMN, background_color="#393432"))
        
        return box
    

    def setup_rankings(self):
        ranking_list_box = self.get_list_box()
        ranking_sort_box = self.get_sort_box()
        add_entry_box = self.get_add_entry_box()
        search_entry_box = self.get_search_box()
        edit_entry_box = self.get_edit_entry_box()

        con, cur = get_connection(self.db_path)
        cur.executescript("""
            CREATE TABLE IF NOT EXISTS book_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            added_date DATE DEFAULT (date('now', 'localtime')),
            title TEXT NOT NULL,
            author TEXT,
            start_year INTEGER,
            end_year INTEGER,
            tags TEXT,
            grade INTEGER NOT NULL
            );
                          
            CREATE TABLE IF NOT EXISTS movie_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            added_date DATE DEFAULT (date('now', 'localtime')),
            title TEXT NOT NULL,
            director TEXT,
            start_year INTEGER,
            end_year INTEGER,
            tags TEXT,
            grade INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS series_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            added_date DATE DEFAULT (date('now', 'localtime')),
            title TEXT NOT NULL,
            creator TEXT,
            start_year INTEGER,
            end_year INTEGER,
            tags TEXT,
            grade INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS music_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            added_date DATE DEFAULT (date('now', 'localtime')),
            artist TEXT NOT NULL,
            tags TEXT,
            grade INTEGER NOT NULL
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
        """)
        con.commit()

        self.update_rankings(load=True, con_cur=(con, cur))
        con.close()

        return ranking_list_box, ranking_sort_box, add_entry_box, search_entry_box, edit_entry_box


    def update_rankings(self, load=False, con_cur=None):
        self.widgets["sort added_date"][1].max = date.today()
        if load:
            self.load_rankings(None, con_cur=con_cur)
        

    def ranking_get_data(self, rankings={}, search=None, con_cur=None):
        con, cur = get_connection(self.db_path, con_cur)

        # rankings
        for t in rankings:
            sort, filters = rankings[t]

            ## sorting criteria
            sort_criterias = []
            for c_o in sort:
                criteria, order = c_o
                string = f"{criteria} {order}" if criteria not in self.type_to_person.values() and criteria != "title" else f"LOWER({criteria}) {order}"
                sort_criterias.append(string)
            sorting = "ORDER BY " + ", ".join(sort_criterias) if sort_criterias else ""

            ## filter criteria
            filter_criterias = []
            filter_values = []
            
            for c_v in filters:
                criteria, value = c_v
                if criteria == "grade":
                    from_grade, to_grade = value
                    filter_criterias.append("grade >= ? and grade <= ?")
                    filter_values.append(from_grade)
                    filter_values.append(to_grade)
                elif criteria == self.type_to_person[t]:
                    filter_criterias.append(f"LOWER({criteria}) LIKE LOWER(?)")
                    filter_values.append(f"%{value}%")
                elif criteria == "tags":
                    for tag in value:
                        filter_criterias.append("LOWER(tags) LIKE LOWER(?)")
                        filter_values.append(f"%{tag}%")
                elif criteria == "start_year":
                    from_year, to_year = value
                    filter_criterias.append("start_year >= ? AND start_year <= ?")
                    filter_values.append(from_year)
                    filter_values.append(to_year)
                elif criteria == "added_date":
                    from_date, to_date = value
                    filter_criterias.append("added_date >= ? AND added_date <= ?")
                    filter_values.append(from_date)
                    filter_values.append(to_date)

            filtering = "WHERE " + " AND ".join(filter_criterias) if filter_criterias else ""

            ## query
            query = f"""
                SELECT * FROM {t}_entries
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
                OR LOWER({self.type_to_person[t]}) LIKE LOWER(?)
            """
            
            # add title search if needed and execute
            if t != "music":
                query += " OR LOWER(title) LIKE LOWER(?)"
                query += " ORDER BY title ASC;"
                cur.execute(query, (s, f"%{s}%", f"%{s}%",))
            else:
                query += " ORDER BY artist ASC;"
                cur.execute(query, (s, f"%{s}%",))

            self.data["search"] = cur.fetchall()

        close_connection(con, con_cur)  
    

    def load_rankings(self, widget, con_cur=None):
        # setup 
        if not widget:
            self.ranking_get_data({t:([],[]) for t in self.ranking_types}, con_cur=con_cur)

            for t in self.ranking_types:
                data = self.data["rankings"][t]
                items = self.get_ranges(data)
                self.widgets[f"{t} range"].items = items

        else:  
            widget_id = widget.id.split()

            if widget_id[1] == "range":
                t = widget_id[0]
                data = self.data["rankings"][t]
                box = self.widgets[f"{t} ranking box"]
                box.clear()

                start, end = [int(i) for i in widget.value.split('–')]
                if start == 0 and end == 0:
                    box.add(
                        toga.Label(
                        "Added entries will appear here.",
                        style=Pack(padding=10, font_size=12, color="#EBF6F7")))
                else:
                    for i in range(start-1, end):
                        e = data[i]
                        id = e[0]
                        if id not in self.widgets["entries"][t]:
                            entry_box = self.get_entry_box(t, e)
                            self.widgets["entries"][t][id] = entry_box
                        box.add(self.widgets["entries"][t][id])

            elif widget_id[0] == "sort":
                t = self.data["load type"]
                self.ranking_get_data({t:(self.data["load sorting"][t], self.data["load filtering"][t])})
                items = self.get_ranges(self.data["rankings"][t])
                self.widgets[f"{t} range"].items = items

            elif widget_id[0] == "search":
                t = self.search_type.value.lower()
                input = self.search_input.value.strip()
                self.ranking_get_data(search=(t, input))
                box = self.search_result_box
                box.clear()

                if (data := self.data["search"]):
                    for e in data:
                        box.add(self.get_entry_box(t, e, True))
                else:
                    box.add(
                        toga.Label(
                        "No entries found.",
                        style=Pack(padding=10, font_size=12, color="#EBF6F7")))

    
    def change_range(self, widget):
        t, button, _ = widget.id.split()
        w = self.widgets[f"{t} range"]
        value = w.value
        obj = w.items.find(value)
        idx = w.items.index(obj)
        if button == "back":
            if idx != 0:
                w.value = w.items[idx-1].value
        elif button == "next":
            if len(w.items) != idx+1:
                w.value = w.items[idx+1].value


    def type_change(self, widget):
        t = widget.value.lower()
        tab = widget.id.split()[0]
        if tab == "sort":
            self.sort_criterias[0].items = self.criterias[t]
            for i in range(3):
                self.sort_criterias[i].value = self.data["sorting"][t][i][0]
                self.sort_orders[i].value = self.data["sorting"][t][i][1]
            box = self.filter_box
            box.clear()
            for w in self.filters[t]:
                box.add(w)
            data = self.data["filtering"][t]
            for c in data:
                if c != "grade" and c != "start_year" and c != "added_date":
                    self.widgets[f"sort {c}"].value = data[c]
                else: 
                    self.widgets[f"sort {c}"][0].value, self.widgets[f"sort {c}"][1].value = data[c]

        elif tab == "search":
            self.search_input.value = ""
            self.search_result_box.clear()
            title = "title, " if t != "music" else ""
            placeholder = f"{title}{self.type_to_person[t]} or ID"
            self.search_input.placeholder = placeholder

        else:    
            box = self.widgets[f"{tab} top_box"]
            box.clear()

            if t == "book" or t == "movie" or t == "series":
                box.add(
                    self.widgets[f"{tab} title label"], self.widgets[f"{tab} title"], self.widgets[f"{tab} switch"], toga.Divider(style=Pack(padding=(0,80), background_color="#27221F")),
                    self.widgets[f"{tab} {t}_person label"], self.widgets[f"{tab} person"], toga.Divider(style=Pack(padding=(0,80), background_color="#27221F")),
                    self.widgets[f"{tab} year box"], toga.Divider(style=Pack(padding=(0,80), background_color="#27221F")),
                    self.widgets[f"{tab} tags label"], self.widgets[f"{tab} tags"], toga.Divider(style=Pack(padding=(0,80), background_color="#27221F")),
                    self.widgets[f"{tab} grade label"], self.widgets[f"{tab} grade"])
            elif t == "music":
                box.add(
                    self.widgets[f"{tab} {t}_person label"], self.widgets[f"{tab} person"], self.widgets[f"{tab} switch"], toga.Divider(style=Pack(padding=(0,80), background_color="#27221F")),
                    self.widgets[f"{tab} tags label"], self.widgets[f"{tab} tags"], toga.Divider(style=Pack(padding=(0,80), background_color="#27221F")),
                    self.widgets[f"{tab} grade label"], self.widgets[f"{tab} grade"])
            
        self.type_change_check = False


    def start_year_change(self, widget):
        add = widget.id.split()[0] == "add"
        year = widget.value
        end_widget = self.add_end_year if add else self.edit_end_year
        end_widget.min = end_widget.value = year


    async def add_entry(self, widget):
        t = self.add_type.value.lower()
        if t != "music":
            start_year, end_year = self.add_start_year.value, self.add_end_year.value
            if not start_year and end_year:
                await self.app.dialog(toga.InfoDialog("Error", "End year cannot exist without start year."))
                return 0

            title = self.add_title.value.strip()
            title = titlecase(title) if self.add_switch.value else title
            if not title:
                await self.app.dialog(toga.InfoDialog("Error", "Title must be specified."))
                return 0

        person_value = self.add_person.value
        person = [p.strip() for p in person_value.split(",")]
        if t == "music":   
            if not person_value:
                await self.app.dialog(toga.InfoDialog("Error", "Artist must be specified."))
                return 0
            if self.add_switch.value:
                for i in range(len(person)):
                    person[i] = HumanName(person[i])
                    person[i].capitalize(force=True)
                    person[i] = str(person[i])
                person = ", ".join(sorted(person))
            else:
                person = ", ".join(person)

        elif person:
            for i in range(len(person)):
                person[i] = HumanName(person[i])
                person[i].capitalize(force=True)
                person[i] = str(person[i])
            person = ", ".join(sorted(person))
        
        tags = self.add_tags.value.lower().split(",")
        tags = sorted([t.strip() for t in tags])
        tags = titlecase(", ".join(tags))

        grade = self.grade_to_int[self.add_grade.value]

        if t != "music":
            years = [int(y) if y else None for y in (start_year, end_year)]
            query = f"""
                INSERT INTO {t}_entries (title, {self.type_to_person[t]}, start_year, end_year, tags, grade)
                VALUES (?, ?, ?, ?, ?, ?);
            """
            values = (title, person, years[0], years[1], tags, grade)
        else:
            query = """
                INSERT INTO music_entries (artist, tags, grade)
                VALUES (?, ?, ?);
            """
            values = (person, tags, grade)
        
        con, cur = get_connection(self.db_path)
        cur.execute(query, values)
        con.commit()

        self.ranking_get_data(rankings={t: (self.data["load sorting"][t], self.data["load filtering"][t])}, con_cur=(con, cur))

        con.close()

        items = self.get_ranges(self.data["rankings"][t])
        self.widgets[f"{t} range"].items = items

        self.app.open_ranking(widget=None, tab=t.capitalize())


    async def remove_entry_dialog(self, widget):
        result = await self.app.dialog(toga.QuestionDialog("Confirmation", "Art thou certain thou wishest to remove the entry?"))
        if result:
            await self.remove_entry()


    async def remove_entry(self):
        t = self.edit_type.value.lower()
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

        if id in self.widgets["entries"][t]:
            del self.widgets["entries"][t][id]

        items = self.get_ranges(self.data["rankings"][t])
        self.widgets[f"{t} range"].items = items

        self.app.open_ranking(widget=None, tab=t.capitalize())
        

    async def save_entry_dialog(self, widget):
        result = await self.app.dialog(toga.QuestionDialog("Confirmation", "Art thou certain thou wishest to save the entry?"))
        if result:
            await self.save_entry()


    async def save_entry(self):
        t = self.edit_type.value.lower()
        id = self.temp_edit_id

        if t != "music":
            start_year, end_year = self.edit_start_year.value, self.edit_end_year.value
            if start_year and end_year:
                if start_year > end_year:
                    await self.app.dialog(toga.InfoDialog("Error", "Start year cannot be after end year."))
                    return 0
            elif not start_year and end_year:
                await self.app.dialog(toga.InfoDialog("Error", "End year cannot exist without start year."))
                return 0

            title = self.edit_title.value.strip()
            title = titlecase(title) if self.edit_switch.value else title
            if not title:
                await self.app.dialog(toga.InfoDialog("Error", "Title must be specified."))
                return 0

        person = [p.strip() for p in self.edit_person.value.split(",")]
        if t == "music":
            if not person:
                self.app.dialog(toga.InfoDialog("Error", "Artist must be specified."))
                return 0
            else:
                if self.edit_switch.value:
                    for i in range(len(person)):
                        person[i] = HumanName(person[i])
                        person[i].capitalize(force=True)
                        person[i] = str(person[i])
                    person = ", ".join(sorted(person))
                else:
                    person = ", ".join(person)
        elif person:
            for i in range(len(person)):
                person[i] = HumanName(person[i])
                person[i].capitalize(force=True)
                person[i] = str(person[i])
            person = ", ".join(sorted(person))
        
        tags = self.edit_tags.value.lower().split(",")
        tags = sorted([t.strip() for t in tags])
        tags = titlecase(", ".join(tags))

        grade = self.grade_to_int[self.edit_grade.value]

        if t != "music":
            years = [int(y) if y else None for y in (start_year, end_year)]
            query = f"""
                UPDATE {t}_entries
                SET title = ?, {self.type_to_person[t]} = ?, start_year = ?, end_year = ?, tags = ?, grade = ?
                WHERE id = ?;
            """
            values = (title, person, years[0], years[1], tags, grade, id)
        else:
            query = """
                UPDATE music_entries
                SET artist = ?, tags = ?, grade = ?
                WHERE id = ?;
            """
            values = (person, tags, grade, id)
        
        con, cur = get_connection(self.db_path)
        cur.execute(query, values)
        con.commit()
        
        self.ranking_get_data(rankings={t: (self.data["load sorting"][t], self.data["load filtering"][t])}, con_cur=(con, cur))

        con.close()
        
        if id in self.widgets["entries"][t]:
            del self.widgets["entries"][t][id]

        items = self.get_ranges(self.data["rankings"][t])
        self.widgets[f"{t} range"].items = items

        self.app.open_ranking(widget=None, tab=t.capitalize())


    def criteria_change(self, widget): 
        value = widget.value
        items = widget.items
        n = int(widget.id.split()[2])
        s_c = self.sort_criterias
        s_o = self.sort_orders
        if value == "—":
            if n != 3:
                s_c[n].items = [c.value for c in items]
                s_c[n].enabled = False
                s_o[n].value = "Asc"
                s_o[n].enabled = False
        else:
            if n != 3:
                s_c[n].items = [c.value for c in items if c.value != value]
                s_c[n].enabled = True
                s_o[n].enabled = True
                

    def reset_sort(self, widget):
        self.sort_criterias[0].value = "—"
        self.sort_orders[0].value = "Asc"


    def reset_filter(self, widget):
        self.sort_grades[0].value, self.sort_grades[1].value = "E", "S"
        self.sort_tags.value = ""
        self.sort_added_dates[0].value, self.sort_added_dates[1].value = date(2024, 7, 25), date.today()
        if self.sort_type.value.lower() != "music":
            self.sort_person.value = ""
            self.sort_start_years[0].value, self.sort_start_years[1].value = "", ""

    def format_title(self, title, max_length=48):
        if len(title) > max_length:
            words = title.split()
            first_row = ""
            second_row = ""
            
            for word in words:
                if len(first_row) + len(word) + 1 <= max_length:
                    first_row += word + " "
                else:
                    break
            first_row = first_row.rstrip()

            for word in words[len(first_row.split()):]:
                if len(second_row) + len(word) + 1 <= max_length:
                    second_row += word + " "
                else:
                    break
            second_row = second_row.rstrip()

            if len(second_row) < max_length and words[len(first_row.split())+len(second_row.split()):]:
                remaining_length = max_length - len(second_row) - 4
                second_row = second_row[:remaining_length].rstrip() + "..."

            return first_row, second_row
        
        else:
            return title, ""

    def format_person(self, person, max_length=38):
        if len(person) > max_length:
            people = person.split(", ")
            
            result = ""
            
            for i, person in enumerate(people):
                if i == 0:
                    temp_result = person
                else:
                    temp_result = result + ", " + person
                
                if len(temp_result) <= max_length:
                    result = temp_result
                else:
                    if i == 0:
                        return "..."
                    else:
                        return result + ", ..."
            
            return result
    
        else:
            return person
        

    def format_tags(self, tags, first_max_length=42, second_max_length=48):
        if len(tags) > first_max_length:
            tag_list = tags.split(", ")
            
            first_row = ""
            second_row = ""
            
            for tag in tag_list:
                if len(first_row) + len(tag) + (1 if first_row else 0) <= first_max_length:
                    if first_row:
                        first_row += ", "
                    first_row += tag
                else:
                    first_row += ","
                    break
            
            for tag in tag_list[len(first_row.split(", ")):]:
                if len(second_row) + len(tag) + (1 if second_row else 0) <= second_max_length:
                    if second_row:
                        second_row += ", "
                    second_row += tag
                else:
                    if second_row:
                        second_row += ", ..."
                    break
            
            return first_row, second_row
        else:
            return tags, ""
        

    def get_entry_box(self, entry_type, entry, edit_button=False):
        id = entry[0]
        added_date = entry[1]
        grade = self.int_to_grade[entry[-1]]

        if entry_type != "music":
            rows = self.format_title(entry[2])
            title = rows[0] + '\n' + rows[1]
            person = self.format_person(entry[3]) if entry[3] else "—"
            if entry[4]:
                if entry[4] == entry[5]:
                    year = entry[4]
                else:
                    year = f"{entry[4]}–{entry[5]}"
            else:
                year = "—"
            if entry[6]:
                rows = self.format_tags(entry[6])
                tags = rows[0] + '\n' + rows[1]
            else:
                tags = "—\n"

            id_label = toga.Label(
                f"[{id:06d}]", 
                style=Pack(padding=4, font_size=11, color="#EBF6F7"))
            main_label = toga.Label(
                title, 
                style=Pack(padding=4, font_size=11, font_weight="bold", color="#EBF6F7"))
            middle_label = toga.Label(
                f"{self.type_to_person[entry_type].capitalize()}: {person}\nYear: {year} | Added: {added_date}\nTags: {tags}", 
                style=Pack(padding=4, font_size=11, color="#EBF6F7"))
            grade_label = toga.Label(
                f"Grade: {grade}", 
                style=Pack(padding=4, font_size=11, color="#EBF6F7"))
            
        else:
            artist = entry[2]
            if entry[3]:
                rows = self.format_tags(entry[3])
                tags = rows[0] + '\n' + rows[1]
            else:
                tags = "—\n"

            id_label = toga.Label(
                f"[{id:06d}]", 
                style=Pack(padding=4, font_size=11, color="#EBF6F7"))
            main_label = toga.Label(
                artist, 
                style=Pack(padding=4, font_size=11, font_weight="bold", color="#EBF6F7"))
            middle_label = toga.Label(
                f"Added: {added_date}\nTags: {tags}", 
                style=Pack(padding=4, font_size=11, color="#EBF6F7"))
            grade_label = toga.Label(
                f"Grade: {grade}", 
                style=Pack(padding=4, font_size=11, color="#EBF6F7"))
        
        children = [id_label, main_label, middle_label, grade_label]
        if edit_button:
            if (button_id := f"{id} edit_button") not in self.widgets["entries"][entry_type]:
                self.widgets["entries"][entry_type][button_id] = toga.Button(
                    "Edit", id=button_id, on_press=self.app.open_ranking_edit_entry, 
                    style=Pack(padding=4, height=42, font_size=12, color="#EBF6F7", background_color="#27221F"))
            children.append(self.widgets["entries"][entry_type][button_id])
        children.append(toga.Divider(style=Pack(background_color="#27221F")))
        entry_box = toga.Box(children=children, style=Pack(direction=COLUMN))
        
        return entry_box
    

    def get_ranges(self, entries):
        ranges = []
        entries_number = len(entries)
        chunk_size = 40

        start = 1
        if entries_number == 0:
            ranges = [(0, 0)]
        while entries_number > 0:
            end = start + min(entries_number, chunk_size) - 1
            ranges.append([start, end])
            entries_number -= chunk_size
            start = end + 1
        
        items = ['–'.join([str(i) for i in r]) for r in ranges]

        return items
    

    def check_sort_inputs(self, widget):
        t = self.sort_type.value.lower()

        # filter 
        filtering = []       
        grades = [self.grade_to_int[self.sort_grades[i].value] for i in range(2)]
        if grades[0] > grades[1]:
            self.app.info_dialog("Error", "The from (first) grade cannot be higher than the to (second) grade.")
            return 0
        filtering.append(("grade", grades))
        
        if (tags := self.sort_tags.value):
            filtering.append(("tags", [tag.strip() for tag in tags.split(",")]))

        dates = (self.sort_added_dates[0].value, self.sort_added_dates[1].value)
        if dates[0] > dates[1]:
            self.app.info_dialog("Error", "The from (first) date cannot be higher than the to (second) date.")
            return 0
        filtering.append(("added_date", dates))

        if t != "music":
            if (person := self.sort_person.value):
                filtering.append((self.type_to_person[t], person.strip()))
            
            start_year = self.sort_start_years[0].value
            end_year = self.sort_start_years[1].value
            if start_year or end_year:
                if start_year and end_year:
                    if start_year[0] > end_year[1]:
                        self.app.info_dialog("Error", "The from (first) year cannot be higher than the to (second) year.")
                        return 0
                    years = (int(start_year), int(end_year))
                elif start_year:
                    years = (int(start_year), date.today().year)
                elif end_year:
                    years = (-2601, int(end_year))
                filtering.append(("start_year", years))
            
            self.data["filtering"][t]["person"] = person
            self.data["filtering"][t]["start_year"] = (start_year, end_year)

        self.data["filtering"][t]["tags"] = tags
        self.data["filtering"][t]["grade"] = [self.int_to_grade[grades[i]] for i in range(2)]
        self.data["filtering"][t]["added_date"] = [self.sort_added_dates[i].value for i in range(2)]

        self.data["load filtering"][t] = filtering

        # sort
        sort = [(self.sort_criterias[i].value, self.sort_orders[i].value) for i in range(3)]
        self.data["sorting"][t] = sort
        sorting = []
        for i in sort:
            if i[0] != "—":
                c = i[0].lower().replace("year", "start_year").replace("added date", "added_date")
                o = "ASC" if i[1] == "Asc" else "DESC"
                sorting.append((c, o))

        self.data["load sorting"][t] = sorting

        # type
        self.data["load type"] = t

        self.load_rankings(widget)

        self.app.open_ranking(widget=None, tab=t.capitalize())

    
    def load_edit_box(self, widget):
        id = int(widget.id.split()[0])
        self.temp_edit_id = id
        t = self.search_type.value.lower()

        values = f"{self.type_to_person[t]}, tags, grade"
        values += ", title, start_year, end_year" if t != "music" else ""
        query = f"""
            SELECT {values} FROM {t}_entries
            WHERE id = ?
        """
        con, cur = get_connection(self.db_path)
        cur.execute(query, (id,))
        entry = cur.fetchone()
        con.close()

        widgets = ["person", "tags", "grade"]
        widgets += ["title", "start_year", "end_year"] if t != "music" else []
        for i in range(len(widgets)):
            self.widgets[f"edit {widgets[i]}"].value = self.int_to_grade[entry[i]] if i == 2 else entry[i]
        self.widgets["edit switch"].value = False


    def clear_add_box(self):
        for w in ["title", "person", "tags", "start_year", "end_year", "grade", "switch"]:
            if w == "grade":
                self.widgets[f"add {w}"].value = "S"
            elif w == "switch":
                self.widgets[f"add {w}"].value = True
            else:
                self.widgets[f"add {w}"].value = ""


    async def reset_ranking_dialog(self, widget):
        result = await self.app.dialog(toga.QuestionDialog("Confirmation", "Are you sure you wish to reset Rankings database?"))
        if result:
            await self.reset_ranking()


    async def reset_ranking(self):
        con, cur = get_connection(self.db_path)
        
        for t in self.type_to_person:
            query = f"DROP TABLE {t}_entries;"
            cur.execute(query)
            con.commit()

        cur.executescript("""
            CREATE TABLE book_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            added_date DATE DEFAULT (date('now', 'localtime')),
            title TEXT NOT NULL,
            author TEXT,
            start_year INTEGER,
            end_year INTEGER,
            tags TEXT,
            grade INTEGER NOT NULL
            );
                          
            CREATE TABLE movie_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            added_date DATE DEFAULT (date('now', 'localtime')),
            title TEXT NOT NULL,
            director TEXT,
            start_year INTEGER,
            end_year INTEGER,
            tags TEXT,
            grade INTEGER NOT NULL
            );

            CREATE TABLE series_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            added_date DATE DEFAULT (date('now', 'localtime')),
            title TEXT NOT NULL,
            creator TEXT,
            start_year INTEGER,
            end_year INTEGER,
            tags TEXT,
            grade INTEGER NOT NULL
            );

            CREATE TABLE music_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            added_date DATE DEFAULT (date('now', 'localtime')),
            artist TEXT NOT NULL,
            tags TEXT,
            grade INTEGER NOT NULL
            );

            CREATE INDEX idx_book_added_date ON book_entries (added_date);
            CREATE INDEX idx_book_title ON book_entries (title);
            CREATE INDEX idx_book_author ON book_entries (author);
            CREATE INDEX idx_book_start_year ON book_entries (start_year);
            CREATE INDEX idx_book_end_year ON book_entries (end_year);
            CREATE INDEX idx_book_tags ON book_entries (tags);
            CREATE INDEX idx_book_grade ON book_entries (grade);

            CREATE INDEX idx_movie_added_date ON movie_entries (added_date);
            CREATE INDEX idx_movie_title ON movie_entries (title);
            CREATE INDEX idx_movie_director ON movie_entries (director);
            CREATE INDEX idx_movie_start_year ON movie_entries (start_year);
            CREATE INDEX idx_movie_end_year ON movie_entries (end_year);
            CREATE INDEX idx_movie_tags ON movie_entries (tags);
            CREATE INDEX idx_movie_grade ON movie_entries (grade);

            CREATE INDEX idx_series_added_date ON series_entries (added_date);
            CREATE INDEX idx_series_title ON series_entries (title);
            CREATE INDEX idx_series_creator ON series_entries (creator);
            CREATE INDEX idx_series_start_year ON series_entries (start_year);
            CREATE INDEX idx_series_end_year ON series_entries (end_year);
            CREATE INDEX idx_series_tags ON series_entries (tags);
            CREATE INDEX idx_series_grade ON series_entries (grade);
          
            CREATE INDEX idx_music_added_date ON music_entries (added_date);
            CREATE INDEX idx_music_artist ON music_entries (artist);
            CREATE INDEX idx_music_tags ON music_entries (tags);
            CREATE INDEX idx_music_grade ON music_entries (grade);
        """)
        con.commit()
        con.close()

        self.app.setup_ui(rankings=True)

        await self.app.dialog(toga.InfoDialog("Success", "Rankings database was successfully reset."))