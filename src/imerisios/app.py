"""
A versatile app for everyday use.
"""
import toga
from toga.style import Pack
from toga.constants import COLUMN, ROW
from datetime import date
import json
from pathlib import Path
import sqlite3 as sql
import threading
import time
import schedule
import asyncio
import weakref
from titlecase import titlecase
from imerisios.mylib.coin import CoinFlip
from imerisios.mylib.todo import ToDo
from imerisios.mylib.habit import Habits
from imerisios.mylib.journal import Journal
from imerisios.mylib.ranking import Rankings
from imerisios.mylib.tools import language_to_alpha3, reverse_dict


class Imerisios(toga.App):
    def startup(self, manual=False):
        self.sizes = self.screens[0].size
        # app directory
        self.config_dir = self.paths.config
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.data_dir = self.paths.data
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.cache_dir = self.paths.cache
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # today date 
        self.today = date.today()

        # settings 
        self.settings_path = self.config_dir / "settings.json"
        if not self.settings_path.exists():
            self.settings = {
                "language": "English",
                "theme": "Charcoal"      
            }

            self.save_settings(self.settings)
        else:
            with open(self.settings_path) as f:
                self.settings = json.load(f)

        # language
        self.strings = ""
        self.load_strings()
        self.languages = ["English", "한국어", "Русский", "Українська", "Dansk", "Latina"]
        self.maps = {"system_to_localized": self.strings["app"]["themes"]}
        self.maps["localized_to_system"] = reverse_dict(self.maps["system_to_localized"])

        # bg, darker bg, text colors
        with open(self.paths.app / "resources/themes/themes.json") as f:
            self.themes = json.load(f)

        self.clrs = self.themes[self.settings["theme"]]

        self.widgets_dict = {"theme change": [weakref.WeakSet() for _ in range(3)]}

        self.setup_settings = True
        self.setup_coin = True
        self.setup_todo = True
        self.setup_habits = True
        self.setup_journal = True
        self.setup_rankings = True

        # menu
        self.setup_ui(menu=True)

        # commands
        add_str = self.strings["common"]["add"]

        menu_str = self.strings["app"]["menu"]
        menu_group = toga.Group(f"0 {menu_str}")
        self.menu_command = toga.Command(self.open_menu, text=menu_str, group=menu_group, enabled=False)

        settings_str = self.strings["app"]["settings"]
        settings_group = toga.Group(f"1 {settings_str}")
        self.settings_command = toga.Command(self.open_settings, text=settings_str, group=settings_group)

        todo_str = self.strings["todo"]["todo"]
        todo_group = toga.Group(f"2 {todo_str}")
        self.todo_command = toga.Command(self.open_todo, text=todo_str, group=todo_group)
        self.add_task_command = toga.Command(self.open_add_task, text=add_str, group=todo_group)
        self.task_history_command = toga.Command(self.open_task_history, text=self.strings["todo"]["history"], group=todo_group)

        habit_group = toga.Group(f"3 {self.strings['habit']['habits']}")
        self.habit_tracker_command = toga.Command(self.open_habit_tracker, text=self.strings["habit"]["tracker"], group=habit_group)
        self.habit_details_command = toga.Command(self.open_habit_details, text=self.strings["habit"]["details"], group=habit_group)
        self.habit_manage_command = toga.Command(self.open_add_habit, text=add_str, group=habit_group)

        journal_str = self.strings["journal"]["journal"]
        journal_group = toga.Group(f"4 {journal_str}")
        self.journal_command = toga.Command(self.open_journal, text=journal_str, group=journal_group)
        self.notes_command = toga.Command(self.open_journal_notes, text=self.strings["journal"]["notes"], group=journal_group)
        self.add_note_command = toga.Command(self.open_add_note, text=add_str, group=journal_group)

        rankings_str = self.strings["ranking"]["rankings"]
        ranking_group = toga.Group(f"5 {rankings_str}")
        self.ranking_command = toga.Command(self.open_ranking, text=rankings_str, group=ranking_group)
        self.ranking_add_command = toga.Command(self.open_ranking_add_entry, text=add_str, group=ranking_group)
        self.ranking_search_command = toga.Command(self.open_ranking_search, text=self.strings["ranking"]["search"], group=ranking_group)

        self.commands.add(
            self.menu_command, 
            self.todo_command, 
            self.settings_command, 
            self.task_history_command, 
            self.add_task_command, 
            self.habit_tracker_command, 
            self.habit_details_command, 
            self.habit_manage_command,
            self.journal_command,
            self.notes_command,
            self.add_note_command,
            self.ranking_command,
            self.ranking_add_command,
            self.ranking_search_command
        )
        
        # main window
        if not manual:
            self.main_window = toga.MainWindow(title=self.formal_name)
            
        self.main_window.content = self.widgets_dict["menu box"]
        self.build_toolbar([(self.menu_command, False), (self.settings_command, True)])
        self.main_window.show()

        # scheduler 
        schedule.every().minute.do(self.day_change_sync_wrapper)
        
        scheduler_thread = threading.Thread(target=self.run_scheduler)
        scheduler_thread.daemon = True
        scheduler_thread.start()
        

    def setup_ui(self, menu=False, settings=False, coin_flip=False, todo=False, habits=False, journal=False, rankings=False):
        tabs = [
            self.strings["coin"]["coin_flip"], self.strings["todo"]["todo"], 
            self.strings["habit"]["habits"], self.strings["journal"]["journal"], 
            self.strings["ranking"]["rankings"], self.strings["app"]["general"]
        ]
        
        # menu
        if menu:
            button_height = int(self.sizes[1] / 5 * 0.93)
            boxes = []
            for val, func, img_path, padd in [
                (tabs[0], self.open_coin, "coin", (2,0,0)), 
                (tabs[1], self.open_todo, "todo", (0,0,2)), 
                (tabs[2], self.open_habit_tracker, "habit", (2,2,0)), 
                (tabs[3], self.open_journal, "journal", (0,0,2)), 
                (tabs[4], self.open_ranking, "ranking", (2,2,0))
            ]:
                button = toga.Button(
                    val, on_press=func, 
                    style=Pack(flex=0.5, height=button_height, font_size=16, color=self.clrs[2], background_color=self.clrs[1])
                )
                img = toga.ImageView(toga.Image(f"resources/images/menu/{img_path}.png"), style=Pack(flex=0.5, padding=padd))
                chld = [button, img] if padd[0] != 0 else [img, button]
                box = toga.Box(children=chld, style=Pack(direction=ROW, flex=0.2))
                boxes.append(box)

                self.reg([button])

            self.widgets_dict["menu box"] = toga.Box(
                children=boxes, 
                style=Pack(direction=COLUMN, background_color=self.clrs[0])
            )
            
            self.reg([self.widgets_dict["menu box"]])
        
        # coin flip
        if coin_flip:
            coin = CoinFlip(self)
            self.coin_box = coin.get_coin_box()
            
            self.setup_coin = False 

        # todo
        if todo:
            db_path = self.data_dir / "todo.db"
            self.todo = ToDo(self, db_path)
            self.todo_box, self.todo_history_box, self.todo_add_edit_box = self.todo.setup_todo()
            
            self.setup_todo = False

        # habits
        if habits:
            db_path = self.data_dir / "habit.db"
            img_path = self.cache_dir / "calendar_img.png"
            self.habits = Habits(self, db_path, img_path)
            self.habit_tracker_box, self.habit_details_box, self.add_habit_box, self.habit_more_box = self.habits.setup_habits()
            
            self.setup_habits = False

        # journal
        if journal:
            db_path = self.data_dir / "journal.db"
            self.journal = Journal(self, db_path)
            self.journal_box, self.journal_entries_box, self.journal_notes_box, self.journal_notes_add_box, self.journal_notes_edit_box = self.journal.setup_journal()
            
            self.setup_journal = False

        # rankings
        if rankings:
            db_path = self.data_dir / "ranking.db"
            self.rankings = Rankings(self, db_path)
            self.ranking_box, self.ranking_sort_box, self.ranking_add_edit_box, self.ranking_search_box = self.rankings.setup_rankings()
            
            self.setup_rankings = False

        # settings
        if settings:
            def get_label(txt):
                return toga.Label(
                    txt, 
                    style=Pack(padding=(14,20,0), text_align="center", font_weight="bold", font_size=18, color=self.clrs[2])
            )
            
            def get_button(txt, func, h=100):
                return toga.Button(
                    txt, on_press=func, 
                    style=Pack(height=h, padding=4, font_size=12, color=self.clrs[2], background_color=self.clrs[1])
            )
            

            tab_widgets = {}

            reset_str = self.strings["app"]["reset_db_label"]

            ## todo
            async def reset_todo_dialog(widget):
                self.setup_ui(todo=self.setup_todo)
                await self.todo.reset_todo_dialog()

            todo_label = get_label(tabs[1])
            reset_todo_button = get_button(reset_str, reset_todo_dialog)
            
            tab_widgets["todo"] = [todo_label, self.get_div((14,0)), reset_todo_button]

            ## habits
            async def reset_habit_records_dialog(widget):
                self.setup_ui(habits=self.setup_habits)
                await self.habits.reset_habit_records_dialog()

            async def add_last_week_records_dialog(widget):
                self.setup_ui(habits=self.setup_habits)
                await self.habits.add_last_week_records_dialog()

            async def remove_habit_by_id(widget):
                self.setup_ui(habits=self.setup_habits)

                if id := self.widgets_dict["settings habit_id input"].value:
                    answer = await self.app.dialog(
                        toga.QuestionDialog(self.strings["common"]["confirmation"], self.strings["habit"]["remove_habit_question"])
                    )
                    if answer:
                        await self.habits.remove_habit_by_id(int(id))

            async def reset_habit_dialog(widget):
                self.setup_ui(habits=self.setup_habits)
                await self.habits.reset_habit_dialog()


            habit_label = get_label(tabs[2])
            reset_today_habit_records_button = get_button(self.strings["habit"]["reset_today_records"], reset_habit_records_dialog)
            add_last_week_records_button = get_button(self.strings["habit"]["add_last_week_records"], add_last_week_records_dialog)

            habit_remove_label = toga.Label(
                "ID:", 
                style=Pack(padding=(10,20), font_size=16, color=self.clrs[2])
            )
            self.widgets_dict["settings habit_id input"] = toga.NumberInput(
                min=1, step=1, 
                style=Pack(flex=0.85, padding=(4,18,0), height=44, font_size=12, color=self.clrs[2], background_color=self.clrs[1])
            )
            habit_remove_chld = [habit_remove_label, self.widgets_dict["settings habit_id input"]]
            habit_remove_box = toga.Box(
                children=habit_remove_chld, 
                style=Pack(direction=ROW)
            )
            remove_habit_button = get_button(self.strings["common"]["remove"], remove_habit_by_id)

            reset_habit_button = get_button(reset_str, reset_habit_dialog)
            
            tab_widgets["habits"] = [
                habit_label, self.get_div((14,0)), 
                reset_today_habit_records_button, self.get_div((14,0)), 
                add_last_week_records_button, self.get_div((14,0)), 
                habit_remove_box, remove_habit_button, self.get_div((14,0)),
                reset_habit_button
            ]

            self.reg(habit_remove_chld)

            ## journal
            async def remove_journal_entry_dialog(widget):
                self.setup_ui(journal=self.setup_journal)
                await self.journal.remove_entry_dialog(self.widgets_dict["settings journal_remove date"].value)

            async def reset_journal_dialog(widget):
                self.setup_ui(journal=self.setup_journal)
                await self.journal.reset_journal_dialog()


            journal_label = get_label(tabs[3])
            
            journal_remove_date_label = toga.Label(
                f"{self.strings['common']['date']}:", 
                style=Pack(padding=(10,20), font_size=16, color=self.clrs[2])
            )
            self.widgets_dict["settings journal_remove date"] = journal_remove_date = toga.DateInput(
                min=date(2024, 7, 15),
                max=self.today,
                style=Pack(padding=(0,20), width=200, color=self.clrs[2])
            )
            journal_remove_chld = [journal_remove_date_label, journal_remove_date]

            journal_remove_date_box = toga.Box(
                children=journal_remove_chld, 
                style=Pack(direction=ROW)
            )
            journal_remove_button = get_button(self.strings["journal"]["remove_journal_entry"], remove_journal_entry_dialog)

            reset_journal_button = get_button(reset_str, reset_journal_dialog)
            
            tab_widgets["journal"] = [
                journal_label, self.get_div((14,0)), 
                journal_remove_date_box, journal_remove_button, self.get_div((14,0)), 
                reset_journal_button
            ]

            self.reg(journal_remove_chld)

            ## ranking
            async def reset_ranking_dialog(widget):
                self.setup_ui(rankings=self.setup_rankings)
                await self.rankings.reset_ranking_dialog()

            ranking_label = get_label(tabs[4])
            
            category_label = toga.Label(
                f"{self.strings['ranking']['category']}:", 
                style=Pack(padding=(6,18,0), font_size=16, color=self.clrs[2])
            )
            category_selection = toga.Selection(
                items=self.strings["ranking"]["categories"],
                style=Pack(padding=(0,18), height=44, flex=0.8)
            )
            category_box = toga.Box(
                children=[category_label, category_selection],
                style=Pack(direction=ROW)
            )
            tags = []
            for i in range(2):
                tags.append(
                    toga.TextInput(
                        placeholder=self.strings["ranking"]["replace_tag_input_placeholders"][i],
                        style=Pack(padding=(0,18,0), height=44, font_size=12, color=self.clrs[2], background_color=self.clrs[1])
                    )
                )
            
            async def ranking_replace_tag_check(widget):
                if old := tags[0].value.strip():
                    old = titlecase(old)
                    new = tags[1].value.strip()
                    new = titlecase(new) if new else None
                    if "," in old or (new and "," in new):
                        await self.dialog(toga.InfoDialog(self.strings["common"]["error"], self.strings["ranking"]["replace_tag_error"]))
                    else:
                        tags[0].value = tags[1].value = ""

                        self.setup_ui(rankings=self.setup_rankings)
                        await self.rankings.replace_entries_tag_dialog(category_selection, old, new)

            replace_tag_button = get_button(self.strings["ranking"]["replace_tag"], ranking_replace_tag_check)
            
            reset_ranking_button = get_button(reset_str, reset_ranking_dialog)
            
            tab_widgets["rankings"] = [
                ranking_label, self.get_div((14,0)), 
                category_box, tags[0], tags[1], replace_tag_button, self.get_div((14,0)), 
                reset_ranking_button
            ]

            ## general
            general_label = get_label(self.strings["app"]["general"])
            
            gen_boxes = []
            for t in ("theme", "language"):
                label = toga.Label(
                    f"{self.strings['app'][t]}:", 
                    style=Pack(padding=(6,18,0), font_size=16, color=self.clrs[2])
                )
                if t == "theme":
                    items = [self.maps["system_to_localized"][theme] for theme in sorted(self.themes.keys())]
                    value = self.maps["system_to_localized"][self.settings["theme"]]
                else: 
                    items = self.languages
                    value = self.settings["language"]
                self.widgets_dict[f"settings {t} selection"] = toga.Selection(
                    items=items,
                    value=value,
                    style=Pack(padding=(0,18), height=44, flex=0.8)
                )
                chld = [label, self.widgets_dict[f"settings {t} selection"]]
                a_box = toga.Box(
                    children=chld,
                    style=Pack(direction=ROW)
                )
                gen_boxes.append(a_box)

                self.reg(chld)
            theme_button = get_button(self.strings["app"]["apply_theme"], self.change_theme)
            language_button = get_button(self.strings["app"]["change_language"], self.change_language)

            ### dbs
            backup_databases_button = get_button(self.strings["app"]["backup_databases"], self.backup_databases)
            restore_databases_button = get_button(self.strings["app"]["restore_databases"], self.restore_databases)
            
            tab_widgets["general"] = [
                general_label, self.get_div((14,0)), 
                gen_boxes[0], theme_button, self.get_div((14,0)),
                gen_boxes[1], language_button, self.get_div((14,0)), 
                backup_databases_button, restore_databases_button
            ] 
            
            
            def open_settings_tab(widget):
                t = self.settings_tabs[widget.text]
                self.widgets_dict["settings container"].content = self.widgets_dict[f"settings {t} box"]
                self.enable_commands()

            self.settings_tabs = dict()
            temp = []
            settings_buttons = []
            new_tabs = tabs[-1:] + tabs[1:-1]
            system_tabs = ["general", "todo", "habits", "journal", "rankings"]
            for i in range(len(new_tabs)):
                settings_tab = new_tabs[i]
                t = system_tabs[i]
                self.widgets_dict[f"settings {t} box"] = toga.Box(children=tab_widgets[t], style=Pack(direction=COLUMN, background_color=self.clrs[0]))
                button = get_button(settings_tab, open_settings_tab, 120)
                if t == "general":
                    button.style.padding_top = 18
                settings_buttons.append(button)
                if t != "rankings":
                    div = self.get_div((14,0))
                    settings_buttons.append(div) 

                temp.extend([self.widgets_dict[f"settings {t} box"]] + tab_widgets[t])

                self.settings_tabs[settings_tab] = t

            self.widgets_dict["settings box"] = toga.Box(children=settings_buttons, style=Pack(direction=COLUMN, background_color=self.clrs[0]))
            self.widgets_dict["settings container"] = toga.ScrollContainer(content=self.widgets_dict["settings box"], horizontal=False)

            self.setup_settings = False

            self.reg(temp + settings_buttons + [
                self.widgets_dict["settings box"], category_label, journal_remove_date, journal_remove_date_label
            ])


    async def day_change(self):
        if self.today != date.today():
            self.today = date.today()

            if not self.setup_todo:
                self.todo.update_todo(True)
            if not self.setup_habits:
                self.habits.update_habit(True, details=False, tracking=False)
            if not self.setup_journal:
                self.journal.update_journal(True)
            if not self.setup_settings:
                self.widgets["settings journal_remove date"].max = self.today

            await self.app.dialog(toga.InfoDialog(self.strings["app"]["day_change"], self.strings["app"]["day_change_success"]))
            
    
    def day_change_sync_wrapper(self):
        asyncio.run(self.day_change())


    def run_scheduler(self):
        while True:
            schedule.run_pending()
            time.sleep(1)


    def build_toolbar(self, commands: list=[]):
        self.main_window.toolbar.clear()
        for c in commands:
            c[0].enabled = c[1]
            self.main_window.toolbar.add(c[0])


    def enable_commands(self, disable: list=[]):
        for c in self.commands:
            c.enabled = True if c not in disable else False


    def open_coin(self, widget):
        self.setup_ui(coin_flip=self.setup_coin)

        self.main_window.content = self.coin_box
        self.build_toolbar([(self.menu_command, True)])


    def open_todo(self, widget, tab=None):
        tab = tab or self.strings["todo"]["types"][0]

        self.setup_ui(todo=self.setup_todo)

        self.todo_box.current_tab = tab
        self.main_window.content = self.todo_box
        self.enable_commands([self.todo_command])
        self.build_toolbar([(self.menu_command, True), (self.task_history_command, True), (self.add_task_command, True)])
    

    def open_task_history(self, widget, tab=None):
        tab = tab or self.strings["todo"]["tiers"][0]

        self.setup_ui(todo=self.setup_todo)

        if self.todo.task_history_load:
            self.todo.load_tasks(tiers=list(self.todo.task_history_load))
            self.todo.task_history_load.clear()

        self.todo_history_box.current_tab = tab
        self.main_window.content = self.todo_history_box
        self.enable_commands()
        self.build_toolbar([(self.menu_command, True), (self.todo_command, True)])

    
    def open_add_task(self, widget): 
        self.setup_ui(todo=self.setup_todo)

        self.todo.set_tab_on("add")
        self.main_window.content = self.todo_add_edit_box
        self.enable_commands()
        self.build_toolbar([(self.menu_command, True), (self.todo_command, True), (self.add_task_command, False)])


    async def open_edit_task(self):
        self.todo.set_tab_on("edit")
        self.main_window.content = self.todo_add_edit_box
        self.enable_commands()
        self.build_toolbar([(self.menu_command, True), (self.todo_command, True), (self.add_task_command, False)])


    def open_habit_tracker(self, widget):
        self.setup_ui(habits=self.setup_habits)

        self.habits.prepare_tracker_container()
        self.main_window.content = self.habit_tracker_box

        self.enable_commands()
        self.build_toolbar([(self.menu_command, True), (self.habit_details_command, True), (self.habit_manage_command, True)])


    def open_habit_details(self, widget):
        self.setup_ui(habits=self.setup_habits)
        
        if self.habits.details_setup:
            self.habits.habit_get_data(details=True)
            self.habits.load_habits(None, tracker=False, details=True)
            self.habits.details_setup = False
        self.habits.prepare_details_containers()
        self.habit_details_box.current_tab = self.strings["habit"]["tracked"]
        self.main_window.content = self.habit_details_box

        self.enable_commands()
        self.build_toolbar([(self.menu_command, True), (self.habit_tracker_command, True), (self.habit_manage_command, True)])


    def open_add_habit(self, widget):
        self.setup_ui(habits=self.setup_habits)

        self.habits.clear_add_habit()

        self.main_window.content = self.add_habit_box
        self.enable_commands()
        self.build_toolbar([(self.menu_command, True), (self.habit_tracker_command, True), (self.habit_details_command, True)])

    
    def open_habit_more(self, habit_id):
        self.habit_more_box.position = toga.Position(0,0)
        self.main_window.content = self.habit_more_box

        self.habits.load_habit_more(habit_id)

        self.enable_commands()
        self.build_toolbar([(self.menu_command, True), (self.habit_tracker_command, True), (self.habit_details_command, True)])


    def open_journal(self, widget):
        self.setup_ui(journal=self.setup_journal)

        self.main_window.content = self.journal_box
        self.build_toolbar([(self.menu_command, True)])


    def open_journal_entries(self, widget):
        self.main_window.content = self.journal_entries_box
        self.build_toolbar([(self.menu_command, True), (self.journal_command, True)])


    def open_journal_notes(self, widget):
        self.setup_ui(journal=self.setup_journal)

        self.journal.prepare_notes_container()
        self.main_window.content = self.journal_notes_box

        self.build_toolbar([(self.menu_command, True), (self.journal_command, True), (self.add_note_command, True)])


    def open_add_note(self, widget):
        self.setup_ui(journal=self.setup_journal)

        self.journal.clear_note_add_box()

        self.main_window.content = self.journal_notes_add_box
        self.build_toolbar([(self.menu_command, True), (self.notes_command, True), (self.add_note_command, False)])


    def open_edit_note(self, widget):
        self.setup_ui(journal=self.setup_journal)

        id = int(widget.id.split()[0])
        
        self.journal.load_edit_note_box(id)

        self.main_window.content = self.journal_notes_edit_box
        self.build_toolbar([(self.menu_command, True), (self.notes_command, True)])

    
    def open_ranking(self, widget, tab=None):
        tab = tab or self.strings["ranking"]["categories"][0]

        self.setup_ui(rankings=self.setup_rankings)
        
        if self.main_window.content in [self.ranking_search_box, self.ranking_add_edit_box, self.ranking_sort_box]:
            tab = self.rankings.widgets_dict["category selection"].value
            
        self.ranking_box.current_tab = tab
        self.main_window.content = self.ranking_box
        self.enable_commands([self.ranking_command])
        self.build_toolbar([(self.menu_command, True), (self.ranking_search_command, True), (self.ranking_add_command, True)])

    
    def open_ranking_sort(self, widget):
        self.setup_ui(rankings=self.setup_rankings)

        category = self.ranking_box.current_tab.text

        self.rankings.set_tab_on("sort", category=category)

        self.main_window.content = self.ranking_sort_box
        self.build_toolbar([(self.menu_command, True), (self.ranking_command, True)])

    
    def open_ranking_add_entry(self, widget):
        self.setup_ui(rankings=self.setup_rankings)
        
        category = None  
        if self.main_window.content == self.ranking_box:
            category = self.ranking_box.current_tab.text

        self.rankings.set_tab_on("add", category=category)

        self.main_window.content = self.ranking_add_edit_box
        self.enable_commands([self.ranking_add_command])
        self.build_toolbar([(self.menu_command, True), (self.ranking_command, True), (self.ranking_search_command, True)])

    
    def open_ranking_search(self, widget):
        self.setup_ui(rankings=self.setup_rankings)

        category = None  
        if self.main_window.content == self.ranking_box:
            category = self.ranking_box.current_tab.text

        self.rankings.set_tab_on("search", category=category)

        self.main_window.content = self.ranking_search_box
        self.enable_commands([self.ranking_search_command])
        self.build_toolbar([(self.menu_command, True), (self.ranking_command, True), (self.ranking_add_command, True)])


    def open_ranking_edit_entry(self, widget):
        self.setup_ui(rankings=self.setup_rankings)

        self.rankings.set_tab_on("edit", widget=widget)

        self.main_window.content = self.ranking_add_edit_box
        self.build_toolbar([(self.menu_command, True), (self.ranking_command, True), (self.ranking_search_command, True)])


    def open_menu(self, widget):
        self.main_window.content = self.widgets_dict["menu box"]
        self.enable_commands()
        self.build_toolbar([(self.menu_command, False), (self.settings_command, True)])


    def open_settings(self, widget):
        self.setup_ui(settings=self.setup_settings)

        self.main_window.content = self.widgets_dict["settings container"]
        self.widgets_dict["settings container"].content = self.widgets_dict["settings box"]
        self.enable_commands()
        self.build_toolbar([(self.menu_command, True), (self.settings_command, False)])   


    async def backup_databases(self, widget):
        result = await self.app.dialog(
            toga.ConfirmDialog(self.strings["common"]["warning"], self.strings["app"]["backup_question"])
        )
        if result:
            from java import jclass
            import sqlite3 as sql

            Environment = jclass("android.os.Environment")
            backup_folder = Path(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS).getAbsolutePath())
            backedup = []

            def backup_database(db_path, backup_path):
                con = sql.connect(db_path)
                with open(backup_path, 'w', encoding='utf-8') as f:
                    for line in con.iterdump():
                        f.write(f"{line}\n")
                con.close()

            db_names = ["todo", "habit", "journal", "ranking"]
            db_paths = [self.data_dir / f"{db}.db" for db in db_names]
            backup_paths = [backup_folder / f"IMRS_{db}.sql" for db in db_names]

            for i in range(len(db_names)):
                backup_database(db_paths[i], backup_paths[i])
                backedup.append(db_names[i])

            backedup = [db+".db" for db in backedup]

            idx = 0 if len(backedup) <= 1 else 1
            await self.app.dialog(toga.InfoDialog(self.strings["common"]["success"], self.strings["app"]["backup_success"][idx].format(dbs=backedup)))

    
    async def restore_databases(self, widget):
        result = await self.app.dialog(toga.ConfirmDialog(self.strings["common"]["warning"], self.strings["app"]["restore_question"]))
        if result:
            from java import jclass
            import sqlite3 as sql

            Environment = jclass("android.os.Environment")
            backup_folder = (self.paths.app / Path(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS).getAbsolutePath()))

            def restore_database(backup_path, db_path):
                with open(backup_path, 'r', encoding='utf-8') as f:
                    sql_script = f.read()

                if db_path.exists() and db_path.is_file():
                    db_path.unlink()

                con = sql.connect(db_path)

                try:
                    con.executescript(sql_script)
                    print("Database restored successfully!")
                except Exception as e:
                    print(f"Error restoring database: {e}")
                
                con.close()

            db_names = ["todo", "habit", "journal", "ranking"]
            db_paths = [self.data_dir / f"{db}.db" for db in db_names]
            backup_paths = [backup_folder / f"IMRS_{db}.sql" for db in db_names]

            restored = []

            for i in range(len(db_names)):
                if backup_paths[i].exists():
                    restore_database(backup_paths[i], db_paths[i])
                    restored.append(db_names[i])

            restored = [db+".db" for db in restored]

            self.setup_todo = "todo.db" in restored
            self.setup_habits = "habit.db" in restored 
            self.setup_journal = "journal.db" in restored
            self.setup_rankings = "ranking.db" in restored

            idx = 0 if len(restored) <= 1 else 1
            await self.app.dialog(toga.InfoDialog(self.strings["common"]["success"], self.strings["app"]["backup_success"][idx].format(dbs=restored)))


    def change_theme(self, widget):
        new_theme = self.maps["localized_to_system"][self.widgets_dict["settings theme selection"].value]
        if new_theme != self.settings["theme"]:
            self.settings["theme"] = new_theme
            self.clrs = self.themes[self.settings["theme"]]
            for i in range(3):
                for w in tuple(self.widgets_dict["theme change"][i]):
                    if i != 2: 
                        w.style.background_color = self.clrs[i]
                    else:
                        w.style.color = self.clrs[i]

            self.save_settings(self.settings)


    def reg(self, widgets=[]):
        for w in widgets:
            if not isinstance(w, str):
                if isinstance(w, toga.Box):
                    self.widgets_dict["theme change"][0].add(w)
                elif not isinstance(w, (toga.OptionContainer, toga.ScrollContainer, toga.Selection)):
                    if not isinstance(w, toga.Divider):
                        self.widgets_dict["theme change"][2].add(w)
                    if isinstance(w, (toga.Button, toga.Divider, toga.TextInput, toga.MultilineTextInput, toga.NumberInput)):
                        self.widgets_dict["theme change"][1].add(w)


    def save_settings(self, settings: dict):
        with open(self.settings_path, "w") as f:
            json.dump(settings, f, indent=4)


    def get_div(self, padding=0):
        return toga.Divider(style=Pack(padding=padding, background_color=self.clrs[1]))
    
    
    def change_language(self, widget):
        new_lang = self.widgets_dict["settings language selection"].value
        if new_lang != self.settings["language"]:
            self.settings["language"] = new_lang
            
            self.save_settings(self.settings)

            self.startup(manual=True)


    def load_strings(self):
        lang = language_to_alpha3[self.settings["language"]]
        with open(self.paths.app / f"resources/languages/{lang}.json") as f:
            self.strings = json.load(f)


def main():
    return Imerisios()