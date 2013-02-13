# -*- coding: utf-8 -*-
__author__ = 'nivs'
from PyQt4 import QtCore, QtGui, uic
from itertools import product
from os.path import join, exists
from os import remove
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

    def fVar(self, index):
        index -= 1
        self.nameFile[index] = str(index + 1) + "_data.db"
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
        self.initial()

    def showEvent(self, e):
        self.initial()

    def closeEvent(self, e):
        try:
            if self.file['input'] is not None:
                self.file.close()
            else:
                self.file.close()
                remove(self.nameFile)
        except:
            self.file.close()
            remove(self.nameFile)

    def initial(self):
        try:
            if self.file['input'][0] is not None:
                self.butAnaliz.setEnabled(True)
                self.butDelete.setEnabled(True)
        except:
            self.butAnaliz.setEnabled(False)
            self.butOutput.setEnabled(False)
            self.butDelete.setEnabled(False)
        try:
            if self.file['analiz'][0] is not None:
                self.butOutput.setEnabled(True)

        except:
            self.butOutput.setEnabled(False)

    def fVar(self):
        self.parent.show()
        self.close()

    def fInput(self):
        self.input = InputWind(self, self.file)
        self.input.move(self.x(), self.y())
        self.hide()
        self.input.show()

    def fAnaliz(self):
        self.analiz = AnalizWind(self, self.file)
        self.analiz.move(self.x(), self.y())
        self.hide()
        self.analiz.show()

    def fOutput(self):
        self.output = OutputWind(self, self.file)
        self.output.move(self.x(), self.y())
        self.hide()
        self.output.show()

    def fDelete(self):
        self.delete = DeleteWind(self, self.file)
        self.delete.move(self.x(), self.y())
        self.hide()
        self.delete.show()

    def fBack(self):
        self.parent.show()
        self.close()


class InputWind(QtGui.QWidget):
    def __init__(self, parent, file):
        QtGui.QWidget.__init__(self)
        uic.loadUi(join('ui', 'input.ui'), self)
        self.file = file
        self.parent = parent
        self.initial()
        self.butPrev.setDisabled(True)
        self.connect(self.butNext, QtCore.SIGNAL("clicked()"), self.fNext)
        self.connect(self.butPrev, QtCore.SIGNAL("clicked()"), self.fPrev)
        self.butBack.clicked.connect(self.fBack)
        self.textWind.setFocus()

    def showEvent(self, e):
        self.initial()

    def initial(self):
        try:
            if self.file['input'][0] is not None:
                self.newFile = False
                self.data = self.file['input']
                self.cur = 0
                self.textWind.setPlainText(addN(self.data[self.cur][1:]))
                self.fInput('Prev')
                self.butNext.setText('Next >>')
        except:
            self.newFile = True
            self.data = []
            self.cur = -1

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
        self.parent.show()
        self.close()


class AnalizWind(QtGui.QWidget):
#    Список вида [принзнак классификации, значения признака классификации]
    def __init__(self, parent, file):
        QtGui.QWidget.__init__(self)
        uic.loadUi(join('ui', 'analiz.ui'), self)
        self.file = file
        self.parent = parent
        self.butBack.clicked.connect(self.fBack)

    def showEvent(self, e):
        self.oldData = self.file['input']
        self.lenParent = len(self.oldData)
        self.head = []
        for i in self.oldData:
            self.head.append(i[0])
        self.dictData = {}
        for i in self.oldData:
            for j in i:
                self.dictData[j] = i[0]
        self.data = []
        self.err = []
        for i in range(1, len(self.oldData) + 1):
            for j in product(*self.oldData[:i]):
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
                if i == self.data[-1]:
                    raise StopIteration

    def start(self):  # Начало обхода цикла
        self._generator = self.loopGenerator()  # Инициализация цикла
        next(self._generator)

    def stop(self):  # Завершение цикла
        self.hide()
        self.file['analiz'] = [self.ok, self.dictData, self.unzip(self.dictTrust(self.ok, self.dictData, self.head))]
        self.output = OutputWind(self, self.file)
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
        self.parent.show()
        self.close()

    # Смотрим, какие признаки классификации остались
    def dictTrust(self, data, dictData, head):
        trust = []
        for i in head:
            for j in data:
                for k in j:
                    if i == dictData[k]:
                        trust.append(dictData[k])
        return trust

    # Возвращает уникальные значения (убирает повторы)
    def unzip(self, data):
        seen = set()
        seen_add = seen.add
        return [x for x in data if x not in seen and not seen_add(x)]


class OutputWind(QtGui.QWidget):
    def __init__(self, parent, file):
        QtGui.QWidget.__init__(self)
        uic.loadUi(join('ui', 'output.ui'), self)
        self.file = file
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
            self.finish.show()
        except:
            self.finish = PrintWind(self.data, self.dictData, self.head, self.newHead)
            self.finish.show()

    def fBack(self):
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
    def __init__(self, parent, file):
        QtGui.QWidget.__init__(self)
        uic.loadUi(join('ui', 'delete.ui'), self)
        self.file = file
        self.parent = parent
        self.butData.clicked.connect(self.fData)
        self.butAnaliz.clicked.connect(self.fAnaliz)
        self.butClose.clicked.connect(self.fClose)
        self.butData.setEnabled(True)
        self.butAnaliz.setEnabled(False)
        try:
            if self.file['analiz'] is not None:
                self.butAnaliz.setEnabled(True)
        except:
            pass

    def fData(self):
        del self.file['input']
        self.fClose()

    def fAnaliz(self):
        del self.file['analiz']
        self.butAnaliz.setEnabled(False)
        self.parent.butOutput.setEnabled(False)

    def fClose(self):
        self.close()
        self.parent.show()


if __name__ == "__main__":
    import sys

    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
