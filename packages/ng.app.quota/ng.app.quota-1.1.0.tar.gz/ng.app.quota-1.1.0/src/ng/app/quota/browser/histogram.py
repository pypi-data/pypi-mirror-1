### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based quota package

$Id: histogram.py 52854 2009-04-07 13:18:13Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 12897 $"

from zope.proxy import removeAllProxies
from ng.app.quota.interfaces import IQuota
from pd.lib.linear_quantizator import quantizator, elastic


class Histogram(object) :

    def __init__(self,context,request) :
        super(Histogram,self).__init__(context,request)

        quota = removeAllProxies(IQuota(self.context))
        
        res = quota.osz.values()
        
        # Если нет объектов для отображения или есть только 1 элемент - устанавливаем
        # соответствующий флаг и выходим
        if len(res) < 2:
            self.isEnoughData = False
            return
        else:
            self.isEnoughData = True

        # Размер каждого объекта высчитывается как сумма длин заголовка и тела
        # Находим минимальный и максимальный размеры объектов
        self.vn = min(quota.osz.values())
        self.vx = max(quota.osz.values())
        
        # число объектов Note внутри сайта
        self.count = len(quota.osz.values())

        if self.vn == self.vx:
            self.size = 1
            return [ { "count" : self.count, "height" : 100, "size" : self.vn } ]

        # Число столбиков на будущей диаграмме. Его значение - не меньше 5 и не больше 30.
        self.size = max(5, min(self.count / 10 + 1, 30))

        # Cреднее арифметическое размеров всех эелемнтов
        self.average = 0.
        # Суммарный размер элементов
        size = 0.

        if 'quantization' in self.request :
            res = quantizator([ (x,x) for x in quota.osz.values() ],self.size)
            d = {}
            for value,key in res :
                l = d.setdefault(key,[0,0])
                l[0]+=1
                l[1]+=value
                size+=value
                            
            lc = [ count for (count,sum) in d.values() ]
            mx = max(lc)
            mn = min(lc)
            
            self.h = [ {'count': y , 'height':int(100.*(y-mn)/(mx-mn)), "size" : z/y }  for x,(y,z) in sorted(d.items())] 
            for a in self.h :
                print a              
        else :
            # формируем список из self.size элементов со значением 0
            self.h = [0]*self.size 


            # Проходим по всем элементам в контейнере
            for value in quota.osz.values() :
                #считаем суммарный объём всех элементов
                size += value
                # считаем, в какой из отрезков разбиения попадает каждый объект из quota.osz
                # Для этого число интервалов разбиения делим на разброс значений размеров
                # объектов и умножаем на размер текущего объекта
                self.h[int((self.size-1)*(value-self.vn) / (self.vx-self.vn))] += 1

                # Находим средний размеров объектов
            mx = max(self.h)
            mn = min(self.h)
        
            self.h = [ { "count" : x, "height" : (x-mn)*100/(mx-mn), "size" : y*(self.vx-self.vn) / self.size+self.vn } for x,y in zip(self.h,range(0,len(self.h))) ]

        self.average = size / self.count
        # Повторно устаналиваем данные значения, потому что мы могли их менять в процессе
        # построения диаграммы
        #self.vn = min(quota.osz.values())
        #self.vx = max(quota.osz.values())
