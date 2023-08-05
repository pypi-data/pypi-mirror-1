from base import *
from heartbeat import HeartBeat
from maintenance import Maintenance
from haproxy import HAProxy
from pound import Pound
from lvs import LVS


HEARTBEAT = HeartBeat()
HAPROXY = HAProxy()
POUND = Pound()
LVS = LVS()


class View(Base):

    @expose(template="fosswallproxy.templates.menu")
    def index(self):
        menu = dict(
                haproxy = 'HAProxy Configuration',
                heartbeat = 'HeartBeat Configuration',
                pound = 'Pound Configuration',
                #lvs = 'LVS Configuration',
            )
        return dict(
                title='View',
                menu=menu,
            )

    haproxy = HAPROXY.view
    heartbeat = HEARTBEAT.view
    lvs = LVS.view
    pound = POUND.view


class Edit(Base):

    @expose(template="fosswallproxy.templates.menu")
    def index(self):
        menu = dict(
                #global_ = 'Global Configuration',
                haproxy = 'Modify Servers (Layer 7 HAProxy)',
                #real = 'Modify Real Servers',
                #virtual = 'Modify Virtual Servers',
                ssl = 'Modify SSL (Pound) Termination',
                heartbeat = 'Modify HeartBeat configuration',
            )
        return dict(
                title='Edit',
                menu=menu,
            )

    haproxy = HAPROXY.list_servers
    heartbeat = HEARTBEAT.edit_conf
    real = haproxy
    virtual = haproxy

    real_modify = HAPROXY.real_modify
    real_new = HAPROXY.real_new
    real_remove = HAPROXY.real_remove

    virtual_modify = HAPROXY.virtual_modify
    virtual_new = HAPROXY.virtual_new
    virtual_remove = HAPROXY.virtual_remove

    ssl = POUND.list
    ssl_modify = POUND.modify
    ssl_new = POUND.new
    ssl_remove = POUND.remove


class Root(Base):

    @expose(template="fosswallproxy.templates.menu")
    def index(self):
        menu = dict(
                view = 'View Configurations',
                edit = 'Edit Configurations',
                maintenance = 'Maintenance',
                #reports = 'Reports',
            )
        return dict(
                title='Fosswall Active Load Balancer',
                menu=menu,
            )


    view = View()
    edit = Edit()
    reports = index
    maintenance = Maintenance()


