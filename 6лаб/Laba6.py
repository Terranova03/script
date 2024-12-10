import sys
import pandas as pd
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QComboBox,
    QTextEdit, QFileDialog, QWidget, QLineEdit, QLabel
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class DataApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Analysis and Visualization")
        self.setGeometry(100, 100, 1200, 700)  # Увеличенное окно
        self.initUI()
        self.data = None  # Переменная для хранения данных
    
    def initUI(self):
        # Основной макет
        self.layout = QVBoxLayout()
        
        # Кнопка загрузки файла
        self.load_button = QPushButton("Load CSV")
        self.load_button.clicked.connect(self.load_data)
        
        # Поле для отображения статистики
        self.stats_field = QTextEdit()
        self.stats_field.setReadOnly(True)
        
        # Выбор типа графика
        self.graph_type = QComboBox()
        self.graph_type.addItems(["Line Chart", "Histogram", "Pie Chart"])
        self.graph_type.currentIndexChanged.connect(self.update_plot)
        
        # Поле для ввода новых данных
        self.manual_input_label = QLabel("Add New Data (Format: Date,Value1,Value2,Category):")
        self.manual_input = QLineEdit()
        self.manual_input.returnPressed.connect(self.add_data)
        
        # Холст для графика
        self.figure = Figure(figsize=(10, 6))  # Изначальный размер фигуры
        self.plot_canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        
        # Компоновка интерфейса
        self.layout.addWidget(self.load_button)
        self.layout.addWidget(self.stats_field)
        self.layout.addWidget(self.graph_type)
        self.layout.addWidget(self.manual_input_label)
        self.layout.addWidget(self.manual_input)
        self.layout.addWidget(self.plot_canvas)
        
        # Установка центрального виджета
        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)
    
    def load_data(self):
        # Открытие диалога для выбора файла
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)")
        if file_path:
            # Загрузка данных
            self.data = pd.read_csv(file_path)
            
            # Отображение статистики
            stats = f"Rows: {self.data.shape[0]}\nColumns: {self.data.shape[1]}\n\n"
            stats += str(self.data.describe())
            self.stats_field.setText(stats)
            
            # Построение графика
            self.update_plot()
    
    def update_plot(self):
        if self.data is None:
            return
        
        self.ax.clear()  # Очистка предыдущего графика
        graph_type = self.graph_type.currentText()
        
        if graph_type == "Line Chart":
            if "Date" in self.data.columns and "Value1" in self.data.columns:
                self.figure.set_size_inches(14, 6)  # Увеличение ширины фигуры
                self.data["Date"] = pd.to_datetime(self.data["Date"])  # Преобразование даты
                self.ax.plot(self.data["Date"], self.data["Value1"], label="Value1")
                self.ax.set_title("Line Chart (Date vs Value1)")
                self.ax.set_xlabel("Date")
                self.ax.set_ylabel("Value1")
                self.ax.tick_params(axis='x', rotation=45)  # Поворот меток оси X
                self.figure.tight_layout()  # Автоматическое размещение элементов
        
        elif graph_type == "Histogram":
            if "Date" in self.data.columns and "Value2" in self.data.columns:
                self.figure.set_size_inches(10, 6)  # Вернуть стандартный размер
                self.data["Date"] = pd.to_datetime(self.data["Date"])  # Преобразование даты
                grouped_data = self.data.groupby("Date")["Value2"].sum()  # Группировка по дате
                self.ax.bar(grouped_data.index, grouped_data.values, color='skyblue', edgecolor='black')
                self.ax.set_title("Histogram (Date vs Value2)")
                self.ax.set_xlabel("Date")
                self.ax.set_ylabel("Sum of Value2")
                self.ax.tick_params(axis='x', rotation=45)  # Поворот меток оси X
                self.figure.tight_layout()
        
        elif graph_type == "Pie Chart":
            if "Category" in self.data.columns:
                self.figure.set_size_inches(10, 6)  # Вернуть стандартный размер
                category_counts = self.data["Category"].value_counts()
                self.ax.pie(category_counts, labels=category_counts.index, autopct='%1.1f%%', startangle=90)
                self.ax.set_title("Pie Chart (Category)")
        
        self.ax.legend(loc='best')
        self.plot_canvas.draw()
    
    def add_data(self):
        if self.data is None:
            self.stats_field.setText("Please load data first!")
            return
        
        # Получение и обработка ввода
        new_data = self.manual_input.text()
        try:
            new_row = new_data.split(",")
            new_row_dict = {
                "Date": new_row[0],
                "Value1": float(new_row[1]),
                "Value2": float(new_row[2]),
                "Category": new_row[3]
            }
            self.data = pd.concat([self.data, pd.DataFrame([new_row_dict])], ignore_index=True)
            self.stats_field.setText("Data added successfully!")
            self.update_plot()
        except (IndexError, ValueError):
            self.stats_field.setText("Invalid input format! Use: Date,Value1,Value2,Category")

# Запуск приложения
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DataApp()
    window.show()
    sys.exit(app.exec_())
