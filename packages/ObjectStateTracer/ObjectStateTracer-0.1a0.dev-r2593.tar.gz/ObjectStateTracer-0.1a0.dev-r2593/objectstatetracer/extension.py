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

from exceptions import *

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
        return # FIXME: This keeps happening during tests.
        raise Exception('Tried to start the OST extension twice')
    
    locked = True
    
    log.info('OST starting')
    
    init_classes()
    
    # start the helper controller
    if config.get("objectstatetracer.controller.on", False):
        cherrypy.root.objectstatetracer = HistoryController()
    
    # save original methods
    SQLObject._orig_set = SQLObject.set
    SQLObject._orig_setattr = SQLObject.__setattr__
    SQLObject._orig_SO_finishCreate = SQLObject._SO_finishCreate
    
    # add decorators
    SQLObject.set = audit_set(SQLObject.set)    
    SQLObject.__setattr__ = audit_setattr(SQLObject.__setattr__)
    SQLObject._SO_finishCreate = audit_create(SQLObject._SO_finishCreate)
    
    # add a new base on SQLObject:
    SQLObject.__bases__ = SQLObject.__bases__ + (SOOSTBase,)
    
    log.info('OST initialized')

def shutdown_extension():
    global locked
    if not locked:
        return
    
    log.info('OST stopping')
    
    # delete helper controller
    if config.get("objectstatetracer.controller.on", False):
        del cherrypy.root.objectstatetracer
    
    # reset original methods
    SQLObject.set = SQLObject._orig_set
    SQLObject.__setattr__ = SQLObject._orig_setattr
    SQLObject._SO_finishCreate = SQLObject._orig_SO_finishCreate
    del SQLObject._orig_set
    del SQLObject._orig_setattr
    del SQLObject._orig_SO_finishCreate
        
    # delete SOOSTBase from the bases
    bases = list(SQLObject.__bases__)
    bases.remove(SOOSTBase)
    SQLObject.__bases__ = tuple(bases)
    
    locked = False
    log.info('OST stopped')

def init_classes():
    from model import hub
    
    hub.begin()
    
    ObjectStateTrace.createTable(ifNotExists=True)
    TraceData.createTable(ifNotExists=True)
    RejectVote.createTable(ifNotExists=True)
    ApproveVote.createTable(ifNotExists=True)
    ObjectState.createTable(ifNotExists=True)
    
    hub.commit()
    hub.end()

def register_class(class_, auth_schema=None, force=False):
    """
    If no auth_schema is specified, only tracing will be enabled for the class
    """
    if locked:
        raise Exception('Registering a class is only possible at startup')
    
    if class_ in classes and not force:
        raise ClassAlreadyRegistered(class_)
    
    if class_ not in classes:
        classes.append(class_)
    
    if auth_schema:
        auth_schema.attach_class(class_)
    auth_schemas[class_] = auth_schema

