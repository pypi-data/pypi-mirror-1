import sys, commands
from base import *
from poundconf import poundconf


class Pound(Base):
    filename = BASE_DIR + '/pound/pound.cfg'
    conf = poundconf.PoundConf(filename)

    def copy(self):
        cp_command = 'sudo scp %s root@lbslave:/etc/ha.d/haresources > /dev/null 2>&1 &' % (self.filename)
        stat = os.system(cp_command)
        stat = commands.get_output(cp_command)

    @expose(template="fosswallproxy.templates.ssl_list")
    def list(self):
        servers = self.conf.listen
        return dict(
                title='SSL Termination (pound)',
                servers = self.conf.listen,
            )

    @expose(template="fosswallproxy.templates.ssl_modify")
    def modify(self, id, action=None, v_ip=None, v_port=None, r_ip=None, r_port=None):
        id = int(id)
        listen = self.conf.listen[id]
        if action is None:
            action = 'modify'
        elif action == 'modify':
            self.conf.modify_listen(id, v_ip, v_port, r_ip, r_port)
            self.conf.write()
            flash('Successfully modified SSL Termination')
            redirect('ssl')
        return dict(
                title='SSL Termination (pound)',
                servers = self.conf.listen,
                listen = listen,
                action = action,
                id = id,
            )

    @expose(template="fosswallproxy.templates.ssl_modify")
    def new(self, action=None, v_ip=None, v_port=None, r_ip=None, r_port=None, **kw):
        listen = self.conf.create_listen(v_ip, v_port, r_ip, r_port)
        if action is None:
            action = 'create'
        elif action == 'create':
            self.conf.add_listen(listen)
            self.conf.write()
            flash('Successfully created new SSL Termination')
            redirect('ssl')
        return dict(
                title='SSL Termination (pound)',
                servers = self.conf.listen,
                listen = listen,
                action = action,
            )

    @expose()
    def remove(self, id):
        id = int(id)
        listen = self.conf.listen[id]
        msg = 'Successfully removed %s:%s' % (
                listen.Address.value,
                listen.Port.value,
            )
        self.conf.remove_listen(id)
        self.conf.write()
        flash(msg)
        redirect('ssl')
        return msg

    @expose(template="fosswallproxy.templates.view")
    def view(self):
        return dict(
                title='SSL Termination (pound)',
                conf=str(self.conf),
            )


