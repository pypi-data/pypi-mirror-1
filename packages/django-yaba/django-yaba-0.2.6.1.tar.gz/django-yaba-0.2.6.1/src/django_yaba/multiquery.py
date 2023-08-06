class MultiQuerySet(object):
    def __init__(self, *args, **kwargs):
        self.querysets = args
        self._count = None
    
    def _clone(self):
        querysets = [qs._clone() for qs in self.querysets]
        return MultiQuerySet(*querysets)
    
    def __repr__(self):
        return repr(list(self.querysets))
                
    def count(self):
        if not self._count:
            self._count = sum([qs.count() for qs in self.querysets])
        return self._count
    
    def __len__(self):
        return self.count()
    
    def __iter__(self):
        for qs in self.querysets:
            for item in qs.all():
                yield item

    def __getitem__(self, item):
        indices = (offset, stop, step) = item.indices(self.count())
        items = []
        total_len = stop - offset
        for qs in self.querysets:
            if len(qs) < offset:
                offset -= len(qs)
            else:
                items += list(qs[offset:stop])
                if len(items) >= total_len:
                    return items
                else:
                    offset = 0
                    stop = total_len - len(items)
                    continue

