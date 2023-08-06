from fasta import FastaRecord 

class TblFastaRecord(FastaRecord):
    __slots__ = ('fh', 'start', 'stop')
    ext = ".h5"

    def __init__(self, tbl, start, stop):

        self.tbl     = tbl
        self.stop    = stop
        self.start   = start

    def __len__(self):
        return self.stop - self.start

    @classmethod
    def prepare(self, filename):


        return open(filename, "r")

    @classmethod
    def modify_flat(self, flat_file):
        return None
    
    def _adjust_slice(self, islice):
        if not islice.start is None and islice.start < 0:
            istart = self.stop + islice.start
        else:
            istart = self.start + (0 if islice.start is None else islice.start)


        if not islice.stop is None and islice.stop < 0:
            istop = self.stop + islice.stop
        else:
            istop = self.stop if islice.stop is None else (self.start + islice.stop)
        return istart, istop

    def __getitem__(self, islice):
        fh = self.fh
        fh.seek(self.start)
        if isinstance(islice, (int, long)):
            if islice < 0:
                fh.seek(self.stop + islice)
            else:
                fh.seek(self.start + islice)
            return fh.read(1)

        if islice.start == 0 and islice.stop == sys.maxint:
            if islice.step in (1, None):
                return fh.read(self.stop - self.start)
            return fh.read(self.stop - self.start)[::islice.step]
        
        istart, istop = self._adjust_slice(islice)

        fh.seek(istart)

        l = istop - istart

        if islice.step in (1, None):
            return fh.read(l)

        return fh.read(l)[::islice.step]


    def __str__(self):
        return self[:]

    def __repr__(self):
        return "%s('%s', %i..%i)" % (self.__class__.__name__, self.fh.name,
                                   self.start, self.stop)

    @property
    def __array_interface__(self):
        return {
            'shape': (len(self), ),
            'typestr': '|S1',
            'version': 3,
            'data': buffer(self)
        }
