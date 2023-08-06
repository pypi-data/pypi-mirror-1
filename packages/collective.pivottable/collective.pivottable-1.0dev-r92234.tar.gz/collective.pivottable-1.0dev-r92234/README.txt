Introduction
============

This package helps creates `Pivot Tables`_ using your Python objects as source.

Developed by lucmult - Luciano Pacheco at `Simples Consultoria`_.

You don't need SQL, but can use row retrieved from your database.

You need :

- A list of your objects
- A dict mapping your object's attributes (or methods) 
- An attribute (or method) to use as column name

NOTE: An attribute can be :

- an attribute
- a method (callable), without args
- can use Zope Acquisition, but it's optional, can safely used without Zope ;-)

Let's show a example.

Define your class ::

    >>> class Purchase(object):
    ...     def __init__(self, cost=0.0, price=0.0, month='', ou=''):
    ...         self.cost = cost
    ...         self.price  = price
    ...         self.month = month
    ...         self.ou = ou
    ...     def gain(self):
    ...         return (self.price - self.cost) / self.cost

A class representing your purchases.

Let's do some purchases ::

    >>> purschases = [Purchase(cost=5.0, price=7, month='jan', ou='NY'), 
    ...               Purchase(cost=5.0, price=7, month='jan', ou='NY'),
    ...               Purchase(cost=14.66, price=4946.68, month='feb', ou='NY'),
    ...               Purchase(cost=7.33, price=7184.90, month='mar', ou='NY'), 
    ...               Purchase(cost=7.33, price=7834.92, month='apr', ou='NY'),
    ...               Purchase(cost=73.3, price=8692.67, month='may', ou='NY'), 
    ...               Purchase(cost=128.28, price=9552.14, month='jun', ou='NY'), 
    ...               Purchase(cost=58.64, price=8828.44, month='jul', ou='NY'), 
    ...               Purchase(cost=128.28, price=9652.73, month='aug', ou='NY'), ]

    >>> purschases += [Purchase(cost=14.66, price=463.61, month='jan', ou='RJ'), 
    ...                Purchase(cost=14.66, price=4946.68, month='feb', ou='RJ'),
    ...                Purchase(cost=7.33, price=7184.90, month='mar', ou='RJ'), 
    ...                Purchase(cost=7.33, price=7834.92, month='apr', ou='RJ'),
    ...                Purchase(cost=73.3, price=8692.67, month='may', ou='RJ'), 
    ...                Purchase(cost=128.28, price=9552.14, month='jun', ou='RJ'), 
    ...                Purchase(cost=58.64, price=8828.44, month='jul', ou='RJ'), 
    ...                Purchase(cost=128.28, price=9652.73, month='aug', ou='RJ'), ]


Now we have a list of objects ;-).

You can use a callback function to format values to display in your genereated table ::

    >>> def formatter(value):
    ...     if isinstance(value, float):
    ...         return '%.2f' % value
    ...     else:
    ...         return '%s' % value

It have a built-in example to display as string ::

    >>> from collective.pivottable import StringTable
    >>> tbl = StringTable() 

Define an attrbute to name cols ::

    >>> tbl.attr_to_name_col = 'month'

Define the attrs mapping and how aggregate the values ::

    >>> tbl.attrs_to_fill_row = [{'attr': 'cost', 'label': 'Cost Total', 'callback': formatter, 'aggr_func': Sum}, 
    ...                          {'attr': 'price', 'label': "Sell's Price", 'callback': formatter , 'aggr_func': Sum}, 
    ...                          {'attr': 'gain', 'label': 'AVG Gain %', 'callback': formatter, 'aggr_func': Avg},
    ...                          {'attr': 'ou', 'label': 'OU', 'callback': formatter, 'aggr_func': GroupBy}]

Pass your objects to tbl ::

    >>> tbl.objects = purschases

Set a name to first col ::

    >>> tbl.first_col_title = 'Purchases'

Get your text table ::

    >>> tbl.show()
    Purchases       OU      jan     feb     mar     apr     may     jun     jul     aug
    Cost Total      RJ      14.66   14.66   7.33    7.33    73.30   128.28  58.64   128.28
    Sell's Price    RJ      463.61  4946.68 7184.90 7834.92 8692.67 9552.14 8828.44 9652.73
    AVG Gain %      RJ      30.62   336.43  979.20  1067.88 117.59  73.46   149.55  74.25
    Cost Total      NY      5.00    14.66   7.33    7.33    73.30   128.28  58.64   128.28
    Sell's Price    NY      7       4946.68 7184.90 7834.92 8692.67 9552.14 8828.44 9652.73
    AVG Gain %      NY      0.40    336.43  979.20  1067.88 117.59  73.46   149.55  74.25    

Or get a list of rows and cols (main use) ::

    >>> for line in tbl.getAllRows():
    ...     print line
    ...
    ['Purchases', 'OU', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug']
    ['Cost Total', 'RJ', '14.66', '14.66', '7.33', '7.33', '73.30', '128.28', '58.64', '128.28']
    ["Sell's Price", 'RJ', '463.61', '4946.68', '7184.90', '7834.92', '8692.67', '9552.14', '8828.44', '9652.73']
    ['AVG Gain %', 'RJ', '30.62', '336.43', '979.20', '1067.88', '117.59', '73.46', '149.55', '74.25']
    ['Cost Total', 'NY', '5.00', '14.66', '7.33', '7.33', '73.30', '128.28', '58.64', '128.28']
    ["Sell's Price", 'NY', '7', '4946.68', '7184.90', '7834.92', '8692.67', '9552.14', '8828.44', '9652.73']
    ['AVG Gain %', 'NY', '0.40', '336.43', '979.20', '1067.88', '117.59', '73.46', '149.55', '74.25']
    []   

The module aggregate_functions provides some aggregates functions, that you can case  ::

    >>> from collective.pivottable.aggregate_functions import Avg, First, GroupBy, Last, Max, Min, Sum

The Base API to create a aggregate_function is ::

    >>> class Sum(object):
    ...     def __init__(self):
    ...         self.values = []
    ...     def append(self, value):
    ...         self.values.append(value)
    ...     def __call__(self):
    ...         return sum(self.values)

In other words, a append and a __call__, the __init__ is optional.

.. _Pivot Tables: http://en.wikipedia.org/wiki/Pivot_table
.. _Simples Consultoria: http://www.simplesconsultoria.com.br
