#Some values we use as default, user will be able to change them afterwards via the GUI
EXPORT_FOLDER_NAME='importtool_exports_%s' # We will want to make this date dependant to allow multiple exports
SQLMONGER_FILE_NAME='database.sqlite' # a descriptive db name will hurt no one
MONGER_FILES_FOLDER='external_files' #A container for files of ATFile objects.

#from Products.mongerorm import SQLMonger
from mongerorm import SQLMonger
from Products.CMFCore.utils import UniqueObject, getToolByName
from OFS.SimpleItem import SimpleItem
from Globals import InitializeClass
import re, transaction, AccessControl, glob, os, sys
from threading import Thread

from ZPublisher.HTTPRequest import HTTPRequest
from ZPublisher.HTTPResponse import HTTPResponse
from ZPublisher.BaseRequest import RequestContainer



#exported_files_path = "/tmp/"
#monger = SQLMonger(exported_files_path + SQLMONGER_FILE_NAME)
#mongerfiles_path = exported_files_path + 'mongerfiles/'



def stringize(o):
    return repr(o)

dublin_core_accessors = {
    'contributors':'Contributors',
    'created': 'CreationDate',
    'creators':'Creators',
    'description':'Description',
    'effective': 'EffectiveDate',
    'expires': 'ExpirationDate',
    'modified': 'ModificationDate',
    'publisher': 'Publisher',
    'subject': 'Subject',
    'title': 'Title',
    'rights': 'Rights',
    'language': 'Language',
    'format': 'Format'
}

topic_dict = {  'ATBooleanCriterion': ('bool', 'setBool'),
                'ATPortalTypeCriterion': ('value', 'setValue'),
                'ATSelectionCriterion': ('value','setValue'),
                'ATSortCriterion': ('reversed','setReversed'),
                'ATSimpleStringCriterion': ('value','setValue'),
                'ATPathCriterion': ('value','setValue')}

global CURRENT_THREAD_HANDLER, MONGER_HANDLER, MONGER_FILES_PATH
CURRENT_THREAD_HANDLER=None
MONGER_HANDLER=None
MONGER_FILES_PATH=None


class ImportTool(UniqueObject, SimpleItem):
    """
    Import tool: This tool contains all the magic to import from a exporfolder
    """
    id = 'Massive SQL Content Import Tool'
    meta_type= 'Massive SQL Content Import Tool'
    plone_tool = 1
    import_root_path = "/"
    from_path = "/"
    current_import = None
    special_attributes = {  'owner': 'setOwner',
                            '_propertyMap': 'setPropertyMap',
                            'propertyItems': 'setPropertyItems',
                            'workflow_state': 'setWorkflowState',
                            'workflow_id': 'setWorkflowId',
                            'portal_type': 'setPortalType',
                            'meta_type': 'setMetaType',
                            'panelsConfig': 'setPanelsConfig',
                            'showOnFrontpage': 'setShowOnFrontpage'}

    def getImportThread(self):
        return CURRENT_THREAD_HANDLER

    def setImportThread(self, thread_handler):
        global CURRENT_THREAD_HANDLER
        CURRENT_THREAD_HANDLER = thread_handler

    def getExportsPath(self):
        ihome = os.getenv('INSTANCE_HOME')
        sql_xptr_home = os.path.join(ihome,'var','sql_exporter')
        if not os.path.exists(sql_xptr_home):
            os.makedirs(sql_xptr_home)
        return sql_xptr_home

    def getExports(self):
        """
        Returns a list of the available exports, we can not know for sure, but
        we do a guess that is better than having the user guessing
        """
        sql_xptr_home = self.getExportsPath()
        exports_list = []
        if os.path.isdir(sql_xptr_home):
            exports_list = glob.glob(os.path.join(sql_xptr_home, EXPORT_FOLDER_NAME % "*"))
            #double check, we expect the returned results to be folders
            exports_list= [os.path.split(afolder)[-1] for afolder in exports_list if os.path.isdir(afolder)]
        return exports_list

    def start_import(self, to_import):
        new_thread_started = False
        if (not self.getImportThread()) or (self.getImportThread() and (not self.getImportThread().isAlive())):
            self.current_import = to_import
            global MONGER_HANDLER, MONGER_FILES_PATH
            export_folder=os.path.join(self.getExportsPath(), to_import)
            sys.path.append(self.getExportsPath())
            import_info = __import__(to_import, globals, locals, ['info'])
            sys.path.pop(-1)
            self.from_path = import_info.info.from_path
            MONGER_FILES_PATH=os.path.join(export_folder, MONGER_FILES_FOLDER)
            MONGER_HANDLER=SQLMonger(os.path.join(export_folder, SQLMONGER_FILE_NAME))
            #self.setImportThread(Thread(target=self.run))
            #self.getImportThread().start()
            self.run()
            new_thread_started = True
        return new_thread_started

    def cancel_import(self):
        self.getImportThread()

    #------------------------------------------------------------------------------------------------
    def setOwner(self, users_tool, SQLItem, plone_item):
        """
        Give ownership to the original user (if the user exists), some objects
        do not have exported owner for strange reasons, just in case we check
        """
        if 'owner' in SQLItem.keys():
            plone_item.changeOwnership(users_tool.getUser(SQLItem.owner))

    def setPropertyMap(self, users_tool,  SQLItem, plone_item):
        """
        Setting of all the properties that the original object had.
        BEWARE: Some properties, such as layout, might make your object behave
        in weird ways if not all the content has been imported or the property
        is deprecated.
        """
        if not SQLItem._propertyMap:
            return
        for each_prop in SQLItem._propertyMap:
            property_id = each_prop.get('id')
            a_value = dict(SQLItem.propertyItems).get(property_id,"")
            if not plone_item.hasProperty(property_id):
                plone_item.manage_addProperty(id=property_id, value=a_value, type=each_prop.get('type'))
            else:
                plone_item._updateProperty(id=property_id, value=a_value)

    def notYetImplementedMethod(self, users_tool, SQLItem, plone_item):
        """
        I prefer an empty callback to a bunch of exceptions so this is only
        here for consistence
        """
        pass

    setPropertyItems = notYetImplementedMethod

    def setWorkflowState(self, users_tool, SQLItem, plone_item):
        if not (SQLItem.workflow_state and SQLItem.workflow_id):
            return

        portal_workflow = getToolByName(plone_item, 'portal_workflow')
        if portal_workflow.getChainFor(plone_item) != SQLItem.workflow_id:
            portal_workflow.setChainForPortalTypes(pt_names=[plone_item.portal_type],
                                                    chain=SQLItem.workflow_id)
        visible_statuses={'visible':'show',
                          'members_only':'publish_for_members',
                          'pending':'submit',
                          'private': None,
                          'published':'publish'}

        workflow_state = visible_statuses[SQLItem.workflow_state]
        hide_actions = {    'member_workflow' : 'hide',
                            'simple_publication_workflow': 'retract' }
        statuses= [a_status for a_status in hide_actions.keys() if a_status in SQLItem.workflow_id]
        try:
            if statuses and (SQLItem.workflow_state in visible_statuses.keys()):
                portal_workflow.doActionFor(plone_item, hide_actions[statuses[0]])
                if visible_statuses.get(SQLItem.workflow_state, None) is not None:
                    portal_workflow.doActionFor(plone_item, workflow_state )
            else:
                portal_workflow.setStatusOf(SQLItem.workflow_id, plone_item, SQLItem.workflow_state)
        except:
            pass

    setWorkflowId = notYetImplementedMethod

    setPortalType = notYetImplementedMethod

    setMetaType = notYetImplementedMethod


    def topic_factory(self, SQLItem, folder):
        """
        Criterions, even if represented by objects, need to be created using methods
        other than the regular object invoke factory
        """
        if SQLItem.portal_type in topic_dict.keys():
            if SQLItem.id in folder.objectIds():
                folder.deleteCriterion(SQLItem.id)
            new_crit = folder.addCriterion(SQLItem.field, SQLItem.portal_type)
            try:
                getattr(new_crit,topic_dict.get(SQLItem.portal_type)[1])(
                        getattr(SQLItem, topic_dict.get(SQLItem.portal_type)[0]))
            except:
                pass


    def workflow_object(self, SQLItem, portal_object):
        try:
            plone_item = portal_object.restrictedTraverse(SQLItem.url.replace('%20', ' '))
            self.setWorkflowState(SQLItem, plone_item)
        except:
            print "Faulted trying to set workflow for ", SQLItem.url
            pass
        for child in SQLItem.childs():
            self.workflow_object(child, portal_object)

    def relate_runner(self, folder):
        """
        This will run the creator of relation between objects, you want to be able to run
        this separately since relations have to be created once all objects exist.
        """
        for bicho in MONGER_HANDLER.load_many(self.import_root_path):
            self.relate_object(bicho, folder)
        transaction.commit()

    def folder_fill(self, folder, acl_users):
        for bicho in MONGER_HANDLER.load_many(""):
            self.create_object(bicho, folder, acl_users)
        transaction.commit()

    def relate_object(self, SQLItem, folder):
        portal_types = getToolByName(folder,'portal_types')
        portal_object = getToolByName(folder,'portal_url').getPortalObject()
        if SQLItem.portal_type not in portal_types.keys():
            return
        if SQLItem.id not in folder.objectIds():
            return
        for field in folder[SQLItem.id].schema.fields():
            if field.type == 'reference' and field.getName()!= 'relatedItems':
                create_relation(SQLItem, folder[SQLItem.id], field, portal_object)
        for child in SQLItem.childs():
            relate_object(child, folder[SQLItem.id])

    def create_relation(self, SQLItem, plone_item, field, portal_object):
        """
        Create the relations between objects that have relation (du'h) fields
        """
        relation_list = []
        obj_repr_pattern = re.compile(r'\<.* at (%s.*)\>' % self.import_root_path)
        relations_from_sqlitem = getattr(SQLItem, field.getName())
        if isinstance(relations_from_sqlitem, str):
            relations_from_sqlitem = [relations_from_sqlitem]

        try:
            relations_from_sqlitem = iter(relations_from_sqlitem)
        except TypeError:
            # this is not an interable, lest do nothing whith this
            return

        for item in relations_from_sqlitem:
            match = obj_repr_pattern.search(item)
            if match and match.groups():
                print 'INSTEAD of %s will use' % (item),
                item = match.groups()[0]
                print item
            if item.startswith('%s/' % self.import_root_path):
                item = item[1+len(self.import_root_path):]
            try:
                related_item = portal_object.restrictedTraverse(item.replace('%20', ' '))
            except:
                continue
            if related_item:
                try:
                    related_item = related_item.UID()
                except AttributeError:
                    continue
            relation_list.append(related_item)

        getattr(plone_item, field.mutator)(relation_list)

    def cleanup_item_before_filling(self, plone_item):
        if plone_item.meta_type == 'FormFolder':
            # We are going to remove the default fields that are created when
            # instancing a FormFolder
            to_remove = set(['replyto','topic','comments']).intersection(plone_item.objectIds())
            if to_remove:
                plone_item.manage_delObjects(list(to_remove))

    def create_newsletter_susbcriber(self, SQLItem, folder):
        """
        PloneGazette newsletter subscribers, even though they are/where stored as elements
        are only created correctly trough Gazette proper subscription methods.
        """
        #Ok, I really can't remember in which case this can happen, but trust me, it can
        if folder.portal_type == 'NewsletterTheme':
            NLProvider = folder
        else:
            NLProvider = folder.aq_parent

        if NLProvider.portal_type ==  'NewsletterTheme':

            if not NLProvider.alreadySubscriber(SQLItem.title):
                subscriber = NLProvider.createSubscriberObject(SQLItem.id)
                if 'active' in dir(SQLItem) or 'active' in SQLItem._extra_attrs.keys():
                    active = SQLItem.active
                else:
                    # The exporter failed to set this, set default True
                    active = True
                subscriber.edit(format=SQLItem.format,
                                active=active,
                                email=SQLItem.title)
                NLProvider._subscribersCount += 1

    def create_object(self, SQLItem, folder, acl_users):
        """
        The base object creation logic, this will call all necessary helper methods that create
        special types or set special values
        """
        plone_item_id = SQLItem.id
        if (SQLItem.portal_type is None) or ('folder' in SQLItem.portal_type.lower()):
            print "%s %s %s" % (SQLItem.url,plone_item_id,SQLItem.portal_type)
        portal_types = getToolByName(folder,'portal_types')

        if SQLItem.portal_type not in portal_types.keys():
            #We Would like to create these types, but we have not the required products
            return

        if folder.portal_type == 'Topic':
            #This means that we are almost certainly a Topic criteria
            #Topic criterias have their own way of being created
            self.topic_factory(SQLItem, folder)
            return

        if plone_item_id not in folder.objectIds():
            if (SQLItem.title == 'Member profiles'):
                return

            if  (SQLItem.portal_type in ['Subscriber']):
                self.create_newsletter_subscriber(SQLItem, folder)
                return

            try:
                plone_item_id = folder.invokeFactory(SQLItem.portal_type, id=plone_item_id)
            except KeyError, e:
                print "******* KEY ERROR *************\n"
            except (AccessControl.unauthorized.Unauthorized, ValueError), e:
                #Two things can be the trigger for Unauthorized at this point:
                # * The containing we should have explicitly allowed this type
                #  in the containing folder
                # * This item can not be created with a simple invokeFactory
                this_type = portal_types[folder.portal_type]
                if this_type.filter_content_types:
                    this_type_types = this_type.allowed_content_types
                    this_type.allowed_content_types = this_type_types + (SQLItem.portal_type, )
                    plone_item_id = folder.invokeFactory(SQLItem.portal_type, id=plone_item_id)
                else:
                    try:
                        portal_types.constructContent(SQLItem.portal_type, folder, plone_item_id)
                    except:
                        pass
            except Exception, e:
                #Really, this is a really long process, we better continue no mather what
                #TODO: Add a logging system for these errors.
                pass
            else:
                self.cleanup_item_before_filling(folder[plone_item_id])

        #We managed to create the item, now lets set some attributes
        plone_item = folder[plone_item_id]

        #First, the main things, the dublin core attrs.
        for core_attr in dublin_core_accessors:
            try:
                getattr(plone_item, 'set' + dublin_core_accessors[core_attr])(getattr(SQLItem, core_attr))
            except Exception, e:
                if core_attr == "publisher":
                    continue

        attributes =  [a_key for a_key in SQLItem.keys() if a_key
                not in dublin_core_accessors.keys() and a_key
                not in self.special_attributes.keys()]

        for attribute in attributes:
            try:
                if attribute == 'id': #We DO NOT want to change the object's id
                    continue
                #Taking the field from the schema is much easier than just guessing teh accessors
                new_attr = plone_item.schema.get(attribute, None)

                if new_attr:
                    if (new_attr.accessor not in dublin_core_accessors.keys()) and (new_attr.type not in ['reference']):
                        if attribute in ('picture', 'image', 'file'):
                            filepath,filename = getattr(SQLItem, attribute)
                            if filepath:
                                try:
                                    mongerfile = open(os.path.join(MONGER_FILES_PATH,str(filepath)), 'r')
                                    getattr(plone_item, new_attr.mutator)(mongerfile)
                                    mongerfile.close()
                                    if hasattr(new_attr,'setFilename'):
                                        new_attr.setFilename(plone_item,filename)
                                except:
                                    pass
                                else:
                                    # We uploaded the binary file. Plone may have mistaken
                                    # the file type and wrongly overided format,
                                    # so we reset it with sql data
                                    try:
                                        if plone_item.Format() != SQLItem.format:
                                            plone_item.setFormat(SQLItem.format)
                                    except:
                                        pass
                        else:
                            getattr(plone_item, new_attr.mutator)(getattr(SQLItem, attribute))
            except Exception, e:
                #TODO: Make a less general error ignoring
                continue
        for special_attribute in self.special_attributes.keys():
            try:
                getattr(self, self.special_attributes[special_attribute])(acl_users,SQLItem, plone_item)
            except AttributeError, e:
                continue
        plone_item.indexObject()
        self.populate_folderish(SQLItem, plone_item, acl_users)

    def populate_folderish(self, SQLItem, plone_item, acl_users):
        """
        Invoque object creation for each child on the export SQL if present
        """
        if not SQLItem.childs():
            return None
        time_to_commit = 0 #Yea a flag, I know, but this is useful on folders of >1000 objs
        for child in SQLItem.childs():
            time_to_commit += 1
            self.create_object(child, plone_item, acl_users)
            if time_to_commit > 18 :#completely arbitrary number
                transaction.commit()
                time_to_commit = 0
        transaction.commit()

    def fix_recurse_on_topics(self):
        topics = self.aq_parent.portal_catalog(portal_type="Topic")
        for tbrain in topics:
            topic = tbrain.getObject()
            if 'crit__path_ATPathCriterion' not in topic.objectIds():
                continue
            locatie = topic.crit__path_ATPathCriterion
            SQLItem = MONGER_HANDLER.load(locatie.absolute_url_path())
            print SQLItem, repr(SQLItem.recurse), type(SQLItem.recurse)
            locatie.getField('recurse').set(locatie,SQLItem.recurse)

    def subscribers_fixer(self):
        newslettertheme ,= self.portal_catalog(portal_type="NewsletterTheme")
        newslettertheme = newslettertheme.getObject()
        for subs_id in unactive_subscribers:
            try:
                subscriber = newslettertheme.getSubscriberById(subs_id)
            except:
                continue
            else:
                if subscriber is not None:
                    subscriber.edit(format=subscriber.format,
                                    active=False,
                                    email=subscriber.email)

    def run(self):
        if not self.current_import:
            return
        #from Zope import DB
        #conn = DB.open()
        #root = conn.root()
        #app  = root['Application']
        #ctx = self.getContext(app)
        print "running"
        acl_users = getToolByName(self,'acl_users')
        folder = self.restrictedTraverse(self.import_root_path.encode("utf-8"))
        self.folder_fill(folder, acl_users)
        print "finished"
        transaction.commit()
        #conn.close()
        #self.crawl_folders(self)

    def testrun(self):
        portal_object = getToolByName(self,'portal_url').getPortalObject()
        for bicho in MONGER_HANDLER.load_many(self.import_root_path):
            workflow_object(self, bicho, portal_object)
        transaction.commit()

    def getContext(self, app):
        resp = HTTPResponse(stdout=None)
        env = {
            'SERVER_NAME':'localhost',
            'SERVER_PORT':'8080',
            'REQUEST_METHOD':'GET'
            }
        req = HTTPRequest(None, env, resp)
        return app.__of__(RequestContainer(REQUEST = req))

InitializeClass(ImportTool)


def fix_folder_workflow(self):
    folder_reset_workflow(self)

def folder_reset_workflow(folder):
    print 'Reseting workflow to %s' % folder.absolute_url()
    folderishs = []
    if folder.meta_type in ['NewsletterTheme','Newsletter']:
        subitems = folder.objectValues()
    else:
        try:
            subitems = folder.listFolderContents()
        except Exception, e:
            return
    for obj in subitems:
        if obj.id.startswith('portal_') or 'catalog' in obj.meta_type.lower() or obj.id == 'subscribers':
            print 'skipping %s' % obj.absolute_url()
            continue
        if 'catalog' in obj.absolute_url():
            continue
        if obj.isPrincipiaFolderish and not 'topic' in obj.meta_type.lower():
            folderishs.append(obj)
        try:
            workflow_policy = portal_workflow.getChainFor(obj)
            #obj_state = portal_workflow.getInfoFor(obj,'review_state')
            obj_state = MONGER_HANDLER.load(obj.absolute_url_path()).workflow_state
            if obj_state is None:
                print '\n\n\t\tWTF none',obj.absolute_url_path()
        except Exception, e:
            print 'no workflow defined for %s, error: %s' % (obj.absolute_url(),e)
            continue
        if "member_workflow" in workflow_policy:
            try:
                portal_workflow.doActionFor(obj, 'hide')
            except:
                pass # it was alread private
            if obj_state in visible_statuses.keys():
                portal_workflow.doActionFor(obj, visible_statuses[obj_state])
        elif "simple_publication_workflow" in workflow_policy:
            try:
                portal_workflow.doActionFor(obj, 'retract')
            except:
                pass # It was already private
            if obj_state in visible_statuses:
                portal_workflow.doActionFor(obj, visible_statuses[obj_state])
        else:
            print 'MERDE',obj.absolute_url(),obj_state,workflow_policy
    transaction.commit()
    for f in folderishs:
        folder_reset_workflow(f)
