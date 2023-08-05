#poundconf.py

import re
import time


COMMENT_EXP = re.compile('^#')
LISTEN_EXP = re.compile('^Listen')
END_EXP = re.compile('End')





class PoundBase(object):
    _indent = '\t'


class PoundLine(PoundBase):
    _string = ''

    def __init__(self, S):
        self._string = S
        self.get_value()

    def __str__(self):
        return self._string

    def get_value(self):
        vals = self._string.split(' ', 1)
        self.indent_level = vals[0].count(self._indent)
        self.key = vals[0].replace(self._indent, '')
        try:
            self.value = vals[1]
        except IndexError:
            try:
                self.value = vals[1]
            except IndexError:
                self.value = True


class PoundValue(PoundLine):
    def __str__(self):
        indent = self.indent_level*self._indent
        if self.value is not True:
            self._string = '%s%s %s' % (indent, self.key, self.value)
        else:
            self._string = '%s%s' % (indent, self.key)
        return self._string


class PoundSection(PoundBase):
    _options = ()
    _lines = []
    _options_class = {}

    def __str__(self):
        lines = []
        for line in self._lines:
            lines.append(str(line))
        return '\n'.join(lines)

    def assign_opt(self, opt, line):
        if opt in self._options_class.keys():
            pline = self._options_class[opt](line)
        else:
            pline = PoundLine(line)
        setattr(self, opt, pline)
        self._lines.append(pline)

    def parse_line(self, line):
        for opt in self._options:
            if line.startswith(opt):
                self.assign_opt(opt, line)





class PoundListenValue(PoundValue):
    def __init__(self, S=None, key=None, value=None):
        if S is not None:
            self._string = S
            self.get_value()
        else:
            self.indent_level = 1
            self.key = key
            self.value = value


class PoundServiceValue(PoundValue):
    def __init__(self, S=None, key=None, value=None):
        if S is not None:
            self._string = S
            self.get_value()
        else:
            self.indent_level = 4
            self.key = key
            self.value = value


class PoundService(PoundSection):
    _options = (
            'Address',
            'Port',
        )
    _options_class = dict(
            Address = PoundServiceValue,
            Port = PoundServiceValue,
        )

    def __init__(self, S=None):
        self._lines = []
        if S is not None:
            self.content = S
            self.refresh()

    def __str__(self):
        i = self._indent
        lines = [2*i + 'Service']
        lines.append(3*i + 'BackEnd')
        for opt in self._options:
            lines.append(str(getattr(self, opt)))
        lines.append(3*i + 'End')
        lines.append(2*i + 'End')
        return '\n'.join(lines)

    def get_conf(self):
        lines = self.content.split('\n')
        for line in lines:
            self.parse_line(line)
    refresh = get_conf

    def parse_line(self, line):
        indent = re.compile('^%s' % (self._indent))
        for opt in self._options:
            exp = re.compile('%s' % (opt))
            if exp.search(line):
                self.assign_opt(opt, line)


class PoundListen(PoundSection):
    _options = (
            'Address',
            'Port',
            'Cert',
        )
    _options_class = dict(
            Address = PoundListenValue,
            Port = PoundListenValue,
            Cert = PoundListenValue,
        )

    def __init__(self, S=None):
        self._lines = []
        if S is not None:
            self.content = S
            self.refresh()

    def __str__(self):
        lines = ['ListenHTTPS']
        for opt in self._options:
            lines.append(str(getattr(self, opt)))
        lines.append(str(self.service))
        lines.append('End')
        lines.append('')
        return '\n'.join(lines)

    def get_conf(self):
        lines = self.content.split('\n')
        line = lines.pop(0)
        while not re.search('Service', line):
            self.parse_line(line)
            line = lines.pop(0)
        service = []
        while not re.match('^%(i)s%(i)sEnd' % {'i': self._indent}, line):
            service.append(line)
            line = lines.pop(0)
        service.append(line)
        p_service = PoundService('\n'.join(service))
        self.service = p_service
        self._lines.append(p_service)
    refresh = get_conf

    def parse_line(self, line):
        indent = re.compile('^%s' % (self._indent))
        for opt in self._options:
            exp = re.compile('^%s%s' % (self._indent, opt))
            if exp.match(line):
                self.assign_opt(opt, line)


class PoundConf(PoundSection):
    filename = None
    _options = (
            'User',
            'Group',
            'LogLevel',
            'ListenHTTPS',
        )

    def __init__(self, filename=None):
        self.listen = []
        if filename is not None:
            self.filename = filename
            self.refresh()

    def add_listen(self, listen):
        self.listen.append(listen)
        self._lines.append(listen)

    def create_listen(self, v_ip=None, v_port=None, r_ip=None, r_port=None, cert=None):
        listen = PoundListen()
        listen.Address = PoundListenValue(key='Address', value=v_ip)
        listen.Port = PoundListenValue(key='Port', value=v_port)
        listen.Cert = PoundListenValue(key='Cert', value=cert)
        listen.service = PoundService()
        listen.service.Address = PoundServiceValue(key='Address', value=r_ip)
        listen.service.Port = PoundServiceValue(key='Port', value=r_port)
        return listen

    def get_conf(self):
        lines = self.content.split('\n')
        line = lines.pop(0)
        while not LISTEN_EXP.match(line):
            self.parse_line(line)
            line = lines.pop(0)
        while 'End' in lines:
            listen = []
            while not re.match('^End', line):
                listen.append(line)
                line = lines.pop(0)
            line = lines.pop(0) # get rid of End
            p_listen = PoundListen('\n'.join(listen))
            self.listen.append(p_listen)
            self._lines.append(p_listen)

    def modify_listen(self, i, v_ip=None, v_port=None, r_ip=None, r_port=None):
        if v_ip is not None:
            self.listen[i].Address.value = v_ip
        if v_port is not None:
            self.listen[i].Port.value = v_port
        if r_ip is not None:
            self.listen[i].service.Address.value = r_ip
        if r_port is not None:
            self.listen[i].service.Port.value = r_port

    def read(self):
        fd = file(self.filename)
        self.content = fd.read()
        fd.close()

    def refresh(self):
        self.read()
        self.get_conf()

    def remove_listen(self, i):
        listen = self.listen.pop(i)
        ind = self._lines.index(listen)
        self._lines.pop(ind)

    def write(self):
        fd = file(self.filename, 'w')
        fd.write(str(self))
        fd.close()

