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

        self.create_exist_butt()


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

    def create_butt_mark(self, ind, mark = False):
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
        button.setIconSize(1 * QtCore.QSize(button.width(), button.height()))

    def update_butt_mark(self, ind, record_id):
        data = self.get_db_by_date(
            datetime.datetime.date(datetime.datetime.now() - datetime.timedelta(days=self.count_date)))
        button_ind = list(self.button_id_map.keys())[list(self.button_id_map.values()).index(record_id)]
        button = self.buttons_mark[ind]
        new_mark = not data[ind][-1]
        if new_mark:
            self.set_icon_btn_m(button_ind)
        else:
            button.setIcon(QtGui.QIcon())
        self.update_mark_in_bd(record_id, new_mark)


    def create_exist_butt(self):
        self.show()
        data = self.get_db_by_date(datetime.datetime.date(datetime.datetime.now() - datetime.timedelta(days=self.count_date)))
        num_task = len(data)
        self.delete_exist_but()
        for ind in range(num_task):
            record_id = data[ind][0]
            self.create_butt_task(data[ind][1], ind)
            self.create_butt_mark(ind, data[ind][-1])
            self.buttons_task[ind].clicked.connect(partial(self.show_sec_window, record_id)) #record_id
            self.buttons_mark[ind].clicked.connect(partial(self.update_butt_mark, ind, record_id))
            self.button_id_map[ind] = record_id
        # else:
        #     self.update_butt_task(data[i][1], i)
        #     self.create_butt_mark(i, data[i][-1])

    def delete_exist_but(self):
        for button in self.buttons_task.values():
            button.setParent(None)

        for button in self.buttons_mark.values():
            button.setParent(None)
        self.buttons_task.clear()
        self.buttons_mark.clear()
        self.button_id_map.clear()

    # def show_page(self, ind=-1):
    #     self.show()
    #     data = self.get_db_by_date(datetime.datetime.date(datetime.datetime.now() - datetime.timedelta(days=application.count_date)))
    #     num_task = len(data)
    #     if ind == -1:
    #         new_ind = num_task - 1
    #         if num_task > 0:
    #             self.create_butt_task(data[num_task-1][1], num_task-1)
    #             self.create_butt_mark(num_task-1, False)
    #             self.buttons_task[new_ind].clicked.connect(partial(self.show_sec_window, new_ind))  # record_id
    #             self.buttons_mark[new_ind].clicked.connect(partial(self.update_butt_mark, new_ind, new_ind))
    #     else:
    #         self.update_butt_task(data[ind][1], ind)
    #         self.create_butt_mark(ind, data[ind][-1])


    def show_sec_window(self, record_id=-1):
        self.hide()
        self.window_2 = Creator_task(record_id, parent=self)
        if record_id != -1:
            self.window_2.set_info(record_id)
        self.window_2.show()


    def get_db_by_date(self, date):
        cur.execute("""SELECT id, theme, description, mark FROM planes WHERE date = ?""", (date,))
        data = cur.fetchall()
        return data

    def update_mark_in_bd(self, record_id, mark = False):
        cur.execute("""UPDATE planes SET mark = ? WHERE id = ?""", (mark, record_id))
        conn.commit()

class Creator_task(QtWidgets.QMainWindow):
    def __init__(self, record_id, parent=None):
        super(Creator_task, self).__init__()
        self.index = record_id
        self.parent = parent
        self.ui = Ui_Sec_Window()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.save_and_close)

    def set_info(self, index):
        all_bd = self.get_all_db()
        _, theme, description, _, _ = all_bd[self.index]
        self.ui.textEdit.setText(theme)
        self.ui.textEdit_2.setText(description)

    def get_all_db(self):
        cur.execute("""SELECT * FROM planes""")
        all_db = cur.fetchall()
        return all_db

    def save_and_close(self):
        num_task = len(self.get_all_db())
        theme = self.ui.textEdit.toPlainText()
        descrip = self.ui.textEdit_2.toPlainText()
        if theme != '':
            if self.index != -1:
                cur.execute("""UPDATE planes SET theme = ?, description = ? WHERE id = ?""", (theme, descrip, self.index))
            else:
                date = datetime.datetime.date(datetime.datetime.now() - datetime.timedelta(days=application.count_date))
                cur.execute("""INSERT INTO planes (id, theme, description, date, mark) VALUES (?, ?, ?, ?, ?)""",
                            (num_task, theme, descrip, date, False))
            conn.commit()
            self.close()
        self.parent.create_exist_butt()


app = QtWidgets.QApplication([])
application = Planner()

application.show()

sys.exit(app.exec())