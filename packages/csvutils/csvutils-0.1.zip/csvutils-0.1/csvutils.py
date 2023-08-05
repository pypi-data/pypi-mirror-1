#!/usr/bin/env python

'''
Transformation utilities for csv (or csv-like) generated rows.

The standard csv module is very useful for parsing tabular data in CSV format.
Typically though, one or more transformations need to be applied to the generated
rows before being ready to be used; for instance "convert the 3rd column to int,
the 5th to float and ignore all the rest". This module provides an easy way to
specify such transformations upfront instead of coding them every time by hand.

Two classes are currently available, L{SequenceTransformer} and L{MappingTransformer},
that represent each row as a list (like C{csv.reader}) or dict (like C{csv.DictReader}),
respectively.

@requires: Python 2.3 or later.
'''


__all__ = ['RowTransformer', 'SequenceTransformer', 'MappingTransformer']
__author__ = 'George Sakkis <george.sakkis AT gmail DOT com>'

# Python 2.3 support
try: set
except NameError:
    from sets import Set as set

#======= RowTransformer ================================================

class RowTransformer(object):
    '''Abstract base transformer class.'''

    def __init__(self, key_adaptors, **kwds):
        '''Specifies the transformations to apply for each row.

        @param key_adaptors: Specifies the adaptor to transform each column.
            A column is identified by some C{key} and C{adaptor} is either a
            callable C{f(x)} or None (equivalent to the identity C{lambda x:x}).
        @type key_adaptors: Sequence of (key,adaptor) pairs

        @keyword default: An adaptor for all columns not specified explicitly in
            C{key_adaptors}.
        @type default: Callable C{f(x)} or C{None}

        @keyword include: The columns to include for each row:
            - If given, only the items at the respective columns are included,
              in the same order.
            - Otherwise if C{default} is given, all columns are included.
            - Otherwise, if neither C{include} or C{default} are given,
            only the keys specified in C{key_adaptors} are included.
        @type include: Iterable of keys

        @keyword exclude: The columns to exclude for each row. This takes precedence
            over all other options: a column specified in C{exclude} will B{never}
            be included in the transformed rows.
        @type exclude: Iterable of keys
        '''
        self._exclude = set(kwds.get('exclude',()))
        self._key2Adaptor = {}
        include = []
        for key,adaptor in key_adaptors:
            if key in self._key2Adaptor:
                raise ValueError('More than one adaptors for column %r' % key)
            include.append(key)
            self._key2Adaptor[key] = adaptor
        self._default_adaptor = kwds.get('default', None)
        if 'include' in kwds:
            self._include = kwds['include']
        elif 'default' not in kwds:
            # include only the explicitly specified columns
            self._include = include
        else: # include all columns
            self._include = []

    def __call__(self, rows):
        '''Transform the given rows by this transformer.

        @param rows: An iterable of rows. The representation of a row is up to
            concrete subclasses to decide.

        @return: An iterator over the transformed rows.
        '''
        raise NotImplementedError('Abstract method')


#======= SequenceTransformer ===================================================

class SequenceTransformer(RowTransformer):
    '''A L{RowTransformer} that expects and returns rows as I{sequences}.

    Examples:

    >>> import csv
    >>> rows = list(csv.reader(["1,3.34,4-3.2j,John",
    ...                         "4,4,4,4",
    ...                         "0,-1.1,3.4,None"]))

    >>> # by default, SequenceTransformer returns each row as is
    >>> list(SequenceTransformer()(rows)) == rows
    True

    >>> # transform and return the first two columns only
    >>> for row in SequenceTransformer(int,float)(rows):
    ...    print row
    [1, 3.3399999999999999]
    [4, 4.0]
    [0, -1.1000000000000001]

    >>> # as before, but keep the rest columns too
    >>> for row in SequenceTransformer(int, float, default=None)(rows):
    ...    print row
    [1, 3.3399999999999999, '4-3.2j', 'John']
    [4, 4.0, '4', '4']
    [0, -1.1000000000000001, '3.4', 'None']

    >>> # as before, but in reverse column order
    >>> for row in SequenceTransformer(int, float, default=None,
    ...                                include=reversed(xrange(4)))(rows):
    ...    print row
    ['John', '4-3.2j', 3.3399999999999999, 1]
    ['4', '4', 4.0, 4]
    ['None', '3.4', -1.1000000000000001, 0]

    >>> # transform the second column and leave the rest as is
    >>> for row in SequenceTransformer((1,float), default=None)(rows):
    ...    print row
    ['1', 3.3399999999999999, '4-3.2j', 'John']
    ['4', 4.0, '4', '4']
    ['0', -1.1000000000000001, '3.4', 'None']

    >>> # transform and return the 4nd and the 2th column, in this order
    >>> for row in SequenceTransformer((3,str),(1,float))(rows):
    ...    print row
    ['John', 3.3399999999999999]
    ['4', 4.0]
    ['None', -1.1000000000000001]

    >>> # exclude the 4th column and eval() the rest (XXX: Use eval for trusted data only)
    >>> for row in SequenceTransformer(default=eval, exclude=[3])(rows):
    ...    print row
    [1, 3.3399999999999999, (4-3.2000000000000002j)]
    [4, 4, 4]
    [0, -1.1000000000000001, 3.3999999999999999]
    '''

    def __init__(self, *adaptors, **kwds):
        '''Specifies what transformations to apply to each row.

        @param adaptors: The adaptors for selected columns. The i-th adaptor can be:
            - None: C{row[i]} will be left as is.
            - A callable C{f(x)}: C{row[i]} will be transformed by f to C{f(row[i])}.
            - A pair C{(j,A)}: C{row[j]} will be transformed by adaptor A, where
            A can be C{None} or a callable C{f(x)} as above. C{i} is ignored in
            this case.

        @keyword include: It can be:
            - An iterable of indices: Only the items at the respective columns
              are included (except for those that are also in C{exclude}).
            - A positive integer N: shortcut for C{xrange(N)}.

        @keyword default,exclude: See L{RowTransformer.__init__}
        '''
        key_adaptors = []
        for i,adaptor in enumerate(adaptors):
            # check if 'adaptor' is actually an (i,adaptor) pair or not
            try: i,adaptor = adaptor
            except: pass
            if not (isinstance(i,int) and i>=0):
                raise ValueError('Indices must be non-negative integers '
                                 '(%r given)' % i)
            key_adaptors.append((i,adaptor))
        # convert 'include' to a range if an integer is passed
        if isinstance(kwds.get('include'), int):
            kwds['include'] = xrange(kwds['include'])
        RowTransformer.__init__(self, key_adaptors, **kwds)

    def __call__(self, rows):
        '''Transform the given rows by this transformer.

        @param rows: An iterable of sequences.
        @return: An iterator over the transformed rows as lists.
        '''
        exclude = self._exclude
        get_adaptor = self._key2Adaptor.get
        default = self._default_adaptor
        if self._include: # include selected columns
            indexed_adaptors = [(j,get_adaptor(j,default))
                                for j in self._include if j not in exclude]
            for row in rows:
                new_row = [None] * len(indexed_adaptors)
                for i,(j,adaptor) in enumerate(indexed_adaptors):
                    if adaptor is None:
                        new_row[i] = row[j]
                    else:
                        new_row[i] = adaptor(row[j])
                yield new_row
        else: # include all (non-excluded) columns
            excluded = object()
            adaptors = []
            for row in rows:
                new_row = []; append = new_row.append
                for i,value in enumerate(row):
                    try: adaptor = adaptors[i]
                    except IndexError:
                        # this will typically be raised only for the first row
                        if i in exclude:
                            adaptor = excluded
                        else:
                            adaptor = get_adaptor(i,default)
                        adaptors.append(adaptor)
                    if adaptor is not excluded:
                        if adaptor is None:
                            append(value)
                        else:
                            append(adaptor(value))
                yield new_row

#======= MappingTransformer ====================================================

class MappingTransformer(RowTransformer):
    '''A L{RowTransformer} that expects and returns rows as I{mappings}.

    Examples:

    >>> import csv
    >>> rows = list(csv.DictReader(["1,3.34,4-3.2j,John",
    ...                             "4,4,4,4",
    ...                             "0,-1.1,3.4,None" ],
    ...                            fieldnames="IFCS"))

    >>> # by default, MappingTransformer returns each row as is
    >>> list(MappingTransformer()(rows)) == rows
    True

    >>> # transform and return the first two columns only
    >>> for row in MappingTransformer({'I':int,'F':float})(rows):
    ...    print row
    {'I': 1, 'F': 3.3399999999999999}
    {'I': 4, 'F': 4.0}
    {'I': 0, 'F': -1.1000000000000001}

    >>> # as before, but keep the rest columns too
    >>> for row in MappingTransformer({'I':int, 'F':float}, default=None)(rows):
    ...    print row
    {'I': 1, 'C': '4-3.2j', 'S': 'John', 'F': 3.3399999999999999}
    {'I': 4, 'C': '4', 'S': '4', 'F': 4.0}
    {'I': 0, 'C': '3.4', 'S': 'None', 'F': -1.1000000000000001}

    >>> # transform the 'F' column and leave the rest as is
    >>> for row in MappingTransformer({'F':float}, default=None)(rows):
    ...    print row
    {'I': '1', 'C': '4-3.2j', 'S': 'John', 'F': 3.3399999999999999}
    {'I': '4', 'C': '4', 'S': '4', 'F': 4.0}
    {'I': '0', 'C': '3.4', 'S': 'None', 'F': -1.1000000000000001}

    >>> # transform and return the 'F' and 'S' columns
    >>> for row in MappingTransformer({'S':str,'F':float})(rows):
    ...    print row
    {'S': 'John', 'F': 3.3399999999999999}
    {'S': '4', 'F': 4.0}
    {'S': 'None', 'F': -1.1000000000000001}

    >>> # exclude the 'S' column and eval() the rest (XXX: Use eval for trusted data only)
    >>> for row in MappingTransformer(default=eval, exclude=['S'])(rows):
    ...    print row
    {'I': 1, 'C': (4-3.2000000000000002j), 'F': 3.3399999999999999}
    {'I': 4, 'C': 4, 'F': 4}
    {'I': 0, 'C': 3.3999999999999999, 'F': -1.1000000000000001}
    '''

    def __init__(self, adaptors={}, **kwds):
        '''Specifies what transformations to apply to each row.

        @param adaptors: A mapping from column names to adaptors.
        @keyword default,include,exclude: See L{RowTransformer.__init__}
        '''
        RowTransformer.__init__(self, adaptors.items(), **kwds)

    def __call__(self, rows):
        '''Transform the given rows by this transformer.

        @param rows: An iterable of mappings.
        @return: An iterator over the transformed rows as dicts.
        '''
        exclude = self._exclude
        get_adaptor = self._key2Adaptor.get
        default = self._default_adaptor
        if self._include: # include selected columns
            key_adaptors = [(key,get_adaptor(key,default))
                            for key in self._include if key not in exclude]
            for row in rows:
                new_row = {}
                for key,adaptor in key_adaptors:
                    if adaptor is None:
                        new_row[key] = row[key]
                    else:
                        new_row[key] = adaptor(row[key])
                yield new_row
        else: # include all (non-excluded) columns
            excluded = object()
            key2adaptor = {}
            for row in rows:
                new_row = {}
                for key in row:
                    try: adaptor = key2adaptor[key]
                    except KeyError:
                        if key in exclude:
                            adaptor = excluded
                        else:
                            adaptor = get_adaptor(key,default)
                        key2adaptor[key] = adaptor
                    if adaptor is not excluded:
                        if adaptor is None:
                            new_row[key] = row[key]
                        else:
                            new_row[key] = adaptor(row[key])
                yield new_row


if __name__ == '__main__':
    import doctest
    doctest.testmod()
