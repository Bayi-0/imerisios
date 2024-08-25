import time
import sqlite3 as sql
import calendar
import PIL
import calendar
from PIL import Image, ImageDraw, ImageFont

def length_check(widget):
    length = int(widget.id.split()[2])
    if len(widget.value) > length:
        widget.readonly = True
        widget.value = widget.value[:length]
        time.sleep(0.6)
        widget.readonly = False


def get_connection(path, con_cur=None):
    if not con_cur:
        con = sql.connect(path)
        cur = con.cursor()
        return con, cur
    return con_cur
        

def close_connection(con, con_cur):
    if not con_cur:
        con.close()


def create_calendar_image(year, month, file_name, marks):
    # Set up the calendar
    cal = calendar.Calendar()
    month_days = cal.monthdayscalendar(year, month)
    month_name = calendar.month_name[month]

    # Create an image with dark background
    img_width, img_height = 720, 500
    img = Image.new("RGB", (img_width, img_height), "#27221F")
    draw = ImageDraw.Draw(img)

    # Set up fonts
    font = ImageFont.load_default()
    font_large = ImageFont.load_default()

    # Colors
    neutral_text_color = "#EBF6F7"
    success_color = "#7FFF00"  # Light green
    failure_color = "#FF6347"  # Light red
    skip_color = '#87CEEB'  # Light blue

    # Draw month and year
    draw.text((img_width // 2 - 100, 20), f"{month_name} {year}", fill=neutral_text_color, font=font_large)

    # Draw days of the week
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for i, day in enumerate(days):
        draw.text((i * 100 + 50, 100), day, fill=neutral_text_color, font=font)

    # Draw the days and mark specific days
    for week_index, week in enumerate(month_days):
        for day_index, day in enumerate(week):
            if day != 0:  # 0 means no day in this month
                color = neutral_text_color
                if day in marks:
                    if marks[day] == "success":
                        color = success_color
                    elif marks[day] == "failure":
                        color = failure_color
                    elif marks[day] == "skip":
                        color = skip_color
                draw.text((day_index * 100 + 50, week_index * 60 + 150), str(day), fill=color, font=font)

    # Save the image
    img.save(file_name)


def get_month_dicts():
    month_num_to_name = {i: calendar.month_name[i] for i in range(1, 13)}
    month_name_to_num = {name: num for num, name in month_num_to_name.items()}

    return month_num_to_name, month_name_to_num