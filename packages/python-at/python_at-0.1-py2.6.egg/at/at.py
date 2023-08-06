import datetime
import subprocess

OUT_FORMAT = '%a %b %d %H:%M:%S %Y'
IN_FORMAT = '%H:%M %m/%d/%Y'

REPLACE_KWARGS = {'second': 0, 'microsecond': 0}

def parse_atq_stdout_line(stdout_line):
    splitted = stdout_line.split()
    return {
        'number': int(splitted[0]),
        'datetime': datetime.datetime.strptime(
            (' ').join(splitted[1:-2]),
            OUT_FORMAT,
            ),
        'queue': splitted[-2],
        'username': splitted[-1],
        }

def parse_atq_stdout(stdout):
    return [parse_atq_stdout_line(l) for l in stdout.splitlines()]

class AtQ(list):
    def __contains__(self, job):
        return job['number'] in [job['number'] for job in self]

def atq():
    return AtQ(parse_atq_stdout(subprocess.Popen(
            ['atq'], stdout=subprocess.PIPE).communicate()[0]))

def parse_at_stderr(stderr):
    job_number, job_datetime = stderr.strip().split(' at ')
    return {
        'number': int(job_number.split()[-1]),
        'datetime': datetime.datetime.strptime(job_datetime, OUT_FORMAT),
        }

def at(_datetime, popen_args):
    p1 = subprocess.Popen(popen_args, stdout=subprocess.PIPE)
    p2 = subprocess.Popen(
        ['at'] + _datetime.strftime(IN_FORMAT).split(),
        stdin=p1.stdout,
        stderr=subprocess.PIPE,
        )
    return parse_at_stderr(p2.communicate()[1])
    
def atrm(jobs):
    if jobs:
        stderr = subprocess.Popen(
            ['atrm'] + [str(job['number']) for job in jobs], 
            stderr=subprocess.PIPE).communicate()[1]
        if stderr:
            if stderr.startswith('Cannot find jobid'):
                raise IndexError(stderr)
            else:
                raise OSError(stderr)
