from flask import Blueprint, render_template
from flask import request, url_for, redirect
import pandas as pd
import pywhatkit
import sqlite3
import requests
import os
import pyautogui
import time
import datetime
import pytz

UTC = pytz.utc

IST = pytz.timezone('Asia/Kolkata')

send = Blueprint('send', __name__)
CURR_TIME =datetime.datetime.now(IST)
CURR_TIME_STR= CURR_TIME.strftime("%Y-%m-%d %H:%M:%S")
DAY_PRIOR_TIME = CURR_TIME - datetime.timedelta(days=1)
DAY_PRIOR_TIME_STR = DAY_PRIOR_TIME.strftime("%Y-%m-%d %H:%M:%S")

@send.route('/')
def index():
    time_taken = request.args.get("time_taken", None)
    duplicate_count = request.args.get("duplicate_count", None)
    uploaded_count = request.args.get("uploaded_count", None)
    receiver_list = get_receiver_list()
    receiver_list = [{"name": contact[0], "phone": contact[1]} for contact in receiver_list]
    last_sent_list = get_last_sent()
    last_sent_list = [{"name": contact[0], "phone": contact[1], "time_lapsed": get_lapsed_time(contact[3])} for contact
                      in last_sent_list]
    return render_template('index.html', fresh_contacts=receiver_list, time_taken=time_taken,
                           duplicate_count=duplicate_count, uploaded_count=uploaded_count, sent_contacts=last_sent_list)


@send.route('/message/send', methods=['GET', 'POST'])
def send_message():
    print("arrived here")
    message = request.args.get("message")
    no_of_people = int(request.args.get("no_of_people", 10))
    delay = int(request.args.get("delay", 1))
    receiver_list = get_receiver_list(no_of_people)

    time_taken = delay * no_of_people
    time_taken = time.strftime(
        "%H hr %M min %S seconds", time.gmtime(time_taken))
    success_receiver_list = []
    for receiver in receiver_list:
        phone_number = "+" + str(receiver[1])
        try:
            pywhatkit.sendwhatmsg_instantly(phone_no=phone_number,
                                            message=message,
                                            wait_time=delay)
            success_receiver_list += receiver[1]
        except Exception as e:
            print(e)

    if success_receiver_list:
        success_receiver_list = ",".join(["'%s'" % i for i in success_receiver_list])
        conn = get_conn()
        update_last_sent(conn, CURR_TIME_STR, success_receiver_list)

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
                print(value)
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
    update_query = f"update contacts set last_sent_time='{curr_time}' where phone in ({receiver_list_str});"
    conn.execute(update_query)
    conn.commit()


def get_conn():
    return sqlite3.connect('database.db')


def get_receiver_list(limit=10):
    conn = get_conn()
    select_query = f"select * from contacts where last_sent_time<='{DAY_PRIOR_TIME_STR}' " \
                   f"or last_sent_time is null limit {limit};"
    result = conn.execute(select_query)
    result = result.fetchall()
    return result


def get_last_sent(limit=10):
    conn = sqlite3.connect('database.db')
    select_query = f"select * from contacts where last_sent_time is not null order by  last_sent_time desc limit {limit};"
    result = conn.execute(select_query)
    result = result.fetchall()
    return result


def get_lapsed_time(time):
    return time
