# vim: set expandtab ts=4 sw=4 filetype=python:

from __future__ import with_statement

import contextlib, multiprocessing, os, subprocess, sys, tempfile, \
time, warnings

from UserDict import UserDict
from copy import copy
from datetime import datetime, timedelta

from decorator import decorator

def listmofize(x):

    """
    Return x inside a list if it isn't already a list or tuple.
    Otherwise, return x.

    >>> listmofize('abc')
    ['abc']

    >>> listmofize(['abc', 'def'])
    ['abc', 'def']

    >>> listmofize((1,2))
    (1, 2)
    """

    if not isinstance(x, (list, tuple)): return [x]
    else: return x

def attrsearch(o, attr_substr):

    """
    Return a list of any attributes of object o that have the string
    attr_substr in the name of the attribute.

    >>> attrsearch(dict(), 'key')
    ['fromkeys', 'has_key', 'iterkeys', 'keys']

    >>> attrsearch(object(), 'vermicious knid')
    []
    """

    return [a for a in dir(o) if attr_substr.lower() in a.lower()]

def powerset_generator(s):
    """
    s must be a set object.  Remember you'll get 2**len(s) values.

    >>> list(powerset_generator(set('ab')))
    [set([]), set(['a']), set(['b']), set(['a', 'b'])]

    >>> len(list(powerset_generator(set('abcdef'))))
    64

    """

    if len(s) == 0:
        yield set()
    else:
        # Non-destructively choose a random element:
        x = set([iter(s).next()])
        for ss in powerset_generator(s - x):
            yield ss
            yield ss | x

def chunkify(s, chunksize):

    """
    Yield sequence s in chunks of size chunksize.

    >>> list(chunkify('abcdefg', 2))
    ['ab', 'cd', 'ef', 'g']

    >>> list(chunkify('abcdefg', 99))
    ['abcdefg']

    """

    for i in range(0, len(s), chunksize):
        yield s[i:i+chunksize]

class attrdict(UserDict):
    """
    Just like a regular dict, but keys are also available as attributes.

    >>> a = attrdict({'x':1, 'y':2})

    >>> a['x']
    1

    >>> a.x
    1

    >>> a['z']
    Traceback (most recent call last):
        ....
    KeyError: 'z'
    """

    def __getattr__(self, name):
        return self.data[name]

def daterange_generator(from_this_date, increment, until_this_date):

    """
    Yield datetimes from_this_date + increment until until_this_date.

    >>> a = datetime.now()

    >>> b = a + timedelta(minutes=1)

    >>> len(list(daterange_generator(a, timedelta(minutes=1), b)))
    1

    >>> list(daterange_generator(b, timedelta(minutes=1), a))
    []
    """

    x = copy(from_this_date)

    while x < until_this_date:
        yield x
        x += increment


def deprecated(message='Deprecated!'):
    """
    Raise a DeprecationWarning before calling the function.
    """

    def _d(f, *args, **kwargs):
        warnings.warn(message, DeprecationWarning)
        return f(*args, **kwargs)

    return decorator(_d)


def walkup(path="right here"):

    """
    Yield paths closer and closer to the to of the filesystem.
    """

    if path == "right here":
        path = os.getcwd()

    at_top = False
    while not at_top:
        yield path
        parent_path = os.path.dirname(path)
        if parent_path == path:
            at_top = True
        else:
            path = parent_path 


def send_through_pager(s):
    """
    Open up this user's pager and send string s through it.

    If I don't find a $PAGER variable and "which less" fails, I'll just
    print the damn string.
    """

    pager = os.environ.get('PAGER')

    # Look for the less pager.
    if not pager and subprocess.Popen(
        ['which', 'less'],
        stdout=subprocess.PIPE).wait() == 0:

            pager = 'less'


    if pager:
        p = subprocess.Popen([pager], stdin=subprocess.PIPE)
        p.communicate(s)

    else:
        print(s)


def draw_ascii_spinner(delay=0.2):
    for char in '/-\\|':
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
        sys.stdout.write('\r')


def spin_forever():
    while 1:
        draw_ascii_spinner()


@contextlib.contextmanager
def spinning_distraction():
    p = multiprocessing.Process(target=spin_forever)
    p.start()
    try:
        yield

    finally:
        p.terminate()
        sys.stdout.write('\r')
        sys.stdout.flush()


def maybe_add_ellipses(s, maxlen=72):
    """
    If string s is longer than maxlen, truncate it and add on ... to
    the end.

    >>> maybe_add_ellipses('abcdef')
    'abcdef'
    >>> maybe_add_ellipses('abcdef', 3)
    'abc...'
    """

    if len(s) <= maxlen:
        return s

    else:
        return "%s..." % s[:maxlen]


def edit_with_editor(s=None):
    """
    Open os.environ['EDITOR'] and load in text s.
    
    Returns the text typed in the editor, after running strip().
    """

    # This is the first time I've used with!
    with tempfile.NamedTemporaryFile() as t:

        if s:
            t.write(str(s))
            t.seek(0)

        subprocess.call([os.environ.get('EDITOR', 'vi'), t.name])
        return t.read().strip()


def csum(seq):
    """
    Yields the cumulative sum of each element in seq.

    >>> csum([4,3,2,1]) # doctest: +ELLIPSIS 
    <generator object csum at ...>

    >>> zip([3,2,1], csum([3,2,1]))
    [(3, 3), (2, 5), (1, 6)]
    """

    tot = 0

    for x in seq:
        tot += x
        yield tot

def time_ago(date):

    """
    Returns a string like '3 minutes ago' or '8 hours ago'

    Got this from joltz in #python on freenode.  Thanks!

    >>> time_ago(datetime.now() - timedelta(seconds=90))
    'one minute ago'
    >>> time_ago(datetime.now() - timedelta(seconds=900))
    '15 minutes ago'
    >>> time_ago(datetime.now() - timedelta(seconds=60*12))
    '12 minutes ago'
    >>> time_ago(datetime.now() - timedelta(seconds=60*60*4))
    'about 4 hours ago'
    """

    current_date = datetime.now()
    hours_ago = (current_date - date).seconds / 60 / 60
    minutes_ago = (current_date - date).seconds / 60
    days_ago = (current_date - date).days

    if days_ago > 0: # More than 24 hours ago
        return date.strftime('on %h %d, %Y at %I:%M%p')

    if hours_ago >= 1 and hours_ago <= 23: # An hour or more ago
        if hours_ago > 1:
            return "about %s hours ago" % str(hours_ago)
        else:
            return "about an hour ago"

    if minutes_ago >= 0 and minutes_ago <= 59: # Less than an hour ago
        if minutes_ago > 1:
            return "%s minutes ago" % str(minutes_ago)
        elif minutes_ago == 1:
            return "one minute ago"
        else:
            return "just now"


