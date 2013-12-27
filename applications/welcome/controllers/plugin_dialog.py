from plugin_dialog import grid2

response.title=""
response.subtitle=""

def edit():
    """ returns edit view to be placed in a dialog """
    form = SQLFORM(db.plugin_dialog_customer, request.args[0])
    if form.process().accepted:
        response.js="refresh('customer')"
    else:
        response.js="opendialog()"

    return dict(form=form)

def grid():
    """ loads grid via ajax so it can be refreshed when it changes """
    
    action, table, id=request.args(0), request.args(1), request.args(2)

    if action in ["new", "edit"]:
        request.args=[id]
        response.view='plugin_dialog/edit.html'
        return edit()

    grid = SQLFORM.grid(query=db.plugin_dialog_customer,
                        **grid2.defaults1())
    grid2.dialogButtons(grid, ["new", "edit"])
    
    return dict(grid=grid)

def gridpage():
    """ contains multiple components. Each can be refreshed individually if data changes. """
    return dict()

def index():
    redirect(URL(f='gridpage.html'))