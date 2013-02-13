__author__ = 'nivs'
from copy import deepcopy


def prepareToTextBrowser(rawData, dictData, head, newHead):
    data = []
    for i in rawData:
        data.append(list(i))

    # Убирает из списка элементы, содержащиеся в других элементах.
    # К примеру, из t = [['1, 2', ['1, 2, 3']] удалит ['1', '2'].
    err = []
    for i in range(len(data)):
        for j in range(len(data)):
            if data[i][:len(data[j])] == data[j] and data[i] != data[j]:
                err.append(data[j])

    for i in err:
        try:
            data.remove(i)
        except:
            pass

    # Ищет максимальную длину подсписка
    buf = [len(x) for x in data]
    if len(buf) > 1:
        mlen = max(*[len(x) for x in data])
    else:
        mlen = [len(x) for x in data][0]

    # Добавляет к коротким спискам недостающие [''].
    # Сделано для того, чтобы .sort() работал так, как надо.
    for i in data:
        for j in range(mlen - len(i)):
            i.append('')
    data.sort()

    head = unzip(dictTrust(rawData, dictData, head))
    newHead = unzip(dictTrust(rawData, dictData, newHead))

    for i in range(len(head)):
        if head[i] != newHead[i]:
            n = head.index(newHead[i])
            head[i], head[n] = head[n], head[i]
            data = swap(data, i, n)

    final = ''
    for i in head[:-1]:
        final += str(i) + ' - '
    final += head[-1] + '\n\n'
    for i in range(len(data)):
        if data[i] != '':
            if i == 0:
                final += pr(data[i], mlen)
            else:
                final += pr(data[i][raz(data[i], data[i - 1], mlen):], mlen)
    return final


# Смотрим, какие признаки классификации остались
def dictTrust(data, dictData, head):
    trust = []
    for i in head:
        for j in data:
            for k in j:
                if i == dictData[k]:
                    trust.append(dictData[k])
    return trust


# Возвращает уникальные значения (убирает повторы)
def unzip(data):
    seen = set()
    seen_add = seen.add
    return [x for x in data if x not in seen and not seen_add(x)]


# Меняет местами столбцы
def swap(rawData, a, b):

    data = []
    for i in rawData:
        data.append(list(i))

    err = []
    buf = deepcopy(data)
    for i in range(len(buf)):
        try:
            buf[i][a], buf[i][b] = buf[i][b], buf[i][a]
        except IndexError:
            err.append(buf[i])
    for i in err:
        buf.remove(i)
    buf.sort()
    return buf


# Выводит на экран древовидную структуру
def pr(str, _max):
    ink = _max - len(str)
    ret = ''
    for i in range(len(str)):
        if not str[i] == '':
            ret += (i + ink) * 2 * ' ' + str[i] + '\n'
        else:
            break
    return ret


# Высчитывает, на каком элементе начинаются различия между двумя списками
def raz(lst1, lst2, _max):
    ret = 0
    for i in range(_max):
        if lst1[i] == lst2[i]:
            ret += 1
        else:
            return ret
    return ret
