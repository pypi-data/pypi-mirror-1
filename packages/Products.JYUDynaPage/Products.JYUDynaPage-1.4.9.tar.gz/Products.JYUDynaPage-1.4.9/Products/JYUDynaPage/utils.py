# -*- coding:utf-8 -*-

# from zope.app.event.interfaces import IObjectModifiedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
import transaction

def updatePaths(ob, event):
    """ set parent path to empty reference fields """

    # Let's check if our DynaPage is in site root. If it is then we'll use DynaPages own UID
    # as portal root doesn't have UID.
    parent_obj = None
    
    try:
        
        # Because of portal_factory our object is initially created to a path like 
        # http://www.oursite.com/instance/testfolder/portal_factory/DynaPage/jyudynapage-200812110840
        # We need to bypass those extra folders to get the correct path.
        #
        # Although portal_factory is enabled for this context by default profiles, site admin might have
        # turned that off manually. Therefore we have if - else condition where we do the appropriate
        # actions for both cases.
        
        if 'portal_factory' in ob.absolute_url():
            parent_obj = ob.aq_parent.aq_parent.aq_parent
            parent_obj_uid = parent_obj.UID()

        else:
            parent_obj = ob.aq_parent
            parent_obj_uid = parent_obj.UID()


    # Here we can have exception if objects parent is the site root. If that's the case we set lists default 
    # reference to be the object itself.
    except AttributeError, e:

        parent_obj = ob
        parent_obj_uid = parent_obj.UID()

    # Here we set the actual paths for our content. We check if each of our lists already have existing
    # path. If they are empty we set the path to be our parent object.
    if not ob.getFirst_list_path():
        ob.setFirst_list_path(parent_obj.UID())
        transaction.savepoint()
        
    if not ob.getSecond_list_path():
        ob.setSecond_list_path(parent_obj_uid)
        transaction.savepoint()

    if not ob.getThird_list_path():
        ob.setThird_list_path(parent_obj_uid)
        transaction.savepoint()
        
    if not ob.getFourth_list_path():
        ob.setFourth_list_path(parent_obj_uid)
        transaction.savepoint()
