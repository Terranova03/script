import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableView, QLineEdit, QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QMessageBox, QInputDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Смотритель базы Бахматова Антона")
        self.resize(800, 600)

        self.connect_to_db()

        self.table_view = QTableView()
        self.table_view.setModel(self.model)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по заголовку")
        self.search_input.textChanged.connect(self.search_data)

        self.refresh_button = QPushButton("Обновить")
        self.refresh_button.clicked.connect(self.refresh_data)

        self.add_button = QPushButton("Добавить")
        self.add_button.clicked.connect(self.add_record)

        self.delete_button = QPushButton("Удалить")
        self.delete_button.clicked.connect(self.delete_record)

        layout = QVBoxLayout()
        layout.addWidget(self.search_input)
        layout.addWidget(self.table_view)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.refresh_button)
        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.delete_button)

        layout.addLayout(buttons_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    # Подключение к базе
    def connect_to_db(self):
        db = QSqlDatabase.addDatabase("QSQLITE")
        db.setDatabaseName("Laba3.db")

        if not db.open():
            QMessageBox.critical(self, "Ошибка", "Не удалось подключиться к базе данных")
            sys.exit(1)

        self.model = QSqlTableModel()
        self.model.setTable("posts")
        self.model.select()

    # Обновляем данные в таблице
    def refresh_data(self):
        self.model.select()

    # Поиск по заголовку
    def search_data(self):
        search_text = self.search_input.text()
        self.model.setFilter(f"title LIKE '%{search_text}%'")
        self.model.select()

    # Ввод данных для добавления новой записи
    def add_record(self):
        user_id, title, body = self.get_input_data()

        if user_id and title and body:
            print(f"user_id: {user_id}, title: {title}, body: {body}")

            query = QSqlQuery()
            query.prepare("INSERT INTO posts (user_id, title, body) VALUES (?, ?, ?)")

            query.addBindValue(user_id)
            query.addBindValue(title)
            query.addBindValue(body)

            if query.exec_():
                QMessageBox.information(self, "Успех", "Запись успешно добавлена!")
                self.model.select()
            else:
                error_message = query.lastError().text()
                QMessageBox.critical(self, "Ошибка", f"Не удалось добавить запись: {error_message}")
        else:
            QMessageBox.warning(self, "Внимание", "Пожалуйста, заполните все поля")


    # Удаление выбранной записи
    def delete_record(self):
        selected_index = self.table_view.currentIndex()

        if not selected_index.isValid():
            QMessageBox.warning(self, "Ошибка", "Выберите запись для удаления")
            return

        reply = QMessageBox.question(self, "Подтверждение", "Вы уверены, что хотите удалить запись?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.model.removeRow(selected_index.row())
            self.model.select()

    # Форма для получения данных
    def get_input_data(self):
        user_id, ok1 = QInputDialog.getText(self, "User ID", "Введите User ID:")
        title, ok2 = QInputDialog.getText(self, "Title", "Введите Title:")
        body, ok3 = QInputDialog.getText(self, "Body", "Введите Body:")

        if ok1 and ok2 and ok3:
            return user_id, title, body
        return None, None, None


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
