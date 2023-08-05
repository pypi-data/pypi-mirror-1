import re


IP_EXP = re.compile(r"""
   \b                                           # matches the beginning of the string
   (25[0-5]|                                    # matches the integer range 250-255 OR
   2[0-4][0-9]|                                 # matches the integer range 200-249 OR
   [01]?[0-9][0-9]?)                            # matches any other combination of 1-3 digits below 200
   \.                                           # matches '.'
   (25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)       # repeat
   \.                                           # matches '.'
   (25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)       # repeat
   \.                                           # matches '.'
   (25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)       # repeat
   \b                                           # matches the end of the string
   """, re.VERBOSE)

COMMENT_EXP = re.compile('\#')
NODES_EXP = re.compile('node')

class Resources(object):
    def __init__(self, S):
        vals = S.split(' ')
        self.master = vals.pop(0)
        self.ips = []
        self.res = []
        for val in vals:
            if IP_EXP.match(val):
                self.ips.append(val)
            else:
                self.res.append(val)

    def __str__(self):
        S = self.master + ' '
        S += ' '.join(self.ips) + ' '
        S += ' '.join(self.res)
        return S


class HeartBeatConf(object):
    _options = (
            'logfile',
            'logfacility',
            'keepalive',
            'deadtime',
            'warntime',
            'initdead',
            'serial',
            'bcast',
            'auto_failback',
        )
    ping = None

    def __init__(self, filename):
        self.filename = filename
        self.refresh()

    def __str__(self):
        lines = []
        for opt in self._options:
            lines.append('%s %s' % (opt, getattr(self, opt)))
        for n in self.nodes:
            lines.append('node %s' % n)
        if self.ping is not None:
            lines.append('ping %s' % self.ping)
            lines.append('respawn hacluster /usr/lib/heartbeat/ipfail')
        return '\n'.join(lines)

    def get_lines(self):
        fd = open(self.filename)
        lines = fd.readlines()
        fd.close()
        return lines

    def refresh(self):
        lines = self.get_lines()
        self.comments = []
        self.nodes = []
        for line in lines:
            line = line.strip('\n')
            if COMMENT_EXP.match(line):
                self.comments.append(line)
            elif NODES_EXP.match(line):
                self.nodes.append(line.split(' ', 1)[1])
            else:
                vals = line.split(' ', 1)
                setattr(self, vals[0], vals[1])

    def write(self):
        fd = open(self.filename, 'w')
        fd.write(str(self))
        fd.close()


