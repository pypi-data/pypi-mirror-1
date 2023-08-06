def register_admin(module_name, model_class_names):
    from django.contrib import admin
    module = __import__(module_name, {}, {}, [''])
    for model_class_name in model_class_names:
        model = getattr(module, model_class_name)
        admin_class = getattr(module, model_class_name+'Admin', None)
        admin.site.register(model, admin_class)


import time, traceback, logging, sys
class Status(object):
    def __init__(self):
        self.num_successful = 0
        self.failed_ids = []
        self.done = False
        self.cur_idx = 0

    def __repr__(self):
        return u'<Status: %s/%s, %s failed>' % (
            getattr(self, 'cur_idx', '-'),
            getattr(self, 'total', '-'),
            self.num_failed)

    @property
    def num_failed(self): return len(self.failed_ids)

    def start(self):
        self.start_time = time.time()

    def finished(self):
        self.cur_idx = self.total
        self.done = True
        self.end_time = time.time()

    @property
    def rate(self):
        if self.done:
            end_time = self.end_time
        else:
            end_time = time.time()
        return self.cur_idx / (end_time - self.start_time)

    @property
    def time_left(self):
        rate = self.rate
        if rate == 0: return 0
        return (self.total - self.cur_idx) / self.rate

def progress_callback(status):
    sys.stderr.write('%d/%d failed=%d, rate~%.2f per second, left~%.2f sec    \r' % (
            status.cur_idx, status.total, status.num_failed, status.rate, status.time_left))
    if status.done: sys.stderr.write('\n')
    sys.stderr.flush()


def queryset_foreach(queryset, f, batch_size=1000,
                     progress_callback=progress_callback, transaction=True):
    '''
    Call a function for each element in a queryset (actually, any list).

    Features:
    * stable memory usage (thanks to Django paginators)
    * progress indicators
    * wraps batches in transactions
    * can take Managers (e.g., Assertion.objects)
    * warns about DEBUG.
    * handles failures of single items without dying in general.
    * stable even if items are added or removed during processing
    (gets a list of ids at the start)

    Returns a Status object, with the following interesting attributes
      total: number of items in the queryset
      num_successful: count of successful items
      failed_ids: list of ids of items that failed
    '''
    
    from django.conf import settings
    if settings.DEBUG:
        print >> sys.stderr, 'Warning: DEBUG is on. django.db.connection.queries may use up a lot of memory.'
    
    # Get querysets corresponding to managers
    from django.shortcuts import _get_queryset
    queryset = _get_queryset(queryset)
    
    # Get a snapshot of all the ids that match the query
    logging.info('qs4e: Getting list of objects')
    ids = list(queryset.values_list(queryset.model._meta.pk.name, flat=True))

    # Initialize status
    status = Status()
    status.total = len(ids)

    def do_all_objects(objects):
        for id, obj in objects.iteritems():
            try:
                f(obj)
                status.num_successful += 1
            except Exception: # python 2.5+: doesn't catch KeyboardInterrupt or SystemExit
                traceback.print_exc()
                status.failed_ids.append(id)
        
    if transaction:
        # Wrap each batch in a transaction
        from django.db import transaction
        do_all_objects = transaction.commit_on_success(do_all_objects)
    
    from django.core.paginator import Paginator
    paginator = Paginator(ids, batch_size)

    status.start()
    progress_callback(status)
    for page_num in paginator.page_range:
        status.page = page = paginator.page(page_num)
        status.cur_idx = page.start_index()-1
        progress_callback(status)
        objects = queryset.in_bulk(page.object_list)
        do_all_objects(objects)
    status.finished()

    progress_callback(status)

    return status


from functools import wraps
from django.core.cache import cache
from django.utils.http import urlquote
class cached(object):
    '''Decorator to cache the results of a function depending on its parameters.'''
    def __init__(self, keyname, timeout=60):
        '''keyname_func: called with the same parameters as the wrapped function.
        returns a string containing the key.
        timeout: number of seconds to keep the result in the cache.'''
        if not callable(keyname):
            self.keyname_func = lambda *a: keyname % a
        else:
            self.keyname_func = keyname
        self.timeout = timeout

    def __call__(self, func):
        @wraps(func)
        def wrap(*a, **kw):
            # Compute the cache key.
            key = urlquote(self.keyname_func(*a, **kw))
            # Try to get it.
            result = cache.get(key)
            if result is not None:
                return result

            # Doesn't exist in the cache.
            result = func(*a, **kw)
            cache.set(key, result, self.timeout)
            return result
        wrap.is_cached = self.is_cached
        wrap.invalidate = self.invalidate
        return wrap

    def is_cached(self, *a, **kw):
        key = self.keyname_func(*a, **kw)
        return cache.get(key) is not None

    def invalidate(self, *a, **kw):
        key = self.keyname_func(*a, **kw)
        cache.delete(key)

    # Times
    minute = 60
    hour = minute*60
    day = hour*24
    week = day*7
    month = day*30
    year = day*365
