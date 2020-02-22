# from https://stackoverflow.com/questions/3318625/how-to-implement-an-efficient-bidirectional-hash-table

class Bidict(dict):
    """
    Here is a class for a bidirectional dict, inspired by Finding key from 
    value in Python dictionary and modified to allow the following 2) and 3).

    Note that :

    1) The inverse directory bd.inverse auto-updates itself when the standard 
       dict bd is modified.
    2) The inverse directory bd.inverse[value] is always a list of key such 
       that bd[key] == value.
    3) Unlike the bidict module from https://pypi.python.org/pypi/bidict,
       here we can have 2 keys having same value, this is very important.

    Usage:

        bd = Bidict({'a': 1, 'b': 2})  
        print(bd)                     # {'a': 1, 'b': 2}                 
        print(bd.inverse)             # {1: ['a'], 2: ['b']}
        bd['c'] = 1                   # Now two keys have the same value (= 1)
        print(bd)                     # {'a': 1, 'c': 1, 'b': 2}
        print(bd.inverse)             # {1: ['a', 'c'], 2: ['b']}
        del bd['c']
        print(bd)                     # {'a': 1, 'b': 2}
        print(bd.inverse)             # {1: ['a'], 2: ['b']}
        del bd['a']
        print(bd)                     # {'b': 2}
        print(bd.inverse)             # {2: ['b']}
        bd['b'] = 3
        print(bd)                     # {'b': 3}
        print(bd.inverse)             # {2: [], 3: ['b']}
    """

    def __init__(self, *args, **kwargs):
        super(Bidict, self).__init__(*args, **kwargs)
        self.inverse = {}
        for key, value in self.items():
            self.inverse.setdefault(value,[]).append(key) 

    def __setitem__(self, key, value):
        if key in self:
            self.inverse[self[key]].remove(key) 
        super(Bidict, self).__setitem__(key, value)
        self.inverse.setdefault(value,[]).append(key)        

    def __delitem__(self, key):
        self.inverse.setdefault(self[key],[]).remove(key)
        if self[key] in self.inverse and not self.inverse[self[key]]: 
            del self.inverse[self[key]]
        super(Bidict, self).__delitem__(key)