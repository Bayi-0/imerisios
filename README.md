# Imerisios

## Description

The app provides a versatile set of functionalities including coin flip, to-do list, habit tracking, journaling, and rankings. It features a user-friendly interface with dynamic navigation, allowing users to easily switch between different features and access settings. The app also includes backup and restore capabilities for its databases, ensuring user data is safely managed. 

## Installation

1. **Install Python**: Download and install Python from [python.org](https://www.python.org/downloads/).

2. **Set Up a Virtual Environment**:
    ```bash
    python -m venv myenv
    myenv\Scripts\activate # On Windows
    source myenv/bin/activate # On macOS/Linux
    ```

3. **Install Required Packages**:
    ```bash
    pip install briefcase
    ```

4. **Clone the Repository**:
    ```bash
    git clone https://github.com/yourusername/your-repo.git
    cd your-repo
    ```

5. **Create and Build the App**:
    ```bash
    briefcase create android
    briefcase build android
    ```

6. **Install the APK**:
   After building, you will find the .apk file. You can install it using:
    ```bash
    adb install path/to/your-app.apk
    ```

## Usage

Can be installed and used on Android devices. 

Warning: the app's UI is not flexible and looks bad on most of the screens. Works properly on the following screen: 6.67 inches, 1080 x 2400 pixels, 20:9 ratio (~395 ppi density).

## Functionalities

### app.py

#### Features

##### 1. User Interface and Navigation

- **Main Menu**: A central hub with buttons to access various functionalities like Coin Flip, To-do List, Habit Tracker, and Journal. Each button includes an associated image for intuitive navigation.
- **Dynamic Content Switching**: Allows users to switch between different sections of the app seamlessly, including accessing specific functionalities through a toolbar.

##### 2. Coin Flip

- **Coin Flip Interaction**: Users can flip a virtual coin to get a random outcome of either "Heads" or "Tails." The interaction is handled through the `CoinFlip` class and includes distinct visual elements for each side.

##### 3. To-Do List

- **Task Management**: Users can create, view, and manage tasks. The to-do functionality is managed by the `ToDo` class, providing options to create new tasks, view task history, and edit tasks.
- **Task History**: Allows users to view previously created tasks and manage them efficiently.

##### 4. Habit Tracking

- **Habit Tracker**: Users can track and manage their habits. The `Habits` class handles the habit tracking interface, including setting up habit records, managing details, and tracking progress.
- **Habit Management**: Provides options to add, update, and view details about various habits.

##### 5. Journaling

- **Journal Entries**: Users can create and manage journal entries. The `Journal` class provides functionalities to create, view, and edit journal entries and notes.
- **Notes Management**: Users can add and edit notes within their journal.

##### 6. Rankings

- **Ranking Entries**: Users can create and manage rankings for books, movies, and other media. The `Ranking` class provides functionalities to add, view, update, and remove rankings based on user preferences.
- **Rating System**: Users can assign ratings to each entry, allowing for a clear evaluation of their experiences with different media.
- **Category Management**: Users can categorize rankings by type (e.g., book, movie), enabling easy filtering and organization of their ranked entries.

##### 7. Backup and Restore

- **Database Backup**: Allows users to back up their app databases to the device's Downloads folder. Implemented using Android's file system APIs and SQLite.
- **Database Restore**: Restores databases from the Downloads folder, ensuring user data can be recovered if needed.

#### Implementation Details

##### Key Functions

- **`startup`**: Initializes the app, sets up the UI, and starts the scheduler for periodic updates.
- **`setup_ui`**: Configures the user interface for different functionalities including menu, to-do list, habits, and journal.
- **`day_change`**: Updates the app data based on the change of day, triggering updates for to-do tasks, habits, and journal entries.
- **`run_scheduler`**: Runs the scheduler in a separate thread to handle periodic tasks.
- **`build_toolbar`**: Configures the toolbar with specific commands.
- **`enable_commands`**: Enables or disables specific commands based on the current context.

##### User Interface

- **Menu Box**: Displays buttons for accessing different features with associated images.
- **Settings Box**: Displays buttons for accessing different setting-features.
- **Coin Flip Box**: Shows the coin flip interface with options for "Heads" and "Tails."
- **To-Do List Box**: Includes tabs for daily tasks, task history, and task creation.
- **Habit Tracker Box**: Provides views for tracking habits, managing details, and more.
- **Journal Box**: Displays journal entries and notes with options to create and edit content.
- **Rankings Box**: Provides views for rankings, managing ranking entries, and more.

##### Image Resources

- **Coin Flip Image**: Located at `resources/menu/coin.png`. Created using a public domain image, and Adobe Photoshop.
- **To-Do Image**: Located at `resources/menu/todo.png`. Created using a public domain image, and Adobe Photoshop.
- **Habits Image**: Located at `resources/menu/habit.png`. Created using a public domain image, and Adobe Photoshop.
- **Journal Image**: Located at `resources/menu/journal.png`. Created using a public domain image, and Adobe Photoshop.
- **Rankings Image**: Located at `resources/menu/ranking.png`. Created using a public domain image, and Adobe Photoshop.

This section outlines the core functionalities and implementation details of the app, ensuring users understand how to navigate and use each feature effectively.

### tools.py

#### Overview

The `tools.py` file provides utility functions for managing database connections, creating calendar images, handling widget input length, and working with month name mappings.

#### Features

- **Database Connection Management**: Functions for opening and closing SQLite database connections.
  - **`get_connection`**: Opens a database connection and returns the connection and cursor objects.
  - **`close_connection`**: Closes an existing database connection.

- **Calendar Image Creation**: Function to generate and save a visual calendar image with custom marks.
  - **`create_calendar_image`**: Creates an image of a calendar month, highlighting specific days with custom statuses.

- **Widget Input Length Check**: Function to ensure widget input does not exceed a specified length.
  - **`length_check`**: Truncates widget input and temporarily disables input if the length limit is exceeded.

- **Month Name Dictionaries**: Functions to provide mappings for month names and numbers.
  - **`get_month_dicts`**: Returns dictionaries for converting between month numbers and names.

### coin.py

#### Overview

The Coin Flip feature provides a simple, interactive way to make binary decisions. Users can flip a virtual coin to get a random outcome of either "Heads" or "Tails." The feature includes visually distinct representations for each outcome and integrates motivational quotes to enhance the experience.

#### Features

##### 1. Coin Flip Interaction

- **Heads and Tails Boxes**: Display options for "Heads" and "Tails," each with an image and a question to engage the user.
- **Flip Button**: Allows users to flip the coin, resulting in a random display of either the "Heads" or "Tails" box.

##### 2. Visual and Textual Elements

- **Heads Box**: Contains a title, an image of the heads side of the coin, a motivational question, and a button to flip the coin.
- **Tails Box**: Contains a title, an image of the tails side of the coin, a motivational question, and a button to flip the coin.
- **Quotes**: Displays a set of motivational quotes at the top and bottom of the coin flip interface.

#### Implementation Details

##### Key Functions

- **`get_heads_box`**: Creates and returns the UI components for the "Heads" side of the coin.
- **`get_tails_box`**: Creates and returns the UI components for the "Tails" side of the coin.
- **`get_coin_box`**: Assembles the complete coin flip interface, including motivational quotes and the flip button.
- **`flip_coin`**: Handles the coin flip action, randomly switching between the "Heads" and "Tails" boxes.

##### User Interface

- **Heads Box**: Displays the heads side of the coin with associated imagery and a question.
- **Tails Box**: Displays the tails side of the coin with associated imagery and a question.
- **Flip Button**: Triggers the coin flip, updating the main window content with the result.

##### Image Resources

- **Heads Image**: Located at `resources/coin/heads.png`. Created using an AI image-generator, and Adobe Photoshop.
- **Tails Image**: Located at `resources/coin/tails.png`. Created using an AI image-generator, and Adobe Photoshop.

This feature provides a fun and interactive way to make simple decisions with a visual and textual experience.

### todo.py

#### Overview

The To-Do List feature is an integral part of our application, designed to help users manage their tasks efficiently. It includes a range of functionalities to create, update, complete, and delete tasks. The To-Do List integrates seamlessly with the app's other features to provide a cohesive user experience.

#### Features

##### 1. **Task Management**

- **Create Tasks**: Users can add new tasks by specifying the task name, tier, urgency, type, and due date. Tasks are categorized into different types (`daily`, `weekly`, `monthly`, `yearly`) and tiers (`routine`, `challenging`, `significant`, `momentous`).

- **Update Tasks**: Tasks can be edited to update any of their attributes, including task name, tier, urgency, type, and due date.

- **Complete Tasks**: Users can mark tasks as completed. This updates the task's completion date and moves it to the completed tasks list.

- **Delete Tasks**: Tasks can be permanently deleted from the list.

##### 2. **Task Filtering**

- **Task Types**: Tasks are categorized by type, allowing users to filter tasks based on whether they are daily, weekly, monthly, or yearly.

- **Task Tiers**: Tasks are also categorized by tier, which can be filtered to view tasks of a specific tier or to see completed tasks by tier.

##### 3. **Task View**

- **Pending Tasks**: Users can view pending tasks sorted by due date and urgency. Urgency levels are prioritized to ensure that high-priority tasks are easily identifiable.

- **Completed Tasks**: Completed tasks are displayed separately, sorted by completion date, and provide an overview of finished tasks.

##### 4. **Date Management**

- **Date Ranges**: The app automatically calculates and manages date ranges for different task types, ensuring that tasks are correctly categorized based on their due dates.

- **Due Date Validation**: Due dates are validated and constrained based on the task type, preventing tasks from being scheduled outside the allowed date ranges.

- **Load and Refresh**: The app provides functionality to load and refresh task lists, ensuring that users always see up-to-date information.

- **Task History**: The app maintains a history of completed tasks, allowing users to review past tasks by tier.

##### 5. **Database Integration**

- **Task Database**: The To-Do List functionality relies on a SQLite database to store and manage tasks. The database schema includes tables for tasks with various attributes and indexes to optimize performance.

- **Dynamic Updates**: The application dynamically updates task types based on due dates and manages the database schema to ensure data integrity and efficiency.

##### 6. **Reset Functionality**

- **Reset Database**: Users can reset the To-Do database if needed, which drops and recreates the task tables. This is useful for clearing all tasks and starting fresh.

#### Implementation Details

##### Database Schema

The database schema for tasks includes:

- **id**: A unique identifier for each task (`INTEGER PRIMARY KEY AUTOINCREMENT`).
- **task**: The description of the task (`TEXT NOT NULL`).
- **tier**: The importance level of the task (`TEXT CHECK(tier IN ('routine', 'challenging', 'significant', 'momentous')) NOT NULL`).
- **task_type**: The category of the task (`TEXT CHECK(task_type IN ('daily', 'weekly', 'monthly', 'yearly')) NOT NULL`).
- **urgency**: The urgency level of the task (`TEXT CHECK(urgency IN ('low', 'medium', 'high')) NOT NULL`).
- **created_date**: The date the task was created (`DATE DEFAULT (date('now', 'localtime'))`).
- **due_date**: The due date for the task (`DATE NOT NULL`).
- **completed_date**: The date the task was completed (`DATE`).

##### Key Functions

- **setup_todo**: Initializes the To-Do application, creating the necessary database tables and indices.
- **update_todo**: Updates task categories based on current date ranges and task due dates.
- **todo_get_data**: Retrieves tasks from the database based on their type or tier.
- **create_task**: Adds a new task to the database.
- **interact_task**: Handles user interactions with tasks, such as marking them as completed or editing.
- **done_task**: Updates the task status to completed and refreshes the task lists.
- **save_task**: Saves changes made to an existing task.
- **delete_task**: Deletes a task from the database.
- **load_tasks**: Loads and displays tasks based on their type or tier.
- **update_task_types**: Updates task types based on their due dates and the current date range.
- **reset_todo**: Resets the entire To-Do database, including dropping and recreating tables.

##### User Interface

- **Create Task Box**: Allows users to input new task details.
- **Edit Task Box**: Enables users to modify existing tasks.
- **History Box**: Displays completed tasks categorized by their tier.
- **List Box**: Shows tasks based on their type and allows interaction with them.

##### Image Resources

- **Daily Tab Icon**: Located at `resources/todo/daily.png`. Created using Adobe Photoshop.
- **Weekly Tab Icon**: Located at `resources/todo/weekly.png`. Created using Adobe Photoshop.
- **Monthly Tab Icon**: Located at `resources/todo/monthly.png`. Created using Adobe Photoshop.
- **Yealy Tab Icon**: Located at `resources/todo/yearly.png`. Created using Adobe Photoshop.
- **Routine Tab Icon**: Located at `resources/todo/routine.png`. Created using a public domain image and Adobe Photoshop.
- **Challenging Tab Icon**: Located at `resources/todo/challenging.png`. Created using a public domain image and Adobe Photoshop.
- **Significant Tab Icon**: Located at `resources/todo/significant.png`. Created using a public domain image and Adobe Photoshop.
- **Momentous Tab Icon**: Located at `resources/todo/momentous.png`. Created using a public domain image and Adobe Photoshop.

#### Usage

- **Setup**: Initialize the application using the `setup_todo` function.
- **Create Tasks**: Use the Create Task Box to add new tasks.
- **Edit Tasks**: Select a task and use the Edit Task Box to modify its details.
- **Delete Tasks**: Remove tasks using the provided delete functionality.
- **View History**: Check completed tasks in the History Box.

This feature is designed to integrate smoothly with the rest of the application, providing users with a powerful tool for managing their tasks and productivity.

### habit.py

#### Overview

The Habits feature is an integral part of our application, designed to help users track and manage their habits effectively. It includes functionalities to create, update, delete, and reset habits, as well as to track their progress and analyze habit data.

#### Features

##### 1. **Habit Management**

- **Create Habit**: Users can create a new habit and initialize habit records for it. This includes entering a habit name, saving it to the database, and starting records for the current date.
  
- **Delete Habit**: Habits and their records can be permanently deleted after confirming the action through a dialog.

- **Rename Habit**: Existing habits can be renamed, with updates reflected in the database.

- **Reset Habit**: Users can reset the habits database, which involves dropping existing tables and recreating them to start fresh.

##### 2. **Habit Tracking**

- **Change Habit State**: Users can update the state of a habit for a specific date, marking it as 'success', 'failure', or 'skip'. The system adjusts the longest streak as necessary.

- **Change Date**: Changes the current day to show habit records (last 7 days, including today)

- **Set Tracker Date to Today**: Updates the habit tracker date to the current date.

- **Reset Today’s Habit Records**: Resets the state of habit records for the current day.

##### 3. **Habit Analysis**

- **Load Habit Details**: Displays detailed information for a specific habit, including name, creation and completion dates, streaks, and statistics. Visual representations of habit records are shown on a calendar.

#### Implementation Details

##### Database Schema

- **`habits` Table**: Includes `id`, `name`, `longest_streak`, `created_date`, and `completed_date`.
- **`habit_records` Table**: Includes `id`, `habit_id`, `record_date`, and `state`.

##### Key Functions
 
- **`create_habit`**: Handles the creation of a new habit and initializes records.
- **`delete_habit`**: Executes the deletion of a habit.
- **`rename_habit`**: Executes the renaming of a habit.
- **`reset_habit`**: Executes the reset of the habits database.
- **`change_habit_state`**: Updates the state of a habit.
- **`reset_today_habit_records`**: Resets the state of habit records for today.
- **`load_habits`**: Displays habit records for the selected date.
- **`load_habit_more`**: Retrieves and displays detailed information for a habit.
- **`habit_today`**: Sets the habit tracker date to today.

##### User Interface

- **Create Habit Box**: Allows users to create new habits.
- **Habit Tracker Box**: Shows current habit statuses, and streaks for selected date.
- **Habit Details Box**: Shows list of created habits, and their tracking state.
- **Habit More Box**: Shows detailed and analyzed data for selected habit, allows to delete, rename, stop/resume tracking of the opened habit.


##### Image Resources

- **Success State Image**: Located at `resources/habit/success.png`. Created using a public domain image and Adobe Photoshop.
- **Failure State Image**: Located at `resources/habit/failure.png`. Created using a public domain image and Adobe Photoshop.
- **Skip State Image**: Located at `resources/habit/skip.png`. Created using a public domain image and Adobe Photoshop.

#### Usage

- **Create Habit**: Use the habit creation form to add a new habit and initialize records.
- **Manage Habits**: Delete, rename, or track habits through the habit management section.
- **Track Progress**: Update habit states and view detailed analytics and calendar views.

This feature is designed to integrate seamlessly with the rest of the application, offering users a comprehensive tool for tracking and managing their habits effectively. With detailed analytics and intuitive management options, it supports users in building and maintaining positive habits for improved productivity and well-being.

### journal.py

#### Overview

The Journal feature allows users to record and manage their daily thoughts and experiences. It provides functionalities for creating, editing, viewing, and deleting journal entries, and notes, integrating seamlessly with other app features.

#### Features

##### 1. **Entries**

- **Create Entries**: Users can add new journal entries by specifying the entry title, date, and content. Each entry is saved with a unique identifier.
- **Update Entries**: Existing entries can be edited to update their content, title, or date.
- **View Entries**: Users can view their journal entries sorted by date. Entries are displayed in chronological order for easy review.

##### 2. **Notes**

- **Add Notes**: Within journal entries, users can add detailed notes to expand on their thoughts or track additional information.
- **Edit Notes**: Notes can be edited to update or refine the additional information within an entry.
- **Delete Notes**: Notes within entries can be removed if no longer needed.

##### 3. **Date Management**

- **Entry Dates**: The app automatically records the date of each entry, ensuring accurate chronological tracking.
- **Date Navigation**: Users can navigate through entries by selecting specific dates or date ranges.

##### 4. **Database Integration**

- **Journal Database**: The Journal functionality relies on a SQLite database to store and manage entries. The database schema includes tables for entries and notes, optimized for efficient data handling.
- **Dynamic Updates**: The application dynamically updates the journal entries and notes based on user interactions and ensures data integrity

##### 5. **Reset Functionality**

- **Reset Database**: Users can reset the Journal database if needed, which drops and recreates the journal and notes tables. This is useful for clearing all entries and starting fresh.

#### Implementation Details

##### Database Schema

The database schema for journal entries includes:

- **id**: A unique identifier for each entry (`INTEGER PRIMARY KEY AUTOINCREMENT`).
- **title**: The title of the journal entry (`TEXT NOT NULL`).
- **date**: The date of the journal entry (`DATE DEFAULT (date('now', 'localtime'))`).
- **content**: The content of the journal entry (`TEXT NOT NULL`).

The schema for notes includes:

- **id**: A unique identifier for each note (`INTEGER PRIMARY KEY AUTOINCREMENT`).
- **entry_id**: The ID of the journal entry to which the note belongs (`INTEGER NOT NULL`).
- **note_content**: The content of the note (`TEXT NOT NULL`).

##### Key Functions

##### Key Functions

- **setup_journal**: Initializes the Journal application, creating the necessary database tables and indices.
- **update_journal**: Updates the journal data or settings as needed.
- **journal_get_data**: Retrieves the current data from the journal.
- **load_entry**: Loads and displays a specific journal entry.
- **save_entry**: Saves changes made to a journal entry.
- **create_note**: Adds a note to a specific journal entry.
- **update_note**: Updates the content of an existing note.
- **delete_note**: Removes a note from a journal entry.
- **reset_journal**: Resets the entire Journal database, including dropping and recreating tables.

##### User Interface

- **Entry Box**: Allows users to input new journal entry details and view old ones.
- **Note Box**: Displays created notes.
- **Note Create Box**: Allows users to create new notes.
- **Note Read/Edit Box**: Allows users to read/edit created notes.

#### Usage

- **Setup**: Initialize the application using the `setup_journal` function.
- **Entries**: Use the Entry Box to add new journal entries and read existing ones.
- **Notes**: Use the Notes Box to view list of existing notes.
- **Create and Read/Edit Notes**: Use the Create Note Box to create new notes, and Read/Edit Note Box to read/edit existing notes.

This feature integrates seamlessly with the rest of the application, offering a comprehensive tool for recording and reflecting on personal thoughts and experiences.

### ranking.py

#### Overview

The Ranking feature is a vital component of our application, designed to help users evaluate and prioritize the books, movies, and other media they have experienced. This feature allows users to add, update, and remove rankings, providing insights into their preferences and facilitating better recommendations.

#### Features

##### 1. **Ranking Management**

- **Add Rankings**: Users can add new rankings by specifying the title, category (e.g., book, movie), rating, and optional comments. Rankings are categorized to allow easy identification of media types.

- **Update Rankings**: Existing rankings can be edited to update any attributes, including title, category, rating, and comments.

- **Remove Rankings**: Users can permanently remove rankings from their list, allowing for effective management of their evaluations.

##### 2. **Ranking Filtering**

- **Category Filtering**: Rankings can be filtered based on media category (e.g., books, movies), enabling users to focus on specific types of media.

- **Rating Filtering**: Users can view rankings filtered by rating to easily identify highly rated or low-rated media.

##### 3. **Ranking View**

- **Sorted Rankings**: Users can view their rankings sorted by rating or title, providing an organized overview of their evaluations.

- **Detailed View**: Clicking on a ranking reveals additional details, including comments and media type, offering a comprehensive understanding of the user's preferences.

##### 4. **Database Integration**

- **Ranking Database**: The Ranking functionality relies on a SQLite database to store and manage rankings. The database schema includes tables for rankings with relevant attributes, ensuring efficient data retrieval.

- **Dynamic Updates**: The application updates rankings dynamically based on user interactions and maintains data integrity through database constraints.

##### 5. **Reset Functionality**

- **Reset Database**: Users can reset the Ranking database if needed, which drops and recreates the ranking tables. This functionality is useful for starting afresh or clearing out old data.

#### Implementation Details

##### Database Schema

The database schema for rankings includes:

- **id**: A unique identifier for each ranking (`INTEGER PRIMARY KEY AUTOINCREMENT`).
- **title**: The name of the media being ranked (`TEXT NOT NULL`).
- **category**: The type of media (`TEXT CHECK(category IN ('book', 'movie')) NOT NULL`).
- **rating**: The user's rating of the media (`INTEGER CHECK(rating BETWEEN 1 AND 10) NOT NULL`).
- **comments**: Optional comments about the media (`TEXT`).
- **added_date**: The date the ranking was added (`DATE DEFAULT (date('now', 'localtime'))`).

##### Key Functions

- **setup_ranking**: Initializes the Ranking application, creating the necessary database tables and indices.
- **add_entry**: Adds a new ranking entry to the database.
- **update_ranking**: Updates the attributes of an existing ranking.
- **remove_ranking**: Deletes a ranking from the database.
- **ranking_get_data**: Retrieves rankings from the database based on filters like category or rating.
- **reset_ranking**: Resets the entire Ranking database, including dropping and recreating tables.

##### User Interface

- **Rankings List**: Displays rankings sorted by rating or title, allowing interaction with each ranking.
- **Rankings Sort**: Allows users to sort and filter rankings by different criterias.
- **Rankings Search**: Enables users to search for a particular entry in the rankings.
- **Add Ranking Box**: Allows users to input new ranking details, including title, category, and rating.
- **Edit Ranking Box**: Enables users to modify existing rankings.

##### Image Resources

- **Book Tab Icon**: Located at `resources/ranking/book.png`. Created using an image by mikan933 and Adobe Photoshop.
- **Movie Tab Icon**: Located at `resources/ranking/movie.png`. Created using an image by Freepik and Adobe Photoshop.
- **Series Tab Icon**: Located at `resources/ranking/series.png`. Created using an image by cube29 and Adobe Photoshop.
- **Music Tab Icon**: Located at `resources/ranking/music.png`. Created using an image by Freepik and Adobe Photoshop.

#### Usage

- **Setup**: Initialize the application using the `setup_ranking` function.
- **Add Rankings**: Use the Add Ranking Box to input new rankings.
- **Edit Rankings**: Select a ranking and use the Edit Ranking Box to modify its details.
- **Remove Rankings**: Delete rankings using the provided remove functionality.
- **View Rankings**: Check sorted rankings in the Rankings List.

This feature seamlessly integrates with the rest of the application, providing users with a powerful tool for evaluating and managing their media preferences.

## License

This project is licensed under the BSD-3-Clause License - see the [LICENSE](LICENSE) file for details.

## Acknowlegments:

- [**Toga**](https://toga.readthedocs.io/)
- [**Briefcase**](https://briefcase.readthedocs.io/)
- [**Pillow**](https://pillow.readthedocs.io/)
- [**Schedule**](https://schedule.readthedocs.io/)s
- [**Titlecase**](https://pypi.org/project/titlecase/)
- [**Nameparser**](https://nameparser.readthedocs.io/)