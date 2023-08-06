
import hotshot
import time
import os
from webob import Request, Response


class StatsInfo(object):

    def __init__(self, stats, id):
        self.id = id
        self.stats = stats
        self._stats_dict = stats.stats

    @classmethod
    def load_hotshot(cls, filename, id=None):
        id = id or int(time.time())
        pstats = hotshot.stats.load(filename)
        return StatsInfo(pstats, id)

    def get_total_tt(self):
        return self.stats.total_tt
    total_tt = property(get_total_tt)

    def get_total_calls(self):
        return self.stats.total_calls
    total_calls = property(get_total_calls)

    def get_primitive_calls(self):
        return self.stats.prim_calls
    prim_calls = property(get_primitive_calls)

    def iteritems(self, filters=None, sortfields=None, strip_dirs=True):
        """Yield dictionaries of stats ordered by sortfields. If present,
        filters should be a list of strings to filter the results by"""
        sortfields = sortfields or []
        filters = filters or [10]
        if sortfields:
            self.stats.sort_stats(*sortfields)
        fcn_list = self.get_filtered_keys(*filters)
        for func_info in fcn_list:
            filename, line, name = func_info
            cc, nc, tt, ct, callers = self._stats_dict[func_info]
            f_stats = {'tottime': tt,
                       'calls': nc,
                       'cumtime': ct,
                       'filename': filename,
                       'lineno': line,
                       'function': name,
                       'dirname': os.path.dirname(filename),
                       'basename': os.path.basename(filename)}
            if nc == 0:
                f_stats['tottime_percall'] = 0
            else:
                f_stats['tottime_percall'] = tt/nc
            if cc == 0:
                f_stats['cumtime_percall'] = 0
            else:
                f_stats['cumtime_percall'] = ct/cc
            yield f_stats

    def items(self, *args, **kwargs):
        """Yield dictionaries of stats ordered by sortfields. If present,
        filters should be a list of strings to filter the results by"""
        return list(self.iteritems(*args, **kwargs))

    def strip_dirs(self):
        self.stats.strip_dirs()

    def get_filtered_keys(self, *filters):
        stats_dict = self._stats_dict
        if self.stats.fcn_list:
            list = self.stats.fcn_list[:]
        else:
            list = stats_dict.keys()

        for selection in filters:
            list, msg = self.stats.eval_print_amount(selection, list, '')
        return list

    def sort(self, *sortby):
        self.stats.sort_stats(*sortby)


