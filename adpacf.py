# -*- coding: utf-8 -*-
__author__ = 'nivs'
from PyQt4 import QtCore, QtGui, uic
from itertools import product
from os.path import join, exists
from prepareToTextBrowser import prepareToTextBrowser
import shelve


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
        self.nameFile = [None, None, None, None, None]
        self.connect(self.butVar1, QtCore.SIGNAL("clicked()"), lambda: self.fVar(1))
        self.connect(self.butVar2, QtCore.SIGNAL("clicked()"), lambda: self.fVar(2))
        self.connect(self.butVar3, QtCore.SIGNAL("clicked()"), lambda: self.fVar(3))
        self.connect(self.butVar4, QtCore.SIGNAL("clicked()"), lambda: self.fVar(4))
        self.connect(self.butVar5, QtCore.SIGNAL("clicked()"), lambda: self.fVar(5))
        self.ind = 0
        self.move(50, 60)
        self.show()

    def fVar(self, index):
        self.nameFile[index] = str(index) + "_data.db"
        self.var[index] = SelectWind(self, index, self.nameFile[index])
        self.var[index].move(self.x(), self.y())
        self.var[index].show()
        self.hide()


class SelectWind(QtGui.QWidget):
    def __init__(self, parent, var, nameFile):
        QtGui.QWidget.__init__(self)
        uic.loadUi(join('ui', 'select.ui'), self)
        self.var = var
        self.nameFile = nameFile
        self.file = shelve.open(self.nameFile)
        self.butVar.clicked.connect(self.fVar)
        self.parent = parent
        self.butInput.clicked.connect(self.fInput)
        self.butAnaliz.clicked.connect(self.fAnaliz)
        self.butOutput.clicked.connect(self.fOutput)
        self.butDelete.clicked.connect(self.fDelete)
        try:
            if self.file['input']:
                self.butAnaliz.setEnabled(True)
                self.butDelete.setEnabled(True)
        except KeyError:
            self.butAnaliz.setEnabled(False)
            self.butOutput.setEnabled(False)
            self.butDelete.setEnabled(False)
        try:
            if self.file['analiz']:
                self.butOutput.setEnabled(True)
        except KeyError:
            self.butOutput.setEnabled(False)

    def fVar(self):
        self.parent.show()
        self.file.close()
        self.close()

    def fInput(self):
        self.file.close()
        self.input = InputWind(self, self.nameFile)
        self.input.move(self.x(), self.y())
        self.hide()
        self.input.show()

    def fAnaliz(self):
        self.file.close()
        self.analiz = AnalizWind(self, self.nameFile)
        self.analiz.move(self.x(), self.y())
        self.hide()
        self.analiz.show()

    def fOutput(self):
        self.file.close()
        self.output = OutputWind(self, self.nameFile)
        self.output.move(self.x(), self.y())
        self.hide()
        self.output.show()

    def fDelete(self):
        self.input = DeleteWind(self, self.nameFile)
        self.input.move(self.x(), self.y())
        self.hide()
        self.input.show()

    def fBack(self):
        self.file.close()
        self.parent.show()
        self.close()

class InputWind(QtGui.QWidget):
    def __init__(self, parent, nameFile):
        QtGui.QWidget.__init__(self)
        uic.loadUi(join('ui', 'input.ui'), self)
        self.nameFile = nameFile
        self.file = shelve.open(self.nameFile)
        self.parent = parent
        try:
            self.newFile = False
            self.data = self.file['input']
        except KeyError:
            self.newFile = True
            self.data = []
        self.cur = -1
        self.butPrev.setDisabled(True)
        self.connect(self.butNext, QtCore.SIGNAL("clicked()"), self.fNext)
        self.connect(self.butPrev, QtCore.SIGNAL("clicked()"), self.fPrev)
        self.butBack.clicked.connect(self.fBack)
        self.textWind.setFocus()

    def fInput(self, side):
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
            self.file['input'] = self.data
            self.hide()
            self.analiz = AnalizWind(self, self.file)
            self.analiz.move(self.x(), self.y())
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
        self.fInput('Next')

    def fPrev(self):
        self.fInput('Prev')

    def fBack(self):
        self.file.close()
        self.parent.show()
        self.close()


class AnalizWind(QtGui.QWidget):
#    Список вида [принзнак классификации, значения признака классификации]
    def __init__(self, parent, nameFile):
        QtGui.QWidget.__init__(self)
        uic.loadUi(join('ui', 'analiz.ui'), self)
        self.nameFile = nameFile
        self.file = shelve.open(self.nameFile)
        self.parent = parent
        self.butBack.clicked.connect(self.fBack)
        _data = self.file['input']
        self.lenParent = len(_data)
        self.head = []
        for i in _data:
            self.head.append(i[0])
        self.dictData = {}
        for i in _data:
            for j in i:
                self.dictData[j] = i[0]
        self.data = []
        self.err = []
        for i in range(1, len(_data) + 1):
            for j in product(*_data[:i]):
                flagHead = False
                for h in self.head:
                    if h in j:
                        flagHead = True
                if not flagHead:
                    self.data.append(j)
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
        self.file['analiz'] = [self.data, self.dictData, self.head]
        self.output = OutputWind(self, self.nameFile)
        self.output.move(self.x(), self.y())
        self.output.show()

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

    def fBack(self):
        self.file.close()
        self.parent.show()
        self.close()


class OutputWind(QtGui.QWidget):
    def __init__(self, parent, nameFile):
        QtGui.QWidget.__init__(self)
        uic.loadUi(join('ui', 'output.ui'), self)
        self.nameFile = nameFile
        self.file = shelve.open(self.nameFile)
        self.parent = parent
        self.data = self.file['analiz'][0]
        self.dictData = self.file['analiz'][1]
        self.head = self.file['analiz'][2]
        self.ln = len(self.head)
        for i in self.head:
            self.listWidget.addItem(i)
        self.connect(self.butUp, QtCore.SIGNAL("clicked()"), self.fUp)
        self.connect(self.butDown, QtCore.SIGNAL("clicked()"), self.fDown)
        self.butPrint.clicked.connect(self.printData)
        self.butBack.clicked.connect(self.fBack)
        self.listWidget.setItemSelected(self.listWidget.item(0), True)

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
            self.finish = PrintWind(self.data, self.dictData, self.head, self.newHead)
            self.finish.show()

    def fBack(self):
        self.file.close()
        self.parent.show()
        self.close()


class PrintWind(QtGui.QWidget):
#   data - всевозможные сочетания всех элементов значений признаков классификаций
#   dictData - словарь соответствия элементов data и head
#   head - список признаков классификаций
    def __init__(self, data, dictData, head, newHead):
        QtGui.QWidget.__init__(self)
        uic.loadUi(join('ui', 'print.ui'), self)
        self.print(data, dictData, head, newHead)

    def print(self, data, dictData, head, newHead):
        self.textBrowser.setPlainText(prepareToTextBrowser(data, dictData, head, newHead))


class DeleteWind(QtGui.QWidget):
    def __init__(self, parent, nameFile):
        QtGui.QWidget.__init__(self)
        uic.loadUi(join('ui', 'delete.ui'), self)
        self.nameFile = nameFile
        self.file = shelve.open(self.nameFile)
        self.parent = parent
        self.butData.clicked.connect(self.fData)
        self.butAnaliz.clicked.connect(self.fAnaliz)
        self.butClose.clicked.connect(self.fClose)

    def fData(self):
        pass

    def fAnaliz(self):
        pass

    def fClose(self):
        pass


if __name__ == "__main__":
    import sys

    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
