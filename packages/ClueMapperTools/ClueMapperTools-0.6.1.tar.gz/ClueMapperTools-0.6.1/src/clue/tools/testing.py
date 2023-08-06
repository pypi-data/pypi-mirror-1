from clue.tools import fileio
import atexit


class Mock(object):
    """A mock class.

      >>> m = Mock(a=1)
      >>> m.a
      1
    """

    def __init__(self, **kw):
        self.__dict__.update(kw)


class MockDict(Mock):

    def __getitem__(self, k):
        return getattr(self, k)


_tracker = fileio.TempTracker()
gen_tempfile = _tracker.gen_tempfile
gen_tempdir = _tracker.gen_tempdir

atexit.register(_tracker.cleanup)
