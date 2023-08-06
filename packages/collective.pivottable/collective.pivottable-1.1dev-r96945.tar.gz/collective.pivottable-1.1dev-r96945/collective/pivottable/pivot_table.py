# -*- coding: UTF-8 -*-
import csv

try:
    from Acquisition import aq_get
except ImportError:
    aq_get = None

from aggregate_functions import *

class PivotTable(object):
    keys_fields = None
    _aggregated = None
    cols = None
        
    def __init__(self, objects=None, attr_to_name_col='', attrs_to_fill_row=None, show_total_col=False, show_total_row=False, first_col_title='X', total_col_title='Total', total_row_title='Total:'):
        ''' 
        @objects = A list of objects used to make the Pivot Table
        @attr_to_name_col = Name of Attribute (attr or method) of object, to use to get the title of columns
        @attrs_to_fill_row = A list of dict, like this: 
                              [{'attr': 'title', 'label':'Pretty Title'}, 
                               {'attr2': 'myValue', 'label': 'A sample', 'callback': my_func}
                               {'attr3': 'age', 'label': 'User age', 'aggr_func': Sum}
                               ]
                              where 'attr' Attribute's name and 'label' is used to label the row
                              callback is callable that will called to format the value like this:
                              def my_fun(value):
                                if isinstance(value, float):
                                    return '%.2f' % value
                                else:
                                    return '%s' % value
                               aggr_func: How aggregate values, see aggregate_functions module for more 
                               details. defaults is Group By

        @show_total_col = Show a last col with the sum of the row
        @show_total_row = Show a last row with the sum of the cols
        @first_col_title = A label to first col, the first col is the column with the labels, of attrs_to_fill_row
        @total_col_title = The title of the column with the sums, when show_total_col is True
        @total_row_title = The title (label), of the row with the sums, when show_total_row is True
        
        '''
        if not objects:
            self.objects = []  # a list of objects to will generate the table
        else:
            self.objects = objects

        self.attr_to_name_col = attr_to_name_col
        if not attrs_to_fill_row:
            self.attrs_to_fill_row = []
        else:
            self.attrs_to_fill_row = attrs_to_fill_row

        self.show_total_col = show_total_col
        self.show_total_row = show_total_row

        self.first_col_title = first_col_title
        self.total_col_title = total_col_title
        self.total_row_title = total_row_title


    def getAttrValue(self, obj, attr_name):
        ''' Returns the the value of attr from object '''

        _marker = []
        if hasattr(obj, attr_name):
            attr = getattr(obj, attr_name, _marker)
        elif aq_get:
            attr = aq_get(obj, attr_name, _marker)
        else:
            raise AttributeError("Attribute: '%s' not found in %s " % (attr_name, obj))

        if callable(attr):
            value = attr()
        else:
            value = attr

        return value

    def fmtValue(self, field, value):
        callback = field.get('callback')
        fmt_value = value
        if callback:
            fmt_value = callback(value)

        return fmt_value

    def getValue(self, obj, field):
        attr = field['attr']
        value = self.getAttrValue(obj, attr)

        return value 

    def _getGroupBys(self):
        ''' Returns the fields that is GroupBy '''
        ret = []

        for field in self.attrs_to_fill_row:
            field.setdefault('aggr_func', GroupBy) 
            aggr_func = field.get('aggr_func')

            if aggr_func is GroupBy:
                ret.append(field)

        return ret

    @property
    def getKeysFields(self):
        ''' Returns all fields that have aggregate function GroupBy, that will be the key in the row '''
        if not self.keys_fields:
            self.keys_fields = self._getGroupBys()

        return self.keys_fields

    @property
    def getValuesFields(self):
        ''' Returns all fields that have aggregate function diferent from GroupBy, that will be used
        to compute value for columns '''
        keys_fields = self.getKeysFields
        values_fields =  [field for field in self.attrs_to_fill_row if field not in keys_fields]

        return values_fields

    def _getKeyTuple(self, obj):
        ''' Get the value of keys fields, computed/formated value, that is used as key in the row'''
        keys_fields = self.getKeysFields
        key_value = []
        for field in keys_fields:
            value = self.getValue(obj, field)
            fmt_value = self.fmtValue(field, value)
            key_value.append(fmt_value)
        return tuple(key_value)


    @property
    def aggregated(self):
        if not self._aggregated:
            self._aggregated = self.aggregate()

        return self._aggregated

    def aggregate(self):
        ''' Aggregate the objects based on aggr_funcs '''

        ret = {}
        keys_fields = self.getKeysFields
        values_fields =  [field for field in self.attrs_to_fill_row if field not in keys_fields]

        for obj in self.objects:
            key_value = self._getKeyTuple(obj)

            ret.setdefault(key_value, {})
            col_name = str(self.getAttrValue(obj, self.attr_to_name_col))

            for idx, field in enumerate(values_fields):
                label = str(field.get('label', idx))
                ret[key_value].setdefault(label, {})

                aggregator = ret[key_value][label].get(col_name, None)

                if aggregator is None:
                    aggr = field.get('aggr_func')

                    ret[key_value][label][col_name] = aggr()
                    aggregator = ret[key_value][label][col_name]

                value = self.getValue(obj, field)
                
                aggregator.append(value)

        return ret

    def getAllRows(self):
        ''' Returns all lines (a list of lists), with first row header, 
        then the lines, last row footer '''

        return [self.getHeader()] + self.getRows() + [self.getFooter()]

    def getHeader(self):
        ''' Returns the columns' Headers '''
        self._name_col = []
        cols = [self.first_col_title]

        cols += [field.get('label', '') for field in self.getKeysFields ] 

        for obj in self.objects:
            col_name = self.getAttrValue(obj, self.attr_to_name_col) 
            if not col_name in cols:
                cols.append(col_name)
                self._name_col.append(col_name)

        if self.show_total_col:
            cols.append(self.total_col_title)

        self.cols = cols
        return cols

    def getRows(self):
        ''' Returns a list with list of columns, like this: [[1, 2, 4], [4, 3, 2]]'''
        aggregated = self.aggregated
        col_names = self.cols or self.getHeader()

        self.row_total = row_total = {}
        rows = []

        for key in aggregated:
            for idx, field in enumerate(self.getValuesFields):
                row_label = str(field.get('label', idx))
                cols = [row_label]
                cols += [k for k in key]
                column_total = []

                for col_name in col_names:
                    aggr = aggregated[key].get(row_label, {}).get(col_name)
                    if aggr: 

                        attr = field['attr']

                        value = aggr() # compute the aggregated value
                        fmt_value = self.fmtValue(field, value)

                        cols.append(fmt_value)
                        column_total.append(value)
                        row_total.setdefault(col_name, [])
                        row_total[col_name].append(value)
                    else:
                        if col_name in self._name_col:
                            cols.append(None)


                if self.show_total_col:
                    total = sum(column_total)
                    cols.append(total)


                rows.append(cols)

        return rows

    def getFooter(self):
        ''' Returns the footer, the a line with totals summing of each column '''
        cols = []
        if self.show_total_row:
            cols.append(self.total_row_title)
            cols += ['-'  for k in self.getKeysFields]
            
            totals = []
            col_names = self.cols or self.getHeader()
            
            for col_name in col_names:
                values = self.row_total.get(col_name)
                if not values is None:
                    col = total = sum(values)
                    cols.append(col)

                    totals.append(total)

            if self.show_total_col:
                total = sum(totals)
                cols.append(total)

        return cols


class StringTable(PivotTable):
    def show(self):
        print self.stringTable()

    def stringTable(self):
        ''' Returns the table as string, then you can show in console or in a 
        txt file '''
        
        lines = []
        for line in self.getAllRows():
            lines.append('\t'.join([str(col) for col in line]))

        return '\n'.join(lines)

class CSVTable(PivotTable):
    name_file = None
    def saveFile(self):
        tmpfile = open(self.name_file, 'w')
        writer = csv.writer(tmpfile, delimiter=';')
        writer.writerows(self.getAllRows())
        tmpfile.close()
        return tmpfile.name

def console():
    from pprint import pprint

    class Purchase(object):
        def __init__(self, cost=0.0, price=0.0, month='', ou=''):
            self.cost = cost
            self.price  = price
            self.month = month
            self.ou = ou

        def gain(self):
            return (self.price - self.cost) / self.cost

    purschases = [Purchase(cost=5.0, price=7, month='jan', ou='NY'), 
            Purchase(cost=5.0, price=7, month='jan', ou='NY'),
            Purchase(cost=14.66, price=4946.68, month='feb', ou='NY'),
            Purchase(cost=7.33, price=7184.90, month='mar', ou='NY'), Purchase(cost=7.33, price=7834.92, month='apr', ou='NY'),
            Purchase(cost=73.3, price=8692.67, month='may', ou='NY'), Purchase(cost=128.28, price=9552.14, month='jun', ou='NY'), 
            Purchase(cost=58.64, price=8828.44, month='jul', ou='NY'), Purchase(cost=128.28, price=9652.73, month='aug', ou='NY'), ]

    purschases += [Purchase(cost=14.66, price=463.61444144, month='jan', ou='RJ'), Purchase(cost=14.66, price=4946.68, month='feb', ou='RJ'),
            Purchase(cost=7.33, price=7184.90, month='mar', ou='RJ'), Purchase(cost=7.33, price=7834.92, month='apr', ou='RJ'),
            Purchase(cost=73.3, price=8692.67, month='may', ou='RJ'), Purchase(cost=128.28, price=9552.14, month='jun', ou='RJ'), 
            Purchase(cost=58.64, price=8828.44, month='jul', ou='RJ'), Purchase(cost=128.28, price=9652.73, month='aug', ou='RJ'), ]

    def formatter(value):
        if isinstance(value, float):
            return '%.2f' % value
        else:
            return '%s' % value

    fmt = StringTable() #PivotTable()
    fmt.attr_to_name_col = 'month'
    fmt.attrs_to_fill_row = [{'attr': 'cost', 'label': 'Cost Total', 'callback': formatter, 'aggr_func': Sum}, 
                             {'attr': 'price', 'label': "Sell's Price", 'callback': formatter , 'aggr_func': Sum}, 
                             {'attr': 'gain', 'label': 'AVG Gain %', 'callback': formatter, 'aggr_func': Avg},
                             {'attr': 'ou', 'label': 'OU', 'callback': formatter, 'aggr_func': GroupBy}]
    fmt.objects = purschases
    fmt.first_col_title = 'Purchases'
    #fmt.show_total_row = True
    #fmt.show_total_col = True


    print '-----'
    fmt.show()

    my_csv = CSVTable(attr_to_name_col = 'month', 
                      attrs_to_fill_row = [{'attr': 'cost', 'label': 'Cost Total', 'callback': formatter, 'aggr_func': Sum}, 
                                           {'attr': 'price', 'label': "Sell's Price", 'callback': formatter , 'aggr_func': Sum}, 
                                           {'attr': 'gain', 'label': 'Gain SUM %', 'aggr_func': Sum},
                                           {'attr': 'ou', 'label': 'Organization Unit', 'callback': formatter, 'aggr_func': GroupBy}],
                   objects = purschases,
                   first_col_title = 'Purchases',
                   show_total_row = False,
                   show_total_col = False)

    my_csv.name_file = 'output2_purchases.csv'
    print my_csv.saveFile()


if __name__ == "__main__":
    import doctest
    doctest.testfile("testing.txt")

