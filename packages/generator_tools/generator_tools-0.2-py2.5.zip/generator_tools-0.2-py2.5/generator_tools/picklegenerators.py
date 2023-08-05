import pickle
import types
import sys
from copygenerators import*
import warnings

warnings.simplefilter("always",PendingDeprecationWarning)

__all__ = ["GeneratorSnapshot", "pickle_generator", "unpickle_generator", "GeneratorPickler", "GeneratorUnpickler"]


def pickle_generator(f_gen, filelike):
    '''
    @param f_gen: generator object
    @param filename: destination file for pickling generator
    '''
    pickle.dump(GeneratorSnapshot(f_gen), filelike)
    filelike.close()

def unpickle_generator(filelike):
    '''
    @param filename: source file of pickled generator
    '''
    gen_snapshot = pickle.load(filelike)
    filelike.close()
    return copy_generator(gen_snapshot, copy_filter = lambda loc: True)


class GeneratorPickler_Deprecated(pickle.Pickler):
    def __init__(self, f):
        if isinstance(f, (str, unicode)):
            lineno = sys._getframe(0).f_lineno +1

            warnings.warn_explicit("string argument not supported in generator_tools 0.3 - use filelike instead!\n" , PendingDeprecationWarning, "picklegenerators.py", lineno)
            self.filelike = None
            self.filename = f
        else:
            self.filelike = f

    def pkl_device_new(self):
        return open(self.filename, "wb")

    def pkl_device_load(self):
        return open(self.filename, "rb")

    def pickle_generator(self, f_gen):
        pkl_device = self.pkl_device_new()
        lineno = sys._getframe(0).f_lineno +1

        warnings.warn_explicit("method pickle_generator deprecated in generator_tools 0.3 - use dump() instead!\n" , PendingDeprecationWarning, "picklegenerators.py", lineno)
        return pickle_generator(f_gen, pkl_device)

    def unpickle_generator(self):
        pkl_device = self.pkl_device_load()
        lineno = sys._getframe(0).f_lineno +1

        warnings.warn_explicit("method upickle_generator deprecated in generator_tools 0.3 - use GeneratorUnpickle.load() instead!\n" , PendingDeprecationWarning, "picklegenerators.py", lineno)
        return unpickle_generator(pkl_device)


class GeneratorPickler(GeneratorPickler_Deprecated):

    def dump(self, f_gen):
        '''
        Overloaded method of Pickler
        '''
        if self.filelike is None:
            self.filelike = self.pkl_device_new()
        return pickle_generator(f_gen, self.filelike)


class GeneratorUnpickler(pickle.Unpickler):
    def __init__(self, filelike):
        self.filelike = filelike

    def load(self):
        return unpickle_generator(self.filelike)




