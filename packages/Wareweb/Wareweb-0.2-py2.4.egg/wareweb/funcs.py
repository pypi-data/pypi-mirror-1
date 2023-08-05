"""
General-(web-)purpose functions for use in your applications.
"""
import cgi
import urllib
import re
import datetime

__all__ = ['html_quote', 'url_quote', 'html_quote_whitespace']

def html_quote(v):
    """
    HTML quote the value.  None becomes an empty string.  If a value
    has an ``__html__`` method, that will be called to get the HTML.
    """
    if v is None:
        return ''
    if hasattr(v, '__html__'):
        return v.__html__()
    if isinstance(v, basestring):
        return cgi.escape(v, 1)
    return cgi.escape(str(v), 1)

def url_quote(v):
    """
    URL quote the value.  None becomes the empty string.  Dictionaries
    are mapped to 
    """
    if isinstance(v, dict):
        return urllib.urlencode(v)
    elif v is None:
        return ''
    else:
        return urllib.urlquote(str(v))

_whitespace_re = re.compile(r'[ ][ ]+')

def html_quote_whitespace(v, newlines=True, strip=True):
    """
    HTML quote a value, and then make sure its whitespace is
    preserved.  If ``newlines`` is true, then also turn newlines into
    ``<br>`` -- otherwise just horizontal whitespace will be preserved
    (using ``&nbsp;``).
    """
    v = html_quote(v)
    if strip:
        v = v.strip()
    v = v.replace('\t', ' '*4)
    if newlines:
        lines = v.splitlines()
        for i in range(len(lines)):
            if lines[i].startswith(' '):
                lines[i] = '&nbsp;'+lines[i][1:]
        v = '<br />\n'.join(lines)
    v = _whitespace_re.sub(_sub_white, v)
    return v

def _sub_white(m):
    if len(m.group(0)) % 2:
        return m.group(0).replace('  ', '&nbsp; ')
    else:
        return '&nbsp;'+'&nbsp; '*(len(m.group(0))/2)

def format_date_relative(date):
    """
    Formats a date relative to the current time.  The result
    will be dates like 'Yesterday', 'Wednesday 10:00am',
    '12 May 2003', etc.

    Specifically:

      * If in the last 24 hours, just give the time.
      * If yesterday, give 'yesterday TIME'
      * If in the last 7 days, give 'DAY_OF_WEEK TIME'
      * If in the same calendar year, give 'DAY_OF_MONTH MONTH'
      * Otherwise gives 'DAY_OF_MONTH MONTH YEAR'

    It uses english names when appropriate (e.g., Apr or Thu).
    """
    if date is None:
        return ''
    if isinstance(date, datetime.datetime):
        now = datetime.datetime.now()
    elif isinstance(date, datetime.date):
        now = datetime.date.today()
    else:
        raise ValueError(
            "Unknown type of date: %r" % date)
    year = date.year
    month = date.month
    day = date.day
    if now.year == year:
        if now.month == month:
            if (now - date) < datetime.timedelta(days=7):
                if now.day == day:
                    return format_time(date)
                elif now.day - 1 == day:
                    return 'Yest %s' % format_time(date)
                else:
                    return date.strftime('%a ') + format_time(date)
            elif (now - date) < datetime.timedelta(days=7):
                return date.strftime('%a %d %b')
            else:
                return date.strftime('%d %b')
        else:
            return date.strftime('%d %b')
    else:
        return date.strftime('%d %b \'%y')

def format_time(t):
    """
    Formats the time, like 4:20pm; unlike strftime, it lower-cases
    the am/pm, and doesn't create hours with leading zeros.
    """
    text = t.strftime('%I:%M%p')
    text = text[:-2] + text[-2:].lower()
    if text.startswith('0'):
        text = text[1:]
    return text

