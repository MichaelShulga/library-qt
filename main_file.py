import sqlite3
import sys
from os import listdir
from os.path import isfile, join
from PyQt5 import uic  # Импортируем uic
from PyQt5.QtWidgets import QApplication, QMainWindow

from admin_file import MainAdminWindow
from user_file import MainPupilWindow


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('start_window.ui', self)  # Загружаем дизайн

        # иницилизация
        self.db = None
        self.con = None
        self.pupil_window = None
        self.admin_window = None

        #  добавление баз данных
        data_bases_path = 'data_bases'
        data_bases = [f for f in listdir(data_bases_path) if isfile(join(data_bases_path, f))]
        for i in data_bases:
            self.comboBox.addItem(i)

        # настройка виджетов
        self.pushButton.clicked.connect(self.run_login)
        self.pushButton.setEnabled(False)
        self.lineEdit.textChanged.connect(self.update_button)
        self.lineEdit_2.textChanged.connect(self.update_button)  # доступ к кнопке

    def run_login(self):
        self.statusBar().clearMessage()  # очистка статус бара

        # подключение к базе данных
        self.db = f'data_bases\\{self.comboBox.currentText()}'
        self.con = sqlite3.connect(self.db)

        login, password = self.lineEdit.text(), self.lineEdit_2.text()

        # проверка на существование пользователя
        cur = self.con.cursor()
        exist = cur.execute(f'select type from users '
                            f'where login = "{login}" and password = "{password}"').fetchall()

        if exist:
            user_type = exist[0][0]
            if user_type == 0:  # продолжить как ученик
                self.pupil_window = MainPupilWindow(login, self.db)
                self.pupil_window.show()
            elif user_type == 1:  # продолжить как администратор
                self.admin_window = MainAdminWindow(self.db)
                self.admin_window.show()
        else:
            self.statusBar().showMessage('login или password указаны не верно')

    def update_button(self):
        self.pushButton.setEnabled(bool(self.lineEdit.text()) and bool(self.lineEdit_2.text()))


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    sys.excepthook = except_hook
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())
