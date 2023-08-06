import os.path
import cPickle as pickle
import base64
import logging
from csc.divisi.dict_mixin import MyDictMixin as DictMixin

### The old blending stuff that was here moved into blending.py.

def get_picklecached_thing(filename, func=None, name=None):
    # This functionality is superceded by PickleDict.get_lazy.
    if name is None: name = filename
    if filename.endswith('.gz'):
        import gzip
        opener = gzip.open
    else:
        opener = open
    try:
        f = opener(filename, 'rb')
        print 'Loading', name
        result = pickle.load(f)
        f.close()
    except IOError:
        if func is None: raise
        print 'Computing', name
        result = func()
        print 'Saving', name
        f = opener(filename, 'wb')
        pickle.dump(result, f, -1)
        f.close()
    return result

class ItemToAttrAdaptor(object):
    # List of things never to try to forward to the base object, because they're
    # just part of various dynamic introspection stuff.
    _blacklist = set(('_getAttributeNames', 'trait_names'))
    _passthrough = set(('mkdir',))

    def __init__(self, obj):
        '''
        Operations to attributes on this object translate to operations on
        items in obj.

        Except when you retrieve a PickleDict; then you get another ItemToAttrAdaptor.
        '''
        self._obj = obj

    def __repr__(self):
        return 'ItemToAttrAdaptor(%r)' % (self._obj,)

    def __getattr__(self, key):
        if key in self._blacklist: raise AttributeError(key)
        if key in self._passthrough and hasattr(self._obj, key):
            return getattr(self._obj, key)
        res = self._obj[key]
        return res if not isinstance(res, PickleDict) else res.d
    
    def __setattr__(self, key, val):
        if key.startswith('_') or key in self._blacklist:
            return super(ItemToAttrAdaptor, self).__setattr__(key, val)
        self._obj[key] = val

    def __delattr__(self, key):
        del self._obj[key]

    def __dir__(self):
        # This is only useful for Python 2.6+.
        return self._obj.keys() + list(self._passthrough)

def human_readable_size(sz, multiplier=1000, sizes=['B', 'kB', 'MB', 'GB']):
    '''
    Returns a "human-readable" formatting of a number of bytes.

    >>> human_readable_size(5)
    '5.00B'
    >>> human_readable_size(1500)
    '1.50kB'
    >>> human_readable_size(1500*1000)
    '1.50MB'
    '''
    for name in sizes:
        if sz < multiplier:
            break
        sz = sz / float(multiplier)
    return '%.2f%s' % (sz, name)

def get_ipython_history(num_entries=15):
    from IPython import ipapi
    ip = ipapi.get()
    if ip is None: return None
    input_lines = [item.strip() for item in ip.user_ns['In']]
    return [item for item in input_lines
            if item and not item.startswith('?') and not item.endswith('?')][-num_entries:]
    

class PickleDict(object, DictMixin):
    '''
    A PickleDict is a dict that dumps its values as pickles in a
    directory. It makes a convenient dumping ground for temporary
    data.

    >>> import tempfile
    >>> dirname = tempfile.mkdtemp()
    >>> pd = PickleDict(dirname)

    Let's clear out the directory so the tests start from a known state.
    
    >>> pd._clear()

    >>> pd['abc'] = 123
    >>> pd['abc']
    123

    It keeps an internal cache, so to make sure it's actually storing
    persistently, let's make a new one.

    >>> pd = PickleDict(dirname)
    >>> pd['abc']
    123

    It behaves like a dictionary:

    >>> pd.keys()
    ['abc']
    >>> pd.items()
    [('abc', 123)]

    If you're just using string keys, you can use the item-to-attr
    adaptor `d`:

    >>> pd.d.abc
    123
    >>> pd.d.key = 'val'
    >>> del pd.d.abc

    But unlike a normal Python dict, if you change the contents of a
    list or dict or Tensor that you've pickled, PickleDict won't know
    that you changed it, unless you tell it:

    >>> pd.d.a = [1, 2, 3]
    >>> pd.d.a.append(4)
    >>> pd.d.a = pd.d.a # Force a re-store

    Or you can explicitly say that something changed:

    >>> pd.changed('a')
    >>> pd.changed() # re-writes everything that's in the cache.
    
    PickleDict actually supports any hashable item as a key, by
    pickling then base64-encoding the key (prepending a `:`). If you
    see a bunch of odd-looking files, that's where they came from.

    >>> pd[1,2,3] = 4,5,6
    >>> pd[':abc'] = 'abc' # just to test...
    >>> pd.clear_cache()
    >>> ':abc' in pd.keys()
    True

    Subdirectories are also supported:

    >>> subdir = pd.mkdir('sub')
    >>> pd['sub'][7,8] = 9, 10
    >>> subdir[7,8]
    (9, 10)

    And you can rename things:

    >>> pd.rename('sub', 'dir2')
    >>> pd['dir2'][7, 8]
    (9, 10)

    It can also lazily compute an expensive function only if the
    result is not already pickled. (This replaces
    get_picklecached_thing.)

    >>> def thunk():
    ...     print 'Expensive calculation...'
    ...     return 42
    ... 
    >>> pd.get_lazy('the_answer', thunk)
    Expensive calculation...
    42
    >>> pd.get_lazy('the_answer', thunk)
    42
    >>> 'the_answer' in pd
    True

    Metadata is stored in a _meta subdirectory, as pickled
    dictionaries. One thing stored is the type of the object, so you
    don't have to load it to see what type it is.

    >>> pd['_meta']['the_answer']['type'] == str(int)
    True

    If you were running from within IPython, the metadata dict also
    includes 'context', which holds your last 15 IPython inputs.
    '''
    special_character = '+'
    
    def __init__(self, dir, gzip=True, store_metadata=True, log=True):
        self._logger = logging.getLogger('csc.divisi.util.PickleDict')
        self._log = log
        self._dir = os.path.abspath(os.path.expanduser(dir))
        self._gzip = gzip
        self._store_metadata = store_metadata
        if not os.path.isdir(self._dir):
            os.makedirs(self._dir)
        self.clear_cache()

    def __repr__(self):
        return 'PickleDict(%r)' % self._dir

    @property
    def d(self): return ItemToAttrAdaptor(self)
    
    def path_for_key(self, key):
        if not isinstance(key, basestring) or key.startswith(self.special_character):
            key = self.special_character+base64.urlsafe_b64encode(pickle.dumps(key, -1))
        return os.path.join(self._dir, key)

    def key_for_path(self, path):
        if path.startswith(self.special_character):
            return pickle.loads(base64.urlsafe_b64decode(path[1:]))
        return path

    def clear_cache(self):
        self._cache = {}

    def _load(self, key):
        '''
        Just load some data, bypassing the cache.
        '''
        path = self.path_for_key(key)
        if self._store_metadata and key == '_meta':
            if '_meta' not in self:
                self.mkdir('_meta')
            return MetaPickleDict(path)

        if os.path.isdir(path):
            # Keep sub-PickleDict objects in cache, so that they
            # can cache their own data.
            return PickleDict(path, gzip=self._gzip, store_metadata=self._store_metadata)
        if not os.path.exists(path):
            raise KeyError(key)
        if self._log: self._logger.info('Loading %r...', key)
        try:
            import gzip
            return pickle.load(gzip.open(path))
        except IOError:
            return pickle.load(open(path))
        
        
    def __getitem__(self, key):
        if key not in self._cache:
            self._cache[key] = self._load(key)
        return self._cache[key]
    
    def __setitem__(self, key, val):
        if self._log: self._logger.info('Saving %r...', key)
        self._cache[key] = val
        import gzip
        opener = gzip.open if self._gzip else open
        f = opener(self.path_for_key(key), 'wb')
        pickle.dump(val, f, -1)
        if self._log: self._logger.info('Saved %r (%s)', key, human_readable_size(f.tell()))
        f.close()

        if self._store_metadata:
            meta = {}
            meta['type'] = str(type(val))

            # Add IPython history
            try:
                meta['context'] = get_ipython_history(num_entries=20)
            except ImportError:
                pass
            self['_meta'][key] = meta

    def __delitem__(self, key):
        self._cache.pop(key, None) # don't fail if it's not cached.
        os.remove(self.path_for_key(key))


    def __setattr__(self, key, val):
        if not key.startswith('_'):
            if self._log: self._logger.warn('Setting attributes on PickleDict instances isn\'t persistent. You probably intended to use pickle_dir.d.attribute instead.')
        super(PickleDict, self).__setattr__(key, val)


    def _nuke(self):
        '''
        Destroy the directory tree, aka, ``rm -rf``.
        '''
        import shutil
        shutil.rmtree(self._dir)
        
        
    def _clear(self):
        '''
        Clear everything in the directory.
        '''
        self._nuke()
        os.makedirs(self._dir)
        self.clear_cache()

    
    def clear(self):
        raise NotImplementedError("`clear`? Do you really mean that? If so, run _clear instead.")
    
    def changed(self, name=None, ignore_not_present=False):
        if name is None:
            for k, v in self._cache.iteritems():
                if not isinstance(v, PickleDict):
                    self[k] = v
        else:
            if name not in self._cache and not ignore_not_present:
                raise KeyError('%s was not cached (so it could not have been changed in memory).' % name)
            self[name] = self._cache[name]
        
    def mkdir(self, name):
        os.mkdir(self.path_for_key(name))
        return self[name]

    def rename(self, old, new):
        os.rename(self.path_for_key(old), self.path_for_key(new))
        if old in self._cache:
            if not isinstance(self._cache[old], PickleDict):
                self._cache[new] = self._cache[old]
            del self._cache[old]


    def __iter__(self):
        return (self.key_for_path(filename) for filename in os.listdir(self._dir) if filename != '_meta')

    def has_key(self, key):
        return os.path.exists(self.path_for_key(key))


    # This is the replacement for get_picklecached_thing:
    def get_lazy(self, key, thunk):
        if key in self:
            #logging.info('get_lazy: found %r.' % (key,))
            return self[key]

        if self._log: self._logger.info('get_lazy: computing %r.' % (key,))
        result = thunk()
        self[key] = result
        return self[key]


class MetaPickleDict(PickleDict):
    def __init__(self, dir):
        super(MetaPickleDict, self).__init__(dir, gzip=False, store_metadata=False, log=False)
        

PickleDir = PickleDict
