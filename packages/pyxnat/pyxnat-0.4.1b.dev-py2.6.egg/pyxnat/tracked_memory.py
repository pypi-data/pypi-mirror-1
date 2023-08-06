import os
import sys
import pickle
import shutil
import functools

module_path = os.path.dirname(os.path.abspath(__file__))

if os.path.join(module_path, 'externals') not in sys.path:
    sys.path.append(os.path.join(module_path, 'externals'))

from joblib import Memory
from joblib.memory import MemorizedFunc

from pathutils import Lock

class TrackedMemorizedFunc(MemorizedFunc):
    def __init__(self, func, cachedir, ignore=None, save_npy=True, 
                                    mmap_mode=None, debug=False):

        MemorizedFunc.__init__(self, func, cachedir, ignore, save_npy,
                                                     mmap_mode, debug)

        self._cachefile = os.path.join(self._get_func_dir(), 'memorized.pkl')
        self._init()

    def __call__(self, *args, **kwargs):
        lock = Lock(self._cachefile, timeout=0.5)
        lock.lock()
        output = super(TrackedMemorizedFunc, self).__call__(*args, **kwargs)
        lock.unlock()
        self.track(*args, **kwargs)

        return output

    def call(self, *args, **kwargs):
        lock = Lock(self._cachefile, timeout=0.5)
        lock.lock()
        output = super(TrackedMemorizedFunc, self).call(*args, **kwargs)
        lock.unlock()

        return output

    def _init(self):
        lock = Lock(self._cachefile, timeout=0.5)
        lock.lock()

        if not os.path.exists(self._get_func_dir()):
            os.makedirs(self._get_func_dir())

        if not os.path.exists(self._cachefile):

            fd = open(self._cachefile, 'w')
            pickle.dump([], fd)
            fd.close()

        lock.unlock()
       
    def tracked(self):
        self._init()

        lock = Lock(self._cachefile, timeout=0.5)
        lock.lock()

        fd = open(self._cachefile, 'r')
        history = pickle.load(fd)
        fd.close()

        lock.unlock()

        return history

    def force_output(self, output, *args, **kwargs):
        self._check_previous_func_code(stacklevel=3)
        self._persist_output(output, self.get_output_dir(*args, **kwargs))
        self.track(*args, **kwargs)

    def is_memorized(self, *args, **kwargs):
        return os.path.exists(self.get_output_dir(*args, **kwargs))

    def track(self, *args, **kwargs):
        self._init()

        lock = Lock(self._cachefile, timeout=0.5)
        lock.lock()

        fd = open(self._cachefile, 'r')
        tmp_index = pickle.load(fd)
        fd.close()

        if (args, kwargs) not in tmp_index:
            tmp_index.append((args, kwargs))

        fd = open(self._cachefile, 'w')        
        pickle.dump(tmp_index, fd)
        fd.close()

        lock.unlock()

    def clear_tracks(self, *args, **kwargs):
        self._init()

        lock = Lock(self._cachefile, timeout=0.5)
        lock.lock()

        if self.is_memorized(*args, **kwargs):
            shutil.rmtree(self.get_output_dir(*args, **kwargs))

        fd = open(self._cachefile, 'r')
        tmp_index = pickle.load(fd)
        fd.close()

        tmp_index.remove((args, kwargs))

        fd = open(self._cachefile, 'w')
        pickle.dump(tmp_index, fd)
        fd.close()

        lock.unlock()

    args_index = property(tracked)
    tracks = property(tracked)


class TrackedMemory(Memory):
    def __init__(self, cachedir, save_npy=True, mmap_mode=None, debug=False):
        Memory.__init__(self, cachedir, save_npy, mmap_mode, debug)

    def cache(self, func=None, ignore=None):
        """ Decorates the given function func to only compute its return
            value for input arguments not cached on disk.

            Returns
            -------
            decorated_func: MemorizedFunc object
                The returned object is a MemorizedFunc object, that is 
                callable (behaves like a function), but offers extra
                methods for cache lookup and management. See the
                documentation for :class:`joblib.memory.MemorizedFunc`.
        """
        if func is None:
            # Partial application, to be able to specify extra keyword 
            # arguments in decorators
            return functools.partial(self.cache, ignore=ignore)
        if self.cachedir is None:
            return func
        return TrackedMemorizedFunc(func, cachedir=self.cachedir,
                                   save_npy=self.save_npy,
                                   mmap_mode=self.mmap_mode,
                                   ignore=ignore,
                                   debug=self._debug)

    def clear(self, warn=True):
        """ Erase the complete cache directory.
        """
        if warn:
            self.warn('Flushing completely the cache')
        shutil.rmtree(self.cachedir)

        # os.access is for mswindows that doesn't release 
        # the folder handler rapidly enough
        os.access(self.cachedir, os.R_OK | os.W_OK)
        os.makedirs(self.cachedir)


