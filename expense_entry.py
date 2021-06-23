import sys

from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import (
    QApplication,
    QLineEdit,
    QVBoxLayout,
    QGroupBox,
    QGridLayout,
    QWidget, QPushButton, QLabel, QSpinBox, QMenu, QMainWindow, qApp, QComboBox,
)


class MyApp(QWidget):

    def __init__(self):
        super().__init__()

        self.spinbox = QSpinBox()
        self.lbl4 = QLabel('Month')
        self.lbl2 = QLabel('Estimated Expenditure')
        self.lbl1 = QLabel('Income')
        self.lbl3 = QLabel('Expenses')
        self.initUI()

    def initUI(self):
        grid = QGridLayout()
        grid.addWidget(self.income(), 0, 0)
        grid.addWidget(self.data_entry(), 1, 0)

        self.setLayout(grid)

        self.setWindowTitle('Data Entry')
        self.setGeometry(400, 400, 600, 600)
        self.show()

    def income(self):
        groupbox = QGroupBox('Income And Expenditure')
        btn1 = QPushButton('Add', self)
        btn1.setCheckable(True)
        btn1.toggle()

        btn2 = QPushButton(self)
        btn2.setText('Clear')

        # For Income
        Income = QLineEdit()
        Income.setValidator(QIntValidator())

        Spent = QLineEdit()
        Spent.setValidator(QIntValidator())

        vbox = QVBoxLayout()
        vbox.addWidget(self.lbl1)
        vbox.addWidget(Income)

        vbox.addWidget(self.lbl2)
        vbox.addWidget(Spent)
        vbox.addWidget(btn1)
        vbox.addWidget(btn2)

        groupbox.setLayout(vbox)

        return groupbox

    def data_entry(self):
        groupbox = QGroupBox('Data Entry')
        btn3 = QPushButton('Add', self)
        btn3.setCheckable(True)
        btn3.toggle()

        btn4 = QPushButton(self)
        btn4.setText('Clear')

        self.lbl1 = QLabel('Item Name')
        Item_Name = QLineEdit('')

        # For categories
        self.lbl2 = QLabel('Categories')
        Categories = QComboBox(parent=self)
        Categories.addItems([
            "Water",
            "Electricity",
            "Rent",
            "Automobile-loan",
            "Home-loan",
            "Groceries",
            "Internet",
            "Phone",
            "Entertainment",
            "Travel",
            "Fuel",
            "Eat-Outs"
        ])

        # For Expenses
        Expenses = QLineEdit()
        Expenses.setValidator(QIntValidator())

        # For Month
        self.spinbox.setMinimum(1)
        self.spinbox.setMaximum(12)
        # self.spinbox.setRange(-10, 30)
        self.spinbox.setSingleStep(2)

        vbox = QVBoxLayout()
        # Item Vbox
        vbox.addWidget(self.lbl1)
        vbox.addWidget(Item_Name)
        # Categories Vbox
        vbox.addWidget(self.lbl2)
        vbox.addWidget(Categories)
        # expenses vbox
        vbox.addWidget(self.lbl3)
        vbox.addWidget(Expenses)
        # For month Vbox
        vbox.addWidget(self.lbl4)
        vbox.addWidget(self.spinbox)
        vbox.addStretch()
        vbox.addStretch(1)
        vbox.addWidget(btn3)
        vbox.addWidget(btn4)

        groupbox.setLayout(vbox)

        return groupbox


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())
