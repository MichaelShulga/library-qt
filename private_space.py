import sqlite3
import sys

from PyQt5 import uic  # Импортируем uic
from PyQt5.QtWidgets import QApplication, QMainWindow


class PrivateSpace(QMainWindow):
    def __init__(self, db, login):
        super().__init__()
        uic.loadUi('private_space.ui', self)
        # иницилизация
        self.con = sqlite3.connect(db)
        self.login = login

        cur = self.con.cursor()

        #  получение данных об ученике
        name, grade = cur.execute(
             f'select name, grade from pupils where login = {self.login}').fetchone()
        password = cur.execute(
            f'select password from users where login = {self.login}').fetchone()

        #  настройка виджетов
        self.lineEdit.setText(str(self.login))
        self.lineEdit_2.setText(str(password[0]))
        self.lineEdit_3.setText(name)
        self.lineEdit_4.setText(str(grade))
        self.lineEdit.setEnabled(False)
        self.lineEdit_3.setEnabled(False)
        self.lineEdit_4.setEnabled(False)
        self.pushButton.clicked.connect(self.edit_password)

    def edit_password(self):
        password = self.lineEdit_2.text()
        if not password:
            self.label_5.setText('Неверный формат пароля')
            return

        cur = self.con.cursor()

        # обновление данных
        cur.execute(
            f'update users set password = "{password}" Where login = "{self.login}"').fetchall()
        self.con.commit()
        self.destroy()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    sys.excepthook = except_hook
    app = QApplication(sys.argv)
    ex = PrivateSpace('data_bases\\library.db', 4)
    ex.show()
    sys.exit(app.exec_())
