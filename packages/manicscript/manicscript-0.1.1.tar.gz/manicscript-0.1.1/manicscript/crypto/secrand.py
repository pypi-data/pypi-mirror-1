import random, struct

class SecureRandom(random.Random):
        def __init__(self, paranoid=True):
                self._file = None
                self._paranoid = paranoid
                self.seed(None)
        def seed(self, ignore):
                if self._file:
                        try:
                                close(self._file)
                        except:
                                pass
                if self._paranoid:
                        fname = '/dev/random'
                else:
                        fname = '/dev/urandom'
                self._file = open(fname, 'r')
        def getstate(self):
                return None
        def setstate(self, ignore):
                pass
        def jumpahead(self, ignore):
                pass
        def random(self):
                return abs(struct.unpack('I', self._file.read(4))[0])/(0.+(1<<32))
