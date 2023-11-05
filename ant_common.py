# Общие объекты и методы
from copy import deepcopy

import networkx as nx
from PyQt5.QtCore import QEvent
from PyQt5.QtGui import QIcon, QFont, QIntValidator, QDoubleValidator
from PyQt5.QtWidgets import QMessageBox

# Параметры алгоритма
default_args = {'heuristic_rel' : 2, 'pheromone_rel': 1, 'ant_number': 50,
                'pheromone_count': 10, 'evaporation_rate': 0.2, 'iters': 50,
                'gamma': 0.3, 'q0': 0.9}
args = deepcopy(default_args)

# Метод сброса параметров
def reset_args():
    global args
    args = deepcopy(default_args)

# Событие "новое ребро"
class NewEdge(QEvent):
    Type = QEvent.Type(QEvent.registerEventType())

    def __init__(self, start, end, weight=None):
        QEvent.__init__(self, NewEdge.Type)
        self.start = start
        self.end = end
        self.weight = weight

# Печатает путь для заданного графа
def get_path(graph: nx.DiGraph):
    start_v = new_v = 1
    path = str(start_v)
    if len(graph.edges) != len(graph.nodes) or len(graph.nodes) == 0:
        return 'No solution found'
    for _ in range(len(graph.edges)):
        new_v = list(graph.out_edges(new_v))
        if new_v:
            new_v = new_v[0][1]
            path += ' -> ' + str(new_v)
        else:
            return 'No solution found'
    return path

# Сообщение об ошибке
def input_error(text):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setText('Неверно введены данные')
    msg.setInformativeText(text)
    msg.setWindowTitle('Ошибка')
    msg.setWindowIcon(QIcon('warning.png'))
    msg.exec()


# Информационное окно
def info(text):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setText('Сведения о работе программы:')
    msg.setInformativeText(text)
    msg.setWindowTitle('Сведения')
    msg.setWindowIcon(QIcon('info.png'))
    msg.exec()

# Основной шрифт, валидаторы проверяющие тип ввода
f = QFont("Times", 10)
title_f = QFont("Times", 10, QFont.Bold, QFont.StyleItalic)
only_int = QIntValidator()
only_float = QDoubleValidator()
only_float.setNotation(QDoubleValidator.StandardNotation)

# Текст с инструкциями
default_text = '1. Click on input graph field to add vertex.\n' \
               '2. Click at vertex and draw to the other to add edge.\n' \
               '3. You can change weights in table above.\n' \
               '4. You can change parameters in options window.\n' \
               '5. When you finished construction of graph, click start to solve.\n' \
               '6. Here you will see the results.\n' \
               '7. Reset to repeat.'