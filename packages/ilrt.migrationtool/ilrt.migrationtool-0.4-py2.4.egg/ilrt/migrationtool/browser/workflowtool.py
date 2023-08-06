from zope.interface import implements
from zope.component import getUtility
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize.compress import xhtml_compress
from plone.memoize.instance import memoize

from Products.CMFCore.utils import getToolByName

from Products.CMFCore.interfaces import ISiteRoot
from ilrt.migrationtool.browser.interfaces import IWorkflowMigrationView

class WorkflowMigrationView(BrowserView):
    """
    Migrates content from one workflow to another via a manually
    tailored mapping implemented as an adjunct to the site migration tool
    """

    implements(IWorkflowMigrationView)
    _template = ViewPageTemplateFile('templates/manage_workflow.pt')
    _workflows = None
    _mapping = {}
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.portal = getUtility(ISiteRoot)
        self.workflow_tool = getToolByName(self.portal,'portal_workflow')
        self.aok = 0
        self.tok = 0
        self.fok = 0

    def __call__(self):
        """ Handle the zmi manage form actions -
            set migration,
            set mapping
            or run migration
        """
        wf_from = self.request.get('wf_from',None)
        wf_to = self.request.get('wf_to',None)
        if wf_from or wf_to:
            out = self.setWorkflowMigration(wf_from, wf_to)
            if out:
                self.request['out'] = out
                
        states = self.request.get('state',[])
        if states:
            for record in states:
                self._mapping[record['from']] = record['to']

        if self.request.get('run_migration',''):
            self.resetMsgCounters()
            msg = self.transferObjectsState(wf_from, wf_to, self.getLocale())
            if msg:
                self.request['out'] = msg
            else:
                self.request['out'] = self.migrateMsg(wf_from, wf_to)
        return xhtml_compress(self._template())


    def resetMsgCounters(self):
        """ Reset the counters to zero """
        self.aok = 0
        self.tok = 0
        self.fok = 0
        return

    def migrateMsg(self, wf_from, wf_to):
        """ Generate the message of what the migration has done """
        msg = "You have migrated %s to %s" % (wf_from, wf_to)
        msg += " with %s successful transitions," % str(self.tok)
        msg += " %s failed transitions" % str(self.fok)
        msg += " and %s objects already in the right state" % str(self.aok)
        return msg

    def getLocale(self):
        """ Return a folder from a relative path
            Default to the whole portal
        """
        path = self.request.get('locale','/')
        obj = self.portal
        for part in path.split('/'):
            if part and hasattr(obj,part):
                obj = getattr(obj,part)
        return obj

    @memoize    
    def listWorkflows(self):
        """ Return a vocab of id,title dictionarys for the workflows available
        """
        vocab = []
        for wf in self.workflow_tool.items():
            vocab.append({'id':wf[0],'title':getattr(wf[1],'title',wf[0])}) 
        return vocab

    @memoize
    def setWorkflowMigration(self,wf_from,wf_to):
        """
        Set the worflows for the migration
        """
        out = "The workflows have been selected for mapping."
        if not wf_from or not wf_to:
            return "<h4>You must select a workflow from each dropdown</h4> \
                    <p>Please select from the 'from workflow' and 'to workflow' \
                    dropdowns and resubmit</p>"
        if wf_from == wf_to:
            return "<h4>You do not need to migrate a workflow to itself</h4> \
                    <p>Please change either the 'from workflow' or \
                    the 'to workflow' dropdown and resubmit"
        self._workflows = [None, None]
        for wf in self.workflow_tool.items():
            if wf_from == wf[0]:
                self._workflows[0] = wf[1]
            elif wf_to == wf[0]:
                self._workflows[1] = wf[1]
        if not self._workflows[0]:
            self._workflows = None
        return

    @memoize
    def getStates(self,wf,id='return vocab'):
        """ Return the states for a workflow as a vocab -
            or if given a state id then that state as a dictionary
        """
        workflow_folder = getattr(self.workflow_tool, wf, None)
        vocab = []
        if workflow_folder:
            state_folder = getattr(workflow_folder, 'states', None)
            if state_folder is not None:
                for state in state_folder.objectValues():
                    if state.id==id:
                        return {'id':state.id,'title':state.title}
                    vocab.append({'id':state.id,'title':state.title})
        if id == 'return vocab':
            return vocab
        else:
            return None

    @memoize
    def getTransitionStateMap(self,wf):
        """ Return a dictionary mapping the lists of transistions
            required for any possible change from one state to another
            for the supplied worflow id.
        """
        workflow_folder = getattr(self.workflow_tool, wf, None)
        from_trans = {}
        to_trans = {}
        transpath = {}
        if workflow_folder:
            trans_folder = getattr(workflow_folder, 'transitions', None)
            if trans_folder is not None:
                for trans in trans_folder.objectValues():
                    to_state = getattr(trans,'new_state_id','')
                    if to_trans.has_key(to_state):
                        to_trans[to_state].add(trans.getId())
                    else:
                        to_trans[to_state] = set([trans.getId(),])
                state_folder = getattr(workflow_folder, 'states', None)
                states = []
                for state in state_folder.objectValues():
                    from_trans[state.getId()] = set(getattr(state,'transitions',[]))
                    states.append(state.getId())
                orderedstates = states
                
                def findStateTrans(end):
                    """ Find a state and transistion that arrives at this
                        end state - ordered states has the from_state first
                        - Use to traverse down transitions needed
                    """
                    for start in orderedstates:
                        intersect = from_trans[start] & to_trans[end] 
                        if intersect:
                            return [start,intersect.pop()]
                    return [None,None]
                
                for from_state in states:
                    orderedstates.remove(from_state)
                    orderedstates.insert(0,from_state)
                    for to_state in states:
                        if from_state != to_state:
                            fromto = from_state + '>' + to_state
                            common = from_trans[from_state] & to_trans[to_state]
                            if common:
                                transpath[fromto] = [common.pop(),]
                            else:
                                end = to_state
                                start = ''
                                depth = 0
                                transpath[fromto] = []
                                while from_state != start:
                                    depth += 1
                                    start, trans = findStateTrans(end)
                                    if not start or depth>10:
                                        raise "The workflow %wf is broken in that \
                                               it has states that cannot be transitioned \
                                               between from any other states" % wf
                                    transpath[fromto].append(trans)
                                    end = start
                                transpath[fromto].reverse()
        return transpath
        
    @memoize
    def getWorkflowMigration(self):
        """ Return the workflow [from,to] list """
        return self._workflows

    @memoize
    def getStateMapping(self):
        """ Return the mapping of states """
        return self._mapping

    def _runTransfer(self, wf_from, wf_to, mapping, container=None):
        """ Run a transfer directly rather than via the zmi manage forms """
        self._mapping = mapping
        if not container:
            container = self.portal
        msg = self.setWorkflowMigration(wf_from, wf_to)
        if not msg:
            self.resetMsgCounters()            
            msg = self.transferObjectsState(wf_from, wf_to, container)
        if not msg:
            msg = self.migrateMsg(wf_from, wf_to)
        return msg
        

    def transferObjectsState(self, wf_from, wf_to, container):
        """ Moves objects from whatever state they were in within
            one workflow - to the map specified state in another
        """
        objs = container.objectValues()
        workflow = self.workflow_tool.getWorkflowById(wf_to)
        comment = "ilrt.migrationtool migrated state from %s to %s" % \
                                                         (wf_from,wf_to)
        transmap = self.getTransitionStateMap(wf_to)
        if not transmap:
            return 'This workflow has no transitions so must be single state'
        for obj in objs:
            from_state = self.workflow_tool.getInfoFor(obj,
                                     'review_state', wf_id=wf_from)
            if from_state:
                to_state = self._mapping.get(from_state,None)
                if to_state:
                    current_state = self.workflow_tool.getInfoFor(obj,
                                                'review_state', wf_id=wf_to)
                    if current_state != to_state:
                        for trans in transmap[current_state + '>' + to_state]:
                            if self._tryTransition(workflow=workflow,
                                                obj=obj,
                                                transition=trans,
                                                comment=comment):
                                self.tok += 1
                            else:
                                self.fok += 1
                            if self.workflow_tool.getInfoFor(obj,
                                    'review_state', wf_id=wf_to) == current_state:
                                raise "Unable to translate %s to %s" % \
                                       ('/'.join(obj.getPhysicalPath()), to_state)
                    else:
                        self.aok += 1
            if obj.isPrincipiaFolderish:
                self.transferObjectsState(wf_from, wf_to, obj)
        return 

    def _tryTransition(self, workflow, obj, transition, comment):
        """Try to perform a workflow transition on the object,
           returns true on success
        """
        if workflow:
            tdef = workflow.transitions.get(transition, None)
            if tdef:
                try:
                    workflow._executeTransition(obj,
                                             tdef=tdef,
                                             kwargs={'comment': comment})
                    catalog = getToolByName(self.portal, 'portal_catalog')
                    catalog.reindexObject(obj,
                             idxs=['review_state','allowedRolesAndUsers'])
                    return True
                except:
                    return False
        return False
    
