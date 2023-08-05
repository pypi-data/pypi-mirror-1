import cStringIO
import difflib
import os
import re
import shutil
import sys
import traceback

npass = 0
nfail = 0

print '-'*80
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Fake out sys.exit()
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def exit(*args,**kwargs):
    global nfail
    #nfail += 1
    print "ERROR: got system exit"
    
sys.exit = exit

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Read special XML markup in TEX file, record tag, attributes and body
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

f = open('../docs/cfgparse.tex')
content = f.read()
f.close()

lowercontent = content.lower()
npass_exp = lowercontent.count('<stdout') + lowercontent.count('<cline')

tag_group = '(?P<tag>file|python|stdout|stderr|cline)'
attribs_group = '(?P<attribs>.*?)'
tag_line = '\n%% <%s%s>.*?' % (tag_group,attribs_group)
beg_verb = r'\n\\begin{verbatim}.*?\n'
body = '(?P<body>.*?\n)'
end_verb = r'\\end{verbatim}'
pattern = ''.join([tag_line,beg_verb,body,end_verb])
xml_sect_regexp = re.compile(pattern,re.DOTALL)

attrib_regexp = re.compile('''(?P<name>\w+)=['"](?P<value>[\w\.]*)['"]''')

sections = []

def xml_section_recorder(sr_mo):
    attribs = dict()
    def attrib_recorder(ar_mo):
        attribs[ar_mo.group('name')] = ar_mo.group('value')
    attrib_regexp.sub(attrib_recorder,sr_mo.group('attribs'))
    sections.append((sr_mo.group('tag'),attribs,sr_mo.group('body')))    

xml_sect_regexp.sub(xml_section_recorder,content)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Process special XML markup
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

subdir = '_cfgparse_tex_doctest'
if os.path.exists(subdir):
    shutil.rmtree(subdir)
os.mkdir(subdir)
os.chdir(subdir)

testdir = os.getcwd()

try:
    # for python 2.4 and later
    differ = difflib.HtmlDiff()
    diffext = 'diff.html'
except AttributeError:
    # for python 2.3 and earlier
    class Diff(object):
        def make_file(self,flines,tlines,fdesc,tdesc):
            flines = [fdesc] + flines
            tlines = [tdesc] + tlines
            return '\n'.join(difflib.ndiff(flines,tlines))
    differ = Diff()
    diffext = 'diff.txt'

for tag,attribs,body in sections:
    id = attribs.get('id')
    if tag == 'file':
        # print "creating file:",attribs['name']
        f = open(attribs['name'],'w')
        f.write(body)
        f.close()
    elif tag == 'python':
        if id:
            f = open(id,'w')
            f.write(body)
            f.close()
        print "executing python (id=%s)" % id
        stdout, sys.stdout = sys.stdout, cStringIO.StringIO()
        stderr, sys.stderr = sys.stderr, cStringIO.StringIO()
        try:
            exec body
            error = None
        except KeyboardInterrupt:
            stdout, sys.stdout = sys.stdout.getvalue(), stdout
            stderr, sys.stderr = sys.stderr.getvalue(), stderr
            raise
        except:
            stdout, sys.stdout = sys.stdout.getvalue(), stdout
            stderr, sys.stderr = sys.stderr.getvalue(), stderr
            nfail += 1
            type,value,tb = sys.exc_info()[0:3]
            tb = traceback.format_list(traceback.extract_tb(tb)[1:])
            offset = int(tb[0].replace(',',' ').split()[3])
            tb[1:1] = '    %s\n' % body.split('\n')[offset-1]
            e = ''.join(traceback.format_exception_only(type,value))
            print "ERROR: \n%s\n%s" % (''.join(tb),e)
            #type,value = sys.exc_info()[0:2]
            #exception = traceback.format_exception_only(type,value)
        else:
            stdout, sys.stdout = sys.stdout.getvalue(), stdout
            stderr, sys.stderr = sys.stderr.getvalue(), stderr
    elif tag == 'cline':
        result = []
        body = body.replace('[CWD]',testdir)
        for line in body.split('\n'):
            if line.strip() == '$':
                result.append(line)
            elif line.startswith('$ '):
                result.append(line)
                fi,fo,fe = os.popen3(line[2:])
                fi.close()
                result.append(fo.read()+fe.read())
        result = '\n'.join(result)
        if body == result:
            npass += 1
            print "pass: comparing command line (id=%s)" % id
        else:
            nfail += 1
            print "ERROR: comparing command line (id=%s)" % id
            flines = body.split('\n')
            tlines = result.split('\n')
            f = open('cline_%s.txt'%id,'w')
            f.write(result)
            f.close()
            f = open('cline_%s.%s'%(id,diffext),'w')
            f.write(differ.make_file(flines,tlines,'baseline','cline (id=%s)'%id))
            f.close()
    elif tag == 'stdout':
        if body == stdout:
            npass += 1
            print "pass: comparing stdout (id=%s)" % id
        else:
            nfail += 1
            print "ERROR: comparing stdout (id=%s)" % id
            flines = body.split('\n')
            tlines = stdout.split('\n')
            f = open('stdout_%s.txt'%id,'w')
            f.write(stdout)
            f.close()
            f = open('stdout_%s.%s'%(id,diffext),'w')
            f.write(differ.make_file(flines,tlines,'baseline','stdout (id=%s)'%id))
            f.close()
    elif tag == 'stderr':
        if body == stderr:
            npass += 1
            print "pass: comparing stderr (id=%s)" % id
        else:
            nfail += 1
            print "ERROR: comparing stderr (id=%s)" % id
            flines = body.split('\n')
            tlines = stderr.split('\n')
            f = open('stderr_%s.%s'%(id,diffext),'w')
            f.write(differ.make_file(flines,tlines,'baseline','stderr (id=%s)'%id))
            f.close()
    else:
        print "ERROR: unknown tag '%s'" % tag
    # print '-'*40

if nfail == 0 and npass == npass_exp:        
    print "PASS (%s)" % npass
else:
    print "nfail=%d" % nfail
    print "npass=%d (%d expected)" % (npass,npass_exp)
    print "FAIL" 

#import doctest
#print '='*90
#doctest.testfile("cfgparse.tex",optionflags=doctest.ELLIPSIS)
 
