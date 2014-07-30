# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################
import paramiko


def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    if auth.user is None:
        redirect(URL('default','user', args='login'))
    if session.error:
        response.flash = "Oh Crap! Something went wrong! Check with Nazarii!"
    tbl = db.servers
    tbl.port.readable = False
    tbl.username.readable = False
    tbl.id.readable = False
    tbl.passwd.readable = False
    tbl.allow_managing.readable = False
    query = db.servers.id >0
    used_server = session.used_server or 0
    db(db.servers.id !=used_server).update(running_time = '')
    db.servers.config.represent = lambda value, row: DIV(value if value else '-',_class='config', _id=str(row.id)+'.config')
    links = [lambda row: A(TAG.BUTTON('Get running time'), _href=URL("default","get_server_info",args=[row.id])),
             lambda row: A(TAG.BUTTON('Restart'), _href=URL("default","restart",args=[row.id])) if row.allow_managing else False,
             lambda row: A(TAG.BUTTON('Update addons'), _href=URL("default","update_addons",args=[row.id])) if row.allow_managing else False,
    ]
    grid = SQLFORM.grid(query,paginate=10, links=links, orderby='address', details=False, searchable=False)
    return dict(grid=grid)


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())

def connect(server_obj):
    address = server_obj.address
    passwd = server_obj.passwd
    username = server_obj.username
    port = int(server_obj.port)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(address, username=username, password=passwd, port=port)
    return ssh

@auth.requires_login()
def get_server_info():
    server_id = request.args[0]
    server_obj = db(db.servers.id == server_id).select()[0]
    ssh = connect(server_obj)
    try:
        stdin, stdout, stderr = ssh.exec_command("ps -eo etime,cmd | grep openerp-server")
        res = stdout.readlines()
        if res:
            res = [line for line in res if 'python' in line]
            for arg in res[0].split(' '):
                if arg:
                    running_time = arg
                    break
            server_obj.update(running_time=running_time)
            db(db.servers.id==server_id).update(running_time = running_time)
            session.error = False
            session.used_server = server_id
    except Exception, e:
        raise(e)
        session.error = True
    ssh.close()
    return redirect(URL('index'))

@auth.requires_login()
def restart():
    server_id = request.args[0]
    server_obj = db(db.servers.id == server_id).select()[0]
    ssh = connect(server_obj)
    try:
        stdin, stdout, stderr = ssh.exec_command("ps -eo pid,cmd | grep openerp-server")
        res = stdout.readlines()
        if res:
            res = [line for line in res if 'python' in line]
            for arg in res[0].split(' '):
                if arg:
                    pid = arg
                    break
            ssh.exec_command('kill -9 %s' % pid)
        ssh.exec_command('nohup python /opt/openerp/enapps/ea_server/openerp-server -c /etc/openerp-server-%s.conf &' % server_obj.config[0].lower())
    except:
        session.error = True
    ssh.close()
    return redirect(URL('index'))

@auth.requires_login()
def update_addons():
    server_id = request.args[0]
    server_obj = db(db.servers.id == server_id).select()[0]
    ssh = connect(server_obj)
    ssh.exec_command('nohup python /opt/openerp/enapps/addons//%s/update_modules.py &' % server_obj.config[0].lower())
    ssh.close()
    return redirect(URL('index'))

def update_config():
    id,column = request.post_vars.id.split('.')
    value = request.post_vars.value
    db(db.servers.id == id).update(**{'config':value})
    return value
