from flask import Blueprint, render_template
from flask import request, url_for, redirect
import pandas as pd
import os
import sqlite3
import pyttsx3
import os
import pyautogui
import time
import datetime
import pytz

UTC = pytz.utc

IST = pytz.timezone('Asia/Kolkata')

send = Blueprint('send', __name__)


@send.route('/')
def index():
    time_taken = request.args.get("time_taken", None)
    duplicate_count = request.args.get("duplicate_count", None)
    uploaded_count = request.args.get("uploaded_count", None)
    receiver_list = get_receiver_list()
    receiver_list = [{"name": contact[0], "phone": contact[1]} for contact in receiver_list]
    last_sent_list = get_last_sent()
    last_sent_list = [{"name": contact[0], "phone": contact[1], "time_lapsed" : get_lapsed_time(contact[3])} for contact in last_sent_list]
    return render_template('index.html', fresh_contacts=receiver_list, time_taken=time_taken,
                           duplicate_count=duplicate_count, uploaded_count=uploaded_count,sent_contacts=last_sent_list)


@send.route('/message/send', methods=['GET', 'POST'])
def send_message():
    print("arrived here")
    message = request.args.get("message")
    no_of_people = int(request.args.get("no_of_people", 10))
    delay = int(request.args.get("delay", 1))
    receiver_list = get_receiver_list(no_of_people, update=True)

    time_taken = delay * no_of_people
    time_taken = time.strftime(
        "%H hr %M min %S seconds", time.gmtime(time_taken))
    # os.system('open -a "Sublime Text"')
    # pyautogui.hotkey('command', 'n')
    time.sleep(3)
    return redirect(url_for('send.index', time_taken=time_taken))
    # return render_template('index.html', time_taken=time_taken)


def remove_safely(file_path):
    try:
        os.remove(file_path)
    except:
        pass


@send.route('/upload', methods=['POST'])
def upload():
    uploaded_count = 0
    duplicate_count = 0
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file.filename != '':
            file_path = os.getcwd() + "/" + uploaded_file.filename
            print(file_path)
            if os.path.exists(file_path):
                os.remove(file_path)
            uploaded_file.save(file_path)

            col_names = ['name', 'phone', 'email']
            csv_data = pd.read_csv(file_path, names=col_names, header=None)
            duplicate_count = 0
            for i, row in csv_data.iterrows():
                sql = "INSERT INTO contacts (name, phone, email) VALUES (?,?,?)"
                value = (row['name'], row['phone'], row['email'])
                mysql_conn = sqlite3.connect('database.db')
                try:
                    mysql_conn.execute(sql, value)
                    mysql_conn.commit()
                    uploaded_count += 1
                except sqlite3.IntegrityError:
                    duplicate_count += 1
                mysql_conn.close()
    return redirect(url_for('send.index', duplicate_count=duplicate_count, uploaded_count=uploaded_count))
    # return render_template('index.html', duplicate_count=duplicate_count, uploaded_count=uploaded_count)


def update_last_sent(conn, curr_time, receiver_list_str):
    update_query = "update contacts set last_sent_time='%s' where phone in (%s);" % (curr_time, receiver_list_str)
    print(update_query)
    conn.execute(update_query)
    conn.commit()


def get_receiver_list(limit=10, update=False):
    conn = sqlite3.connect('database.db')
    select_query = "select * from contacts where last_sent_time is null limit %s;" % limit
    result = conn.execute(select_query)
    result = result.fetchall()
    receiver_list = []
    for row in result:
        receiver_list.append(row[1])
    print(receiver_list)
    print(select_query)
    if update:
        receiver_list = ",".join(["'%s'" % i for i in receiver_list])
        curr_time = datetime.datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")
        update_last_sent(conn, curr_time, receiver_list)
    return result


def get_last_sent(limit=10):
    conn = sqlite3.connect('database.db')
    select_query = "select * from contacts where last_sent_time is not null order by  last_sent_time desc limit %s ;" % limit
    result = conn.execute(select_query)
    result = result.fetchall()
    return result

def get_lapsed_time(time):
    return time



