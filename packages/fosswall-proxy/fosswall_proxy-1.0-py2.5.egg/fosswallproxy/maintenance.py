from base import *
import os

ENABLED = 0

class Maintenance(Base):

    @expose(template="fosswallproxy.templates.menu")
    def index(self):
        menu = dict(
                haproxy = 'Restart HAProxy',
                heartbeat = 'Restart Heartbeat',
                pound = 'Restart Pound',
            )
        return dict(
                title='Maintenance',
                menu=menu,
            )

    @expose()
    def haproxy(self):
        cmd = 'sudo /usr/local/sbin/haproxy -f /etc/haproxy/haproxy.cfg -p /var/run/haproxy.pid -sf $(cat /var/run/haproxy.pid) 2>&1'
        msg = 'Disabled HAProxy restart'#dbg
        if self.run(cmd):
            msg = 'Successfully restarted HAProxy'
        flash(msg)
        redirect('index')
        return msg

    @expose()
    def heartbeat(self):
        #cmd = 'sudo /usr/local/sbin/haproxy -f /etc/haproxy/haproxy.cfg -p /var/run/haproxy.pid -sf $(cat /var/run/haproxy.pid) 2>&1'
        cmd = '/etc/init.d/heartbeat restart'
        msg = 'Disabled Heartbeat restart'#dbg
        if self.run(cmd):
            msg = 'Successfully restarted Heartbeat'
        flash(msg)
        redirect('index')
        return msg

    @expose()
    def pound(self):
        cmd = 'sudo /etc/rc.d/init.d/pound restart'
        msg = 'Disabled Pound restart'#dbg
        if self.run(cmd):
            msg = 'Successfully restarted Pound'
        flash(msg)
        redirect('index')
        return msg

    def run(self, cmd):
        if ENABLED:
            send_stat = os.system(cmd)
            if send_stat == 0:
                return True
            else:
                raise Error('Error running %s' % cmd)
        else:
            return False


