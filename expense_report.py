import sys
import os
import time
from datetime import datetime, timedelta

from PyQt5 import QtCore, QtGui, QtWidgets, QtChart

from expense_tracker import config, version


def quit_application():
    QtWidgets.QApplication.quit()


class ExpenseTracker(QtWidgets.QMainWindow, object):
    def __init__(self):
        super(ExpenseTracker, self).__init__()

        self.title = "Expense Tracker"
        self.version = version
        self.splash_screen = QtWidgets.QSplashScreen(
            QtGui.QPixmap(
                os.path.join(
                    os.path.dirname(__file__), "image", "splash.jpg"
                )
            ),
            QtCore.Qt.WindowStaysOnTopHint
        )
        self.show_splash_screen()
        self.setCentralWidget(ExpenseTrackerWidget())
        self.resize(1600, 960)
        self.hide_splash_screen()

    def show_splash_screen(self):
        self.splash_screen.show()
        self.splash_screen.showMessage(
            """
            <div style="align: center">
                <h1>
                    <font color='white'>{}</font>
                </h1>
                <h3>
                    <font color='white'>{}</font>
                </h3>
            </div>
            """.format(self.title, self.version),
            QtCore.Qt.AlignTop | QtCore.Qt.AlignCenter, QtCore.Qt.black
        )

    def hide_splash_screen(self, delay=None):
        time.sleep(delay or 0)
        self.splash_screen.finish(self)


class ExpenseTrackerWidget(QtWidgets.QWidget, object):
    def __init__(self):
        super(ExpenseTrackerWidget, self).__init__()

        #  Interface variables.
        self.clear_button = QtWidgets.QPushButton("Clear")
        self.quit_button = QtWidgets.QPushButton("Quit")
        self.add_button = QtWidgets.QPushButton("Add")
        self.history_button = QtWidgets.QPushButton("History")
        self.category = QtWidgets.QLineEdit()
        self.expense_field = QtWidgets.QLineEdit()
        self.config = config.Configuration()
        self.data = None
        self.current_month = config.CURRENT_MONTH

        # Chart.
        self.table_widget = QtWidgets.QTableWidget()
        self.table_widget.setColumnCount(2)
        self.headers = ("Category", "Expense")
        self.table_widget.setHorizontalHeaderLabels(self.headers)
        self.table_widget.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch
        )
        self.chart_view = PieChartViewer(title=self.current_month)

        self.setLayout(QtWidgets.QGridLayout())

        # Signals and Slots
        self.add_button.clicked.connect(self.add_element)
        self.quit_button.clicked.connect(quit_application)
        self.clear_button.clicked.connect(self.clear_table)
        self.history_button.clicked.connect(self.show_history)
        self.category.textChanged.connect(self.check_disable)
        self.expense_field.textChanged.connect(self.check_disable)
        self.table_widget.itemChanged.connect(self.on_table_edit)

        self.layout().addWidget(self.table_widget, 0, 0, 1, 2)
        self.layout().addWidget(self.chart_view, 0, 3, 1, 2)

        self.layout().addWidget(self.history_button, 2, 0)

        # Fill example data
        self.get_data()
        self.fill_table()
        self.chart_view.set_data(self.data)

    def get_data(self):
        self.data = self.config.get_section("data").get(self.current_month)

    def set_data(self):
        self.config.update_section(
            "data",
            {config.CURRENT_MONTH: self.get_table_data()}
        )

    def get_income(self):
        return self.data.get("income", 0)

    def get_savings(self):
        return self.data.get("savings", 0)

    def get_table_data(self):
        data = dict(self.data)
        for row in range(self.table_widget.rowCount()):
            category = self.table_widget.item(row, 0).text()
            expense = float(self.table_widget.item(row, 1).text())
            data["expenses"][category] = expense

        return data

    def on_table_edit(self, item):
        self.set_data()
        self.get_data()
        self.chart_view.set_data(self.data)

    def add_element(self):
        des = self.category.text()
        expense = self.expense_field.text()

        self.table_widget.insertRow(self.items)
        category_item = QtWidgets.QTableWidgetItem(des)
        expense_item = QtWidgets.QTableWidgetItem(
            "{:.2f}".format(float(expense))
        )
        expense_item.setTextAlignment(QtCore.Qt.AlignRight)

        self.table_widget.setItem(self.items, 0, category_item)
        self.table_widget.setItem(self.items, 1, expense_item)

        self.category.setText("")
        self.expense_field.setText("")

    def check_disable(self):
        if not self.category.text() or not self.expense_field.text():
            self.add_button.setEnabled(False)
        else:
            self.add_button.setEnabled(True)

    def clear_table(self):
        self.table_widget.clearContents()

    def setup_table(self):
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.setSortingEnabled(True)

    def fill_table(self):
        data = self.data.get("expenses").items()
        self.table_widget.setUpdatesEnabled(False)
        self.table_widget.blockSignals(True)
        self.table_widget.clearContents()
        self.table_widget.setColumnCount(len(self.headers))
        self.table_widget.setRowCount(len(data))

        for row, row_data in enumerate(data):
            category, expense = row_data
            self.table_widget.setItem(
                row, 0, QtWidgets.QTableWidgetItem(category)
            )
            self.table_widget.setItem(
                row, 1, QtWidgets.QTableWidgetItem(str(expense))
            )

        self.table_widget.setUpdatesEnabled(True)
        self.table_widget.blockSignals(False)

    def show_history(self):
        last_date = datetime.strptime(
            self.current_month, config.get_date_format()
        )
        month_keys = [self.current_month]

        for interval in range(1, 6):
            last_date = last_date - timedelta(weeks=4)
            month_keys.append(last_date.strftime(config.get_date_format()))

        config_data = self.config.get_section("data")

        history_widget = HistoryViewer(
            {key: config_data.get(key, {}) for key in month_keys},
            parent=self
        )
        history_widget.show()


class MainWindow(QtWidgets.QMainWindow, object):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Expense")
        self.setCentralWidget(ExpenseTrackerWidget())


class PieChartViewer(QtWidgets.QDialog):
    def __init__(self, title, data=None, parent=None):
        super(PieChartViewer, self).__init__(parent=parent)
        self.setLayout(QtWidgets.QGridLayout())
        self.chart_viewer = QtChart.QChartView()
        self.chart_viewer.setRenderHint(QtGui.QPainter.Antialiasing)
        self.chart_viewer.chart().legend().setVisible(False)
        self.chart_viewer.chart().setTitle(title)
        self.series = QtChart.QPieSeries()
        self.chart_viewer.chart().addSeries(self.series)

        self.income_label = QtWidgets.QLabel("Income")
        self.income_field = QtWidgets.QLabel()
        self.savings_label = QtWidgets.QLabel("Savings")
        self.savings_field = QtWidgets.QLabel()

        self.layout().addWidget(self.chart_viewer, 0, 0, 1, 16)
        self.layout().addWidget(self.income_label, 1, 1, 1, 1, QtCore.Qt.AlignLeading)
        self.layout().addWidget(self.income_field, 1, 2, 1, 1, QtCore.Qt.AlignLeading)
        self.layout().addWidget(self.savings_label, 1, 13, 1, 1, QtCore.Qt.AlignTrailing)
        self.layout().addWidget(self.savings_field, 1, 14, 1, 1, QtCore.Qt.AlignTrailing)

        self.data = None
        self.set_data(data)

    def set_data(self, data):
        self.data = data
        self.build()

    def build(self):
        if not self.data:
            return

        self.series.clear()

        for category, expense in self.data["expenses"].items():
            category_slice = QtChart.QPieSlice(category, float(expense))
            category_slice.setLabelVisible(True)
            category_slice.setLabelColor(QtCore.Qt.black)
            category_slice.setLabelPosition(QtChart.QPieSlice.LabelOutside)
            self.series.append(category_slice)

        self.income_field.setText(str(self.data.get("income", "")))
        self.savings_field.setText(str(self.data.get("savings", "")))


class HistoryViewer(QtWidgets.QDialog):
    def __init__(self, data, parent=None):
        super(HistoryViewer, self).__init__(parent=parent)
        self.setLayout(QtWidgets.QGridLayout())
        self.setWindowTitle("History viewer")
        self.setModal(False)
        self.setSizeGripEnabled(True)

        self.data = data
        self.show_history()
        self.resize(1440, 920)

    def clear(self):
        for child in self.layout().children():
            child.deleteLater()

    def get_collated_data(self):
        data = {}

        for month, monthly_data in self.data.items():
            data.setdefault("expenses", {})
            for category, expense in monthly_data["expenses"].items():
                data["expenses"].setdefault(category, 0)
                data["expenses"][category] += expense

            for key, value in monthly_data.items():
                if key == "expenses":
                    continue
                data.setdefault(key, 0)
                data[key] += value

        return data

    def show_history(self):
        self.clear()

        row = 0
        column = 0
        for month, monthly_data in self.data.items():
            if column < 3:
                self.layout().addWidget(
                    PieChartViewer(
                        month,
                        monthly_data
                    ),
                    row,
                    column
                )
                column += 1
            else:
                row += 1
                column = 0

        self.layout().addWidget(
            PieChartViewer(
                "Total",
                self.get_collated_data()
            ),
            row + 1, 0, 1, 3
        )


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.resize(800, 600)
    window.show()
    app.exec_()



