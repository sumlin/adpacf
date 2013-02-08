# -*- coding: utf-8 -*-
__author__ = 'nivs'
from PyQt4 import QtCore, QtGui, uic
from itertools import product
from os.path import join
from prepareToTextBrowser import prepareToTextBrowser


def delTN(a):
    a = a.split('\n')
    b = []
    for i in a:
        if i:
            if i[-1] == '\t':
                b.append(i[:-1])
            else:
                b.append(i)
    return b


def addN(a):
    b = ''
    for i in a:
        b += i + '\n'
    return b[:-1]


class MainWindow(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        uic.loadUi(join('ui', 'main.ui'), self)
        self.var = [None, None, None, None, None]
        self.connect(self.butVar0, QtCore.SIGNAL("clicked()"), lambda: self.fVar(0))
        self.connect(self.butVar1, QtCore.SIGNAL("clicked()"), lambda: self.fVar(1))
        self.connect(self.butVar2, QtCore.SIGNAL("clicked()"), lambda: self.fVar(2))
        self.connect(self.butVar3, QtCore.SIGNAL("clicked()"), lambda: self.fVar(3))
        self.connect(self.butVar4, QtCore.SIGNAL("clicked()"), lambda: self.fVar(4))
        self.ind = 0
        self.move(500, 60)
        self.show()

    def fVar(self, index):
        self.var[index] = WorkWindow()
        self.var[index].move(self.x(), self.y())
        self.var[index].show()
        self.hide()


class WorkWindow(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        uic.loadUi(join('ui', 'work.ui'), self)
        self.data = []
        self.cur = -1
        self.butPrev.setDisabled(True)
        self.connect(self.butNext, QtCore.SIGNAL("clicked()"), self.fNext)
        self.connect(self.butPrev, QtCore.SIGNAL("clicked()"), self.fPrev)
        self.textWind.setFocus()

    def fWork(self, side):
        buf = delTN(self.textWind.toPlainText())
        if self.cur == -1:
            for i in range(len(buf)):
                try:
                    self.data[i][0] = buf[i]
                except IndexError:
                    self.data.append([buf[i]])
            for i in range(len(buf), len(self.data)):
                self.data.pop(i)
        else:
            if self.data[self.cur]:
                self.data[self.cur] = [self.data[self.cur][0]]
            for i in buf:
                self.data[self.cur].append(i)

        if self.cur + 1 == len(self.data) and side == 'Next' and not len(self.data) == 0:
            self.hide()
            self.analiz = Analiz(self.data)
            self.analiz.show()
        else:
            if side == 'Next':
                self.cur += 1
            elif side == 'Prev':
                self.cur -= 1
            try:
                if self.cur == -1:
                    buf = []
                    for i in self.data:
                        buf.append(i[0])
                    self.textWind.setPlainText(addN(buf))
                else:
                    self.textWind.setPlainText(addN(self.data[self.cur][1:]))
            except:
                self.textWind.setPlainText('')
            if self.cur == -1:
                self.label.setText("Введите список признаков классификации")
                self.butPrev.setDisabled(True)
            elif self.cur + 1 == len(self.data):
                self.label.setText(self.data[self.cur][0])
                self.butNext.setText('Finish')
            else:
                self.label.setText(self.data[self.cur][0])
                self.butPrev.setEnabled(True)
                self.butNext.setText('Next >>')
            self.textWind.setFocus()

    def fNext(self):
        self.fWork('Next')

    def fPrev(self):
        self.fWork('Prev')


class Analiz(QtGui.QWidget):
#    data = [['1 класс', '11', '111', '1111'], ['2 класс', '22', '222'], ['3 класс', '33', '333', '3333']]
#    Список вида [принзнак классификации, значения признака классификации]
    def __init__(self, data):
        QtGui.QWidget.__init__(self)
        self.lenParent = len(data)
        self.head = []
        for i in data:
            self.head.append(i[0])
        self.dictData = {}
        for i in data:
            for j in i:
                self.dictData[j] = i[0]
        self.data = []
        self.err = []
        for i in range(1, len(data) + 1):
            for j in product(*data[:i]):
                flagHead = False
                for h in self.head:
                    if h in j:
                        flagHead = True
                if not flagHead:
                    self.data.append(j)

        uic.loadUi(join('ui', 'analiz.ui'), self)
        self.ans = True
        self.ok = []
        self.start()

    def loopGenerator(self):  # Функция с циклом
        for i in self.data:
            er = False
            for j in self.err:
                if i[:len(j)] == j:
                    er = True
            if er:
                self.err.append(i)
            else:
                pr = ''
                for k in i:
                    pr += str(self.dictData[k]) + ' : ' + str(k) + '\n\n'
                self.label.setText(str(pr))
                yield
                if self.ans:
                    self.ok.append(i)
                else:
                    self.err.append(i)

    def start(self):  # Начало обхода цикла
        self._generator = self.loopGenerator()  # Инициализация цикла
        next(self._generator)

    def stop(self):  # Завершение цикла
        self.hide()
        self.choice = ChoiceWind(self.data, self.dictData, self.head)
        self.choice.show()

    def keyPressEvent(self, e):
        flag = False
        if e.key() == QtCore.Qt.Key_Y:
            self.ans = False  # Некие действия после нажатия клавиши
            flag = True
        elif e.key() == QtCore.Qt.Key_L:
            self.ans = True
            flag = True
        if flag:
            try:
                next(self._generator)  # Продвижение на следующую итерацию
            except StopIteration:
                self.stop()  # Циклы закончились, завершение заданий на этом виджете


class ChoiceWind(QtGui.QWidget):
    def __init__(self, data, dictData, head):
        QtGui.QWidget.__init__(self)
        uic.loadUi(join('ui', 'choice.ui'), self)
        self.data = data
        self.dictData = dictData
        self.head = head
        self.ln = len(self.head)
        for i in self.head:
            self.listWidget.addItem(i)
        self.connect(self.upButton, QtCore.SIGNAL("clicked()"), self.fUp)
        self.connect(self.downButton, QtCore.SIGNAL("clicked()"), self.fDown)
        self.printButton.clicked.connect(self.printData)
        self.listWidget.setItemSelected(self.listWidget.item(0), True)
        self.show()

    def change(self, n, k):
        self.listWidget.setItemSelected(self.listWidget.item(n), False)
        self.listWidget.insertItem(n, self.listWidget.takeItem(k))
        self.listWidget.setItemSelected(self.listWidget.item(k), True)

    def fUp(self):
        n = self.listWidget.currentRow()
        if not n == 0:
            self.change(n, n - 1)

    def fDown(self):
        n = self.listWidget.currentRow()
        if not n == self.ln:
            self.change(n, n + 1)

    def getItems(self):
        for i in range(self.listWidget.count()):
            yield self.listWidget.item(i)

    def printData(self):
        self.newHead = []
        for i in self.getItems():
            self.newHead.append(i.text())
        try:
            self.finish.print(self.data, self.dictData, self.head, self.newHead)
        except:
            self.finish = FinishWind(self.data, self.dictData, self.head, self.newHead)
            self.finish.show()


class FinishWind(QtGui.QWidget):
#   data - всевозможные сочетания всех элементов значений признаков классификаций
#   dictData - словарь соответствия элементов data и head
#   head - список признаков классификаций
    def __init__(self, data, dictData, head, newHead):
        QtGui.QWidget.__init__(self)
        uic.loadUi(join('ui', 'finish.ui'), self)
        self.print(data, dictData, head, newHead)

    def print(self, data, dictData, head, newHead):
        self.textBrowser.setPlainText(prepareToTextBrowser(data, dictData, head, newHead))
if __name__ == "__main__":
    import sys

    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
