"""
Returns a human-friendly date relative to now
"""

import datetime

# allow parsing of dates from strings if the dateutil modele is available
try:
    from dateutil import parser
except ImportError:
    parser = None

levels = ('year', 'month', 'day', 'hour', 'minute', 'second')
formatters = {} # functions to be called for each level of granularity

### formatting callbacks

# callbacks to display how many time units ago
time_ago = {}
for level in levels:
    time_ago[level] = lambda diff, date, now, _level=level: diff == 1 and ('%s ' + _level + ' ago') % diff or '%s %ss ago' % ( diff, _level )

# callbacks to display when the date was relative to now
def last_time(diff, level, lookup=None):
    if lookup and diff in lookup:
        return lookup[diff]
    if diff == 1:
        return 'last %s' % level
    if diff == -1:
        return 'next %s' % level
    if diff > 0:
        return '%s %ss ago' % (diff, level)
    if diff < 0:
        return '%s %ss from now' % (diff, level)
    return 'this %s' % level
last = {}
for level in levels:
    last[level] = lambda diff, date, now, _level=level: last_time(diff, _level)
# handle day differently
last['day'] = lambda diff, date, now: last_time(diff, 'day', {0: 'today', 1: 'yesterday', -1: 'tommorow'})
# use a timestamp for today
last['hour'] = last['minute'] = last['second'] = '%l:%M%P today'

datestamp = '%b. %-d, %Y'
default = { 'year': datestamp,
            'month': datestamp,
            }

def day_diff(diff, date, now):
    map = { 1: 'yesterday',
            0: 'today',
            -1: 'tomorrow'}
    if diff in map:
        return map[diff] + ' ' + date.strftime('%l:%M %P')
    if 0 > diff > -7:
        return date.strftime('%A')
    return date.strftime(datestamp)
            
default['day'] = day_diff

# default callbacks
formatters = default

def prettyDate(date, level='day', now=None, **format):
    """
    return a human-friendly date string

    * date : date to be returned as a string

    * level : how fine-grained you want the result to be;  should be one of `levels`

    * now : optional value for now, otherwise it is taken from datetime.datetime.now

    * format : callbacks to format based upon level of granularity.  The keys should be one of levels
    """
    
    assert level in levels

    # convert strings to datetime objects
    if isinstance(date, basestring) and parser:
        date = parser.parse(date)

    # assert that a minimum level of date information
    for i in levels[:3]:
        try:
            assert hasattr(date, i)
        except AssertionError:
            raise ValueError('pretty_date: Unknown date object: %s' % date.__class__)

    timetuple = [] # intentional misnomer
    flag = False
    for i in levels:
        attr = getattr(date, i, None)

        # fill in missing attributes
        if attr is None:
            flag = True
            break

        # convert DateTime objects, which use callables, to something more sane
        if hasattr(attr, '__call__'):
            attr = attr()
            flag = True
        timetuple.append(attr)
    if flag:
        date = datetime.datetime(*timetuple)
    
#     try:
#         callable = sum([hasattr(getattr(date, i),  '__call__') for i in levels])
#     except AttributeError:
#         # assert date objects should have the levels attrs
#         raise ValueError('pretty_date: Unknown date object: %s' % date.__class__)

#     if callable:
#         assert callable == len(levels) # ensure all of the levels are callable
#         date = type('dummydate', (), dict([(i, getattr(date, i)()) for i in levels]))
        
    # find out now, if not given as cached
    if now is None:
        now = datetime.datetime.now()

    # define formatting functions
    _formatters = formatters.copy()
    _formatters.update(format)
    for name, _format in _formatters.items():

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
    assert prettyDate('Jan 16, 2009',now=now, **time_ago) == '5 days ago'
    assert prettyDate('Jan 21, 2006',now=now, **time_ago) == '3 years ago'
    assert prettyDate('Jan 21, 2009', level='minute', now=now, **time_ago) == '15 hours ago'

    # test date stamps
    datestamp = '%b. %d, %Y, %l:%M%P'
    assert prettyDate('Jan 21, 2006', level='minute', now=now, year=datestamp) == 'Jan. 21, 2006, 12:00am'
    _formatters = time_ago.copy()
    _formatters['year'] = datestamp

    assert prettyDate('Jan 20, 2009', level='minute', now=now, **_formatters) == '1 day ago'


    # test the 'last' callbacks
    assert prettyDate('Dec 20, 2008', now=now, **last) == 'last year'
    assert prettyDate('Jan 20, 2009', now=now, **last) == 'yesterday'
    assert prettyDate('Jan 21, 2009', now=now, **last) == 'today'

    assert prettyDate('Jan 21, 2009', level='hour', now=now, **last) == '12:00am today'
    assert prettyDate('10:30 Jan 21, 2009', level='hour', now=now, **last) == '10:30am today'

