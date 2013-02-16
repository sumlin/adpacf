# -*- coding: utf-8 -*-
'''
Построение структур по курсу "Системный анализ в социальной сфере.

Предоставляет возможность построения структуры предприятия
с инвариацией подуровней.

'''

__author__ = 'sumlin'

from PyQt4 import QtCore, QtGui, uic
from itertools import product
from os.path import join
from os import remove
import shelve

from prepareToTextBrowser import prepareToTextBrowser


# Разбивает строку на список.
# Необходима для корректного чтения из PlainTextEdit.
def delTN(a):
    a = a.split('\n')
    b = []
    for i in a:
        b.append(i)
    return b


# Собирает список в строку.
# Необходима для корректной записи в PlainTextEdit.
def addN(a):
    b = ''
    for i in a:
        b += i + '\n'
    return b[:-1]


class MainWindow(QtGui.QWidget):
    '''
    Диалог начального окна. Отображает окно выбора вариантов.
    '''
    def __init__(self):
        QtGui.QWidget.__init__(self)
        uic.loadUi(join('ui', 'main.ui'), self)
        self.var = [None, None, None, None, None]
        self.nameFile = [None, None, None, None, None]
        self.connect(self.butVar1, QtCore.SIGNAL("clicked()"),
                     lambda: self.fVar(1))
        self.connect(self.butVar2, QtCore.SIGNAL("clicked()"),
                     lambda: self.fVar(2))
        self.connect(self.butVar3, QtCore.SIGNAL("clicked()"),
                     lambda: self.fVar(3))
        self.connect(self.butVar4, QtCore.SIGNAL("clicked()"),
                     lambda: self.fVar(4))
        self.connect(self.butVar5, QtCore.SIGNAL("clicked()"),
                     lambda: self.fVar(5))
        self.ind = 0
        self.move(50, 60)

        # Добавление горячих клавишь. 1...5 - вариант №1...5
        for i in range(1, 6):
            self.addAction(QtGui.QAction(self, shortcut=str(i),
                                         triggered=lambda: self.fVar(i)))

    # Создание проекта для работы с новым вариантом.
    # Открытие окна меню.
    # index - номер варианта.
    def fVar(self, index):
        index -= 1
        self.nameFile[index] = str(index + 1) + "_data.db"
        self.var[index] = SelectWind(self, index, self.nameFile[index])
        self.var[index].move(self.x(), self.y())
        self.var[index].show()
        self.hide()


class SelectWind(QtGui.QWidget):
    '''
    Диалог меню проекта выбранного варианта.
    '''
    def __init__(self, parent, var, nameFile):
        QtGui.QWidget.__init__(self)
        uic.loadUi(join('ui', 'select.ui'), self)
        self.nameFile = nameFile
        self.file = shelve.open(self.nameFile)
        self.parent = parent
        self.butVar.clicked.connect(self.fVar)
        self.butInput.clicked.connect(self.fInput)
        self.butAnaliz.clicked.connect(self.fAnaliz)
        self.butOutput.clicked.connect(self.fOutput)
        self.butDelete.clicked.connect(self.fDelete)
        self.addAction(QtGui.QAction(self, shortcut=str(1),
                                     triggered=self.fVar))
        self.addAction(QtGui.QAction(self, shortcut=str(2),
                                     triggered=self.fInput))
        self.addAction(QtGui.QAction(self, shortcut=str(3),
                                     triggered=self.fAnaliz))
        self.addAction(QtGui.QAction(self, shortcut=str(4),
                                     triggered=self.fOutput))
        self.addAction(QtGui.QAction(self, shortcut=str(5),
                                     triggered=self.fDelete))

    # Проверка доступности кнопок.
    def showEvent(self, e):
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

    # Удаление файла БД, если он пуст.
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

    # 5 функций для перехода к другим этапам работы.
    # Возможность активации того или иного этапа определяется
    # в функции showEvent().

    # Выбор вариантов. закрытие текущего проекта.
    def fVar(self):
        self.parent.show()
        self.close()

    # Ввод признаков классификации и их значений.
    def fInput(self):
        self.input = InputWind(self, self.file)
        self.input.move(self.x(), self.y())
        self.hide()
        self.input.show()

    # Анализ соответствия признаков классификации.
    def fAnaliz(self):
        if self.butAnaliz.isEnabled():
            self.analiz = AnalizWind(self, self.file)
            self.analiz.move(self.x(), self.y())
            self.hide()
            self.analiz.show()

    # Вывод полученных данных
    def fOutput(self):
        if self.butOutput.isEnabled():
            self.output = OutputWind(self, self.file)
            self.output.move(self.x(), self.y())
            self.hide()
            self.output.show()

    # Удаление данных.
    def fDelete(self):
        if self.butDelete.isEnabled():
            self.delete = DeleteWind(self, self.file)
            self.delete.move(self.x(), self.y())
            self.hide()
            self.delete.show()


class InputWind(QtGui.QWidget):
    '''
    Диалог ввода данных. Запись в файл происходит при нажатии кнопки "Finish".
    self.file['input'] хранит в себе данные в виде:
    [['1 класс', '11', '111', '1111'], ['2 класс', '22', '222', '2222']]
    [i][0] содержит в себе признаки классификации, [i][1:] - их значения.
    '''
    def __init__(self, parent, file):
        QtGui.QWidget.__init__(self)
        uic.loadUi(join('ui', 'input.ui'), self)
        self.file = file
        self.parent = parent
        self.butPrev.setDisabled(True)
        self.butNext.clicked.connect(self.fNext)
        self.butPrev.clicked.connect(self.fPrev)
        self.butBack.clicked.connect(self.fBack)
        self.addAction(QtGui.QAction(self, shortcut="Alt+Right",
                                     triggered=self.fNext))
        self.addAction(QtGui.QAction(self, shortcut="Alt+Left",
                                     triggered=self.fPrev))
        self.addAction(QtGui.QAction(self, shortcut="Alt+Backspace",
                                     triggered=self.fBack))
        self.textWind.setFocus()

    # Выставление начальных значений при появлении этого окна.
    def showEvent(self, e):
        try:
            # Проверка на наличие сохранённых данных.
            if self.file['input'][0] is not None:
                # Восстановление данных.
                self.data = self.file['input']
                # Перемещение указателя в начальную позицию.
                self.cur = 0
                self.textWind.setPlainText(addN(self.data[self.cur][1:]))
                self.fInput('Prev')
                self.butNext.setText('Next >>')
        except:
            self.data = []
            self.cur = -1

    def fInput(self, side):
        # Чтение из textBrowser.
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

        if self.cur + 1 == len(self.data) and side == 'Next' and \
                not len(self.data) == 0:
            # Завершение ввода данных, их сохранение и переход к другой части.
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

    # Вызывается при нажатии кнопки 'Next >>' или 'Finish'.
    def fNext(self):
        if self.butNext.isEnabled():
            self.fInput('Next')

    # Вызывается при нажатии кнопки '<< Prev'
    def fPrev(self):
        if self.butPrev.isEnabled():
            self.fInput('Prev')

    # Возвращение к окну, вызвавшему это окно.
    def fBack(self):
        self.parent.show()
        self.close()


class AnalizWind(QtGui.QWidget):
    '''
    Диалог анализа данных.
    Запись проимходит при анализе последнего соотношения.
    file['analiz'][0] = [всевозможные сочетания элементых разных признаков]
    file['analiz'][1] = {значение признака классификации:признак классификации}
    file['analiz'][2] = [признаки классификации, которые остались при
                         анализе данных]
    '''
    def __init__(self, parent, file):
        QtGui.QWidget.__init__(self)
        uic.loadUi(join('ui', 'analiz.ui'), self)
        self.file = file
        self.parent = parent
        self.butBack.clicked.connect(self.fBack)
        self.addAction(QtGui.QAction(self, shortcut="Alt+Backspace",
                                     triggered=self.fBack))
        self.addAction(QtGui.QAction(self, shortcut="Alt+Left",
                                     triggered=self.fBack))

    # Сброс на начало цикла при отображении окна.
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
        # Создание всевозможных комбинаций значений признаков
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
        self.file['analiz'] = [self.ok, self.dictData, self.unzip(
            self.dictTrust(self.ok, self.dictData, self.head))]
        self.output = OutputWind(self, self.file)
        self.output.move(self.x(), self.y())
        self.output.show()

    def keyPressEvent(self, e):
        flag = False
        if e.key() == QtCore.Qt.Key_Y or e.text() == 'н':
            self.ans = False  # Некие действия после нажатия клавиши
            flag = True
        elif e.key() == QtCore.Qt.Key_L or e.text() == 'д':
            self.ans = True
            flag = True
        if flag:
            try:
                next(self._generator)  # Продвижение на следующую итерацию
            except StopIteration:
                self.stop()  # Завершение заданий на этом виджете

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
    '''
    Диалог определения отношения признаков классификации.
    '''
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
        self.butUp.clicked.connect(self.fUp)
        self.butDown.clicked.connect(self.fDown)
        self.butPrint.clicked.connect(self.printData)
        self.butBack.clicked.connect(self.fBack)
        self.addAction(QtGui.QAction(self, shortcut="Alt+Up",
                                     triggered=self.fUp))
        self.addAction(QtGui.QAction(self, shortcut="Alt+Down",
                                     triggered=self.fDown))
        self.addAction(QtGui.QAction(self, shortcut="Alt+Space",
                                     triggered=self.printData))
        self.addAction(QtGui.QAction(self, shortcut="Alt+Right",
                                     triggered=self.printData))
        self.addAction(QtGui.QAction(self, shortcut="Alt+Left",
                                     triggered=self.fBack))
        self.addAction(QtGui.QAction(self, shortcut="Alt+Backspace",
                                     triggered=self.fBack))
        self.listWidget.setItemSelected(self.listWidget.item(0), True)

    # Смена местами элементов списка.
    def change(self, n, k):
        self.listWidget.setItemSelected(self.listWidget.item(n), False)
        self.listWidget.insertItem(n, self.listWidget.takeItem(k))
        self.listWidget.setItemSelected(self.listWidget.item(k), True)

    # Сдвиг элемента вверх.
    def fUp(self):
        n = self.listWidget.currentRow()
        if not n == 0:
            self.change(n, n - 1)

    # Сдвиг элемента вниз.
    def fDown(self):
        n = self.listWidget.currentRow()
        if not n == self.ln:
            self.change(n, n + 1)

    # Генератор элементов списка.
    def getItems(self):
        for i in range(self.listWidget.count()):
            yield self.listWidget.item(i)

    # Отображение окна вывода данных.
    def printData(self):
        self.newHead = []
        for i in self.getItems():
            self.newHead.append(i.text())
        # Попытка вызова созданного окна данных.
        try:
            self.finish.print(self.data, self.dictData,
                              self.head, self.newHead)
            self.finish.show()
        # При отсутствии объекта класса PrintWind необходимо его создать,
        # затем вывести данные на экран.
        except:
            self.finish = PrintWind(self.data, self.dictData,
                                    self.head, self.newHead)
            self.finish.show()

    def fBack(self):
        self.parent.show()
        self.close()


class PrintWind(QtGui.QWidget):
    '''
    Окно отображения итоговых данных.
    data = file['analiz'][0]
    dictData = file['analiz'][1]
    head = file['analiz'][2]
    newHead = новый порядок признаков классификаций.
    '''
    def __init__(self, data, dictData, head, newHead):
        QtGui.QWidget.__init__(self)
        uic.loadUi(join('ui', 'print.ui'), self)
        self.print(data, dictData, head, newHead)

    def print(self, data, dictData, head, newHead):
        self.textBrowser.setPlainText(
            prepareToTextBrowser(data, dictData, head, newHead))


class DeleteWind(QtGui.QWidget):
    '''
    Диалог удаления данных.
    '''
    def __init__(self, parent, file):
        QtGui.QWidget.__init__(self)
        uic.loadUi(join('ui', 'delete.ui'), self)
        self.file = file
        self.parent = parent
        self.butData.clicked.connect(self.fData)
        self.butAnaliz.clicked.connect(self.fAnaliz)
        self.butClose.clicked.connect(self.fClose)
        self.addAction(QtGui.QAction(self, shortcut=str(1),
                                     triggered=self.fData))
        self.addAction(QtGui.QAction(self, shortcut=str(2),
                                     triggered=self.fAnaliz))
        self.addAction(QtGui.QAction(self, shortcut=str(3),
                                     triggered=self.fClose))
        self.butData.setEnabled(True)
        self.butAnaliz.setEnabled(False)
        try:
            if self.file['analiz'] is not None:
                self.butAnaliz.setEnabled(True)
        except:
            pass

    # Удаление всех данных их файла.
    def fData(self):
        del self.file['input']
        try:
            del self.file['analiz']
        except:
            pass
        self.fClose()

    # Удаление данных об анализе.
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
