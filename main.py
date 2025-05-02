import sys

from Window import Ui_MainWindow
from Sec_wind import Ui_Sec_Window
from PyQt5 import QtWidgets, QtCore, QtGui
from db import conn, cur
from functools import partial
import datetime
import json

class Planner(QtWidgets.QMainWindow):
    def __init__(self):
        super(Planner, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.button_p, self.button_m = {}, {}
        self.button_id_map = {}
        self.set_date()
        self.create_ep()
        self.button()

    def set_date(self):
        with open('date_transl.json', 'r', encoding="UTF-8") as month:
            self.date_tr = json.load(month)
        now = datetime.datetime.now()
        c_time = now.strftime("%A %d %B").split()
        cur_time = self.date_tr[c_time[0]] + ', ' + c_time[1].lstrip('0') + ' ' + self.date_tr[c_time[2]]
        self.date_ch = 0
        self.ui.label.setText(cur_time)

    def button(self):
        self.ui.pushButton_3.clicked.connect(self.create_np)
        self.ui.pushButton_2.clicked.connect(lambda: self.change_date(1))
        self.ui.pushButton.clicked.connect(lambda: self.change_date(-1))

    def change_date(self, ind):
        self.date_ch += ind
        new_date = datetime.datetime.now() - datetime.timedelta(days=self.date_ch)
        c_time = new_date.strftime("%A %d %B").split()
        cur_time = self.date_tr[c_time[0]] + ', ' + c_time[1].lstrip('0') + ' ' + self.date_tr[c_time[2]]
        self.delete_ep()
        self.create_ep()
        self.ui.label.setText(cur_time)

    def delete_ep(self):
        for i in list(self.button_p.keys()):
            if self.button_p[i] != None:
                self.button_p[i].setParent(None)

        for i in list(self.button_m.keys()):
            if self.button_m[i] != None:
                self.button_m[i].setParent(None)

        self.button_p.clear()
        self.button_m.clear()
        self.button_id_map.clear()

    def create_ep(self):
        db = self.get_db_by_date(datetime.datetime.date(datetime.datetime.now() - datetime.timedelta(days=self.date_ch)))
        count_exp = len(db)
        self.delete_ep()
        for i in range(count_exp):
            record_id = db[i][0]
            self.create_button_p(db[i][1], i)
            self.create_button_m(i, db[i][-1])
            self.button_p[i].clicked.connect(partial(self.show_w2, i))
            self.button_m[i].clicked.connect(partial(self.update_button_m, i, record_id))
            self.button_id_map[i] = record_id

    def create_np(self):
        self.show_w2()

    def show_p(self, ind = -1):
        self.show()
        bd = self.get_db_by_date(datetime.datetime.date(datetime.datetime.now() - datetime.timedelta(days=self.date_ch)))
        count_exp = len(bd)
        if ind == -1:
            self.create_button_p(bd[count_exp-1][1], count_exp-1)
            self.create_button_m(count_exp - 1, bd[ind][-1])
        else:
            self.update_button_p(bd[ind][1], ind)
            self.create_button_m(count_exp-1, bd[ind][-1])

    def update_button_p(self, text, ind):
        self.button_p[ind].setText(text)

    def set_icon_btn_m(self, ind):
        Icon = QtGui.QIcon('Check.png')
        button = self.button_m[ind]
        button.setIcon(Icon)
        button.setIconSize(1 * QtCore.QSize(button.width(), button.height()))


    def update_button_m(self, ind, record_id):
        bd = self.get_db_by_date(datetime.datetime.date(datetime.datetime.now() - datetime.timedelta(days=self.date_ch)))
        button_ind = list(self.button_id_map.keys())[list(self.button_id_map.values()).index(record_id)]
        button = self.button_m[ind]
        new_mark = not bd[ind][-1]
        if bd[button_ind][-1]:
            button.setIcon(QtGui.QIcon())
        else:
            self.set_icon_btn_m(button_ind)
        print(record_id)
        self.update_bm_in_bd(record_id, new_mark)

    def update_bm_in_bd(self, ind, mark = False):
        cur.execute("""UPDATE planes SET mark = ? WHERE id = ?""", (mark, ind))
        conn.commit()

    def create_button_p(self, text, i = 0):
        y_offset = 30
        button = QtWidgets.QPushButton(self.ui.centralwidget)
        button.setObjectName(f"label_{i}")
        button.setGeometry(QtCore.QRect(30, 100 + y_offset * i + i * 101, 441, 101))
        button.setStyleSheet("border-radius: 30px;                   \n"
                                  "\n"
                                  "border: 2px solid #094065;\n")
        font = QtGui.QFont()
        font.setFamily("Segoe UI Light")
        font.setPointSize(20)
        button.setFont(font)
        button.setText(text)
        button.show()
        self.button_p[i] = button

    def create_button_m(self, i = 0, mark = False):
        y_offset = 30
        button = QtWidgets.QPushButton(self.ui.centralwidget)
        button.setObjectName(f"label_{i}")
        button.setGeometry(QtCore.QRect(480, 100 + y_offset * i + i * 101, 91, 91))
        button.setStyleSheet("border: 2px solid #094065;")
        button.installEventFilter(self)
        button.show()
        self.button_m[i] = button
        if mark:
            self.set_icon_btn_m(i)

    def show_w2(self, ind = -1):
        self.hide()
        self.w2 = Info()
        if ind != -1:
            self.w2.set_info(ind)
        self.w2.show()
        self.w2.ui.pushButton.clicked.connect(lambda: self.w2.save_and_close(ind))


    def get_all_bd(self):
        cur.execute("""SELECT * FROM planes""")
        all_db = cur.fetchall()
        return all_db

    def get_db_by_date(self, date):
        cur.execute("""SELECT id, theme, description, mark FROM planes WHERE date = ?""", (date, ))
        db = cur.fetchall()
        print(db)
        return db

class Info(QtWidgets.QMainWindow):
    def __init__(self):
        super(Info, self).__init__()
        self.ui = Ui_Sec_Window()
        self.ui.setupUi(self)

    def set_info(self, ind):
        all_bd = application.get_all_bd()
        _, theme, description, _, _ = all_bd[ind]
        self.ui.textEdit.setText(theme)
        self.ui.textEdit_2.setText(description)

    def save_and_close(self, ind = -1):
        count_exp = len(application.get_all_bd())
        theme = self.ui.textEdit.toPlainText()
        desc = self.ui.textEdit_2.toPlainText()
        if ind != -1:
            cur.execute("""UPDATE planes SET theme = ?, description = ? WHERE id = ?""", (theme, desc, ind))
        else:
            date = datetime.datetime.date(datetime.datetime.now() - datetime.timedelta(days=application.date_ch))
            cur.execute("""INSERT INTO planes (id, theme, description, date, mark) VALUES (?, ?, ?, ?, ?)""", (count_exp, theme, desc, date, False))
        conn.commit()
        self.close()
        application.show_p(ind)

app = QtWidgets.QApplication([])
application = Planner()

application.show()

sys.exit(app.exec())


import json
import sys
from Window import Ui_MainWindow
from Sec_wind import Ui_Sec_Window
from PyQt5 import QtWidgets, QtCore, QtGui
import datetime
from db import cur, conn
from functools import partial


class Planner(QtWidgets.QMainWindow):
    def __init__(self):
        super(Planner, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.set_date()
        self.active_click_butt()

        self.buttons_task = {}
        self.buttons_mark = {}
        self.button_id_map = {}

    def active_click_butt(self):
        self.ui.pushButton.clicked.connect(lambda: self.change_date(-1))
        self.ui.pushButton_2.clicked.connect(lambda: self.change_date(1))
        self.ui.pushButton_3.clicked.connect(lambda: self.show_sec_window(-1))

    def set_date(self):
        with open('date_transl.json', 'r', encoding="UTF-8") as months:
            self.date_transl = json.load(months)
        curr_time = datetime.datetime.now().strftime("%A %d %B").split()
        curr_date = f"{self.date_transl[curr_time[0]]}, {curr_time[1].lstrip('0')} {self.date_transl[curr_time[2]]}"
        self.count_date = 0
        self.ui.label.setText(curr_date)

    def change_date(self, num_change):
        self.count_date += num_change
        new_date = datetime.datetime.now() - datetime.timedelta(days=self.count_date)
        new_date = new_date.strftime("%A %d %B").split()
        new_date = f"{self.date_transl[new_date[0]]}, {new_date[1].lstrip('0')} {self.date_transl[new_date[2]]}"
        self.delete_exist_but()
        self.create_exist_butt()
        self.ui.label.setText(new_date)

    def create_butt_task(self, text, ind=0):
        y_offset = 30
        button = QtWidgets.QPushButton(self.ui.centralwidget)
        button.setObjectName(f'label_{ind}')
        button.setGeometry(QtCore.QRect(30, 100 + y_offset * ind + ind * 101, 441, 101))
        button.setStyleSheet("border-radius: 30px;\n"
                             "border: 2px solid #094065;\n")
        font = QtGui.QFont()
        font.setFamily("Segoe UI Light")
        font.setPointSize(20)
        button.setFont(font)
        button.setText(text)
        button.show()
        self.buttons_task[ind] = button

    def update_butt_task(self, text, ind):
        self.buttons_task[ind].setText(text)

    def create_butt_mark(self, ind, mark=False):
        y_offset = 30
        button = QtWidgets.QPushButton(self.ui.centralwidget)
        button.setObjectName(f"label_{ind}")
        button.setGeometry(QtCore.QRect(480, 100 + y_offset * ind + ind * 101, 91, 91))
        button.setStyleSheet("border: 2px solid #094065;")
        button.installEventFilter(self)
        button.show()
        self.buttons_mark[ind] = button
        if mark:
            self.set_icon_btn_m(ind)

    def set_icon_btn_m(self, ind):
        Icon = QtGui.QIcon('Check.png')
        button = self.buttons_mark[ind]
        button.setIcon(Icon)
        button.setIconSize(QtCore.QSize(button.width(), button.height()))

    def update_butt_mark(self, ind, record_id):
        data = self.get_db_by_date(
            datetime.datetime.date(datetime.datetime.now() - datetime.timedelta(days=self.count_date)))
        new_mark = not data[ind][-1]
        button = self.buttons_mark[ind]
        if new_mark:
            self.set_icon_btn_m(ind)
        else:
            button.setIcon(QtGui.QIcon())
        self.update_mark_in_bd(record_id, new_mark)

    def create_exist_butt(self):
        data = self.get_db_by_date(datetime.datetime.date(datetime.datetime.now() - datetime.timedelta(days=self.count_date)))
        num_task = len(data)
        self.delete_exist_but()
        for ind in range(num_task):
            record_id = data[ind][0]
            self.create_butt_task(data[ind][1], ind)
            self.create_butt_mark(ind, data[ind][-1])
            self.buttons_task[ind].clicked.connect(partial(self.show_sec_window, record_id))
            self.buttons_mark[ind].clicked.connect(partial(self.update_butt_mark, ind, record_id))
            self.button_id_map[ind] = record_id

    def delete_exist_but(self):
        for button in self.buttons_task.values():
            button.setParent(None)
        for button in self.buttons_mark.values():
            button.setParent(None)
        self.buttons_task.clear()
        self.buttons_mark.clear()
        self.button_id_map.clear()

    def show_page(self, ind=None):
        self.show()
        data = self.get_db_by_date(
            datetime.datetime.date(datetime.datetime.now() - datetime.timedelta(days=self.count_date)))
        num_task = len(data)
        if ind is None:
            # Создаем новую кнопку для новой записи
            self.create_butt_task("Новая задача", num_task)
            self.create_butt_mark(num_task, False)
        else:
            # Обновляем существующую кнопку
            if ind in self.buttons_task:
                self.update_butt_task(data[ind][1], ind)
            if ind in self.buttons_mark:
                self.create_butt_mark(ind, data[ind][-1])

    def show_sec_window(self, record_id=-1):
        self.hide()
        self.window_2 = Creator_task(record_id, parent=self)
        if record_id != -1:
            self.window_2.set_info(record_id)
        self.window_2.show()

    def get_db_by_date(self, date):
        cur.execute("""SELECT id, theme, description, mark FROM planes WHERE date = ?""", (date,))
        data = cur.fetchall()
        return data or []

    def update_mark_in_bd(self, record_id, mark=False):
        cur.execute("""UPDATE planes SET mark = ? WHERE id = ?""", (mark, record_id))
        conn.commit()


class Creator_task(QtWidgets.QMainWindow):
    def __init__(self, record_id, parent=None):
        super(Creator_task, self).__init__()
        self.record_id = record_id
        self.parent = parent
        self.ui = Ui_Sec_Window()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.save_and_close)

    def set_info(self, record_id):
        all_db = self.get_all_db()
        _, theme, description, _, _ = next((item for item in all_db if item[0] == record_id), (None, "", "", "", ""))
        self.ui.textEdit.setText(theme)
        self.ui.textEdit_2.setText(description)

    def get_all_db(self):
        cur.execute("""SELECT * FROM planes""")
        all_db = cur.fetchall()
        return all_db

    def save_and_close(self):
        theme = self.ui.textEdit.toPlainText()
        descrip = self.ui.textEdit_2.toPlainText()
        if self.record_id != -1:
            cur.execute("""UPDATE planes SET theme = ?, description = ? WHERE id = ?""", (theme, descrip, self.record_id))
            conn.commit()
            self.close()
            self.parent.show_page()
        else:
            date = datetime.datetime.date(datetime.datetime.now() - datetime.timedelta(days=self.parent.count_date))
            cur.execute("""INSERT INTO planes (id, theme, description, date, mark) VALUES (?, ?, ?, ?, ?)""",
                        (len(self.get_all_db()), theme, descrip, date, False))
            conn.commit()
            self.close()
            self.parent.show_page()


app = QtWidgets.QApplication([])
application = Planner()
application.show()
sys.exit(app.exec())


def create_exist_butt(self):
    data = self.get_db_by_date(
        datetime.datetime.date(datetime.datetime.now() - datetime.timedelta(days=self.count_date)))
    num_task = len(data)
    self.delete_exist_but()
    for ind in range(num_task):
        record_id = data[ind][0]
        self.create_butt_task(data[ind][1], ind)
        self.create_butt_mark(ind, data[ind][-1])
        self.buttons_task[ind].clicked.connect(partial(self.show_sec_window, record_id))  # record_id
        self.buttons_mark[ind].clicked.connect(partial(self.update_butt_mark, ind, record_id))
        self.button_id_map[ind] = record_id

def show_page(self, ind=-1):
    self.show()
    data = self.get_db_by_date(datetime.datetime.date(datetime.datetime.now() - datetime.timedelta(days=self.count_date)))
    num_task = len(data)

    if ind == -1:
        # Создаем новую кнопку для новой записи
        if num_task > 0:
            # Если есть существующие задачи, добавляем новую кнопку после последней
            new_ind = num_task
        else:
            # Если задач нет, создаем первую кнопку с индексом 0
            new_ind = 0

        self.create_butt_task("Новая задача", new_ind)
        self.create_butt_mark(new_ind, False)

        # Подключаем сигналы для новой кнопки
        self.buttons_task[new_ind].clicked.connect(partial(self.show_sec_window, new_ind))
        self.buttons_mark[new_ind].clicked.connect(partial(self.update_butt_mark, new_ind, new_ind))

    else:
        # Обновляем существующую кнопку
        if ind in self.buttons_task and ind in self.buttons_mark:
            self.update_butt_task(data[ind][1], ind)
            self.create_butt_mark(ind, data[ind][-1])
        else:
            print(f"Warning: Button with index {ind} does not exist.")