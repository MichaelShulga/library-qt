import os
import sqlite3
import sys

from PIL import Image
from PyQt5 import uic  # Импортируем uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QDialog

from private_space import PrivateSpace


class MainPupilWindow(QMainWindow):
    def __init__(self, login, db):
        super().__init__()
        #  инициализация
        uic.loadUi('pupil_window.ui', self)

        # иницилизация
        self.login = login
        self.db = db
        self.button_dict = None
        self.widget = None
        self.vbox = None
        self.second_form = None
        self.private_info_window = None
        self.con = sqlite3.connect(db)

        self.updateTable()

        #  обновление данных при изменении параметров ввода
        self.comboBox.currentTextChanged.connect(self.updateTable)
        self.comboBox_2.currentTextChanged.connect(self.updateTable)
        self.lineEdit.textChanged.connect(self.updateTable)
        self.lineEdit_2.textChanged.connect(self.updateTable)

        #  Личная информация
        self.pushButton.clicked.connect(self.private_space)

        #  оформление заказа
        self.pushButton_2.clicked.connect(self.checkout)

    def updateTable(self):
        cur = self.con.cursor()
        grade, name, author, query_type = self.comboBox.currentText(), self.lineEdit.text(), \
            self.lineEdit_2.text(), self.comboBox_2.currentText()
        self.widget = QWidget()  # Widget that contains the collection of Vertical Box
        self.vbox = QVBoxLayout()  # The Vertical Box that contains the Horizontal Boxes of  labels and buttons
        parameters = []  # параметры поиска
        if grade != 'Все':
            parameters.append(f'grade like "%{grade}%"')
        if query_type == 'Долги':
            books = str(cur.execute(f'select books from pupils where login = {self.login}').fetchone()[0]).split()
            books = tuple(int(i) for i in books)
            if len(books) < 2:
                books = str(books).replace(',', '')
            parameters.append(f'id in {books}')
        query = f'select id, name, author from library'
        if parameters:
            query = query + ' where ' + ' and '.join(parameters)
        print(query)
        info = [(i[0], i[1]) for i in cur.execute(query).fetchall() if
                name.lower() in i[1].lower() and author.lower() in i[2].lower()]
        self.button_dict = dict()
        for book_id, name in info:
            button = QPushButton(name)
            button.clicked.connect(self.book_info)
            self.vbox.addWidget(button)

            self.button_dict[button] = book_id

        self.widget.setLayout(self.vbox)
        self.scrollArea.setWidget(self.widget)

    def book_info(self):
        book_id = self.button_dict[self.sender()]
        self.second_form = BookInfoWindow(self, book_id)
        self.second_form.show()

    def checkout(self):
        list_books = [self.listWidget.item(i).text() for i in range(self.listWidget.count())]
        cur = self.con.cursor()
        for i in list_books:
            book_id, operation = i.split(';')
            books = list(str(cur.execute(f'select books from pupils where login = {self.login}').fetchone()[0]).split())
            if operation == 'Сдать':
                books.remove(book_id)
                books = ' '.join(books)
                cur.execute(f'update pupils set books = "{books}" where login = {self.login}').fetchall()
                cur.execute(f'update library set n = n + 1').fetchall()
                self.con.commit()
            elif operation == 'Получить':
                books.append(book_id)
                books = ' '.join(books)
                cur.execute(f'update pupils set books = "{books}" where login = {self.login}').fetchall()
                cur.execute(f'update library set n = n - 1').fetchall()
                self.con.commit()
        self.listWidget.clear()
        self.updateTable()

    def private_space(self):
        self.private_info_window = PrivateSpace(self.db, self.login)
        self.private_info_window.show()


class BookInfoWindow(QDialog):
    def __init__(self, main_window, book_id):
        super().__init__()
        #  инициализация
        uic.loadUi('book_info.ui', self)
        self.main_window = main_window
        self.con = self.main_window.con
        cur = self.con.cursor()

        #  получение данных об учебнике и долгах ученика
        name, author, grade, image, self.n = cur.execute(
            f'select name, author, grade, image, n from library where id = {book_id}').fetchone()

        # изображение
        image = f'images\\{image}.jpg'
        im = Image.open(image)
        x, y = im.size
        im = im.resize((280, 280 * y // x))
        file_name = 'edit_image.jpg'
        im.save(file_name)
        self.label_5.setPixmap(QPixmap(file_name))
        os.remove(file_name)

        # информация об учебнике
        self.lineEdit.setText(str(book_id))
        self.lineEdit_2.setText(name)
        self.lineEdit_3.setText(author)
        self.lineEdit_4.setText(str(grade))

        # доступ к кнопкам
        self.buttons_availability()

        self.pushButton.clicked.connect(self.book_operation)  # сдать учебник
        self.pushButton_2.clicked.connect(self.book_operation)  # получить учебник
        self.pushButton_3.clicked.connect(self.remove_book)  # удалить учебник из списка

    def buttons_availability(self):
        cur = self.con.cursor()
        book_id = self.lineEdit.text()
        books = str(
            cur.execute(f'select books from pupils where login = {self.main_window.login}').fetchone()[0]).split()
        list_books = [self.main_window.listWidget.item(i).text() for i in range(self.main_window.listWidget.count())]
        self.pushButton.setEnabled(book_id in books and f'{book_id};Сдать' not in list_books)
        self.pushButton_2.setEnabled(book_id not in books and self.n > 0 and f'{book_id};Получить' not in list_books)
        self.pushButton_3.setEnabled(book_id in (i.split(';')[0] for i in list_books))

    def book_operation(self):
        operation = self.sender().text()
        self.main_window.listWidget.addItem(f'{self.lineEdit.text()};{operation}')
        self.buttons_availability()  # доступ к кнопкам

    def remove_book(self):
        book_id = self.lineEdit.text()
        list_books = [self.main_window.listWidget.item(i).text().split(';')[0] for i in
                      range(self.main_window.listWidget.count())]
        self.main_window.listWidget.takeItem(list_books.index(book_id))  # удаление
        self.buttons_availability()  # доступ к кнопкам


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    sys.excepthook = except_hook
    app = QApplication(sys.argv)
    ex = MainPupilWindow(4, 'data_bases\\library.db')
    ex.show()
    sys.exit(app.exec_())
