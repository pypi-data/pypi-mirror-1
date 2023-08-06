#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, os.path, math, fnmatch, re, time, calendar, string, socket, sys, md5, random, ConfigParser, socket
from copy import copy
from sets import Set
geocoder = None
try:
    import GeoIP
    geocoder = GeoIP.new(GeoIP.GEOIP_MEMORY_CACHE)
except:
    pass


LOG_LEVEL          = 1        # 0 == quiet, 1 == normal, 2 == debug
DISC_SYNC_CNT      = 100000   # number of records to hold in memory before flushing to disk
SORT_BUFFER_LENGTH = 100000   # number of records to hold before triggering a sort & prune operation
PROGRESS_INTERVAL  = 20000    # ie warn('processed X lines...')

# randomize the disc sync and sort_buffer len to reduce the 
# chance of thrashing the disks in mutlicore mode.
DISC_SYNC_CNT      += (DISC_SYNC_CNT * 0.08 * random.random())
SORT_BUFFER_LENGTH += (SORT_BUFFER_LENGTH * 0.08 * random.random())


def warn(s):
    if LOG_LEVEL < 1: return
    sys.stderr.write(s+'\n')


# change these defaults in your wtop.cfg file
LOG_ROOT = LOG_FILE = LOG_FILE_TYPE = LOG_FORMAT = DEFAULT_OUTPUT_FIELDS = MAX_REQUEST_TIME = MIN_RPS = re_robots =re_generic = re_classes = None
config = {}


# yes, this is ugly.
def configure(cfg_file=None):
    global config, LOG_ROOT, LOG_FILE, LOG_FILE_TYPE, LOG_FORMAT, DEFAULT_OUTPUT_FIELDS, MAX_REQUEST_TIME, MIN_RPS,re_robots,re_generic,re_classes,LOG_PATTERN,LOG_COLUMNS

    if not cfg_file:
        cfg_file    = '/etc/wtop.cfg'                              # unix, osx, etc
        if os.name != 'posix' and os.environ.has_key('HOMEPATH'):  # windows
            cfg_file = os.path.join(os.environ.get('HOMEPATH'), 'wtop.cfg')

    if not os.path.exists(cfg_file):
        raise Exception("can't read config file: '%s'" % cfg_file)

    config = ConfigParser.ConfigParser()
    config.read(cfg_file)

    LOG_ROOT               = config.get('main', 'log_root')
    LOG_FILE               = config.get('main', 'log_file')
    LOG_FILE_TYPE          = config.get('main', 'log_file_type')
    LOG_FORMAT             = config.get('main', 'log_format')
    DEFAULT_OUTPUT_FIELDS  = config.get('main', 'default_output_fields').split(',')
    MAX_REQUEST_TIME       = int(config.get('wtop', 'max_request_time'))
    MIN_RPS                = float(config.get('wtop', 'min_rps'))   
    classes = [(o, config.get('classes', o)) for o in config.options('classes')]

    ## compile a godawful bunch of regexps
    re_robots  = re.compile(config.get('patterns', 'robots'), re.I)
    re_generic = re.compile(config.get('patterns', 'generic'))
    re_classes = [(x[0], re.compile(x[1], re.I)) for x in classes]

    if LOG_FILE_TYPE == 'apache':
        # these may be overridden later by the logrep command line program because it
        # knows the fields the user asked for.
        LOG_PATTERN,LOG_COLUMNS = format2regexp(config.get('main', 'log_format'))


def flatten(x):
    result = []
    for el in x:
        if hasattr(el, "__iter__") and not isinstance(el, basestring):
            result.extend(flatten(el))
        else:
            result.append(el)
    return result



# translate log format string into a column list and regexp
restr            = r'(\S+)'
restr_skipped    = r'\S+'
requoted         = r'([^"]*)'
requoted_skipped = r'[^"]*'

# {DIRECTIVE_SYMBOL: (FIELD_NAME, REGEX_WHEN_NEEDED, REGEX_WHEN_SKIPPED)}
LOG_DIRECTIVES = {
    'h' : ('ip',         restr, restr_skipped),  # rhost is an odd one, since the default Apache is %h
    'a' : ('ip',         restr, restr_skipped),  # but HostnameLookups changes its content. bleh.
    'l' : ('auth',       restr, restr_skipped),
    'u' : ('username',   restr, restr_skipped),
    't' : ('timestamp',  r'\[?(\S+(?:\s+[\-\+]\d+)?)\]?', r'\[?\S+(?:\s+[\-\+]\d+)?\]?'),
    'r' : ('request',    r'(\S+ \S+ \S+)', r'\S+ \S+ \S+'),
    'm' : ('method',     restr, restr_skipped),
    'D' : ('msec',       restr, restr_skipped),
    'q' : ('query',      restr, restr_skipped),
    'D' : ('msec',       restr, restr_skipped),
    's' : ('status',     restr, restr_skipped),
    'b' : ('bytes',      restr, restr_skipped), 
    'B' : ('bytes',      restr, restr_skipped), # NB: may change to 'bytes_out'
    'I' : ('bytes_in',   restr, restr_skipped),
    'v' : ('domain',     restr, restr_skipped), # Host header
    'V' : ('domain',     restr, restr_skipped), # actual vhost. May clobber %v
    'p' : ('port',       restr, restr_skipped),
    '{ratio}n' : ('ratio', requoted, requoted_skipped), #todo: need generic %{foo}X parsing?
    '{host}i' : ('host', requoted, requoted_skipped), 
    '{referer}i' : ('ref', requoted, requoted_skipped), 
    '{user-agent}i' : ('ua', requoted, requoted_skipped)
}

# lower-case some apache header options.
def lcase(s):
    if s.find('{') > -1:
        return s.lower()
    return s

# given an Apache LogFormat string and an optional list of relevant fields,
# returns a regular expression that will parse the equivalent log line and 
# extract the necessary fields.
def format2regexp(fmt, relevant_fields=()):
    red = re.compile('%[\>\<\!,\d]*([\}\{\w\-]+)')
    directives = map(lcase, red.findall(fmt))
    colnames = []
    pat = fmt
    for k in directives:
        if not LOG_DIRECTIVES.has_key(k) and not k.find('{') > -1:
            continue

        field, pattern, skip_pattern = LOG_DIRECTIVES[k]
        atom = pattern
        if (not relevant_fields) or (field in relevant_fields):
            colnames.append(field)
        else:
            atom = skip_pattern

        if k.find('{') > -1:
            p = re.compile('%[\>\<\!,\d]*'+k.replace('}', '.').replace('{', '.'), re.I)
            pat = p.sub(atom, pat, re.I)
        else:
            pat = re.sub('%[\>\<\!,\d]*'+k, atom, pat)

    leftover = red.findall(pat)
    if leftover:
        warn('unrecognized format directives: %%%s' % ', %'.join(leftover))

    return pat, flatten(colnames)


    
# NCSA log format is whimsical. often a 0 is printed as '-'
def safeint(s):
    return int(s.replace('-', '0'))

### timestamp parsing
# This method is about 500% faster than the regex/strptime/timegm way. 
months = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}

# "There are 40 time zones instead of 24 as popularly believed..."
# http://en.wikipedia.org/wiki/List_of_time_zones
tzs = {'-0800': 28800, '+1000': -36000, '+1245': -40500, '+0330': -9000, '-0100': 3600, '+0930': -30600, '+1100': -39600, '-0900': 32400, '+1130': -37800, '+0700': -25200, '-0330': 12600, '-0700': 25200, '+0600': -21600, '-0600': 21600, '+0845': -26100, '-0500': 18000, '+0530': -16200, '+0100': -3600, '-0400': 14400, '+0000': 0, '-0430': 16200, '-0930': 34200, '+0300': -10800, '+1400': -50400, '+1030': -34200, '+0200': -7200, '+0900': -32400, '+0630': -19800, '+0545': -15300, '-0300': 10800, '+0800': -28800, '-1000': 36000, '-0200': 7200, '+0430': -12600, '-1100': 39600, '+0500': -18000, '-1200': 43200, '+1200': -43200, '+0400': -14400, '+1300': -46800}

# number of days from given year/month and 1 Jan 1970
# hack: only accurate from 1970 to 2099
month_offset = (0,31,59,90,120,151,181,212,243,273,304,334)
def date_ordinal(y, m):
    return ((y - 1970) * 365) + (y / 4) - 493 + month_offset[m-1]

# 21/Jul/2008:18:09:00 -0700   -->   1216688940
def apache2unixtime(t):
    return (((((date_ordinal(int(t[7:11]), months[t[3:6]]) + int(t[0:2]))*24) + int(t[12:14]))*60 + int(t[15:17]))*60) + int(t[18:20]) + tzs.get(t[21:26], 0)

# 21/Jul/2008:18:09:00 -0700   -->   (2008, 7, 21, 18, 9)
def apache2dateparts(t):
    return int(t[7:11]), months[t[3:6]], int(t[0:2]), int(t[12:14]), int(t[15:17])


# keeps a count of seen remote IP addresses. returns
# a value for the ipcnt field.
# nb: possbile memory problem with > 10M records
reip = re.compile(r'^\d+\.\d+\.\d+\.\d+$')
ipcnts = {}
def count_ips(ip):
    # compact the ip to 4 bytes for the ipcnts table
    ipkey = ip
    if reip.match(ip): # hack: some people still have HostnameLookups on
        ipkey = socket.inet_aton(ip)
    ipcnts[ipkey] = ipcnts.get(ipkey, 0) + 1
    return ipcnts[ipkey]


# Apache's %D returns an int of microseconds. nginx's $request_time
# equivalent is a float of S.MMM, so do the Right Thing.
# returns *milli*seconds
def fix_usec(s):
    if s.find('.') > -1:
        return int(float(s) * 1000)
    else:
        return int(s)/1000

# given a user-agent string, return (0, '') or (1, <MATCH>)
def parse_bots(ua):
    m = re_robots.search(ua)
    if m: return (1, ua[m.start():m.end()])
    return (0, '')

# '/'         --> 'home'
# '/foo.jpg'  --> 'img'
def classify_url(url):
    for classname, pattern in re_classes:
        if pattern.search(url):
            return classname
    m = re_generic.search(url)
    if m: return m.group(1)
    return 'UNKNOWN'

# return domain part of a URL.
# 'http://www.foo.com/bar.html'                 --> 'www.foo.com'
# 'example.com:8800/redirect.php?url=blah.html' --> 'example.com:8800'
re_domain = re.compile(r'(?:http://)?([^/]+)')
def domain(url):
    m = re_domain.match(url)
    if m: return m.group(1)
    return url


# todo.. the ':' thing is a defense against ipv6 addresses
# also we're kind of relying on the OS to cache ip resolutions
ipcache = {}
def lookup_ip(rhost):
    if not ipcache.has_key(rhost):
        if (reip.match(rhost) or rhost[0] == ':'): return rhost
        try:
            ipcache[rhost] = socket.gethostbyname(rhost)
        except:
            ipcache[rhost] = rhost
    return ipcache[rhost]

# field massage & mapping to derived fields
# SOURCE-FIELD, (DERIVED-FIELDS), FUNCTION
# note that 'class' derives from 'url', which derives from 'request'
col_fns = [
    ('msec',       ('msec',),    fix_usec),
    ('status',     ('status',),  int),
    ('bytes',      ('bytes',),   safeint),
    ('ip',         ('ipcnt',),   count_ips),
    ('ua',         ('bot', 'botname'),  parse_bots),
    ('ua',         ('uas',),     (lambda s: s[:30])),
    ('request',    ('method', 'url', 'proto'),    (lambda s: s.split(' '))),
    ('url',        ('class',),   classify_url),
    ('timestamp',  ('year', 'month', 'day', 'hour', 'minute'),   apache2dateparts),
    ('timestamp',  ('ts',),      apache2unixtime),
    ('ref',        ('refdom',),  domain),
]

# only possible if the geocoding lib is loaded. 
# hack: this does NOT work if HostnameLookups is on.
if geocoder: 
    col_fns.append(('ip', ('country',), (lambda ip: str(geocoder.country_name_by_addr(ip)))))
    col_fns.append(('ip', ('cc',),      (lambda ip: str(geocoder.country_code_by_addr(ip)))))

def hostname_hack():
    global col_fns
    col_fns = [('ip', ('ip',), lookup_ip)] + col_fns


def listify(x):
    if not hasattr(x,'__iter__'): return (x,)
    return x

# apply the col_fns to the records
def field_map(log, relevant_fields, col_fns):
    # get only the column functions that are necessary
    relevant_col_fns = filter((lambda f: relevant_fields.intersection(f[1])), col_fns)
    for record in log:
        for source_col, new_cols, fn in relevant_col_fns:        
            record.update(dict(zip(new_cols, listify(fn(record[source_col])))))
        yield record

# given a list of fields the user has asked for, look at the col_fns
# structure to see what parent fields they might depend on. for example, 
# 'year' depends on 'timestamp'. The idea is to only extract the fields
# from the raw log line that we actually need.
# two levels is ok for now and I'm too tired to write something recursive
def field_dependencies(requested_fields):
    deps = Set(requested_fields)
    deps = Set(flatten(map((lambda f: f[0:2]), filter((lambda f: deps.intersection(f[1])), col_fns))))
    deps = flatten(map((lambda f: f[0:2]), filter((lambda f: deps.intersection(f[1])), col_fns)))
    return Set(deps + requested_fields)


# This, believe it or not, is the work function. It takes in raw log
# lines and emits a generator of mapped, derived, massaged log records.
def apache_log(loglines, LOG_PATTERN, LOG_COLUMNS, relevant_fields):
    logpat     = re.compile(LOG_PATTERN) 
    groups     = (logpat.search(line) for line in loglines) 
    tuples     = (g.groups() for g in groups if g) 
    log        = (dict(zip(LOG_COLUMNS,t)) for t in tuples) 
    log        = field_map(log, relevant_fields, col_fns)
    return log

##########################################################################
## IIS-specific stuff. Can't be arsed to libraryize it.

#{'date':'2008-07-21', 'time':'18:09:00'} --> 1216663740
def iis2unixtime(r):
    return (((((date_ordinal(int(r['date'][0:4]), int(r['date'][5:7])) + int(r['date'][8:10]))*24) + int(r['time'][0:2]))*60 + int(r['time'][3:5]))*60) + int(r['time'][7:9])

def fix_query(q):
    if q[0] == '-': return ''
    return '?' + q

# source cols, parsing function takes whole record
iis_col_fns = [
    (('query',),                      (lambda x: fix_query(x['query']))),
    (('url',),                        (lambda x: x['path']+x['query'])),
    (('ts',),                         iis2unixtime),
    (('year','month','day'),          (lambda x: x['date'].split('-'))),
    (('hour','minute','second'),      (lambda x: x['time'].split(':'))),
    (('msec',),                       (lambda x: int(x['msec']))),
    (('status',),                     (lambda x: int(x['status']))),
    (('bytes',),                      (lambda x: int(x['bytes']))),
    (('ipcnt',),                      (lambda x: count_ips(x['ip']))),
    (('bot', 'botname'),              (lambda x: parse_bots(x['ua']))),
    (('uas',),                        (lambda x: x['ua'][:30])),
    (('class',),                      (lambda x: classify_url(x['url']))),
    (('refdom',),                     (lambda x: domain(x['ref']))),
]
if geocoder: 
    iis_col_fns.append((('country',),     (lambda x: str(geocoder.country_name_by_addr(x['ip'])))))
    iis_col_fns.append((('cc',),          (lambda x: str(geocoder.country_code_by_addr(x['ip'])))))

def iis_field_map(log, relevant_fields, col_fns):
    # get only the column functions that are necessary
    relevant_col_fns = filter((lambda f: relevant_fields.intersection(f[0])), iis_col_fns)
    for record in log:
        for new_cols, fn in relevant_col_fns:        
            record.update(dict(zip(new_cols, listify(fn(record)))))
        yield record

def iis_log(loglines, relevant_fields):
    cols = ('date', 'time', 's_sitename', 's_computername', 's_ip', 'method', 'path', 'query', 'port', 'user', 'ip', 
       'proto', 'ua', 'cookie', 'ref', 'vhost', 'status', 'substatus', 'win32_status', 'bytes_in', 'bytes', 'msec')
    tuples     = (line.split(' ') for line in loglines)
    log        = (dict(zip(cols,t)) for t in tuples) 
    log        = iis_field_map(log, relevant_fields, iis_col_fns)
    return log
##########################################################################

# this could be implemented as a -f filter, but this is faster.
def filter_by_class(reqs, include, exclude):
    for r in reqs:
        if (include and r['class'] not in include) or (exclude and r['class'] in exclude):
            continue
        yield r

def logs_for_date(dt):
    return sorted(gen_find(LOG_FILE+'.'+dt,LOG_ROOT), key=(lambda x: safeint(x.split('.')[-1])))

# support for the most common rotatelogs scheme, which is to rotate at midnight
def todays_logs():
    gmt_midnight = int(time.time() / 86400) * 86400
    r_file = "%s%s.%d" % (LOG_ROOT, LOG_FILE, gmt_midnight)
    if os.path.isfile(r_file): 
        return [r_file]
    return [LOG_ROOT + LOG_FILE]

def yesterdays_logs(): 
    gmt_yesterday = (int(time.time() / 86400) - 1) * 86400
    return ["%s%s.%d" % (LOG_ROOT, LOG_FILE, gmt_yesterday)]

def latest_log():
    return todays_logs()


# these alternative functions handle Netscaler-style logs: YYYYMMDD.log.1, YYYYMMDD.log.2, etc
# def logs_for_date(dt):
#     return sorted(gen_find(dt + '*.log*',LOG_ROOT), key=(lambda x: safeint(x.split('.')[-1])))
# def todays_logs(): 
#     return logs_for_date(time.strftime('%Y%m%d', time.localtime(time.time())))
# def yesterdays_logs(): 
#     return logs_for_date(time.strftime('%Y%m%d', time.localtime(time.time()-86400)))
#def latest_log():
#    return todays_logs()[-1]


## apache log funcs from David Beazley's generators talk
def gen_find(filepat,top): 
    for path, dirlist, filelist in os.walk(top): 
        for name in fnmatch.filter(filelist,filepat): 
            yield os.path.join(path,name)  

def gen_open(filenames): 
    for name in filenames: 
        handle = open(name)
        yield handle
        handle.close()

def gen_cat(sources): 
    for s in sources: 
        for item in s: 
            yield item 

def gen_grep(pat, lines): 
    patc = re.compile(pat) 
    for line in lines: 
        if patc.search(line): yield line 

def lines_from_dir(filepat, dirname): 
    names   = gen_find(filepat,dirname) 
    files   = gen_open(names) 
    lines   = gen_cat(files) 
    return lines 

def follow(thefile):
    last_seen = time.time()
    thefile.seek(0,2)      # Go to the end of the file 
    while True: 
         line = thefile.readline() 
         if not line:
             # hack: if the log is silent for awhile, it may have been rotated.
             if time.time() - last_seen > 30:
                 logfile = latest_log()[0] # todo: broken & stupid. necessary for netscaler
                 warn('no input for 30 seconds. reopening (%s)' % logfile)
                 thefile.close()
                 thefile = open(logfile) 
                 thefile.seek(0,2)
                 last_seen = time.time()   # so we don't start going nuts on the file.

             time.sleep(0.3)    # Sleep briefly 
             continue

         last_seen = time.time()
         yield line 


class circular_buffer(list):
    def __init__(self, length, initval=0):
        self.pointer = 0
        self += [initval] * length
        self.length = length    # actually maxlength
        self.cnt = 0            # real length
        
    def append(self, item):
        self.pointer %= self.length
        self.__setitem__(self.pointer, item)
        self.pointer += 1
        self.cnt = min(self.cnt+1, self.length)

    def __len__(self):
        return self.cnt


# round-robin database that only reports stats for the last X given seconds.
class rrd2:
    def __init__(self, length, window):
        self.length = length
        self.window = float(window)
        self.buf = circular_buffer(length, (0, 0, 0))

    def append(self, item, msec):
        self.buf.append((time.time(), item, msec))

    def get(self):
        ts = time.time()
        items = sorted(filter((lambda x: (ts-x[0]) < self.window), self.buf))
        if items:
            return items, float(ts - items[0][0])
        else:
            return [], 1.0

    def avg(self):
        items, mwindow = self.get()
        cnt = 0
        for item in items:
            cnt += item[1]
        return cnt / mwindow

    def stats(self):
        items, mwindow = self.get()
        cnt = 0
        msec_tot = 0
        msec_mn = 1<<32
        msec_mx = 0
        msecs = []

        for item in items:
            cnt += item[1]
            msec_tot += item[2]
            msec_mn = min(msec_mn, item[2])
            msec_mx = max(msec_mx, item[2])
            msecs.append(item[2])

        if not cnt: return (0,0,0,0,'',0,0)
        
        rps = cnt / mwindow
        msec_avg = msec_tot / float(cnt)
        msec_stddev = stddev(msecs, msec_avg)
        sparkline = hist_sparkline(msecs, msec_mn, msec_mx)
        return (rps, msec_avg, cnt, msec_stddev, sparkline, msec_mn, msec_mx)

def stddev(lst, avg):
    avg = float(avg)+1
    lst_len = len(lst)+1
    sumdist = sum([(avg - r) ** 2 for r in lst])
    return math.sqrt(abs(sumdist / lst_len)) / avg


    

# given a list of numbers, generates a very sketchy 
# ascii graph of the distribution.
sp_chars = (' ', '.','-','o','O','@','#')
#sp_chars = ('∙', '*', '⋆', '✶', '✸', '✦', '❖')
sp_steps = len(sp_chars)
tiles = 10
def hist_sparkline(lst, mn, mx):
    cnts = {}
    tot = len(lst)
    rn = mx-mn
    step = (rn / tiles) + 1

    if rn == 0:
        return sp_chars[0] * tiles

    steps = [int((x-mn)/step) for x in lst]
    for x in steps:
        cnts[x] = cnts.get(x, 0) + 1

    return ''.join([ sp_chars[int(round(cnts.get(x, 0)/float(tot) * (sp_steps-1)))]  for x in range(tiles)])

# 8.5444    -->  "8.54"
# 0.99222   -->  ".99"    
# 0.0000001 -->  "--"
def pretty_float(f):
    if f < 0.01: return '--'
    return ('%.2f' % f).replace('0.', '.')




# these two are suspiciously similar to gen_grep
def line_filter(lines, pat):
    r = re.compile(pat, re.I)
    for ln in lines:
        if r.search(ln):
            yield ln

def line_exclude(lines, pat):
    r = re.compile(pat, re.I)
    for ln in lines:
        if not r.search(ln):
            yield ln


# 100:1,2:desc --> limit 100, column 1 then column 2, descending order
def compile_orderby(commands):
    c = commands.split(':')
    limit = int(c[0])
    order_by = 0
    descending = True
    if len(c) > 1:
        order_by = map(int, c[1].split(','))
    if len(c) > 2:
        descending = (c[2][0].lower() == 'd')
    return limit, order_by, descending

# "sum(foo),bar,max(baz)"  -->  ('sum', 'foo'), (None, 'bar'), ('max', 'baz')
re_agg = re.compile(r'(?:(sum|count|avg|min|max|var|dev)\(([a-z\*1]+|)\)|([a-z]+))')
def compile_aggregates(commands):
    fields = re_agg.findall(commands)
    needed_fields = []
    all_fields = []
    group_by_fields = []
    has_agg = False
    for f in fields:
        if f[1] != '':
            needed_fields.append(f[1])
            all_fields.append((f[0:2]))
            has_agg = True
        else:
            needed_fields.append(f[2])
            all_fields.append((None, f[2]))
            group_by_fields.append(f[2])

    return needed_fields, all_fields, group_by_fields, has_agg


# This is a compiler for teeny tiny pattern match language.
# Given a string like "bytes<100,msec>1000", it returns a function that filters
# iterables of dicts by those conditions, with lazy evaluation. The operators are
#
#  >, < =, !=    comparison
#  ~, !~         regexp, not regexp
#
#  Example:  "foo~^ba+,baz>100"    
#   This returns true if the foo key matches "ba", "baa", "bar" but not "abad" 
#   AND if the value of the baz key is greater than 100.
#
#  There is implicit conversion of strings that look like numbers. 
#  There is also support for = and != of multiple values:
#    
#  foo=(one,two,three)
#  foo=one|two|three
#
#
recmp = re.compile(r'([a-z]+)(>|<|=|\!=|\!~|\~)([^,]+)')
def compile_filter(commands):
    tests = commands.split(',')
    conditions = [recmp.match(string).groups() for string in tests]
    cmp_operators = {'<': -1, '>': 1, '=': 0, '!=': 0}
    fields = [x[0] for x in conditions]

    # casts the "value" of the conditions to the same type as the given 
    # example. "100" becomes 100 if the example value is numeric. If the
    # operator is "~", the condition is compiled to a regular expression.
    def typecast(example):
        castfns = dict([(k, type(v)) for k,v in example.iteritems()])
        ret = []
        for key,op,value in conditions:
            if op[-1] == '~':
                ret.append((key,op,re.compile(value)))
            else:
                ret.append((key,op,castfns[key](value)))
        return ret

    # lazy eval of conditions. 
    def predicate(obj, conditions):
        for key, op, value in conditions:
            if op[-1] == '~': 
                if (not value.search(str(obj[key]))) != (op == '!~'):
                    return False
            elif (cmp_operators[op] == cmp(obj[key], value)) == (op == '!='):
                return False
        return True

    #the compiled function to be returned.
    def fn(lst):
        first = lst.next()
        conditions = typecast(first)
        if predicate(first, conditions):   #bleh. generators.
            yield first

        for item in lst:
            if predicate(item, conditions): 
                yield item

    return fn, fields



def tail_n(filename, num):
    for line in os.popen('tail -%d "%s"' % (num, filename)):
        yield line

## modes
def gen_top_stats(reqs, every=5):
    stats = {}
    last_print = 0

    for r in reqs:
        # record a hit for the given status class (2xx, 3xx, 4xx, 5xx, slow) to generate rps stats
        stats.setdefault(r['class'], (rrd2(20000, 30), rrd2(2000, 30), rrd2(200, 30), rrd2(200, 30), rrd2(200, 30)))

        if r['msec'] < MAX_REQUEST_TIME:
            stats[r['class']][(r['status']/100)-2].append(1, r['msec']) # 200 = 0, 3xx = 1, 4xx = 2, etc

        else: # log it in the "slow" bucket
            stats[r['class']][4].append(1, r['msec'])
            
        if (time.time() - last_print) > every:
            last_print = time.time()
            yield stats


def apache_top_mode(reqs):
    for stats in gen_top_stats(reqs, every=5):
        buf = []
        buf.append('% 34s     req/s   avg   min              max     3xx     4xx     5xx     slow' % '')
        buf.append('                   ----------------------------------------------------------------------------------------')

        for c in sorted(stats.keys()):
            # detailed stats for "200 OK" requests, simple averages for the rest
            rps, avg, cnt, stdev, sparkline, mn, mx = stats[c][0].stats()
            if rps < MIN_RPS or cnt < 2: 
                continue
            x3, x4, x5, slow = map(lambda x: pretty_float(x.avg()), stats[c][1:])
            buf.append('% 34s % 9s % 5d % 4d  %s % 5d % 7s % 7s % 7s % 7s' % (
                    c, pretty_float(rps), avg, mn, sparkline, mx, x3, x4, x5, slow))

        print "\n".join(buf) + "\n\n\n"


# for both tail and grep mode
def print_mode(reqs, fields):
    for r in reqs:
        print '\t'.join([str(r[k]) for k in fields])


# compact ids for a dict, given a list of keys to use as the unique identifier
# {'foo':bar,'a':'b'}, ('foo'), 6   -->  "b\315\267^O\371"  (first 6 bytes of md5('bar'))
# HACK: the default byte_len of 6 (48 bits) should be fine for most applications. If you 
# expect to process more than 10 to 15 million aggregate records (eg, grouping by url 
# or user-agent over millions of logs) AND you need absolute accuracy, by all means
# increase the byte_len default.
def id_from_dict_keys(h, keys, byte_len=6):
    return md5.md5(','.join([str(h[k]) for k in keys])).digest()[0:byte_len]


def keyfns(order_by):
    if order_by and len(order_by) > 1:
        key_fn =  (lambda v: [v[1][i] for i in order_by])
        key_fn2 = (lambda v: [v[i]    for i in order_by])
    else:
        key_fn =  (lambda v: v[1][order_by[0]])
        key_fn2 = (lambda v:    v[order_by[0]])
    return key_fn, key_fn2

def sort_fn(order_by, descending, limit):
    key_fn, key_fn2 = keyfns(order_by)
    return (lambda table: sorted(table.itervalues(), key=key_fn2, reverse=descending)[0:limit])

#bleh -- this fn is too long
MAXINT = 1<<64
def calculate_aggregates(reqs, agg_fields, group_by, order_by=None, limit=0, descending=True, tmpfile=None):
    table = {}
    cnt = 0
    using_disk = False
    if tmpfile:
        import shelve
        table = shelve.open(tmpfile,flag='n',writeback=True)
        using_disk = True

    # each aggregate record will start as a list of values whose
    # default depends on the agg function. Also take the opportunity
    # here to build a formatting string for printing the final results.
    fmt        = ['%s'] * len(agg_fields)
    blank      = [0]    * (len(agg_fields)+1) # that +1 is for a count column
    needed_post_fns = []
    for i,f in enumerate(agg_fields):
        op, field = f
        if op == 'min':
            blank[i+1] = MAXINT

        elif op == 'var' or op == 'dev':
            blank[i+1] = (0, 0)  # sum, squared sum
            needed_post_fns.append((op, i+1))
            fmt[i] = '%.2f'

        elif op == 'avg':
            fmt[i] = '%.2f'
    fmt = '\t'.join(fmt)

    # the None function is for pass-through fields eg 'class' in 'class,max(msec)'
    agg_fns = {
        None:    (lambda i, r, field, table, key: r[field]),
        'count': (lambda i, r, field, table, key: table[key][0]), # count(*) is always just copied from col 0
        'sum':   (lambda i, r, field, table, key: table[key][i] + r[field]), 
        'min':   (lambda i, r, field, table, key: min(r[field], table[key][i])), 
        'max':   (lambda i, r, field, table, key: max(r[field], table[key][i])), 
        'avg':   (lambda i, r, field, table, key: ((table[key][i] * (table[key][0]-1)) + r[field]) / float(table[key][0])),
        'var':   (lambda i, r, field, table, key: (table[key][i][0]+r[field], table[key][i][1]+(r[field]**2))), 
        'dev':   (lambda i, r, field, table, key: (table[key][i][0]+r[field], table[key][i][1]+(r[field]**2))), 
    }

    # post-processing for more complex aggregates
    post_fns = {
        'var':   (lambda sums, sq_sums, count: (sq_sums - ((sums ** 2) / float(count))) / float(count)),
        'dev':   (lambda sums, sq_sums, count: math.sqrt((sq_sums - ((sums ** 2) / float(count))) / float(count)) / ((sums / float(count))+1))
    }

    # various stuff needed if we are also running a limit/sort
    if limit:
        running_list = {}
        key_fn, key_fn2 = keyfns(order_by)

    lastt = time.time()

    for r in reqs:
        cnt += 1
        if cnt % PROGRESS_INTERVAL == 0: 
            t = time.time() - lastt
            lastt = time.time()
            warn ('%0.2f processed %d records...' % (t, cnt))

        key = id_from_dict_keys(r, group_by)
        if not table.has_key(key):
            table[key] = copy(blank)

        table[key][0] += 1 # always keep record count regardless of what the user asked for
        for idx,(op,field) in enumerate(agg_fields):
            table[key][idx+1] = agg_fns[op](idx+1, r, field, table, key)

        # sort & prune periodically
        if limit:
            running_list[key] = table[key]
            if cnt % SORT_BUFFER_LENGTH:
                running_list = dict(sorted(running_list.iteritems(), key=key_fn, reverse=descending)[0:limit])

        if using_disk and cnt % DISC_SYNC_CNT == 0:
            warn ('sync()ing records to disk...')
            table.sync()
            warn ('done.')
    
    if limit: 
        records = running_list
    else:
        records = table

    # todo: the arg signature is not generic. what other agg functions do people want?
    if needed_post_fns:
        cnt = 0
        for k in records.iterkeys():
            for (fn, col_idx) in needed_post_fns:
                records[k][col_idx] = post_fns[fn](records[k][col_idx][0], records[k][col_idx][1], records[k][0])
            cnt += 1
            if using_disk and cnt % DISC_SYNC_CNT == 0:
                warn ('sync()ing records to disk...')
                table.sync()


    # return the records & printing format
    # for silly reasons we have to also return the tmpfile and the table object.
    return records, fmt, tmpfile, table

def agg_mode(rows, fmt):
    for row in rows:
        print fmt % tuple(row[1:])




## experimental RRDtool mode for generating timeseries graphs
def normalize(lst, total, scale):
    return [int(round((x/float(total))*scale)) for x in lst]

from subprocess import call

def create_rrd(klass, ts, step=5):
    print "creating rrd", klass, ts
    rowcnt = 86400 / step
    call(["rrdtool",  
        'create',
        '%s.rrd' % klass,
        '--step','%d' % step,
        '--start', '%s' % ts,
       "DS:rps2xx:GAUGE:5:0:5000",
       "DS:rps3xx:GAUGE:5:0:5000",
       "DS:rps4xx:GAUGE:5:0:5000",
       "DS:rps5xx:GAUGE:5:0:5000",
       "DS:msec:GAUGE:5:0:10000",
       "RRA:AVERAGE:0.5:1:%s"%rowcnt,
       "RRA:AVERAGE:0.5:1:%s"%rowcnt,
       "RRA:AVERAGE:0.5:1:%s"%rowcnt,
       "RRA:AVERAGE:0.5:1:%s"%rowcnt,
       "RRA:AVERAGE:0.5:1:%s"%rowcnt])

# coordinate all the godawful rrdtool command options
def create_graph(klass, ts, length, rpslim, mseclim, type="brief"):
    print "creating graph", klass, ts
    common = [
          '-s', str(ts-length), '-e', str(ts),
          '--color', 'BACK#ffffff00', '--color', 'SHADEA#ffffff00', '--color', 'SHADEB#ffffff00',
          '--color', 'CANVAS#eeeeee00', '--color', 'GRID#eeeeee00', 
          '--color', 'MGRID#eeeeee00', 
          '--color', 'AXIS#999999', '--color', 'ARROW#999999',
          '-w', '300','--units-length','4', '--no-legend',
          '--slope-mode']

    if type=="brief":
        common += ['-h', '40', '-a', 'PNG','--x-grid', 'none']
    else:
        common += ['-h', '40', '-w', '750']

    # requests / second graph
    call(['rrdtool', 'graph', 
          '%s.%s.rps.png'%(klass,type)] + common + [ 
          "DEF:OK=%s.rrd:rps2xx:AVERAGE" % klass,
          "AREA:OK#44ee00:OK",
          "DEF:REDIRECT=%s.rrd:rps3xx:AVERAGE"  % klass,
          "AREA:REDIRECT#2a89ed:REDIRECT",
          "DEF:NOTFOUND=%s.rrd:rps4xx:AVERAGE"  % klass,
          "AREA:NOTFOUND#f59d18:NOTFOUND",
          "DEF:ERROR=%s.rrd:rps5xx:AVERAGE"  % klass,
          "AREA:ERROR#dd0000:ERROR"])

    # response time graph
    call(['rrdtool', 'graph',
          '%s.%s.msec.png'%(klass,type)] + common + [
          '--upper-limit', str(mseclim), '--rigid', 
          '--y-grid','%s:%s' % (mseclim,mseclim),
          '--units-exponent','0',  
          '--slope-mode', 
          "DEF:MSEC=%s.rrd:msec:AVERAGE" % klass,
          "AREA:MSEC#8888cc:MSEC"])


def create_rrd_page(classes, rpslim, mseclim):
    buf = []

    buf.append("""
    <table cellspacing="0" width="920">
    <tr class="r1">
        <td align="right" width="120" ><b>All Pages</b>&nbsp;</td>
        <td colspan="2">
        <img src="all.halfday.rps.png"  />
        <img src="all.halfday.msec.png"  />
        </td></tr>
    """)

    buf.append(""" 
        <tr><td>&nbsp;</td><td align="center"><b>Traffic Volume (req/sec)</b></td><td align="center"><b>Avg Response Time (msec)</b></td></tr>
    """)

    i = 0
    for c in classes[1:]:
        buf.append("""
        <tr class="r%d">
        <td width="120" align="right"><b>%s</b></td>
        <td>
        <img src="%s.brief.rps.png"  />
        </td>
        <td>
        <img src="%s.brief.msec.png"  />
        </td></tr>
        """ % (i%2, c.replace('_', ' '), c,c))
        i += 1

    (open("rrd.html", 'w')).write('<style>.r1{background:#eeeeee} body{font-family: arial} img {padding:2px;}</style><meta http-equiv="refresh" content="30" />' + ''.join(buf))



def rrd_mode(reqs, step=5, msec_max=2000, hist_steps=10, hist_scale=100, do_hist=False):
    last_chart = 0
    cur_time = 0
    stats = {'all':dict(count=[0,0,0,0], total_msec=0, hist=[0]*hist_steps)}
    classes = {}

    rpslim = 5
    mseclim = 2000

    for r in reqs:
        if not cur_time: cur_time = r['ts']
        
        # init the pseudo-class 'all'
        if not classes.has_key('all'):
            classes['all'] = True
            create_rrd('all', r['ts'], 1)

        r['class'] = r['class'].replace(':', '_').replace('/', '')

        # lazy init rrd file
        if not classes.has_key(r['class']):
            create_rrd(r['class'], r['ts'], 1)
            classes[r['class']] = True

        # time to emit some stats
        if r['ts'] >= cur_time+step:
            print cur_time
            for k in classes:
                if not stats.has_key(k):
                    continue 
                v = stats[k]

                if do_hist:
                    histogram = normalize(v['hist'], v['count'][0], hist_scale)

                call(["rrdtool", "update", "%s.rrd"% k, "%d:%s:%s:%s:%s:%s" % (
                    r['ts'], 
                    int(v['count'][0]/float(step)), 
                    int(v['count'][1]/float(step)),
                    int(v['count'][2]/float(step)), 
                    int(v['count'][3]/float(step)),
                    v['total_msec'] / (v['count'][0]+1))])

            cur_time = r['ts']
            stats = {'all':dict(count=[0,0,0,0], total_msec=0, hist=[0]*hist_steps)}

        else: # gather stats
            stats.setdefault(r['class'], dict(count=[0,0,0,0], total_msec=0, hist=[0]*hist_steps))
            stats[r['class']]['count'][(r['status']/100)-2] += 1
            stats['all']['count'][(r['status']/100)-2] += 1

            if r['status'] < 299:
                stats[r['class']]['total_msec'] += r['msec']
                stats['all']['total_msec'] += r['msec']
                
                if do_hist:
                    stats[r['class']]['hist'][min(min(r['msec'], msec_max)/(msec_max/hist_steps), hist_steps-1)] += 1

        # time to emit some graphs
        if cur_time - last_chart > 30:
            last_chart = cur_time


            create_graph('all', cur_time, 43200, rpslim, mseclim, 'halfday')
            
            for k in classes.keys():
                create_graph(k, cur_time, 1800, rpslim, mseclim, 'brief')
            create_rrd_page(sorted(classes.keys()), rpslim, mseclim)

