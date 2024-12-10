import sys
import asyncio
import aiohttp
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QProgressBar,
    QLabel, QTableWidget, QTableWidgetItem, QHBoxLayout, QMessageBox, QInputDialog
)
from PyQt5.QtCore import QThread, pyqtSignal, QTimer

# Подключение к базе данных
DB_PATH = 'Laba5.db'
TABLE_CREATION_QUERY = '''CREATE TABLE IF NOT EXISTS posts (
                            id INTEGER PRIMARY KEY AUTOINCREMENT, 
                            userId INTEGER, 
                            title TEXT, 
                            body TEXT)'''


# Поток для загрузки данных
class DataLoaderThread(QThread):
    data_loaded_signal = pyqtSignal(list)

    async def fetch_data(self):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://jsonplaceholder.typicode.com/posts") as response:
                await asyncio.sleep(2)  # Задержка
                return await response.json()

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        data = loop.run_until_complete(self.fetch_data())
        self.data_loaded_signal.emit(data)
        loop.close()


# Поток для сохранения данных
class DataSaverThread(QThread):
    progress_signal = pyqtSignal(int)
    data_saved_signal = pyqtSignal()

    def __init__(self, data):
        super().__init__()
        self.data = data

    def run(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(TABLE_CREATION_QUERY)

        for index, post in enumerate(self.data):
            cursor.execute("INSERT OR REPLACE INTO posts (id, userId, title, body) VALUES (?, ?, ?, ?)",
                           (post['id'], post['userId'], post['title'], post['body']))
            conn.commit()
            self.progress_signal.emit(int((index + 1) / len(self.data) * 100))
            QThread.msleep(50)  # Задержка

        conn.close()
        self.data_saved_signal.emit()


# Главное окно приложения
class AppWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)

        self.load_button = QPushButton('Загрузить данные')
        self.load_button.clicked.connect(self.load_data)
        self.layout.addWidget(self.load_button)

        self.progress_bar = QProgressBar(self)
        self.layout.addWidget(self.progress_bar)

        self.status_label = QLabel('Ожидание...', self)
        self.layout.addWidget(self.status_label)

        self.data_table = QTableWidget(self)
        self.data_table.setColumnCount(4)
        self.data_table.setHorizontalHeaderLabels(['ID', 'User ID', 'Title', 'Body'])
        self.layout.addWidget(self.data_table)

        # Добавление кнопок
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Добавить запись")
        self.add_button.clicked.connect(self.add_record)
        self.delete_button = QPushButton("Удалить запись")
        self.delete_button.clicked.connect(self.delete_record)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.delete_button)
        self.layout.addLayout(button_layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_for_updates)
        self.timer.start(100000)  # каждые 100 секунд

    def load_data(self):
        self.status_label.setText("Загрузка данных...")
        self.progress_bar.setValue(0)

        # Поток для загрузки данных
        self.loader_thread = DataLoaderThread()
        self.loader_thread.data_loaded_signal.connect(self.on_data_loaded)
        self.loader_thread.start()

    def on_data_loaded(self, data):
        self.status_label.setText("Данные загружены, сохранение в базу...")
        self.progress_bar.setValue(0)

        # Поток для сохранения данных
        self.saver_thread = DataSaverThread(data)
        self.saver_thread.data_saved_signal.connect(self.on_data_saved)
        self.saver_thread.progress_signal.connect(self.progress_bar.setValue)  # Подключение сигнала
        self.saver_thread.start()


    def on_data_saved(self):
        self.status_label.setText("Данные сохранены в базу.")
        self.load_saved_data()

    def load_saved_data(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM posts")
        rows = cursor.fetchall()
        self.data_table.setRowCount(len(rows))

        for row_index, row in enumerate(rows):
            for col_index, value in enumerate(row):
                self.data_table.setItem(row_index, col_index, QTableWidgetItem(str(value)))

        conn.close()

    def add_record(self):
        user_id, ok1 = QInputDialog.getText(self, "User ID", "Введите User ID:")
        title, ok2 = QInputDialog.getText(self, "Title", "Введите Title:")
        body, ok3 = QInputDialog.getText(self, "Body", "Введите Body:")

        if ok1 and ok2 and ok3:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(TABLE_CREATION_QUERY)
            cursor.execute("INSERT INTO posts (userId, title, body) VALUES (?, ?, ?)",
                           (user_id, title, body))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Успех", "Запись успешно добавлена!")
            self.load_saved_data()

    def delete_record(self):
        current_row = self.data_table.currentRow()
        if current_row >= 0:
            post_id = self.data_table.item(current_row, 0).text()
            reply = QMessageBox.question(
                self, "Подтверждение удаления", f"Вы уверены, что хотите удалить запись ID {post_id}?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM posts WHERE id = ?", (post_id,))
                conn.commit()
                conn.close()
                self.load_saved_data()

    def check_for_updates(self):
        self.status_label.setText("Проверка обновлений...")
        self.load_data()


# Запуск приложения
app = QApplication(sys.argv)
window = AppWindow()
window.setWindowTitle("Асинхронное приложение с таблицей")
window.resize(800, 600)
window.show()
sys.exit(app.exec_())
