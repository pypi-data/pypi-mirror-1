r"""
[Check __repr__ and __str__ methods]

>>> c = cfgparse.ConfigParser()
>>> c.add_option('name') # doctest: +ELLIPSIS
<Option at ...: name>
>>> c.add_option('very_long_name',dest='dest') # doctest: +ELLIPSIS
<Option at ...: very_long_name>

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#  INI Format
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# [Simple INI format (old format)]

# not found
>>> c = cfgparse.ConfigParser()
>>> opt1 = c.add_option('opt1')
>>> opt2 = c.add_option('opt2')
>>> junk = c.add_file(content='''
... [DEFAULT]
... ''')
>>> try:
...     opts = c.parse()
... except SystemExit:
...     pass
sys.exit(0)
>>> print_sys_stderr() # doctest: +NORMALIZE_WHITESPACE
SE| ERROR: Configuration File Parser
SE|
SE| Option: opt1
SE| No valid default found.
SE| keys=DEFAULT
SE|
SE| Option: opt2
SE| No valid default found.
SE| keys=DEFAULT
SE| --|

# single default section (colon and equal sign interchangeable)
>>> c = cfgparse.ConfigParser()
>>> opt1 = c.add_option('opt1',default='unknown',keys=[])
>>> junk = c.add_option('opt2',default='unknown',keys=[])
>>> junk = c.add_option('opt3',default='unknown',keys=[])
>>> junk = c.add_option('opt4',default='unknown',keys=[])
>>> junk = c.add_file(content='''
... [DEFAULT]
... opt1 = val1
... opt2 = val2
... opt3=val3
... opt4=val4
... ''')
>>> options = c.parse()
>>> [options.opt1,options.opt2,options.opt3,options.opt4]
['val1', 'val2', 'val3', 'val4']

# add another section (make sure it is ignored)
>>> junk = c.add_option('opt5',default='unknown',keys=['KEY1'])
>>> junk = c.add_file(content='''
... [DEFAULT]
... opt5 = val5
... [KEY1]
... opt1 = val1_k1
... opt5 = val5_k1
... ''')
>>> options = c.parse()
>>> [options.opt1,options.opt5]
['val1', 'val5_k1']
>>> opt1.get('KEY1')
'val1_k1'

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# [Extended INI format]

# section names (and extended sections) with commas separating keys

>>> c = cfgparse.ConfigParser()
>>> junk = c.add_option('driver',default='unknown',keys='key1,key2')
>>> junk = c.add_option('path',default='unknown',keys='key1,key2,key3,key4')
>>> junk = c.add_file(content='''
... [key1,key2]
... driver = driver_12
... path[key3,key4] = path_1234
... ''')
>>> options = c.parse()
>>> options.driver
'driver_12'
>>> options.path
'path_1234'

# section names (and extended sections) with periods separating keys

>>> c = cfgparse.ConfigParser()
>>> junk = c.add_option('driver',default='unknown',keys='key1,key2')
>>> junk = c.add_option('path',default='unknown',keys='key1,key2,key3,key4')
>>> junk = c.add_file(content='''
... [key1.key2]
... driver = driver_12
... path[key3.key4] = path_1234
... ''')
>>> options = c.parse()
>>> options.driver
'driver_12'
>>> options.path
'path_1234'

# section names (and extended sections) with single quotes (') for periods and commas in keys

>>> c = cfgparse.ConfigParser()
>>> junk = c.add_option('driver',default='unknown',keys=['a.b.c','d,e,f'])
>>> junk = c.add_file(content='''
... ['a.b.c','d,e,f']
... driver = driver_abcdef
... ''')
>>> options = c.parse()
>>> options.driver
'driver_abcdef'

# section names (and extended sections) with single quotes for periods and commas in keys

>>> c = cfgparse.ConfigParser()
>>> junk = c.add_option('driver',default='unknown',keys=["a.b.c","d,e,f"])
>>> junk = c.add_file(content='''
... ["a.b.c","d,e,f"]
... driver = driver_abcdef
... ''')
>>> options = c.parse()
>>> options.driver
'driver_abcdef'

# <include> in default section
# <include> in section (contents placed under that section)

>>>
>>> # make INI file 2
>>> temp.make('_tcp_file2.ini','''
... [DEFAULT]
... <keys> = keyf2
... driver = driver_f2d
... 
... [keyf2]
... <keys> = ignored
... driver = driver_f2k
... ''')
>>>
>>> # make INI file 3
>>> temp.make('_tcp_file3.ini','''
... [DEFAULT]
... <keys> = keyf3
... driver = driver_f3d
... 
... [keyf3]
... <keys> = ignored
... driver = driver_f3k
... ''')
>>>
>>> # make INI file 1 (heredoc) and setup parser
>>> c = cfgparse.ConfigParser()
>>> junk = c.add_option('driver',default='unknown',keys='keyf1')
>>> junk = c.add_file(content='''
... [DEFAULT]
... <keys> = keyf1
... <include> = _tcp_file2.ini
... [keyf1]
... <keys> = ignored
... <include> = _tcp_file3.ini
... ''')
>>> 
>>> # file 2 and 3 should now be read because of parse
>>> options = c.parse()
>>> pp(c.option_dicts['driver']) # doctest: +ELLIPSIS
{'DEFAULT': <OptionPair at ...: driver_f2d>,
 'keyf1': {'DEFAULT': <OptionPair at ...: driver_f3d>,
           'keyf3': <OptionPair at ...: driver_f3k>},
 'keyf2': <OptionPair at ...: driver_f2k>}
>>> print c.keys
keyf1,keyf2,DEFAULT
>>> temp.clean()

# %(ABS_PATH(...)s substitution and relative path resolution

# >>>
# >>> # make INI file
# >>> temp.make('_tcp/file.ini','''
# ... [DEFAULT]
# ... path = %(ABSPATH(no/exist))s
# ... ''')
# >>>
# >>> # make INI heredoc and setup parser
# >>> c = cfgparse.ConfigParser()
# >>> junk = c.add_option('path',default='unknown')
# >>> junk = c.add_file(content='''
# ... [DEFAULT]
# ... <include> = _tcp/file.ini
# ... ''')
# >>>
# >>> # parse it and check proper path set
# >>> options = c.parse()
# >>> print "path =",options.path.replace('\\','/')
# path = [[CWD]]/_tcp/no/exist
# >>> #temp.clean()

# <keys> in default section work, <keys> in other sections don't

>>> c = cfgparse.ConfigParser()
>>> junk = c.add_option('driver',default='unknown')
>>> junk = c.add_option('path',default='unknown')
>>> junk = c.add_file(content='''
... [DEFAULT]
... <keys> = key1,key2
... [key1,key2]
... <keys> = key3
... driver = driver_12
... path[key3] = path_123
... ''')
>>> options = c.parse()
>>> options.driver
'driver_12'
>>> options.path
'unknown'
>>> print c.keys
key1,key2,DEFAULT

# <keys_variable>

# make sure same variable never read more than once
# make sure key_vars in sections other than other are ignored
# make sure key_vars in <include> file are accepted
>>> temp.make('_tcp/file.ini','''
... [DEFAULT]
... <keys_variable> = VAR1
... [SOMEKEY]
... <keys_variable> = VAR2
... ''')
>>> c = cfgparse.ConfigParser()
>>> c.keys.add_cmd_keys('cmd')
>>> c.keys.add_cfg_keys('cfg')
>>> junk = c.add_file(content='''
... [DEFAULT]
... <keys_variable> = VAR34,VAR5
... <include> = _tcp/file.ini
... [KEY]
... <keys_variable> = VAR6
... ''')
>>> junk = c.parse()
>>> c.keys.add_env_keys(['VAR1']) # repeat ignored
>>> c.keys.add_env_keys(['VAR7']) # new
>>> c.keys.get('app')
['app', 'cmd', 'env3', 'env4', 'env5', 'env1', 'env7', 'cfg', 'DEFAULT']

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#  .py Configuration Files
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #



# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#  ConfigParser() Options
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# default_env

>>> temp.make('_tcp1.ini','''
... [DEFAULT]
... opt1 = val1
... ''')

>>> temp.make('_tcp2.ini','''
... [DEFAULT]
... opt2 = val2
... ''')

>>> temp.make('_tcp3.ini','''
... [DEFAULT]
... opt3 = val3
... ''')

>>> c = cfgparse.ConfigParser()
>>> junk = c.add_env_file('FILE1')
>>> junk = c.add_env_file('FILE2')
>>> junk = c.add_env_file('FILE3')
>>> junk = c.add_option('opt1')
>>> junk = c.add_option('opt2')
>>> junk = c.add_option('opt3')
>>> options = c.parse()
>>> options.opt1
'val1'
>>> options.opt2
'val2'
>>> options.opt3
'val3'

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# read_all=True (False case tested by normal INI tests)

# make INI file
>>> temp.make('_tcp_file.ini','''
... [DEFAULT]
... opt1 = val1
... ''')

# make heredoc INI and setup parser
>>> c = cfgparse.ConfigParser()
>>> opt1 = c.add_option('opt1',default='unknown',keys=[])
>>> junk = c.add_file(content='''
... [key]
... <include> = _tcp_file.ini
... ''')
>>> options = c.parse(read_all=True)
>>> options.opt1
'unknown'
>>> print c._pending
[]
>>> pp(c.option_dicts['opt1']) # doctest: +ELLIPSIS
{'key': <OptionPair at ...: val1>}
>>> opt1.get('key')
'val1'

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# allow_py=False (True case is in Python testing)

# make heredoc INI and setup parser
# this .py file does not exist but since .py is not allowed it is ignored anyway
>>> c = cfgparse.ConfigParser()
>>> junk = c.add_file(content='''
... [DEFAULT]
... <include> = _tcp_file.py
... ''')
>>> options = c.parse()
>>> print c.option_dicts
{}

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#  optpar partnership
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# type, metavar attribute sharing

>>> o = optparse.OptionParser()
>>> c = cfgparse.ConfigParser()
>>> oo = o.add_option('--opt',type='int',metavar='OPTION')
>>> co = c.add_option('opt')
>>> junk = c.add_file(content='''
... [DEFAULT]
... opt = 1
... ''')
>>> opts, args = c.parse(optparser=o)
>>> opts.opt
1
>>> co.type
'int'
>>> co.metavar
'OPTION'

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# choices attribute sharing

>>> o = optparse.OptionParser()
>>> c = cfgparse.ConfigParser()
>>> oo = o.add_option('--opt',type='choice',choices=['a','b'])
>>> co = c.add_option('opt')
>>> junk = c.add_file(content='''
... [DEFAULT]
... opt = a
... ''')
>>> opts, args = c.parse(optparser=o)
>>> opts.opt
'a'

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# keys

# check that keys from command line get added properly
>>> o = optparse.OptionParser()
>>> c = cfgparse.ConfigParser()
>>> c.add_optparse_keys_option(o)
>>> c.keys.add_cmd_keys('cmd1')
>>> c.keys.add_cfg_keys('cfg1')
>>> c.keys.add_env_keys('VAR1')
>>> opts, args = c.parse(optparser=o,args=['-kcmd2'])
>>> opts, args = c.parse(optparser=o,args=['--keys=cmd3'])
>>> c.keys.get('app')
['app', 'cmd1', 'cmd2', 'cmd3', 'env1', 'cfg1', 'DEFAULT']

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# cfgfiles

# setup: create temporary files
>>> temp.make('_tcp_file1.ini','''
... [DEFAULT]
... opt1 = val1
... ''')
>>> temp.make('_tcp_file2.ini','''
... [DEFAULT]
... opt2 = val2
... ''')
>>> temp.make('_tcp_file3.ini','''
... [DEFAULT]
... opt3 = val3
... ''')

# check that config files from command line get added properly
>>> o = optparse.OptionParser()
>>> c = cfgparse.ConfigParser()
>>> c.add_optparse_files_option(o)
>>> junk = c.add_option('opt1')
>>> junk = c.add_option('opt2')
>>> opts, args = c.parse(optparser=o,args=['--cfgfiles=_tcp_file1.ini,_tcp_file2.ini'])
>>> opts.opt1
'val1'
>>> opts.opt2
'val2'
>>> junk = c.add_option('opt3')
>>> opts, args = c.parse(optparser=o,args=['--cfgfiles=_tcp_file3.ini'])
>>> opts.opt3
'val3'

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# help optparse and cfgparse (check modification of help strings)

>>> o = optparse.OptionParser()
>>> junk = o.add_option('-u','--opt1',help='This is the help text for opt1.')
>>> junk = o.add_option('-d','--opt2',help='This is the help text for opt2.')
>>> junk = o.add_option('-t','--opt3',help='This is the help text for opt3.')
>>> junk = o.add_option('-x','--opt5')
>>> junk = o.add_option('-y','--opt6')
>>> c = cfgparse.ConfigParser()
>>> c.add_optparse_help_option(o.add_option_group('configuration file option'))
>>> junk = c.add_option('opt1')
>>> junk = c.add_option('opt2')
>>> junk = c.add_option('opt4',help='This is the help text for opt4.')
>>> junk = c.add_option('opt5',help='This is the help text for opt5.')
>>> junk = c.add_option('opt6')

# generate command line help
>>> try:
...     opts, args = c.parse(optparser=o,args=['--help'])
... except SystemExit:
...     pass
usage: cfgparse_py_doctest.py [options]
<BLANKLINE>
options:
  -h, --help            show this help message and exit
  -u OPT1, --opt1=OPT1  This is the help text for opt1.  See also 'opt1'
                        option in configuration file help.
  -d OPT2, --opt2=OPT2  This is the help text for opt2.  See also 'opt2'
                        option in configuration file help.
  -t OPT3, --opt3=OPT3  This is the help text for opt3.
  -x OPT5, --opt5=OPT5  See also 'opt5' option in configuration file help.
  -y OPT6, --opt6=OPT6  See also 'opt6' option in configuration file help.
<BLANKLINE>
  configuration file option:
    --cfghelp           Show configuration file help and exit.
sys.exit(0)

# generate command line help again to make sure "see also" note not added twice.
>>> try:
...     opts, args = c.parse(optparser=o,args=['--help'])
... except SystemExit:
...     pass
usage: cfgparse_py_doctest.py [options]
<BLANKLINE>
options:
  -h, --help            show this help message and exit
  -u OPT1, --opt1=OPT1  This is the help text for opt1.  See also 'opt1'
                        option in configuration file help.
  -d OPT2, --opt2=OPT2  This is the help text for opt2.  See also 'opt2'
                        option in configuration file help.
  -t OPT3, --opt3=OPT3  This is the help text for opt3.
  -x OPT5, --opt5=OPT5  See also 'opt5' option in configuration file help.
  -y OPT6, --opt6=OPT6  See also 'opt6' option in configuration file help.
<BLANKLINE>
  configuration file option:
    --cfghelp           Show configuration file help and exit.
sys.exit(0)
    
# generate configuration file help
>>> try:
...     opts, args = c.parse(optparser=o,args=['--cfghelp'])
... except SystemExit:
...     pass
Configuration file options:
  opt1=OPT1  This is the help text for opt1.  See also '-u/--opt1' command
             line switch.
  opt2=OPT2  This is the help text for opt2.  See also '-d/--opt2' command
             line switch.
  opt4=OPT4  This is the help text for opt4.
  opt5=OPT5  This is the help text for opt5.  See also '-x/--opt5' command
             line switch.
  opt6=OPT6  See also '-y/--opt6' command line switch.
sys.exit(0)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# help optparse and cfgparse
# %default substitution
# help suppression)
# metavar

>>> o = optparse.OptionParser()
>>> c = cfgparse.ConfigParser()
>>> c.add_optparse_help_option(o.add_option_group('configuration file option'))
>>> junk = c.add_option('opt1',metavar='VAL1',default="value1",help='Help for opt1 (default=%default).')
>>> junk = c.add_option('opt2',default="value2",help=cfgparse.SUPPRESS_HELP)

# generate command line help
>>> try:
...     opts, args = c.parse(optparser=o,args=['--cfghelp'])
... except SystemExit:
...     pass
Configuration file options:
  opt1=VAL1  Help for opt1 (default=value1).
sys.exit(0)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#  type checks
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

>>> c = cfgparse.ConfigParser()
>>> junk = c.add_file(content='''
... [DEFAULT]
... <keys> = key1,key2
... opt1 = 1
... [key1]
... opt2[key2] = 2
... ''')
>>> junk = c.add_option('opt1',type='int',help='Help for option.')
>>> junk2 = c.add_option('opt2',type='int',help='Help for option.')

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# integer

# pass
>>> c.parse().opt1
1

# fail
>>> c.option_dicts['opt1']['DEFAULT'].value = 'abc'
>>> try:
...     c.parse().opt1
... except SystemExit:
...     pass
sys.exit(0)
>>> print_sys_stderr() # doctest: +NORMALIZE_WHITESPACE +ELLIPSIS
SE| ERROR: Configuration File Parser
SE|
SE| Option: opt1
SE| File: .../heredoc
SE| Section: [DEFAULT]
SE| Line: 4
SE| Cannot convert 'abc' to an integer
SE| --|

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# float

# pass
>>> junk.type = 'float'
>>> c.option_dicts['opt1']['DEFAULT'].value = '1.0'
>>> c.parse().opt1
1.0

# fail
>>> c.option_dicts['opt1']['DEFAULT'].value = 'abc'
>>> try:
...     c.parse().opt1
... except SystemExit:
...     pass
sys.exit(0)
>>> print_sys_stderr() # doctest: +NORMALIZE_WHITESPACE +ELLIPSIS
SE| ERROR: Configuration File Parser
SE|
SE| Option: opt1
SE| File: .../heredoc
SE| Section: [DEFAULT]
SE| Line: 4
SE| Cannot convert 'abc' to a float
SE| --|

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# long

# pass
>>> junk.type = 'long'
>>> c.option_dicts['opt1']['DEFAULT'].value = '1'
>>> c.parse().opt1
1L

# fail
>>> c.option_dicts['opt1']['DEFAULT'].value = 'abc'
>>> try:
...     c.parse().opt1
... except SystemExit:
...     pass
sys.exit(0)
>>> print_sys_stderr() # doctest: +NORMALIZE_WHITESPACE +ELLIPSIS
SE| ERROR: Configuration File Parser
SE|
SE| Option: opt1
SE| File: /.../heredoc
SE| Section: [DEFAULT]
SE| Line: 4
SE| Cannot convert 'abc' to a long
SE| --|

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# complex

# pass
>>> junk.type = 'complex'
>>> c.option_dicts['opt1']['DEFAULT'].value = '1+2j'
>>> c.parse().opt1
(1+2j)

# fail
>>> c.option_dicts['opt1']['DEFAULT'].value = 'abc'
>>> try:
...     c.parse().opt1
... except SystemExit:
...     pass
sys.exit(0)
>>> print_sys_stderr() # doctest: +NORMALIZE_WHITESPACE +ELLIPSIS
SE| ERROR: Configuration File Parser
SE|
SE| Option: opt1
SE| File: .../heredoc
SE| Section: [DEFAULT]
SE| Line: 4
SE| Cannot convert 'abc' to a complex number
SE| --|

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# choice

# pass
>>> junk.type = 'choice'
>>> junk.choices = ['ABC','DEF','HIJ']
>>> c.option_dicts['opt1']['DEFAULT'].value = 'DEF'
>>> c.parse().opt1
'DEF'

# fail
>>> c.option_dicts['opt1']['DEFAULT'].value = 'abc'
>>> try:
...     c.parse().opt1
... except SystemExit:
...     pass
sys.exit(0)
>>> print_sys_stderr() # doctest: +NORMALIZE_WHITESPACE +ELLIPSIS
SE| ERROR: Configuration File Parser
SE|
SE| Option: opt1
SE| File: .../heredoc
SE| Section: [DEFAULT]
SE| Line: 4
SE| Invalid choice 'abc', must be one of: 'ABC', 'DEF', 'HIJ'
SE| --|

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# subsection

# restore opt1
>>> junk.type = 'int'
>>> c.option_dicts['opt1']['DEFAULT'].value = 1

# pass
>>> c.parse().opt2
2

# fail
>>> c.option_dicts['opt2']['key1']['key2'].value = 'abc'
>>> try:
...     c.parse().opt1
... except SystemExit:
...     pass
sys.exit(0)
>>> print_sys_stderr() # doctest: +NORMALIZE_WHITESPACE +ELLIPSIS
SE| ERROR: Configuration File Parser
SE|
SE| Option: opt2
SE| File: .../heredoc
SE| Section: [key1.key2]
SE| Line: 6
SE| Cannot convert 'abc' to an integer
SE| --|


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#  Option Groups
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

>>> c = cfgparse.ConfigParser(description='This is a really long description '
...         'for the instantiation of the cfgparse.ConfigParser.  It is '
...         'definitely more than one line.')
>>> junk = c.add_option('opt1',help='Help for opt1')
>>> g = c.add_option_group('group 1',description='This is a really long description '
...         'for the creation of an option_group.  It also is definitely more '
...         'than one line.')
>>> junk = g.add_option('opt1a',help='Help for opt1a')
>>> junk = g.add_option('opt1b',help='Help for opt1b')
>>> g = c.add_option_group('group 2')
>>> junk = g.add_option('opt2a',help='Help for opt2a')
>>> junk = g.add_option('opt2b',help='Help for opt2b')
>>> junk = c.add_option('opt3',help='Help for opt3')
>>> junk = c.add_file(content='''
... [DEFAULT]
... opt1 = v1
... opt1a = v1a
... opt1b = v1b
... opt2a = v2a
... opt2b = v2b
... opt3 = v3
... ''')
>>> opts = c.parse()
>>> print "%s %s %s %s" % (opts.opt1a,opts.opt1b,opts.opt2a,opts.opt2b)
v1a v1b v2a v2b
>>> c.print_help()
This is a really long description for the instantiation of the
cfgparse.ConfigParser.  It is definitely more than one line.
<BLANKLINE>
Configuration file options:
  opt1=OPT1      Help for opt1
  opt3=OPT3      Help for opt3
<BLANKLINE>
  group 1:
    This is a really long description for the creation of an option_group.
    It also is definitely more than one line.
<BLANKLINE>
    opt1a=OPT1A  Help for opt1a
    opt1b=OPT1B  Help for opt1b
<BLANKLINE>
  group 2:
    opt2a=OPT2A  Help for opt2a
    opt2b=OPT2B  Help for opt2b


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#  Invalid add_option parameters
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# simple

>>> c = cfgparse.ConfigParser()
>>> junk = c.add_option('opt')
>>> junk = c.add_option('opt_s',keys='section')
>>> junk = c.add_option('opt_ss',keys='subsection')
>>> cf = c.add_file(content='''
... # comment empty line
... opt = val # comment opt/val pair
... [section] # comment section
... opt_s = val_s
... [subsection]
... opt_ss = val_ss
... ''')    
>>> options = c.parse()
>>> options.opt
'val'
>>> options.opt_s
'val_s'
>>> options.opt_ss
'val_ss'

# block

>>> c = cfgparse.ConfigParser()
>>> junk = c.add_option('opt1')
>>> cf = c.add_file(content='''
... # comment empty line
... opt1 = <b>
... line1
... line2
... </b>
... opt2 = hi
... ''')    
>>> options = c.parse()
>>> print_sys_stderr()
>>> options.opt1
'\nline1\nline2\n'

# substitute (default options)

>>> c = cfgparse.ConfigParser()
>>> junk = c.add_option('opt1')
>>> cf = c.add_file(content='''
... opt1 = %(opt2)s Last
... opt2 = First
... ''')    
>>> options = c.parse()
>>> print_sys_stderr()
>>> options.opt1
'First Last'

# substitute (both in same section)

>>> c = cfgparse.ConfigParser()
>>> junk = c.add_option('opt1',keys='section')
>>> cf = c.add_file(content='''
... [section]
... opt1 = %(opt2)s Last
... opt2 = First
... ''')    
>>> options = c.parse()
>>> print_sys_stderr()
>>> options.opt1
'First Last'

# substitute (section in default section)

>>> c = cfgparse.ConfigParser()
>>> junk = c.add_option('opt1',keys='section')
>>> cf = c.add_file(content='''
... [DEFAULT]
... opt2 = First
... [section]
... opt1 = %(opt2)s Last
... ''')    
>>> options = c.parse()
>>> print_sys_stderr()
>>> options.opt1
'First Last'

# substitute ABSPATH()

# >>> c = cfgparse.ConfigParser()
# >>> junk = c.add_option('path')
# >>> cf = c.add_file(content='''
# ... path = %(ABSPATH(./subdir))s
# ... ''')    
# >>> options = c.parse()
# >>> print_sys_stderr()
# >>> options.path.replace('\\','/')
# '[[CWD]]/subdir'

# substitute ABSPATH() with substitution inside

# >>> c = cfgparse.ConfigParser()
# >>> junk = c.add_option('path')
# >>> cf = c.add_file(content='''
# ... path = %(ABSPATH(%(relpath)s))s
# ... relpath = subdir
# ... ''')    
# >>> options = c.parse()
# >>> print_sys_stderr()
# >>> options.path.replace('\\','/')
# '[[CWD]]/subdir'

# modify & write

>>> c = cfgparse.ConfigParser()
>>> junk = c.add_option('opt')
>>> cf = c.add_file(content='''
... # comment empty line
... opt = val # comment opt/val pair
... [section] # comment section
... opt_s = val_s
... [subsection]
... opt_ss = val_ss
... ''')    
>>> options = c.parse()
>>> print_sys_stderr()
>>> junk = cf.set_option('opt','newval')
>>> junk = cf.set_option('new_in_def','value_new_in_default')
>>> junk = cf.set_option('new','brandnew',help="Help for brand new",keys='new.subnew')
>>> cf.write(sys.stdout)
<BLANKLINE>
# comment empty line
opt = newval # comment opt/val pair
new_in_def = value_new_in_default
[section] # comment section
opt_s = val_s
[subsection]
opt_ss = val_ss
<BLANKLINE>
<BLANKLINE>
[new.subnew]
<BLANKLINE>
# Help for brand new
new = brandnew

# substitution failure

>>> c = cfgparse.ConfigParser()
>>> junk = c.add_option('opt1',keys='section')
>>> cf = c.add_file(content='''
... [DEFAULT]
... opt2 = First
... [section]
... opt1 = %(opt3)s Last
... ''')    
>>> options = c.parse() # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
Traceback (most recent call last):
    ...
ConfigParserUserError:
File: .../heredoc
Section: [section]
Line: 5
Interpolation: opt1 << opt3
'opt3' not found in section or in [DEFAULT].

# interpolation infinite loop

>>> c = cfgparse.ConfigParser()
>>> junk = c.add_option('opt1',keys='section')
>>> cf = c.add_file(content='''
... [section]
... opt1 = %(opt2)s
... opt2 = %(opt1)s
... ''')    
>>> options = c.parse() # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
Traceback (most recent call last):
    ...
ConfigParserUserError:
File: .../heredoc
Section: [section]
Line: 3
Interpolation: opt1 << opt2 << opt1 << opt2 << opt1 << opt2 << opt1 << opt2 << opt1 << opt2 << opt1
Maximum nesting level exceeded.

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#  Raising Errors
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# use default exception

>>> c = cfgparse.ConfigParser(exception=True)
>>> junk = c.add_option('opt1')
>>> options = c.parse() # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
Traceback (most recent call last):
    ...
ConfigParserUserError:
Option: opt1
No valid default found.
keys=DEFAULT
<BLANKLINE>

# use custom exception

>>> class CustomException(Exception):
...     pass
>>> c = cfgparse.ConfigParser(exception=CustomException)
>>> junk = c.add_option('opt1')
>>> options = c.parse() # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
Traceback (most recent call last):
    ...
CustomException:
Option: opt1
No valid default found.
keys=DEFAULT
<BLANKLINE>

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#  Adding Notes
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

>>> msg = '  The quick brown fox jumps over the lazy dog.'*3
>>> def f(text):
...     return textwrap.fill(text,70,initial_indent='',subsequent_indent='    ')
>>> c = cfgparse.ConfigParser()
>>> o = optparse.OptionParser()
>>> opt1 = c.add_option('opt1',help='Help for opt1.  See Note (1).')
>>> opt1.add_note(f('(1) Opt1.' + msg))
>>> opt2 = c.add_option('opt2')
>>> opt2.add_note(f('(2) Opt2.' + msg))
>>> c.add_note(f('(3) N1.' + msg))
>>> c.add_note(f('(4) N2.' + msg))
>>> c.add_optparse_help_option(o)
>>> try: # doctest: +NORMALIZE_WHITESPACE
...     c.parse(o,['--cfghelp'])
... except SystemExit:
...     pass
Configuration file options:
  opt1=OPT1  Help for opt1.  See Note (1).
  opt2=OPT2
<BLANKLINE>
Notes:
(1) Opt1.  The quick brown fox jumps over the lazy dog.  The quick
    brown fox jumps over the lazy dog.  The quick brown fox jumps over
    the lazy dog.
(2) Opt2.  The quick brown fox jumps over the lazy dog.  The quick
    brown fox jumps over the lazy dog.  The quick brown fox jumps over
    the lazy dog.
(3) N1.  The quick brown fox jumps over the lazy dog.  The quick brown
    fox jumps over the lazy dog.  The quick brown fox jumps over the
    lazy dog.
(4) N2.  The quick brown fox jumps over the lazy dog.  The quick brown
    fox jumps over the lazy dog.  The quick brown fox jumps over the
    lazy dog.
sys.exit(0)

"""

import cfgparse
import cStringIO
import optparse
import os
import sys
import textwrap
from pprint import pprint as pp

__doc__ = __doc__.replace('[[CWD]]',os.getcwd().replace('\\','/'))

def _getenv(variable,default):
    if variable.startswith('VAR'):
        return ','.join(['env%s' % c for c in variable[3:]])
    elif variable.startswith('FILE'):
        return ','.join(['_tcp%s.ini' % c for c in variable[4:]])
    else:
        return default

class SystemExit(Exception):
    """>>> None # Test"""
    pass

def _new_exit(status=0):
    """>>> None # Test"""
    print 'sys.exit(%s)' % (status)
    raise SystemExit()

class FileMaker(object):
    """>>> None # Test"""
    def __init__(self):
        """>>> None # Test"""
        self.paths = {}
        self.files = {}
    def make(self,path,text):
        """>>> None # Test"""
        dir,name = os.path.split(path)
        try:
            os.makedirs(dir)
        except OSError:
            pass
        f = open(path,'w')
        f.write(text)
        f.close()
        self.paths[dir] = None
        self.files[path] = None
    def clean(self):
        """>>> None # Test"""
        for k,f in self.files.iteritems():
            os.remove(k)
        for k,p in self.paths.iteritems():
            while k:
                try:
                    os.rmdir(k)
                except OSError:
                    k,n = os.path.split(k)
        self.files = {}
        self.paths = {}
        
temp = FileMaker()

def print_sys_stderr():
    text = sys.stderr.getvalue()
    if text:
        sys.stdout.write('SE| %s--|' % '\nSE| '.join(text.split('\n')))
    sys.stderr = cStringIO.StringIO()

def _test():
    """>>> None # Test"""
    print "="*85
    os.getenv = _getenv
    sys.exit = _new_exit
    _sys_stderr = sys.stderr
    sys.stderr = cStringIO.StringIO()
    import doctest
    doctest.testmod()
    temp.clean()
    sys.stderr = _sys_stderr

if __name__ == "__main__":
    _test()





