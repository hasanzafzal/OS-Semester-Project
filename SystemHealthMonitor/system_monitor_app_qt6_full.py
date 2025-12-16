import sys
import psutil
import time
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QStackedWidget, QTableWidget, QTableWidgetItem
)
from PyQt6.QtCore import QTimer, Qt
import pyqtgraph as pg

# ================= MAIN WINDOW =================

class SystemMonitor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("System Health Monitor")
        self.setGeometry(200, 100, 900, 500)

        self.dark_mode = True

        # --------- Main Layout ----------
        main_layout = QHBoxLayout(self)

        # --------- Sidebar ----------
        sidebar = QVBoxLayout()
        sidebar.setSpacing(10)

        self.btn_dashboard = QPushButton("Dashboard")
        self.btn_processes = QPushButton("Processes")
        self.btn_toggle_theme = QPushButton("Toggle Theme")

        sidebar.addWidget(self.btn_dashboard)
        sidebar.addWidget(self.btn_processes)
        sidebar.addStretch()
        sidebar.addWidget(self.btn_toggle_theme)

        sidebar_widget = QWidget()
        sidebar_widget.setLayout(sidebar)
        sidebar_widget.setFixedWidth(160)

        # --------- Pages ----------
        self.pages = QStackedWidget()

        self.dashboard_page = self.create_dashboard_page()
        self.process_page = self.create_process_page()

        self.pages.addWidget(self.dashboard_page)
        self.pages.addWidget(self.process_page)

        # --------- Connections ----------
        self.btn_dashboard.clicked.connect(lambda: self.pages.setCurrentIndex(0))
        self.btn_processes.clicked.connect(lambda: self.pages.setCurrentIndex(1))
        self.btn_toggle_theme.clicked.connect(self.toggle_theme)

        main_layout.addWidget(sidebar_widget)
        main_layout.addWidget(self.pages)

        self.setLayout(main_layout)
        self.apply_theme()

        # --------- Timer ----------
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_dashboard)
        self.timer.timeout.connect(self.update_process_table)
        self.timer.start(1000)

    # ================= DASHBOARD =================

    def create_dashboard_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        self.cpu_label = QLabel()
        self.mem_label = QLabel()
        self.disk_label = QLabel()
        self.time_label = QLabel()

        # Graphs
        self.cpu_data = []
        self.mem_data = []

        self.graph = pg.PlotWidget(title="CPU & Memory Usage (%)")
        self.graph.setYRange(0, 100)
        self.cpu_curve = self.graph.plot(pen='r', name="CPU")
        self.mem_curve = self.graph.plot(pen='g', name="Memory")

        layout.addWidget(self.cpu_label)
        layout.addWidget(self.mem_label)
        layout.addWidget(self.disk_label)
        layout.addWidget(self.graph)
        layout.addWidget(self.time_label)

        return page

    # ================= PROCESS TABLE =================

    def create_process_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        title = QLabel("Top 5 CPU-Consuming Processes")
        title.setStyleSheet("font-size:18px; font-weight:bold;")

        self.process_table = QTableWidget(5, 4)
        self.process_table.setHorizontalHeaderLabels(
            ["PID", "Name", "CPU %", "Memory %"]
        )
        self.process_table.horizontalHeader().setStretchLastSection(True)

        layout.addWidget(title)
        layout.addWidget(self.process_table)

        return page

    # ================= UPDATE FUNCTIONS =================

    def update_dashboard(self):
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        self.cpu_label.setText(f"CPU Usage: {cpu}%")
        self.mem_label.setText(f"Memory Usage: {mem.percent}%")
        self.disk_label.setText(f"Disk Usage: {disk.percent}%")
        self.time_label.setText("Last Updated: " + datetime.now().strftime("%H:%M:%S"))

        self.cpu_data.append(cpu)
        self.mem_data.append(mem.percent)

        if len(self.cpu_data) > 60:
            self.cpu_data.pop(0)
            self.mem_data.pop(0)

        self.cpu_curve.setData(self.cpu_data)
        self.mem_curve.setData(self.mem_data)

    def update_process_table(self):
        processes = sorted(
            psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']),
            key=lambda p: p.info['cpu_percent'],
            reverse=True
        )[:5]

        for row, proc in enumerate(processes):
            self.process_table.setItem(row, 0, QTableWidgetItem(str(proc.info['pid'])))
            self.process_table.setItem(row, 1, QTableWidgetItem(proc.info['name']))
            self.process_table.setItem(row, 2, QTableWidgetItem(f"{proc.info['cpu_percent']}"))
            self.process_table.setItem(row, 3, QTableWidgetItem(f"{proc.info['memory_percent']:.2f}"))

    # ================= THEME =================

    def apply_theme(self):
        if self.dark_mode:
            self.setStyleSheet("""
                QWidget { background-color:#121212; color:white; }
                QPushButton { background:#1f1f1f; padding:8px; }
                QTableWidget { background:#1e1e1e; }
            """)
        else:
            self.setStyleSheet("""
                QWidget { background-color:#f4f4f4; color:black; }
                QPushButton { background:#dddddd; padding:8px; }
                QTableWidget { background:white; }
            """)

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()

# ================= RUN APP =================

app = QApplication(sys.argv)
window = SystemMonitor()
window.show()
sys.exit(app.exec())

