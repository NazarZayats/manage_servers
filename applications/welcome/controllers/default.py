# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    response.flash = T("Welcome to Server's Manager")
    #return auth.wiki()
    servers = db(db.servers).select(orderby="id")
    return dict(servers=servers)


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

@auth.requires_login()
def create():
    #form = SQLFORM(db.servers)
    #return dict(form=form)
    crud.messages.submit_button = "Create"
    form = crud.create(db.servers, next="index")

    return dict(form=form)

@auth.requires_login()
def get_server_info():
    import paramiko
    server_id = request.args[0]
    server_obj = db(db.servers.id == server_id).select()[0]
    address = server_obj.address
    passwd = server_obj.passwd
    service_name = server_obj.service_name
    username = server_obj.username
    port = int(server_obj.port)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(address, username=username, password=passwd, port=port)
    stdin, stdout, stderr = ssh.exec_command("ps -eo etime,cmd | grep %s" % service_name)
    res = stdout.readlines()
    if res:
        res = [line for line in res if 'python' in line]
        print res
        running_time = res[0][:11]
        print running_time
        server_obj.update(running_time=running_time)
        db(db.servers.id==server_id).update(running_time = running_time)
    return redirect(URL('index'))
