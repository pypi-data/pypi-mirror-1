# -*- coding: UTF-8 -*-

"""
yagt improves the pyGTrends tool written by Sal Uryasev
(http://www.juiceanalytics.com/openjuice/programmatic-google-trends-api/).  The
authentication and connection of remains similar.  In addition to provide a
more Pythonic way to manipulate the downloaded data, yagt also give you a
simple command line interface (CLI) to grab data from Google Trends and save to
a csv file.

After install the module, you can access the simple CLI by using::

  $ python -m yagt <query1> <query2> [-u username] [other options]

The output will be saved to ``result.csv'' by default.  For more information
about the options, please use ``python -m yagt -h'' for the help page.  See
``LICENSE.txt'' for license agreement.
"""

__version__ = '0.3.1'

__description__ = """Y's API for Google Trends."""

class TrendsDict(dict):
    """
    A dictionary to store results from Google Trends.  The key 'day' and 'week'
    are exclusive.  They shouldn't be present at the same time.  The value for
    each key is a list of lists.  Each entry (list) in the outer list
    represents a row, and can be supplemented to csv.Writer.

    @cvar order: the order of names of stored sections/parts.
    @ctype order: tuple
    """

    order = (None, 'day', 'week', 'region', 'city', 'language')

    def __init__(self, *args, **kw):
        """
        @keyword data: unprocessed downloaded data.  Must specify.
        @type data: basestring
        """
        data = kw.pop('data')
        super(TrendsDict, self).__init__(*args, **kw)
        # split the 5 parts in the data and process each.
        parts = data.split('\n\n\n')
        for part in parts:
            # get the rows for the current part.
            rows = [line.strip().split('\t') for line in part.split('\n')]
            # get the name of the current part.
            if rows[0][0][0].isupper():
                name = rows[0][0].lower()
            else:
                name = None
            # save rows to self.
            self[name] = rows
            # set what key to check.
            if name == 'day':
                key_to_check = 'week'
            elif name == 'week':
                key_to_check = 'day'
        # make sure what shouldn't exist does not exist.
        assert self.get(key_to_check, None) == None

def write_csv(rows, filename):
    """
    Write rows of data to a CSV file.

    @param rows: a list of rows.
    @type rows: list
    @param filename: the name of the file to write to.
    @type filename: str
    @return: nothing.
    """
    from codecs import BOM_UTF8
    from csv import writer
    fobj = open(filename, 'w')
    fobj.write(BOM_UTF8)
    writer = writer(fobj, lineterminator='\n')
    writer.writerows(rows)
    fobj.close()

class Query(object):
    """
    Connect to Google Trends and get queried data.

    @ivar opener: Google Trends opener.
    @itype opener: urllib2.OpenerDirector
    """

    headers = [
        ('Content-type', 'application/x-www-form-urlencoded'),
        ('User-Agent', 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'),
        ('Accept', 'text/plain'),
    ]

    def __init__(self, username, password,
      do_data=False, do_raw=False, do_dict=True):
        """
        Take the authenticating information and connect to Google Trends.
        Create the opener.

        @param username: username of a Google account.
        @type username: str
        @param password: password of a Google account.
        @type password: str
        @keyword do_data: return downloaded data.
        @type do_data: bool
        @keyword do_raw: return also raw data.
        @type do_raw: bool
        @keyword do_dict: return dictionary processed from download data.
        @type do_dict: bool
        """
        from string import ascii_letters, digits
        from random import choice
        from cookielib import CookieJar
        from urllib import urlencode
        from urllib2 import build_opener, HTTPCookieProcessor
        self.do_dict = do_dict
        self.do_data = do_data
        self.do_raw = do_raw
        # request authentication.
        ## prepare connection parameters.
        alphanums = ascii_letters + digits
        GA3T = ''.join(choice(alphanums) for i in range(11))
        GALX = ''.join(choice(alphanums) for i in range(11))
        params = urlencode({
            'GA3T': GA3T,   # unique identifiers for session.
            'GALX': GALX,   # unique identifiers for session.
            'continue': 'http://www.google.com/trends',
            'nui': '1',
            'hl': 'en-US',
            'rmShown': '1',
            'PersistentCookie': 'yes',
            'Email': username,
            'Passwd': password,
            'service': 'trends',
        })
        url = 'https://www.google.com/accounts/ServiceLoginBoxAuth'
        ## make connection and store it into self.
        opener = build_opener(HTTPCookieProcessor(CookieJar()))
        opener.addheaders = self.headers
        opener.open(url, params)
        self.opener = opener
        
    def __call__(self, *args, **kw):
        """
        Download the report of a specific set of query keywords.  All the query
        arguments should be unicode objects.

        @keyword date: a string for the month/year to query.  The format for 
            year is 'YYYY'.  The format for month is 'YYYY-M'.  It can also be
            'mtd' (month to date) or 'ytd' (year to date).  Default is 'all'
            for all the time.
        @type date: str
        @keyword geo: a string for the regions.  Default is 'all' for all
            regions.
        @type geo: str
        @keyword graph: always 'all_csv'.
        @type graph: str
        @keyword sort: an index for on what sorting is based.  0 for the 1st, 1
            for the 2nd keywords, and so on.
        @type sort: int
        @keyword scale: flag for fixed scaling.  0 for relative scaling while 1
            for fixed scaling.
        @type scale: int
        @keyword sa: always 'N'.
        @type sa: str
        @return: a dict processed from data from Google Trends or the data
            itself from Google Trends, or a tuple combining two.
        @rtype: dict/str/tuple
        """
        from urllib import urlencode
        # request information.
        params = dict(
            q=','.join(arg.encode('utf-8') for arg in args),
            date='all',
            geo='all',
            graph='all_csv',
            sort=0,
            scale=0,
            sa='N',
        )
        for key in params.keys():   # don't pull in unused keys.
            params[key] = kw.get(key, params[key])
        params = urlencode(params)
        raw = self.opener.open('http://www.google.com/trends/viz?'+params).read()
        # clean up unwanted characters.
        data = raw.decode('utf-16le')
        data = data.replace('\r\n', '\n').strip().encode('utf-8')
        if data == 'You must be signed in to export data from Google Trends':
            raise ValueError, data
        # craft returns.
        if self.do_dict:
            result = TrendsDict(data=data)
            if self.do_data:
                if self.do_raw:
                    return result, data, raw
                else:
                    return result, data
            else:
                return result
        else:
            if self.do_data:
                if self.do_raw:
                    return data, raw
                else:
                    return data
            else:
                return

class CmdParam(object):
    """
    Command line parameters.
    """
    def __init__(self):
        from optparse import OptionParser, OptionGroup
        op = OptionParser(
            usage='usage: %prog <term1> <term2> ... '
                '[-u username] [other options]',
            version='%%prog %s' % __version__,
        )
        opg = OptionGroup(op, 'Authentication Information')
        opg.add_option('-u', action='store', type='string',
            dest='username', default='',
            help='The username of a Google Account.',
        )
        op.add_option_group(opg)
        opg = OptionGroup(op, 'Query')
        opg.add_option('-d', action='store', type='string',
            dest='date', default='all',
            help='Specify the span of time; default is all; '
                'to specify month, use the format of YYYY-M; '
                'to specify year, use the format of YYYY.',
        )
        opg.add_option('-s', action='store', type='int',
            dest='scale', default='0',
            help='0 (default) for relative scale; 1 for fixed scale.',
        )
        op.add_option_group(opg)
        opg = OptionGroup(op, 'Output')
        opg.add_option('-p', action='store',
            dest='parts', default='day,week',
            help='Specify the part/section to output.  '
                'Use comma to separate multiple parts.',
        )
        opg.add_option('-f', action='store',
            dest='filename', default='result.csv',
            help='Output file name.',
        )
        opg.add_option('-k', action='store_true',
            dest='append_key', default=False,
            help='Flag to append the name of section to the main output file '
                'name.  If set, only the last valid specified section will be '
                'saved, since previous ones will be overridden.  Default is '
                'False.',
        )
        op.add_option_group(opg)
        # set to self.
        self.op = op
        self.options, self.arguments = self.op.parse_args()

def cmdline():
    """
    Command line frontend.

    @return: nothing.
    """
    import sys
    import os
    import getpass
    # get the command line options and arguments.
    clps = CmdParam()
    opts, args = clps.options, clps.arguments
    # get the username/password.
    username = opts.username
    if not username:
        username = raw_input('Username: ')
    password = getpass.getpass('Password: ')
    # connect to Google.
    query = Query(username, password)
    # prepare and make a query to Google Trends.
    kw = dict(date=opts.date)
    args = [arg.decode(sys.stdin.encoding) for arg in args]
    result = query(*args, **kw)
    # save to files.
    parts = opts.parts.split(',')
    for key in parts:
        rows = result.get(key, None)
        if rows == None:
            continue
        filename = opts.filename
        if opts.append_key:
            main, ext = os.path.splitext(filename)
            filename = main + '_%s'%key + ext
        write_csv(rows, filename)

def main():
    cmdline()

if __name__ == '__main__':
    main()
