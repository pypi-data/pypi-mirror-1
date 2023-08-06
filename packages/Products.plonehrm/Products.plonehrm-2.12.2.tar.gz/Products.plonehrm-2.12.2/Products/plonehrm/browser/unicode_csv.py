import cStringIO
import codecs
import csv


class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.

    MvL modified the original version from the Python documentation
    since that version use codecs.getincrementalencoder which is
    introduced in version 2.5 and thus not available in our 2.4.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getencoder(encoding)

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder(data)
        # write to the target stream
        self.stream.write(data[0])
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


class UnicodeDictWriter:
    """Unicode ready version of csv.DictWriter.

    Taken from http://www.halley.cc/code/?python/ucsv.py

    Made writing of the header optional and did some pep8 changes.
    """

    def __init__(self, f, fieldnames, restval="", extrasaction="raise",
                 dialect="excel", header=False, *args, **kwds):
        self.fieldnames = fieldnames    # list of keys for the dict
        self.restval = restval          # for writing short dicts
        if extrasaction.lower() not in ("raise", "ignore"):
            raise ValueError("extrasaction (%s) must be 'raise' or 'ignore'" %
                             extrasaction)
        self.extrasaction = extrasaction
        self.writer = UnicodeWriter(f, dialect, *args, **kwds)
        if header:
            self.writer.writerow(fieldnames)

    def _dict_to_list(self, rowdict):
        if self.extrasaction == "raise":
            for k in rowdict.keys():
                if k not in self.fieldnames:
                    raise ValueError("dict contains fields not in fieldnames")
        return [rowdict.get(key, self.restval) for key in self.fieldnames]

    def writerow(self, rowdict):
        return self.writer.writerow(self._dict_to_list(rowdict))

    def writerows(self, rowdicts):
        rows = []
        for rowdict in rowdicts:
            rows.append(self._dict_to_list(rowdict))
        return self.writer.writerows(rows)
