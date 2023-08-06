def chunk(seq, chunk_size):
    '''
    Chunk a sequence into batches of a given size.

    The chunks are iterators (see itertools.groupby).
    '''
    # Based on a strategy on http://code.activestate.com/recipes/303279/
    from itertools import count, groupby
    c = count()
    for k, g in groupby(seq, lambda x: c.next() // chunk_size):
        yield g


import time, traceback, logging, sys
class Status(object):
    def __init__(self, total=None, report_interval=10):
        self.num_successful = 0
        self.failed_ids = []
        self.done = False
        self.cur_idx = 0
        self.total = total
        self.idx_of_last_report = 0
        self.report_interval = report_interval

    def __repr__(self):
        return u'<Status: %s/%s, %s failed>' % (
            getattr(self, 'cur_idx', '-'),
            getattr(self, 'total', '-'),
            self.num_failed)

    @property
    def num_failed(self): return len(self.failed_ids)

    def start(self):
        self.start_time = time.time()
        self.report()

    def finished(self):
        self.cur_idx = self.total
        self.done = True
        self.end_time = time.time()
        self.report()

    def done_with(self, num=1):
        self.cur_idx += num
        if self.cur_idx - self.idx_of_last_report >= self.report_interval:
            self.report()

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

    def report(self):
        sys.stderr.write('%d/%d failed=%d, rate~%.2f per second, left~%.2f sec    \r' % (
                self.cur_idx, self.total, self.num_failed, self.rate, self.time_left))
        if self.done: sys.stderr.write('\n')
        sys.stderr.flush()
        self.idx_of_last_report = self.cur_idx


class ForEach(object):
    def __init__(self, sequence, func, batch_size=1000, limit=None, stop_on_errors=True,
                 transaction=True, status_class=Status):
        self.status = status_class()
        self.__dict__.update(
            sequence=sequence, func=func, batch_size=batch_size, limit=limit,
            stop_on_errors=stop_on_errors, transaction=transaction, status_class=status_class)

        if transaction:
            # Wrap each batch in a transaction
            from django.db import transaction
            self.do_all_objects = transaction.commit_on_success(self.do_all_objects)

        self.setup_batches()

    def setup_batches(self):
        if isinstance(self.sequence, (list, tuple)):
            self.setup_list_batches()
        else:
            self.setup_queryset_batches()
            
    def setup_list_batches(self):
        self.batches = self.list_batches
        
        if self.limit is not None: self.sequence = self.sequence[:self.limit]
        self.status.total = len(self.sequence)
        self.batches = self.list_batches

    def list_batches(self):
        return chunk(enumerate(self.sequence), self.batch_size)

    def setup_queryset_batches(self):
        self.batches = self.queryset_batches

        from django.conf import settings
        if settings.DEBUG:
            logging.warn('Warning: DEBUG is on. django.db.connection.queries may use up a lot of memory.')

        # Get querysets corresponding to managers
        from django.shortcuts import _get_queryset
        self.queryset = queryset = _get_queryset(self.sequence)

        # Get a snapshot of all the ids that match the query
        logging.info('Getting list of matching objects')

        limited = queryset if self.limit is None else queryset[:self.limit]
        ids = list(limited.values_list(queryset.model._meta.pk.name, flat=True))
        self.status.total = len(ids)

        from django.core.paginator import Paginator
        self.paginator = Paginator(ids, self.batch_size)

    def queryset_batches(self):
        paginator, status, queryset = self.paginator, self.status, self.queryset
        for page_num in paginator.page_range:
            status.page = page = paginator.page(page_num)
            status.cur_idx = page.start_index()-1
            objects = queryset.in_bulk(page.object_list)
            yield objects.iteritems()
        
    def do_all_objects(self, batch):
        status, func = self.status, self.func
        for id, obj in batch:
            try:
                func(obj)
                status.num_successful += 1
            except Exception: # python 2.5+: doesn't catch KeyboardInterrupt or SystemExit
                if self.stop_on_errors: raise
                traceback.print_exc()
                status.failed_ids.append(id)

    def run(self):
        logging.info('Starting batch...')
        status, do_all_objects = self.status, self.do_all_objects
        status.start()
        
        for batch in self.batches():
            do_all_objects(batch)
            status.report()

        status.finished()
        logging.info('Batch complete.')
        return status

    
def foreach(seq, func, **kw):
    '''
    call a function for each element in a queryset (actually, any list
    with a length).

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

    It can run on a normal sequence:
    
    >>> count = 0
    >>> def process(thing):
    ...     global count
    ...     count += 1
    >>> status = foreach(range(50), process, batch_size=10, limit=50, transaction=False)
    >>> status.num_successful
    50

    Or it can use Querysets (or Models or Managers):
    
    >>> from csc.conceptnet4.models import Concept
    >>> count = 0
    >>> status = foreach(Concept, process, batch_size=10, limit=50, transaction=False)
    >>> status.num_successful
    50
    
    '''
    return ForEach(seq, func, **kw).run()


queryset_foreach = foreach
