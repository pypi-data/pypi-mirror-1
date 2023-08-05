import sys, commands
from base import *
from haconf import haconf


class HAProxy(Base):
    filename = BASE_DIR + '/haproxy.cfg'
    conf = haconf.HAConf(filename)

    def copy(self):
        cp_command = 'sudo scp %s root@lbslave:/etc/ha.d/haresources > /dev/null 2>&1 &' % (self.filename)
        stat = os.system(cp_command)
        stat = commands.get_output(cp_command)

    @expose(template="fosswallproxy.templates.virtual_list")
    def list_servers(self):
        self.conf.read()
        servers = self.conf.listen
        return dict(
                title='Servers',
                virtuals=servers,
            )
 
    @expose(template="fosswallproxy.templates.real_modify")
    def real_modify(self, v_id, r_id, action=None, name=None, ip_address=None, port=None, cookie=None, options=''):
        v_id = int(v_id)
        r_id = int(r_id)
        server = self.conf.listen[v_id].server[r_id]
        if action is None:
            action = 'modify'
        elif action == 'modify':
            print 'Modifying real server'
            server.name = name
            server.ip_address = ip_address
            server.port = port
            server.cookie = cookie
            server.options = options
            self.conf.write()
            redirect('real')
        return dict(
                title = 'Modify %s real server' % server.name,
                server = server,
                virtuals = self.conf.listen,
                v_id = v_id,
                r_id = r_id,
                action = action,
            )

    @expose(template="fosswallproxy.templates.real_modify")
    def real_new(self, v_id, r_id='', action=None, name=None, ip_address=None, port=None, options=''):
        v_id = int(v_id)
        if action is None:
            server = haconf.HAServer()
            action = 'create'
        elif action == 'create':
            print 'Creating real server'
            listen = self.conf.listen[v_id]
            server = listen.add_server(
                    name = name,
                    ip_address = ip_address,
                    port = port,
                    options = options,
                )
            self.conf.write()
            redirect('real')
        return dict(
                title = 'New real server',
                server = server,
                virtuals = self.conf.listen,
                v_id = v_id,
                r_id = r_id,
                action = action,
            )

    @expose()
    def real_remove(self, v_id, r_id):
        v_id = int(v_id)
        r_id = int(r_id)
        listen = self.conf.listen[v_id]
        server = listen.server[r_id]
        listen.server.remove(server)
        listen._lines.remove(server)
        self.conf.write()
        msg = 'Successfully removed virtual server %s' % server.name
        flash(msg)
        redirect('virtual')
        return msg

    def restart(self):
        cmd = 'sudo /etc/rc.d/init.d/heartbeat restart > /dev/null 2>&1 &'
        stat = os.system(cmd)
        stat = commands.get_output(cmd)

    @expose(template="fosswallproxy.templates.view")
    def view(self):
        return dict(
                title='HAProxy Configuration',
                conf=str(self.conf),
            )

    @expose(template="fosswallproxy.templates.virtual_modify")
    def virtual_modify(self, v_id, action=None, name=None, ip_address=None, port=None, mode='http', persistent=False):
        server = self.conf.listen[int(v_id)]
        if action is None:
            pass
        elif action == 'modify':
            print 'Modifying virtual server'
            server.name = name
            server.ip_address = ip_address
            server.port = port
            if persistent == 'False':
                persistent = False
            server.change_persistence(persistent)
            server.change_mode(mode)
            self.conf.write()
            redirect('virtual')
        elif action == 'remove':
            self.conf.listen.remove(server)
        return dict(
                title = 'Modify "%s" Virtual Server' % server.name,
                virtuals = self.conf.listen,
                server = server,
                id = v_id,
                action = 'modify',
            )

    @expose(template="fosswallproxy.templates.virtual_modify")
    def virtual_new(self, action=None, name=None, ip_address=None, port=None, mode='http', persistent=False, **kw):
        if action is None:
            server = haconf.HAListen()
        else:
            print 'Adding Virtual Server'
            server = self.conf.add_listen(name=name, ip_address=ip_address, port=port, mode=mode, persistent=persistent)
            #self.conf.listen.append(server)
            self.conf.write()
            redirect('virtual')
        return dict(
                title = 'New Virtual Server',
                server = server,
                virtuals = self.conf.listen,
                action = 'create',
                id = '',
            )

    @expose()
    def virtual_remove(self, v_id):
        server = self.conf.listen[int(v_id)]
        self.conf.listen.remove(server)
        self.conf.write()
        msg = 'Successfully removed virtual server %s' % server.name
        flash(msg)
        redirect('virtual')
        return msg

