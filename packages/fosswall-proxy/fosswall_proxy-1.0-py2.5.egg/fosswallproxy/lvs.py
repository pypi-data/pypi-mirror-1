import sys, commands
from base import *
from lvsconf import lvsconf


class LVS(Base):
    filename = BASE_DIR + '/lvs.cf'
    conf = lvsconf.LVSConf(filename)

    def copy(self):
        cp_command = 'sudo scp %s root@lbslave:/etc/ha.d/haresources > /dev/null 2>&1 &' % (self.filename)
        stat = os.system(cp_command)
        stat = commands.get_output(cp_command)

    @expose(template="fosswallproxy.templates.view")
    def view(self):
        return dict(
                title='LVS',
                conf=str(self.conf),
            )


