# Copyright (c) 2004-2006 by Klein & Partner KEG, Austria
#
# BSD-like licence, see LICENCE.txt
#

from zExceptions import BadRequest
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import manage_addTool
from Products.CMFCore.DirectoryView import addDirectoryViews
from Products.ExternalMethod.ExternalMethod import ExternalMethod
from Products.Archetypes.atapi import listTypes
from Products.Archetypes.Extensions.utils import install_subskin
from Products.Archetypes.Extensions.utils import installTypes
from Products.ATVocabularyManager.config import *
from Products.Archetypes.public import process_types, listTypes


from StringIO import StringIO
import sys

def install(self):
    out = StringIO()
    portal=getToolByName(self,'portal_url').getPortalObject()

    install_dependencies(self, out)

    classes=listTypes(PROJECTNAME)
    installTypes(self, out,
                 classes,
                 PROJECTNAME)

    print >> out, "Successfully installed %s." % PROJECTNAME

    install_subskin(self,out,GLOBALS)

    # remove workflow from vocabulary types

    print >> out, 'Removing workflow from:'
    portal_workflow = getToolByName(self, 'portal_workflow')
    for cl in classes:
        type = cl.get('portal_type')
        print >> out, 'type: %s' % type
        portal_workflow.setChainForPortalTypes([type], '')

    # register folderish classes in use_folder_contents

    props=self.portal_properties.site_properties
    use_folder_tabs=list(props.use_folder_tabs)
    print >> out, 'adding classes to use_folder_tabs:'
    for cl in classes:
        if cl['klass'].isPrincipiaFolderish:
            print >> out, 'type:', cl['klass'].portal_type
            use_folder_tabs.append(cl['klass'].portal_type)

    props.use_folder_tabs=tuple(use_folder_tabs)

    # enable types in portal_factory
    pf_tool = getToolByName(self, 'portal_factory')
    pf_types = pf_tool.getFactoryTypes().keys()
    for cl in classes:
        type_name = cl.get('portal_type')
        if type_name not in pf_types:
            pf_types.append(type_name)
    pf_tool.manage_setPortalFactoryTypes(listOfTypeIds=pf_types)

    try:
        portal.manage_addProduct[PROJECTNAME].manage_addTool(TOOL_META)
    except BadRequest, e:
        # if there is an object with the id of the tool,
        # we'll get a BadRequest Error which we will silently ignore.
        pass

    # set title of tool:
    tool=getToolByName(self, TOOL_NAME)
    tool.title=TOOL_TITLE

    # register tool in control panel
    portal_control_panel=getToolByName(self,'portal_controlpanel',None)
    portal_control_panel.registerConfiglet( TOOL_NAME #id of your Product
        , TOOL_TITLE # Title of your Product
        , 'string:${portal_url}/%s/' % TOOL_NAME
        , 'python:True'   # a condition
        , 'Manage portal' # access permission
        , 'Products'      # section to which the configlet should be added: (Plone,Products,Members)
        , True            # visibility
        , '%sID' % TOOL_META
        , 'atvm_icon.png' # icon in control_panel
        , 'Use it to define dynamic vocabularies.'
        , None
        )

    # dont allow tool listed as content in navtree

    mtntl = list(self.portal_properties.navtree_properties.metaTypesNotToList)
    if not TOOL_META in mtntl:
        mtntl.append(TOOL_META)
        self.portal_properties.navtree_properties._p_changed=1
        self.portal_properties.navtree_properties.metaTypesNotToList=tuple(mtntl)

    # we dont want to find this types in search!
    tns  = list(self.portal_properties.site_properties.types_not_searched )
    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)
    for ctype in content_types:
        ctype = ctype.portal_type
        if not ctype in tns:
            tns.append(ctype)
    self.portal_properties.site_properties._p_changed = 1
    self.portal_properties.site_properties.types_not_searched = tns

    # add metadata-column to portal_catalog
    catalog = getToolByName(portal, 'uid_catalog')
    idxName = 'getTermKeyPath'

    if idxName not in catalog.schema():
        catalog.addColumn(idxName)
        #XXX remove it in uninstall

    if idxName not in catalog.indexes():
        catalog.addIndex(idxName, 'KeywordIndex')
        #XXX remove it in uninstall

    return out.getvalue()

def uninstall(self):
    out = StringIO()
    classes=listTypes(PROJECTNAME)

    #unregister folderish classes in use_folder_contents
    props=getToolByName(self,'portal_properties').site_properties
    use_folder_tabs=list(props.use_folder_tabs)
    print >> out, 'removing classes from use_folder_tabs:'
    for cl in classes:
        print >> out,  'type:', cl['klass'].portal_type
        if cl['klass'].isPrincipiaFolderish and not cl['klass'].portal_type in []:
            if cl['klass'].portal_type in use_folder_tabs:
                use_folder_tabs.remove(cl['klass'].portal_type)

    props.use_folder_tabs=tuple(use_folder_tabs)
    if TOOL_META in self.portal_properties.navtree_properties.metaTypesNotToList:
        self.portal_properties.navtree_properties._p_changed=1
        mtntl = list(self.portal_properties.navtree_properties.metaTypesNotToList)
        mtntl.remove(TOOL_META)
        self.portal_properties.navtree_properties.metaTypesNotToList = tuple(mtntl)

    # unregister tool in control panel
    portal_controlpanel=getToolByName(self, 'portal_controlpanel')
    portal_controlpanel.unregisterConfiglet(TOOL_NAME)

    return out.getvalue()


def install_dependencies(self, out):
    print >> out, '%s depends on %s, try to auto-install.' % (PROJECTNAME,','.join(DEPENDENCIES))
    qi = getToolByName(self,'portal_quickinstaller')
    qi.installProducts(DEPENDENCIES, stoponerror=1)
