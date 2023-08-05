import pickle
import types
from copygenerators import*

__all__ = ["GeneratorSnapshot", "pickle_generator", "unpickle_generator", "GeneratorPickler"]



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
    return copy_generator(gen_snapshot)


class GeneratorPickler(object):
    def __init__(self, filename):
        self.filename = filename

    def pkl_device_new(self):
        return open(self.filename, "wb")

    def pkl_device_load(self):
        return open(self.filename, "rb")

    def pickle_generator(self, f_gen):
        pkl_device = self.pkl_device_new()
        return pickle_generator(f_gen, pkl_device)

    def unpickle_generator(self, f_gen):
        pkl_device = self.pkl_device_load()
        return unpickle_generator(pkl_device)

