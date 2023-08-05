import logging

import cherrypy

import dispatch

from turbogears import config

from decorators import *

from registry import *

from model import *

from sqlobject import SQLObject

from auth import *

from base import *

from state import *

from controllers import HistoryController

log = logging.getLogger('objectstatetracer')

orig_getattr = None
orig_set = None
locked = False

def start_extension():
    global locked
    
    if not config.get("objectstatetracer.on", False):
        return
    
    if locked:
        # why would this happen? happened to me on tests
        return
    locked = True
    
    log.info('OST starting')
    
    init_classes()
    
    # start the helper controller
    cherrypy.root.objectstatetracer = HistoryController()
    
    # save original methods
    SQLObject._orig_set = SQLObject.set
    SQLObject._orig_setattr = SQLObject.__setattr__
    
    # add decorators
    SQLObject.set = audit_set(SQLObject.set)    
    SQLObject.__setattr__ = audit_setattr(SQLObject.__setattr__)
    
    # add a new base on SQLObject:
    SQLObject.__bases__ = SQLObject.__bases__ + (SOOSTBase,)
    
    log.info('OST intialised')

def stop_extension():
    global locked
    if not locked:
        return
    
    # delete helper controller
    del cherrypy.root.objectstatetracer
    
    # reset original methods
    SQLObject.set = SQLObject._orig_set
    SQLObject.__setattr__ = SQLObject._orig_setattr
    del SQLObject._orig_set
    del SQLObject._orig_setattr
        
    # delete SOOSTBase from the bases
    bases = list(SQLObject.__bases__)
    bases.remove(SOOSTBase)
    SQLObject.__bases__ = tuple(bases)
    
    locked = False

def init_classes():
    ObjectStateTrace.createTable(ifNotExists=True)
    RejectVote.createTable(ifNotExists=True)
    ApproveVote.createTable(ifNotExists=True)
    ObjectState.createTable(ifNotExists=True)

def register_class(class_, auth_schema=None):
    """
    If no auth_schema is specified, only tracing will be enabled for the class
    """
    if locked:
        raise 'Registering a class is only possible at startup'
    
    classes.append(class_)
    if auth_schema:
        auth_schema.attach_class(class_)
    auth_schemas[class_] = auth_schema

