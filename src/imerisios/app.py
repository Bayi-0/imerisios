"""
A versatile app for everyday use.
"""
import toga
from toga.style import Pack
from toga.constants import COLUMN, ROW
from datetime import date
import os
import shutil
import threading
import time
import schedule
import asyncio
from imerisios.mylib.coin import CoinFlip
from imerisios.mylib.todo import ToDo
from imerisios.mylib.habit import Habits
from imerisios.mylib.journal import Journal
from imerisios.mylib.ranking import Rankings


class Imerisios(toga.App):
    def startup(self):
        # app directory
        self.app_dir = self.paths.data
        if not os.path.exists(self.app_dir):
            os.makedirs(self.app_dir)
            
        # today date 
        self.today = date.today()

        self.setup_settings = True
        self.setup_todo = True
        self.setup_habits = True
        self.setup_journal = True
        self.setup_rankings = True

        # menu
        self.setup_ui(menu=True, coin_flip=True)
        
        # commands
        menu_group = toga.Group("0 Menu")
        self.menu_command = toga.Command(self.open_menu, text="Menu", group=menu_group, enabled=False)

        settings_group = toga.Group("1 Settings")
        self.settings_command = toga.Command(self.open_settings, text="Settings", group=settings_group)

        todo_group = toga.Group("2 To-do functions")
        self.todo_command = toga.Command(self.open_todo, text="To-do", group=todo_group)
        self.add_task_command = toga.Command(self.open_add_task, text="Add", group=todo_group)
        self.task_history_command = toga.Command(self.open_task_history, text="History", group=todo_group)

        habit_group = toga.Group("3 Habits functions")
        self.habit_tracker_command = toga.Command(self.open_habit_tracker, text="Tracker", group=habit_group)
        self.habit_details_command = toga.Command(self.open_habit_details, text="Details", group=habit_group)
        self.habit_manage_command = toga.Command(self.open_add_habit, text="Add", group=habit_group)

        journal_group = toga.Group("4 Journal functions")
        self.journal_command = toga.Command(self.open_journal, text="Journal", group=journal_group)
        self.notes_command = toga.Command(self.open_journal_notes, text="Notes", group=journal_group)
        self.add_note_command = toga.Command(self.open_add_note, text="Add", group=journal_group)

        ranking_group = toga.Group("5 Rankings functions")
        self.ranking_command = toga.Command(self.open_ranking, text="Rankings", group=ranking_group)
        self.ranking_add_command = toga.Command(self.open_ranking_add_entry, text="Add", group=ranking_group)
        self.ranking_search_command = toga.Command(self.open_ranking_search, text="Search", group=ranking_group)

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
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = self.menu_box
        self.main_window.toolbar.add(self.menu_command, self.settings_command)
        self.main_window.show()

        # scheduler 
        schedule.every().minute.do(self.day_change_sync_wrapper)
        
        scheduler_thread = threading.Thread(target=self.run_scheduler)
        scheduler_thread.daemon = True
        scheduler_thread.start()


    def setup_ui(self, menu=False, settings=False, coin_flip=False, todo=False, habits=False, journal=False, rankings=False):
        # menu
        if menu:
            coin_button = toga.Button(
                "Coin flip", on_press=self.open_coin, 
                style=Pack(flex=0.5, height=154, font_size=24, color="#EBF6F7", background_color="#27221F"))
            todo_button = toga.Button(
                "To-do", on_press=self.open_todo, 
                style=Pack(flex=0.5, height=154, font_size=24, color="#EBF6F7", background_color="#27221F"))
            habit_button = toga.Button(
                "Habits", on_press=self.open_habit_tracker, 
                style=Pack(flex=0.5, height=154, font_size=24, color="#EBF6F7", background_color="#27221F"))
            journal_button = toga.Button(
                "Journal", on_press=self.open_journal, 
                style=Pack(flex=0.5, height=154, font_size=24, color="#EBF6F7", background_color="#27221F"))
            ranking_button = toga.Button(
                "Rankings", on_press=self.open_ranking, 
                style=Pack(flex=0.5, height=154, font_size=24, color="#EBF6F7", background_color="#27221F"))
            
            coin_image = toga.ImageView(toga.Image("resources/menu/coin.png"), style=Pack(flex=0.5, padding=(2,0,0)))
            todo_image = toga.ImageView(toga.Image("resources/menu/todo.png"), style=Pack(flex=0.5, padding=(0,0,2)))
            habit_image = toga.ImageView(toga.Image("resources/menu/habit.png"), style=Pack(flex=0.5, padding=(2,2,0)))
            journal_image = toga.ImageView(toga.Image("resources/menu/journal.png"), style=Pack(flex=0.5, padding=(0,0,2)))
            ranking_image = toga.ImageView(toga.Image("resources/menu/ranking.png"), style=Pack(flex=0.5, padding=(2,2,0)))

            coin_box = toga.Box(children=[coin_button, coin_image], style=Pack(direction=ROW, flex=0.2))
            todo_box = toga.Box(children=[todo_image, todo_button], style=Pack(direction=ROW, flex=0.2))
            habit_box = toga.Box(children=[habit_button, habit_image], style=Pack(direction=ROW, flex=0.2))
            journal_box = toga.Box(children=[journal_image, journal_button], style=Pack(direction=ROW, flex=0.2))
            ranking_box = toga.Box(children=[ranking_button, ranking_image], style=Pack(direction=ROW, flex=0.2))

            self.menu_box = toga.Box(
                children=[coin_box, todo_box, habit_box, journal_box, ranking_box], 
                style=Pack(direction=COLUMN, background_color="#393432"))
        
        # coin flip
        if coin_flip:
            coin = CoinFlip(self)
            self.coin_box = coin.get_coin_box()

        # todo
        if todo:
            db_path = os.path.join(self.app_dir, "todo.db")
            self.todo = ToDo(self, db_path)
            self.todo_box, self.todo_history_box, self.todo_add_box, self.todo_edit_box = self.todo.setup_todo()
            
            self.setup_todo = False

        # habits
        if habits:
            db_path = os.path.join(self.app_dir, "habit.db")
            img_path = os.path.join(self.app_dir, "calendar_img.png")
            self.habits = Habits(self, db_path, img_path)
            self.habit_tracker_box, self.habit_details_box, self.add_habit_box, self.habit_more_box = self.habits.setup_habits()
            
            self.setup_habits = False

        # journal
        if journal:
            db_path = os.path.join(self.app_dir, "journal.db")
            self.journal = Journal(self, db_path)
            self.journal_box, self.journal_entries_box, self.journal_notes_box, self.journal_notes_add_box, self.journal_notes_edit_box = self.journal.setup_journal()
            
            self.setup_journal = False

        # rankings
        if rankings:
            db_path = os.path.join(self.app_dir, "ranking.db")
            self.rankings = Rankings(self, db_path)
            self.ranking_box, self.ranking_sort_box, self.ranking_add_box, self.ranking_search_box, self.ranking_edit_box = self.rankings.setup_rankings()
            
            self.setup_rankings = False

        # settings
        if settings:
            self.setup_ui(todo=self.setup_todo, habits=self.setup_habits, journal=self.setup_journal, rankings=self.setup_rankings)

            reset_todo_button = toga.Button(
                "Reset todo database", on_press=self.todo.reset_todo_dialog, 
                style=Pack(height=120, padding=4, font_size=16, color="#EBF6F7", background_color="#27221F"))
            reset_habit_button = toga.Button(
                "Reset habit database", on_press=self.habits.reset_habit_dialog, 
                style=Pack(height=120, padding=4, font_size=16, color="#EBF6F7", background_color="#27221F"))
            reset_today_habit_records_button = toga.Button(
                "Reset today's habit records", on_press=self.habits.reset_today_habit_records, 
                style=Pack(height=120, padding=4, font_size=16, color="#EBF6F7", background_color="#27221F"))
            reset_journal_button = toga.Button(
                "Reset journal database", on_press=self.journal.reset_journal_dialog, 
                style=Pack(height=120, padding=4, font_size=16, color="#EBF6F7", background_color="#27221F"))
            reset_ranking_button = toga.Button(
                "Reset ranking database", on_press=self.rankings.reset_ranking_dialog, 
                style=Pack(height=120, padding=4, font_size=16, color="#EBF6F7", background_color="#27221F"))
            backup_databases_button = toga.Button(
                "Back up databases", on_press=self.backup_databases, 
                style=Pack(height=120, padding=4, font_size=16, color="#EBF6F7", background_color="#27221F"))
            restore_databases_button = toga.Button(
                "Restore databases", on_press=self.restore_databases, 
                style=Pack(height=120, padding=4, font_size=16, color="#EBF6F7", background_color="#27221F"))
            box = toga.Box(
                children=[
                    reset_todo_button, toga.Divider(style=Pack(padding=(0,80), background_color="#27221F")),
                    reset_habit_button, reset_today_habit_records_button, toga.Divider(style=Pack(padding=(0,80), background_color="#27221F")),
                    reset_journal_button, toga.Divider(style=Pack(padding=(0,80), background_color="#27221F")),
                    reset_ranking_button, toga.Divider(style=Pack(padding=(0,80), background_color="#27221F")),
                    backup_databases_button, restore_databases_button
                ], 
                style=Pack(direction=COLUMN, background_color="#393432"))
            self.settings_box = toga.ScrollContainer(content=box)
            
            self.setup_settings = False


    async def day_change(self):
        if self.today != date.today():
            self.today = date.today()
            self.todo.update_todo()
            self.habits.update_habit(details=False, tracking=False)
            self.journal.update_journal()

            await self.app.dialog(toga.InfoDialog("Day Change", "Everything related to day change has been updated successfully. You may need to relaunch the app."))
            
    
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
        self.main_window.content = self.coin_box
        self.build_toolbar([(self.menu_command, True)])


    def open_todo(self, widget, tab: str="Daily"):
        self.setup_ui(todo=self.setup_todo)

        self.todo_box.current_tab = tab
        self.main_window.content = self.todo_box
        self.enable_commands([self.todo_command])
        self.build_toolbar([(self.menu_command, True), (self.task_history_command, True), (self.add_task_command, True)])
    

    def open_task_history(self, widget, tab: str="Routine"):
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

        self.todo.clear_add_box()
        self.main_window.content = self.todo_add_box
        self.enable_commands()
        self.build_toolbar([(self.menu_command, True), (self.todo_command, True), (self.add_task_command, False)])


    async def open_edit_task(self):
        self.todo.load_edit_box()
        self.main_window.content = self.todo_edit_box
        self.enable_commands()
        self.build_toolbar([(self.menu_command, True), (self.todo_command, True), (self.add_task_command, False)])


    def open_habit_tracker(self, widget):
        self.setup_ui(habits=self.setup_habits)

        self.habits.habit_tracker_list_container.position = toga.Position(0,0)
        self.main_window.content = self.habit_tracker_box

        self.enable_commands()
        self.build_toolbar([(self.menu_command, True), (self.habit_details_command, True), (self.habit_manage_command, True)])


    def open_habit_details(self, widget):
        self.setup_ui(habits=self.setup_habits)
        
        self.habits.habit_details_list_container.position = toga.Position(0,0)
        self.main_window.content = self.habit_details_box

        self.enable_commands()
        self.build_toolbar([(self.menu_command, True), (self.habit_tracker_command, True), (self.habit_manage_command, True)])


    def open_add_habit(self, widget):
        self.setup_ui(habits=self.setup_habits)

        self.habits.clear_add_habit()

        self.main_window.content = self.add_habit_box
        self.enable_commands()
        self.build_toolbar([(self.menu_command, True), (self.habit_tracker_command, True), (self.habit_details_command, True)])

    
    def open_habit_more(self, widget):
        habit_id = int(widget.id.split()[0])

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

        self.journal.journal_notes_list_container.position = toga.Position(0,0)
        self.main_window.content = self.journal_notes_box

        self.build_toolbar([(self.menu_command, True), (self.journal_command, True), (self.add_note_command, True)])


    def open_add_note(self, widget):
        self.setup_ui(journal=self.setup_journal)

        self.main_window.content = self.journal_notes_add_box
        self.build_toolbar([(self.menu_command, True), (self.notes_command, True), (self.add_note_command, False)])


    def open_edit_note(self, widget):
        self.setup_ui(journal=self.setup_journal)

        id = int(widget.id.split()[0])
        
        self.journal.load_edit_note_box(id)

        self.main_window.content = self.journal_notes_edit_box
        self.build_toolbar([(self.menu_command, True), (self.notes_command, True)])

    
    def open_ranking(self, widget, tab: str="Book"):
        self.setup_ui(rankings=self.setup_rankings)

        self.ranking_box.current_tab = tab
        self.main_window.content = self.ranking_box
        self.enable_commands([self.ranking_command])
        self.build_toolbar([(self.menu_command, True), (self.ranking_search_command, True), (self.ranking_add_command, True)])

    
    def open_ranking_sort(self, widget):
        self.setup_ui(rankings=self.setup_rankings)

        self.rankings.sort_filter_container.position = toga.Position(0,0)
        self.rankings.type_change_check = True
        self.rankings.sort_type.value = self.ranking_box.current_tab.text
        if self.rankings.type_change_check:
            self.rankings.type_change(self.rankings.sort_type)

        self.main_window.content = self.ranking_sort_box
        self.build_toolbar([(self.menu_command, True), (self.ranking_command, True)])

    
    def open_ranking_add_entry(self, widget):
        self.setup_ui(rankings=self.setup_rankings)
        
        self.rankings.add_entry_container.position = toga.Position(0,0)
        self.rankings.type_change_check = True
        self.rankings.add_type.value = self.ranking_box.current_tab.text
        if self.rankings.type_change_check:
            self.rankings.type_change(self.rankings.add_type)
        self.rankings.clear_add_box()

        self.main_window.content = self.ranking_add_box
        self.enable_commands([self.ranking_add_command])
        self.build_toolbar([(self.menu_command, True), (self.ranking_command, True)])

    
    def open_ranking_search(self, widget):
        self.setup_ui(rankings=self.setup_rankings)

        self.rankings.type_change_check = True
        self.rankings.search_type.value = self.ranking_box.current_tab.text
        if self.rankings.type_change_check:
            self.rankings.type_change(self.rankings.search_type)

        self.main_window.content = self.ranking_search_box
        self.enable_commands([self.ranking_search_command])
        self.build_toolbar([(self.menu_command, True), (self.ranking_command, True), (self.ranking_add_command, True)])


    def open_ranking_edit_entry(self, widget):
        self.setup_ui(rankings=self.setup_rankings)

        self.rankings.edit_entry_container.position = toga.Position(0,0)
        self.rankings.type_change_check = True
        self.rankings.edit_type.value = self.rankings.search_type.value
        if self.rankings.type_change_check:
            self.rankings.type_change(self.rankings.edit_type)

        self.rankings.load_edit_box(widget)

        self.main_window.content = self.ranking_edit_box
        self.build_toolbar([(self.menu_command, True), (self.ranking_command, True), (self.ranking_search_command, True)])


    def open_menu(self, widget):
        self.main_window.content = self.menu_box
        self.enable_commands()
        self.build_toolbar([(self.menu_command, False), (self.settings_command, True)])


    def open_settings(self, widget):
        self.setup_ui(settings=self.setup_settings)

        self.main_window.content = self.settings_box
        self.enable_commands()
        self.build_toolbar([(self.menu_command, True), (self.settings_command, False)])   


    async def backup_databases(self, widget):
        result = await self.app.dialog(toga.ConfirmDialog("Warning", "All Imerisios databases (that have the same name as when were backed up) in your device's Downloads folder will be rewritten. Proceed?"))
        if result:
            from java import jclass
            import sqlite3 as sql

            Environment = jclass("android.os.Environment")
            backup_folder = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS).getAbsolutePath()

            def backup_database(db_path, backup_path):
                con = sql.connect(db_path)
                with open(backup_path, 'w') as f:
                    for line in con.iterdump():
                        f.write('%s\n' % line)
                con.close()

            db_names = ["todo", "habit", "journal", "ranking"]
            db_paths = [os.path.join(self.app_dir, db+".db") for db in db_names]
            backup_paths = [os.path.join(backup_folder, "IMRS_"+db+".sql") for db in db_names]

            for i in range(len(db_names)):
                backup_database(db_paths[i], backup_paths[i])

            await self.app.dialog(toga.InfoDialog("Success", f"The databases were successfully backed up to {backup_folder}"))

    
    async def restore_databases(self, widget):
        result = await self.app.dialog(toga.ConfirmDialog("Warning", "All Imerisios databases (that have the same name as when were backed up) in your device's Downloads folder will be restored. Proceed?"))
        if result:
            from java import jclass
            import sqlite3 as sql

            Environment = jclass("android.os.Environment")
            backup_folder = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS).getAbsolutePath()

            def restore_database(backup_path, db_path):
                with open(backup_path, 'r') as f:
                    sql_script = f.read()
                statements = sql_script.split(';')

                if os.path.exists(db_path):
                    os.remove(db_path)
                con = sql.connect(db_path)

                for statement in statements:
                    if statement.strip():
                        try:
                            con.execute(statement)
                        except Exception as e:
                            print(f"Error executing statement: {e}")
                con.close()

            db_names = ["todo", "habit", "journal", "ranking"]
            db_paths = [os.path.join(self.app_dir, db+".db") for db in db_names]
            backup_paths = [os.path.join(backup_folder, "IMRS_"+db+".sql") for db in db_names]

            restored = []

            for i in range(len(db_names)):
                if os.path.exists(backup_paths[i]):
                    restore_database(backup_paths[i], db_paths[i])
                    restored.append(db_names[i])

            restored = [db+".db" for db in restored]

            todo = "todo.db" in restored
            habits = "habit.db" in restored 
            journal = "journal.db" in restored
            rankings = "ranking.db" in restored
            self.setup_ui(todo=todo, habits=habits, journal=journal, rankings=rankings)

            await self.app.dialog(toga.InfoDialog("Success", f"Databases {restored} were successfully restored."))

        
def main():
    return Imerisios()