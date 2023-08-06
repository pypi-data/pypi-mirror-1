$Id: README.txt 570 2007-02-13 19:16:27Z azaretsky $

Как использовать продукт topolsort:

    Модуль topolsort.topolsort содержит две функции:

        topSort и baseTopSort
    
    и исключение SortIsNotPossible.

    topSort получает на вход последовательность сортируемых элементов,
    у каждого из которых должны быть такие атрибуты:

        name - уникальный ключ,

        requires - последовательность ключей.

    topSort имеет необязательный параметр reversed. Если reversed=True,
    requires трактуется как элементы, идущие в выходной
    последовательности перед данным. Если reversed=False, requires -
    элементы после данного. По умолчанию reversed=True.

    topSort возвращает генератор, перечисляющий элементы в порядке
    топологической сортировки. Если в графе есть циклы, сортировка
    не возможна. В этом случае после перечисления некоторых элементов
    генерируется исключение SortIsNotPossible, в параметре которго
    содержится список оставшихся элементов.

    Пример::

        from topolsort.topolsort import topSort

        class Elt(object):
            def __init__(self, name, requires=[]):
                self.name = name
                self.requires = requires

            def __repr__(self):
                return 'Elt(%r, %r)' % (self.name, self.requires)

        print list(topSort([Elt(1), Elt(2, [3]), Elt(3, [1])]))
        # получаем [Elt(1, []), Elt(3, [1]), Elt(2, [3])]

        list(topSort([Elt(1), Elt(2, [3]), Elt(3, [1])], reversed=False))
        # получаем [Elt(2, [3]), Elt(3, [1]), Elt(1, [])]

    topSort - это обертка вокруг baseTopSort, исходными данными которой
    является последовательность пар:

        первый элемент - объект
        второй элемент - последовательность объектов

    Объекты из вторых элементов должны принадлежать множеству первых элементов.

    # Re: Первые элементы пар не должны повторяться
    # TODO: В том то и дело, что в норме первые элементы пар могут
    # TODO: повторятся. Кнутовский алгоритм это допускал. И, ваще говоря,
    # TODO: нам это реально надо.

    baseTopSort также имеет параметр reversed с аналогичным смыслом и
    значением по умолчанию.

    Пример::

        from topolsort.topolsort import baseTopSort

        class Elt(object):
            def __init__(self, name, requires=[]):
                self.name = name
                self.requires = requires

            def __repr__(self):
                return 'Elt(%r, %r)' % (self.name, self.requires)

        o1, o2, o3 = (object() for _ in range(3))
        
        print o1, o2, o3
        
        print list(baseTopSort([(o1, []), (o2, [o3]), (o3, [o1])]))
        # o1: <object object at 0xb7da4448>
        # o2: <object object at 0xb7da4450>
        # o3: <object object at 0xb7da4458>
        # [<object object at 0xb7da4448>, <object object at 0xb7da4458>, <object object at 0xb7da4450>]
        # то есть [o1, o3, o2]
