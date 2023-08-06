import datetime

try:
    from dateutil import parser
except ImportError:
    parser = None

levels = ('year', 'month', 'day', 'hour', 'minute', 'second')
formatters = {} # functions to be called for each level of granularity

# some silly defaults
for level in levels:
    formatters[level] = lambda diff, date, now, _level=level: diff == 1 and ('%s ' + _level + ' ago') % diff or '%s %ss ago' % ( diff, _level )

# these callbacks can be altered at the module level

def prettyDate(date, level='day', now=None, **format):
    
    assert level in levels

    # convert strings to datetime objects
    if isinstance(date, basestring) and parser:
        date = parser.parse(date)

    # convert DateTime objects, which use callables, to something more sane
    callable = sum([hasattr(getattr(date, i),  '__call__') for i in levels])
    if callable:
        assert callable == len(levels) # ensure all of the levels are callable
        date = type('dummydate', (), dict([(i, getattr(date, i)()) for i in levels]))
        
    # find out now, if not given as cached
    if now is None:
        now = datetime.datetime.now()

    # define formatting functions
    _formatters = formatters.copy()
    for name, _format in format.items():

        # convert format strings to functions
        if isinstance(_format, basestring):
            _format = lambda diff, date, now, string=_format: date.strftime(string)

        _formatters[name] = _format
            
    #
    for _level in levels:
        diff = getattr(now, _level) - getattr(date, _level)
        if diff or _level == level:
            return _formatters[_level](diff, date, now)

if __name__ == '__main__':

    ### TESTS ###
    # XXX these should really be moved to another file
    
    # find a steady now to test against
    now = parser.parse('15:34 Jan 21, 2009')

    # test basic functionality
    assert prettyDate('Jan 16, 2009',now=now) == '5 days ago'
    assert prettyDate('Jan 21, 2006',now=now) == '3 years ago'
    assert prettyDate('Jan 21, 2009', level='minute', now=now) == '15 hours ago'

    # test date stamps
    stamp = '%b. %d, %Y, %l:%M%P'
    assert prettyDate('Jan 21, 2006', level='minute', now=now, year=stamp) == 'Jan. 21, 2006, 12:00am'
    assert prettyDate('Jan 20, 2009', level='minute', now=now, year=stamp) == '1 day ago'

    # some maybe nicer default formatting
    _formatters = {}    
    def format_date(diff, level, lookup=None):
        """format dates like 'last month' versus '1 month ago'"""
        if lookup and diff in lookup:
            return lookup[diff]
        if diff == 1:
            return 'last %s' % level
        return '%s %ss ago' % (diff, level)
    for level in levels:
        _formatters[level] = lambda diff, date, now, _level=level: format_date(diff, _level)

        # day we handle special
        if level == 'day':
            _formatters[level] = lambda diff, date, now, _level=level: format_date(diff, _level, {0:'today', 1:'yesterday'})

    # use a time for today
    _formatters['hour'] = _formatters['minute'] = _formatters['second'] = '%l:%M%P today'


    # test these callbacks
    assert prettyDate('Dec 20, 2008', now=now, **_formatters) == 'last year'
    assert prettyDate('Jan 20, 2009', now=now, **_formatters) == 'yesterday'
    assert prettyDate('Jan 21, 2009', now=now, **_formatters) == 'today'

    assert prettyDate('Jan 21, 2009', level='hour', now=now, **_formatters) == '12:00am today'
    assert prettyDate('10:30 Jan 21, 2009', level='hour', now=now, **_formatters) == '10:30am today'

