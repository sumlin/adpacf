# -*- coding: utf-8 -*-
__author__ = 'nivs'
from PyQt4 import QtCore, QtGui, uic
from itertools import product
from copy import copy

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
        uic.loadUi("main.ui", self)
        self.var = [None, None, None, None, None]
        self.connect(self.butVar0, QtCore.SIGNAL("clicked()"), lambda : self.fVar(0))
        self.connect(self.butVar1, QtCore.SIGNAL("clicked()"), lambda : self.fVar(1))
        self.connect(self.butVar2, QtCore.SIGNAL("clicked()"), lambda : self.fVar(2))
        self.connect(self.butVar3, QtCore.SIGNAL("clicked()"), lambda : self.fVar(3))
        self.connect(self.butVar4, QtCore.SIGNAL("clicked()"), lambda : self.fVar(4))
        self.ind = 0


    def fVar(self, index):
        self.hide()
        self.var[index] = WorkWindow()
        self.var[index].show()

class WorkWindow(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        uic.loadUi("work.ui", self)
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
                self.butNext.setText('Next >')
            self.textWind.setFocus()

    def fNext(self):
        self.fWork('Next')

    def fPrev(self):
        self.fWork('Prev')

class Analiz(QtGui.QWidget):
    def __init__(self, data):
        QtGui.QWidget.__init__(self)
        data = [['1 класс', '11', '111', '1111'], ['2 класс', '22', '222'], ['3 класс', '33', '333', '3333']]
        self.lenParent = len(data)
        self.head = []
        for i in data:
            self.head.append(i[0])
        self.slovar = {}
        for i in data:
            for j in i:
                self.slovar[j] = i[0]
        print(self.slovar)
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

        uic.loadUi("analiz.ui", self)
        self.ans = True
        self.ok = []
        self.start()

    def loopGenerator(self): # Функция с циклом
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
                    pr += str(self.slovar[k]) + ' : ' + str(k) + '\n\n'
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
        print(self.data)
#        self.finish = FinishWind(self.ok, self.lenParent, self.head)
#        self.finish.show()

    def keyPressEvent(self, e):
        flag = False
        if e.key() == QtCore.Qt.Key_Y:
            self.ans = False # Некие действия после нажатия клавиши
            flag = True
        elif e.key() == QtCore.Qt.Key_L:
            self.ans = True
            flag = True
        if flag:
            try:
                next(self._generator)  # Продвижение на следующую итерацию
            except StopIteration:
                self.stop()  # Циклы закончились, завершение заданий на этом виджете

class FinishWind(QtGui.QWidget):
    def __init__(self, data, lenOldData, head):
        QtGui.QWidget.__init__(self)
        uic.loadUi("finish.ui", self)
        pr = ''
        self.data = [('11',), ('111',), ('1111',), ('11', '22'), ('11', '222'), ('111', '22'), ('111', '222'), ('1111', '22'), ('1111', '222'), ('11', '22', '33'), ('11', '22', '333'), ('11', '22', '3333'), ('11', '222', '33'), ('11', '222', '333'), ('11', '222', '3333'), ('111', '22', '33'), ('111', '22', '333'), ('111', '22', '3333'), ('111', '222', '33'), ('111', '222', '333'), ('111', '222', '3333'), ('1111', '22', '33'), ('1111', '22', '333'), ('1111', '22', '3333'), ('1111', '222', '33'), ('1111', '222', '333'), ('1111', '222', '3333')]
        for i in self.  data:
            pr += str(i) + '\n\n'
        self.textBrowser.setPlainText(str(pr))

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
#   window = MainWindow()
    window = Analiz(1)
#    window = FinishWind('r', 2, 3)
    window.show()
    sys.exit(app.exec_())