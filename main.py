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

    def create_ep(self):
        db = self.get_db_by_date(datetime.datetime.date(datetime.datetime.now() - datetime.timedelta(days=self.date_ch)))
        print(db)
        count_exp = len(db)
        self.delete_ep()
        for i in range(count_exp):
            self.create_button_p(db[i][1], i)
            self.create_button_m(i, db[i][-1])
            self.button_p[i].clicked.connect(partial(self.show_w2, i))
            self.button_m[i].clicked.connect(partial(self.update_button_m, i))


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


    def update_button_m(self, ind):
        bd = self.get_db_by_date(datetime.datetime.date(datetime.datetime.now() - datetime.timedelta(days=self.date_ch)))
        button = self.button_m[ind]
        new_mark = not bd[ind][-1]
        if bd[ind][-1]:
            button.setIcon(QtGui.QIcon())
        else:
            self.set_icon_btn_m(ind)
        self.update_bm_in_bd(ind, new_mark)

    def update_bm_in_bd(self, ind, mark = False):
        cur.execute("""UPDATE planes SET mark = ? WHERE id = ?""", (mark, ind))
        print(mark, ind)
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