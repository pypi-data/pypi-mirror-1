# Release information about ObjectStateTracer

version = "0.1a0"

description = "Traces SQLObject and SQLAlcemy object modifications"

long_description = """The idea is to provide a modification history in a transparent way.

I'm experimenting with SQLObject right now. SQLAlchemy support is not in yet.

When it's enabled it intercepts __setattr__ and the .set() method and tracs the
modifications on it's own table.

It adds a method to the SQLObject instances called get_modification_history()
that will return a list of ObjectStateTrace instances.

This object has 4 key attributes:
* time: moment the modification happened
* column_name: it is the attribute changed in the SQLObject instance
* old_value: value before the change
* new_value: value after the change

To enable this extension add this to your config file:
objectstatetracer.on=True

To use it:
class YourClass(SQLObject)
    ....

from objectstatetracer.extension import register_class

register_class(YourClass)

And the instances of YourClass should be audited for changes.

I couldn't add the WidgetDescription of HistoryPanel (a datagrid that shows the
modifications), because it's far from being finished.

Check the tests for more info.

IT DOES NOT SUPPORT LAZY UPDATES YET

!!!HIGHLY EXPERIMENTAL!!!
Right now this may break your software and/or corrupt your data. 
Use at your own risk!.

"""

author = "Claudio Martinez"
email = "claudio.s.martinez@gmail.com"
license = "MIT"
