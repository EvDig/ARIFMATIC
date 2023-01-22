import sqlite3
import sys

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow, QWidget

import CONSTANTS
from Number_check import is_digit, is_float, is_int
from pyuic import Ui_Dialog, Ui_Dialog_1, Ui_Dialog_2, Ui_Dialog_3, Ui_Dialog_4

click_on_button_1 = False
click_on_button_2 = False


class MainScreen(QMainWindow, Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initUI()
        self.settings = Settings()
        self.difficulty_choose = DifficultyChoose()
        self.database_call = DatabaseCall()

    def initUI(self):
        self.setWindowTitle(CONSTANTS.WINDOW_NAME)
        self.pushButton.clicked.connect(self.click_on_exit)
        self.pushButton_2.clicked.connect(self.click_on_play)
        self.pushButton_3.clicked.connect(self.click_on_settings)
        self.pushButton_4.clicked.connect(self.click_on_statistics)

    def click_on_exit(self):
        raise SystemExit(-1)

    def click_on_play(self):
        self.difficulty_choose.show()
        self.hide()

    def click_on_settings(self):
        self.settings.show()
        self.hide()

    def click_on_statistics(self):
        self.database_call.show()
        self.hide()


class DifficultyChoose(QWidget, Ui_Dialog_1):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initUI()
        self.problem_solving = ProblemSolving()

    def initUI(self):
        self.setWindowTitle(CONSTANTS.WINDOW_NAME)
        self.pushButton_2.clicked.connect(self.click_on_button)
        self.pushButton_4.clicked.connect(self.click_on_button)
        self.pushButton_3.clicked.connect(self.click_on_button)
        self.pushButton.clicked.connect(self.click_on_button)

    def click_on_button(self):
        level_choose = {'Легко': 1, 'Средне': 2, 'Сложно': 3, 'Очень сложно': 4}
        self.problem_solving.level = level_choose[(self.sender().text())]
        self.problem_solving.show()
        self.hide()


class ProblemSolving(QWidget, Ui_Dialog_2):
    def __init__(self, level=1):
        super().__init__()
        self.setupUi(self)
        self.initUI()
        self.level = level
        self.solved_problem = 0

    def initUI(self):
        self.setWindowTitle(CONSTANTS.WINDOW_NAME)
        self.pushButton.clicked.connect(self.check_answer)
        self.pushButton_2.clicked.connect(self.main_screen)

    def check_answer(self):
        problem_generator_and_checker = DataStructurizer()
        data = problem_generator_and_checker.check_answer_and_get_new(self.pushButton.text(),
                                                                      self.lineEdit.text(), self.level,
                                                                      self.label_2.text(),
                                                                      self.solved_problem)
        self.solved_problem = data[5]
        self.pushButton.setText(data[4])
        self.label_2.setText(data[0])  # сам пример
        self.label_5.setText(data[1])  # правильно или нет
        self.label_6.setText(data[2])  # корректное ли число
        self.label_4.setText(data[3])  # показ правильного ответа
        self.lineEdit.setText('')

    def main_screen(self):
        ex.show()
        self.hide()


class Settings(QWidget, Ui_Dialog_3):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initUI()

    def initUI(self):
        self.setWindowTitle(CONSTANTS.WINDOW_NAME)
        self.pushButton.clicked.connect(self.main_screen)
        self.pushButton_2.clicked.connect(self.click_on_button_1)
        self.pushButton_3.clicked.connect(self.click_on_button_2)

    def click_on_button_1(self):
        global click_on_button_1
        if click_on_button_1:
            self.pushButton_2.setStyleSheet('QPushButton {background: white;}')
            click_on_button_1 = False
        else:
            self.pushButton_2.setStyleSheet('QPushButton {background: green;}')
            click_on_button_1 = True

    def click_on_button_2(self):
        global click_on_button_2
        if click_on_button_2:
            self.pushButton_3.setStyleSheet('QPushButton {background: white;}')
            click_on_button_2 = False
        else:
            self.pushButton_3.setStyleSheet('QPushButton {background: green;}')
            click_on_button_2 = True

    def main_screen(self):
        ex.show()
        self.hide()


class DatabaseCall(QWidget, Ui_Dialog_4):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initUI()

    def initUI(self):
        self.setWindowTitle(CONSTANTS.WINDOW_NAME)
        self.pushButton.clicked.connect(self.statistics_update)
        self.pushButton_2.clicked.connect(self.main_screen)

    def statistics_update(self):
        database = DatabaseAgent()
        new_data = database.update_database()
        self.label_4.setText(new_data[0])
        self.label_3.setText(new_data[1])
        self.label_2.setText(new_data[2])

    def main_screen(self):
        ex.show()
        self.hide()


class ProblemGenerator:
    def __init__(self, level):
        self.level = level

    def problem_generator(self):
        import random
        level_requirements = {1: 10, 2: 25, 3: 40, 4: 50}
        with open('txt/Symbols.txt', encoding='utf-8') as f:
            read_data = list(map(str.strip, f.readlines()))
            math_symbols = read_data[self.level - 1]
            problems = []
            for action_number in range(self.level):
                randmath_symbol = str(
                    math_symbols.replace(' ', '')[random.randint(0, len(math_symbols.replace(' ', '')) - 1)])
                action = (str(random.randint(1, level_requirements[self.level])) +
                          randmath_symbol +
                          str(random.randint(1, level_requirements[self.level])))
                if self.level == 4:
                    bracket_chance = random.randint(1, 10)
                    if str(bracket_chance) in '1 2 3':
                        action_old = action[:]
                        action = str('(' + action_old + ')')
                if self.level > 1 and action_number != self.level - 1:
                    problems.append(action + randmath_symbol)
                else:
                    problems.append(action)
            full_problem = [' '.join(problems).replace(' ', ''),
                            round(eval(' '.join(problems).replace(' ', '')), 1)]
            solved_problem = full_problem[1]
            problem = full_problem[0]
            return problem, solved_problem


class DatabaseAgent(object):
    def __init__(self):
        self.database_name = CONSTANTS.DATABASE_NAME

    def add_to_database(self, level, problem, solved_problem, user_answer, correct):
        con = sqlite3.connect(self.database_name)
        cur = con.cursor()
        cur.execute("""INSERT INTO problems(level,problem,corrans,userans,correct)
                                VALUES(?,?,?,?,?)""", (level, problem, solved_problem,
                                                       user_answer, correct)).fetchall()
        con.commit()
        con.close()

    def update_database(self):
        con = sqlite3.connect(self.database_name)
        cur = con.cursor()
        problems_done = len(cur.execute("""SELECT id FROM problems""").fetchall())
        correct_answers = len(cur.execute("""SELECT id FROM problems WHERE correct = 1""").fetchall())
        correct_answers_percent = f'{(correct_answers / problems_done) * 100:.2f}'
        con.close()
        return str(problems_done), str(correct_answers), str(correct_answers_percent)


class DataStructurizer(object):
    def __init__(self):
        self.solved_problem = 0
        self.problem = ''
        self.correct = 0
        self.label_5_text = ''
        self.label_6_text = ''
        self.label_4_text = ''

    def check_answer_and_get_new(self, button_text, user_answer, level, problem, solved_problem):
        self.solved_problem = solved_problem
        self.problem = problem
        global click_on_button_1, click_on_button_2
        database = DatabaseAgent()
        p = ProblemGenerator(level)
        if button_text == 'Ответить' and is_digit(user_answer):
            if is_float(user_answer) and not is_int(user_answer):
                user_answer = (str(round(float(user_answer))))
            if int(user_answer) == int(self.solved_problem):
                self.correct = 1
                if not click_on_button_2:
                    self.label_5_text = 'Правильно'
                database.add_to_database(level, self.problem, self.solved_problem,
                                         int(user_answer), self.correct)
            else:
                self.correct = 0
                if not click_on_button_2:
                    self.label_5_text = 'Неправильно'
                database.add_to_database(level, self.problem, self.solved_problem,
                                         int(user_answer), self.correct)
            full_problem = p.problem_generator()
            self.problem = full_problem[0]
            self.solved_problem = full_problem[1]
            if click_on_button_1:
                self.label_4_text = 'Правильный ответ: ' + str(self.solved_problem)
        elif button_text == 'Начать':
            full_problem = p.problem_generator()
            self.problem = full_problem[0]
            self.solved_problem = full_problem[1]
            if click_on_button_1:
                self.label_4_text = 'Правильный ответ: ' + str(self.solved_problem)
        else:
            self.label_6_text = 'Введите целое число в ответ'

        return self.problem, self.label_5_text, self.label_6_text, self.label_4_text, 'Ответить', \
               self.solved_problem


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainScreen()
    ex.show()
    sys.exit(app.exec())
