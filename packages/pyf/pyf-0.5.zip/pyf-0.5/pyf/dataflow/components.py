from pyf.dataflow.core import runner, component

import itertools
import operator

import logging
logger = logging.getLogger()

from itertools import repeat, chain, izip
try:
    from itertools import izip_longest
except ImportError, AttributeError:
    def izip_longest(*args, **kwds):
        """ Function only available in Python 2.6.
        Reimplemented in Python 2.5 for consistency reason.
        See http://docs.python.org/library/itertools.html#itertools.izip_longest
        """
        fillvalue = kwds.get('fillvalue')
        def sentinel(counter = ([fillvalue]*(len(args)-1)).pop):
            yield counter()         # yields the fillvalue, or raises IndexError
        fillers = repeat(fillvalue)
        iters = [chain(it, sentinel(), fillers) for it in args]
        try:
            for tup in izip(*iters):
                yield tup
        except IndexError:
            pass
    
@component('IN', 'OUTA')
def splitm(source, out, size=3):
    """ Splits a data source in n sources (size kwarg)"""
    yield (out.size(), size)
    for row in source:
        for i in range(size):
            yield (out(i), row)
            
@component('INA', 'OUT')
def sum(ops, out):
    """ yields a sum for data sources for each row.
    can also be used to concatenate lists """
    for row in itertools.izip(*ops):
        print row
        yield reduce(operator.add, row)
        
@component("IN", "OUT")
def inc(value, out, step=1):
    """ increments each value with step kwarg 
    usefull to add a column to a table if passing lists as values,
    and list as step """
    for line in value:
        yield (out, line+step)
            
@component("INA", "OUT")
def all_true_longest(sources, out):
    """ A function that verifies that all the sources still flowing are true.
    If a source doesn't have an item (too short), it is assumed as true.
    If all the sources are true, return true, else return False.
    Useful to check that everything worked in the end of the dataflow chain.
    """
    
    #for row in izip_longest(*sources):
    #    yield reduce(operator.and_, row)
     
    # Non Functionnal equivalent:   
    for row in izip_longest(*sources, **dict(fillvalue=True)):
        cur_state = True
        for item in row:
            cur_state = cur_state and item
        yield cur_state
        
@component('INA', 'OUT')
def status_lookup(sources, out,
                  buffer_num_getters=None, clear_each=10,
                  fillvalue=True):
    """ A function that yields statuses (True/False) and statuses from sources.
    
    It uses a list of buffer getters (functions) to know if there is any result
    left in buffer for a particular source.
    
    Every "clear_each" (nth) iteration it checks for the buffer and consumes it.
    
    This component is especially useful to synchronise sources so they consume
    their own sources in a pseudo synchronous way (useful in tree shapes).
    
    About performance :
    With clear_each set as 1 you can achieve a great memory consumption perf but
    this will reduce the performance of your loop.
    For relatively small records, a value of 10 to 100 is recommended.
    """
    if buffer_num_getters is None:
        raise ValueError('You should set getters for the buffer count')
    
    # Hack to avoid starting iteration before the sources have been defined.
    # Warning: this blocks us from setting sources on the fly.
    yield fillvalue
    
    sources = list(sources)
    burnt_sources = list()
    iteration = 0
    continue_sources = True
    while continue_sources:
        iteration += 1
        for num, source in enumerate(sources):
            continue_source = True
            try:
                while continue_source:
                    yield source.next()
                    if not iteration % clear_each:
                        if buffer_num_getters[num] is None or \
                                buffer_num_getters[num]() < 1:
                            continue_source = False
                    else:
                        continue_source = False
            except StopIteration:
                if not num in burnt_sources:
                    burnt_sources.append(num)
                continue_source = False
                yield fillvalue
                
        if len(burnt_sources) >= len(sources):
            continue_sources = False
        
    yield fillvalue
        
@component("INA", "OUT")
def all_true(sources, out):
    """ A function that verifies that all the sources are true.
    If all the sources are true, return true, else return False.
    Useful to check that everything worked in the end of the dataflow chain
    and to synchronize chain sizes.
    """
    for row in itertools.izip(*sources):
        yield reduce(operator.and_, row)
        
@component("IN", "OUT")
def bufferize(source, out, chunk_size=20):
    """ Group items in buffers. Useful to write N items at once.
    IN: source, an iterator
    OUT: an iterator of groups
    kwarg chunk_size: size of the groups
    """ 
    buffer = list()
    for i, v in enumerate(source):
        buffer.append(v)
        if not (i+1) % chunk_size and not i == 0:
            yield buffer
            buffer = list()
    
    if len(buffer):
        yield buffer
        
@component("IN", "OUT")
def filter_values(values, out, comp=lambda x: True, add_ellipsis=False):
    for item in values:
        if comp(item):
            yield item
        elif add_ellipsis:
            yield Ellipsis