from gluon.contrib import populate

if plugins.dialog.DEBUG!=False:
    plugins.dialog.DEBUG=True
if plugins.dialog.MODEL!=False:
    plugins.dialog.MODEL=True

if plugins.dialog.MODEL:
    db.define_table('plugin_dialog_customer',
            Field('title', requires=IS_IN_SET(['Mr', 'Mrs', 'Ms'], zero=None)),
            Field('name', requires=[IS_NOT_EMPTY()]),
            Field('address1'),
            Field('address2'),
            Field('address3'),
            Field('town'),
            Field('county'))

    if db(db.plugin_dialog_customer.id>0).count()==0:
        populate.populate(db.plugin_dialog_customer,50)