#!/usr/bin/env python
##############################################################################
'''Provide an easy way to concurrently run ssh jobs on a large number of 
   targets, gather output, error messages and results from each and handle 
   timeouts.
'''

__author__  = '''Jim Dennis <answrguy@gmail.com>'''
__url__     = '''http://bitbucket.org/jimd/classh/'''
__license___= '''PSF (Python Software Foundation)'''
__version__ = 0.09


import sys, os, string, signal, re
from time import sleep, time
from subprocess import Popen, PIPE

def debug(str):   # TODO: use logging package?
    if 'DEBUG' in os.environ and os.environ['DEBUG']==sys.argv[0]:
        print >> sys.stderr, str

class JobRecord(object):
    def __init__(self, target):
        self.target   = target
        self.proc     = None      
        self.exitcode = None 
        self.output   = None
        self.errors   = None
        self.started  = time()
        self.stopped  = None

class SSHJobMan(object):
    '''SSH Job Manager
       Given a command and a list of targets (hostnames), concurrently
       run the command on some number (poolsize) of the targets,
       gathering all the results (output, error messages and exit values)
       and handling any timeouts (jobtimeout)
       
       Maintains a dictionary of results, each item of which is a dictionary
       containing the specified types fo results.
    '''

    def __init__(self, hostlist=None, cmd=None, **opts):
        '''
        '''
        self.started = False
        self.poolsize = 100
        self.jobtimeout = 300
        self.sleeptime  = 0.2

        self.pool    = dict()         # for maintaining host/process data
        self.results = dict()  

        self.mergeout = dict()
        self.mergeerr = dict()
        
        self.ssh = [ '/usr/bin/ssh' ]        #TODO: dynamically find this
        self.ssh_args = [ '-oBatchMode=yes'] #TODO: add other batch options?

        self.targets = hostlist
        self.cmd = cmd 

        self.__dict__.update(opts)  # Ugly hack?
        

    def start(self):
        '''Set instance started flag
           Prime the pool with new jobs

           This is deferred from initialization to
           allow the caller to hook self.poll() into
           any signal handling (SIGCHILD, SIGALARM), etc.
        '''

        debug ('Starting')
        self.add_jobs()
        self.started = time()
        

    def add_jobs(self):
        '''Called from start and from poll to fill the pool with
           subprocesses.  While the start method primes the pool, 
           poll method keeps it topped off until all targets have been
           handled.

           Jobs are added to the pool and to the results with a unique
           key.  The poll method removes completed jobs from the pool
           calling the gather method to save their results.  The key
           is used to keep track of each job even if multiple jobs
           go to the same target.  (If there are duplicate targets than
           the additional keys will be of the form: hostname:XX)
        '''

        while self.targets and len(self.pool.keys()) < self.poolsize:
            debug('adding jobs')
            host = self.targets.pop()
            job = JobRecord(host)
            key = host
            if key in self.results:
                x = 0 
                while key + ':' + str(x) in self.results:  # Unique-ify a key
                    x += 1
                key = key + ':' + str(x) 

            try: 
                job.proc = Popen(self.ssh + self.ssh_args + [host] 
                           + [self.cmd], 
                           stdout=PIPE,stderr=PIPE, close_fds=True)
            except OSError, e:
                ## Too many open files, or processes or whatever
                ## Sleep briefly and retry
                debug('Popen failure %s' % e.errno)
                self.targets.insert(0, host)
                sleep(0.1)
                return 

            self.results[key] = 'Placeholder'
            self.pool[key] = job
            debug('... added job %s' % key)

    def poll(self):
        '''Scan pool for completed jobs, 
           call gather() for any of those
           remove completed jobs from pool
           call add_jobs() to top off pool
           return list of completed job keys
        '''
        
        debug ('polling')
        if not self.started:
            self.start()
        reaped = list() 
        for key, job in self.pool.items():
            rv = job.proc.poll()
            if rv is not None:
                debug('job %s is done' % key)
                job.exitcode = rv 
                self.gather(key, job)
                if key in self.pool:
                    del self.pool[key]
                else:  #TODO: only seen with extremely short timeouts
                    debug('key %s not found in pool' % key)
                reaped.append(key)
            # Handle timeouts:
            if self.jobtimeout > 0:
                elapsed = time() - job.started
                if elapsed > self.jobtimeout:
                    debug('job %s timed out after %s seconds' % (key, elapsed))
                    self.kill(job.proc)
                    self.gather(key, job)
                    if key in self.pool:
                        del self.pool[key]
                    else:  #TODO: only seen with extremely short timeouts
                        debug('key %s not found in pool' % key)
                    reaped.append(key)
        debug ('reaped %s jobs' % len(reaped))
        self.add_jobs()
        return reaped

    def gather(self, key, job):
        '''Gather results from a subprocess
           These are stored as a dictionary of jobs
        '''
        debug ('gathering')
        try: 
            (output, errors) = job.proc.communicate()
        except ValueError, e: # Popen error on short timeouts?
            debug ('Popen.communicate exception')
            (output, errors) = ('','')
            job.exitcode = - (1000 + job.exitcode) 
            ##TODO: Popen:Exception
        job.stopped  = time()

        if output.strip() == '':  # If it's all whitespace
            output = ''           # distill it down to nothing

        if errors.strip() == '':  # ditto
            errors = ''

        # Keep messages merged and possibly force intern of results
        if output in self.mergeout:
            self.mergeout[output].append(key)
        else:
            self.mergeout[output] = [key]

        if errors in self.mergeerr:
            self.mergeerr[errors].append(key)
        else:
            self.mergeerr[errors] = [key]

        job.output= output
        job.errors= errors

        self.results[key] = job

            
    def kill(self, proc):
        '''Kill a subprocess which has exceeded its timeout
           called by poll()
        '''
        debug('Killing %s' % proc.pid)
        try:
            os.kill(proc.pid, signal.SIGTERM)
        except OSError:
            debug('Trying SIGKILL!')
            try:
                os.kill(proc.pid, signal.SIGKILL)
            except OSError:
                debug('Ignoring os.kill OSError')


    def wait(self, maxwait=None, snooze=None):
        '''
        '''
        debug ('wait called called with: %s %s ' % (maxwait,snooze))
        return_after=None
        if maxwait is not None:
            # Pre-calculation return time:
            return_after = time() + maxwait
        if snooze is None:
            snooze = self.sleeptime
        if not self.started:
            self.start()
        while not self.done():
            if return_after and time() > return_after:
                return 
            sleep(snooze)
            self.poll()


    def done(self):
        '''We're done when we have been started and
           we have zero remaining jobs in the pool
        '''
        debug ('done called with %s remaining jobs' % len(self.pool.keys()))
        return self.started and not len(self.pool.keys())



# Expand ranges: 
expr = re.compile(r'\[[0-9][-0-9,[]*\]')
def range2list(s):
    '''Given [x-y,a,b-c] return: range(x,y) + [a] + range(b,c)
       Handle decrements and zero-filling if necessary!
    '''
    assert s.startswith('[') and s.endswith(']') 
    if len(s) < 2:
        return [s]
    results = []
    r = s[1:-1]  # extract from enclosing brackets
    for i in r.split(','):  # each p
        if '-' not in i:
            results.append(i)
            continue
        # Else: (it's a range so...)
        t = i.split('-')
        if len(t) != 2:   # punt on degenerate expressions
            results.append(i) 
            continue
        # Else:
        if len(t[0]) > 1 and t[0].startswith('0'):
            fmt = "%%0%sd" % len(t[0])  ## Handle zero fill
        else:
            fmt = "%s"
        try:
            l, u = int(t[0]), int(t[1])
        except ValueError:  # punt on stuff that can't be converted
            results.append(i) # remember i? There's a song about i.
            continue 
        if l > u:
            step=-1
            u -= 1          # Make range INCLUSIVE
        else:
            step=1
            u += 1          # Make range INCLUSIVE
        results.extend([fmt % x for x in range(l,u,step)])
    return results 
        

def expand_range(s):
    '''Return a list of strings with expressions like [n-m,p,t] expanded.

       Examples:
       >>> expand_range("foo")
       ['foo']

       >>> expand_range("foo[1,3,9]")
       ['foo1', 'foo3', 'foo9']

       >>> expand_range("bar[1-3]foo")
       ['bar1foo', 'bar2foo', 'bar3foo']
    '''

    debug("\texpand_range(%s)" % (s))
    results = [] 
    rx = expr.search(s)  # range expression
    if not rx:
        return [s]  # other base case, wrap it in a list
    b,e = rx.span()
    fmt = s[:b] + "%s" + s[e:]  # foo[...]bar -> foo%sbar
    m  = s[b:e]                 # first [...] from 
    for i in range2list(m):
        results.extend(expand_range(fmt % i))
    return results 

        
# Use in print results to munge non-printable chars
filter = string.maketrans(
           string.translate(string.maketrans('',''),
           string.maketrans('',''),string.printable[:-5]),
           '.'*len(string.translate(string.maketrans('',''),
           string.maketrans('',''),string.printable[:-5])))

# Use to munge non-printable while preserving tabs and newlines
lfilter = string.maketrans(
           string.translate(string.maketrans('',''),
           string.maketrans('',''),string.printable[:-3]),
           '.'*len(string.translate(string.maketrans('',''),
           string.maketrans('',''),string.printable[:-3])))


def print_results(key, job):
    errs = ' '.join(job.errors.split('\n'))
    outs = ' '.join(job.output.split('\n')) 
    errs = errs[:60].translate(filter)
    outs = outs[:60].translate(filter)

    pfix = ''.join(["%-48s" % key, "%-5s" % job.exitcode, 
        "(%s)" % ("%0.2f" % (job.stopped - job.started))])
    if job.exitcode:
        print pfix, "\tErrors: ", errs[:40]
    print pfix, "\tOutput: ", outs[:40]

def show_progress(key, job):
    '''Print progress bar as incremental results
       . for successful jobs
       ? for remote errors returned
       ! for timed out / killed jobs
       ~ for (probable) ssh errors 
    '''
    if    job.exitcode  ==      0: res = '.'
    elif  job.exitcode  ==    255: res = '~'
    elif  job.exitcode  ==  -1000: res = '#' # See TODO: Popen:Exception
    elif  job.exitcode   >      0: res = '?'
    elif  job.exitcode   <      0: res = '!'
    sys.stderr.write(res)   # avoid trailing spaciness from print statement
            

def summarize_results(job):
    '''Print the number of success, errors, and timeouts from a job
    '''
    success  = 0
    errs     = 0
    timeouts = 0
    for i in job.values():
        if    i.exitcode  ==  0: success  += 1
        elif  i.exitcode   >  0: errs     += 1
        elif  i.exitcode   <  0: timeouts += 1
    print "\n\n\tSuccessful: %s\tErrors: %s\tSignaled(timeouts): %s" \
      % (success, errs, timeouts)


def comma_join(lst):
    '''Print list in a natural way, joined by commas with the last
       after an ", and " 
    '''
    if len(lst) < 2:
        return lst[0]
    return ', '.join(lst[:-1]) + ', and ' + lst[-1]



def summarize_merged_results(jhand):
    '''Given a job handle (object) print each unique output or error message
       along with the list of hosts from which it was gathered.

       Separately print the number of distinct messages and the number
       of successful and error-returning jobs with no messages.
    '''
    success  = 0
    errs     = 0
    timeouts = 0

    print "\n"  # Ensure a clear line, esp. if progressbar enabled
    for out in jhand.mergeout.keys():
        if out == '':
            continue 
        n = len(jhand.mergeout[out])
        print "Output from (%s hosts): " % n, comma_join(jhand.mergeout[out])
        print "============================================================="
        print out.translate(lfilter)
        print "=============================================================\n"

    for err in jhand.mergeerr.keys():
        if err == '':
            continue 
        n = len(jhand.mergeerr[err])
        print "Errors from (%s hosts): " % n, comma_join(jhand.mergeerr[err])
        print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        print err.translate(lfilter)
        print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n"

    for i in jhand.results.values():
        if    i.exitcode  ==  0: success  += 1
        elif  i.exitcode   >  0: errs     += 1
        elif  i.exitcode   <  0: timeouts += 1
    print "\n\n\tSuccessful: %s\tErrors: %s\tSignaled(timeouts): %s" \
      % (success, errs, timeouts)



def readfile(fname):
    results = []
    try: 
        f = open(fname)
    except EnvironmentError, e:
        ##TODO: logger! 
        print >> sys.stderr, "Error reading %s, %s" % (fname, e)
    for line in f:
        results.append(line.strip())
    return results

usage = '''
usage %%prog [switches] cmd [hostname|./file] [host]./file ...]
version %s
''' % __version__
 
def parse_options():
    from optparse import OptionParser
    parser = OptionParser(usage=usage)

    parser.add_option(
       '-n', '--numjobs', dest='numjobs', 
       action='store', type='int', default=100,
       help="Maximum number of concurrent subprocesses (size of job pool)")

    parser.add_option(
       '-t', '--timeout', dest='timeout', 
       action='store', type='int', default=300,
       help="Maximum number of seconds a job may run before being killed")

    parser.add_option(
       '--progress', dest='progressbar', 
       action='store_true', default=False,
       help="Show progress as . (successful) ? (remote error) ! (timed out)")

    parser.add_option(
       '--noexpand', dest='noexpand', 
       action='store_true', default=False,
       help="Disable expansion of hostname ranges")

    parser.add_option(
       '--mergemsgs', dest='mergemsgs', 
       action='store_true', default=False,
       help="Merge identical output/error messages")
       
    opts, args = parser.parse_args()
    return (parser, opts, args)

if __name__ == "__main__":
    '''First argument is command, rest are hosts.
       Dispatch jobs to hosts and incrementally print results
       or progress bar
    '''

    start = time()
    (parser, options, args) = parse_options()

    if len(args) < 2:
        parser.error("Must specify a command and a list of hosts")

    cmd   = args[0]
    hosts = list()

    handle_completed = print_results
    if options.mergemsgs:
        handle_completed = lambda x,y : None
    if options.progressbar:
        handle_completed = show_progress
    
    for arg in args[1:]:
        if '/' in arg:
            # it's a filename so:
            if options.noexpand:
                hosts.extend(readfile(arg))
            else:
                for each in readfile(arg):
                    hosts.extend(expand_range(each))
        else:
            if options.noexpand:
                hosts.append(arg)
            else:
                hosts.extend(expand_range(arg))

    print >> sys.stderr, "About to run '%s' on %s hosts...\n\n" \
        % (cmd, len(hosts))


    job = SSHJobMan(hosts, cmd, 
        poolsize=options.numjobs,
        jobtimeout=options.timeout)

    job.start()
    
    completed = None
    while not job.done():
        completed = job.poll()
        sleep(0.2)
        if completed:
            for each in completed:
                handle_completed(each, job.results[each])
        
    if not options.mergemsgs:    
        summarize_results(job.results)
    else:
        summarize_merged_results(job)
    
    print "Completed in %s seconds" % (time() - start)


