"""
simple workflow engine refactored from ore.workflow
to minimize dependencies.
"""

from interfaces import MANUAL, AUTOMATIC, SYSTEM
import interfaces

from zope import interface
from zope.event import notify

from zope import component
from zope.component.interfaces import ObjectEvent
from zope.lifecycleevent import ObjectModifiedEvent

from StringIO import StringIO

def NullCondition(wf, context):
    return True

def NullAction(wf, context):
    pass

def nullCheckPermission(permission, principal_id):
    return True

class Transition(object):

    def __init__(self, transition_id, title, source, destination,
                 condition=NullCondition,
                 action=NullAction,
                 trigger=MANUAL,
                 permission=None,
                 order=0,
                 **user_data):
        self.transition_id = transition_id
        self.title = title
        self.source = source
        self.destination = destination
        self.condition = condition
        self.action = action
        self.trigger = trigger
        self.permission = permission
        self.order = order
        self.user_data = user_data
        
    def __cmp__(self, other):
        return cmp(self.order, other.order)

class Workflow( object ):
    
    interface.implements(interfaces.IWorkflow)
    
    def __init__(self, transitions):
        self.refresh(transitions)

    def _register(self, transition):
        transitions = self._sources.setdefault(transition.source, {})
        transitions[transition.transition_id] = transition
        self._id_transitions[transition.transition_id] = transition

    def refresh(self, transitions):
        self._sources = {}
        self._id_transitions = {}
        for transition in transitions:
            self._register(transition)
        self._p_changed = True
        
    def getTransitions(self, source):
        try:
            return self._sources[source].values()
        except KeyError:
            return []
        
    def getTransition(self, source, transition_id):
        transition = self._id_transitions[transition_id]
        if transition.source != source:
            raise interfaces.InvalidTransitionError
        return transition

    def getTransitionById(self, transition_id):
        return self._id_transitions[transition_id]

    def __call__( self, context ):
        return self

    def dot( self ):
        """
        fancier export workflow as dot,

        transition colors
        
         - automatic triggers in green
         - system triggers in yellow if no conditions
         - system triggers in blue if conditional
         - manual triggers in red

        state colors
        
         - end states in red         
        """
        io = StringIO()
        states = set()
        end_states = set()
        print >> io, "digraph workflow {"

        for state, transitions in self._sources.items():
            states.add( state )
            for tid, t in transitions.items():
                option = []
                states.add(  t.destination )
                if t.destination not in self._sources:
                    end_states.add( t.destination )
                if t.trigger is AUTOMATIC:
                    option.append( 'color=green' )
                elif t.trigger is SYSTEM:
                    if not t.condition in (None, NullCondition):
                        option.append( 'color=yellow' )
                    else:
                        option.append('color=blue')
                elif not t.condition in ( None, NullCondition):
                    option.append( 'color=red' )

                print >> io, '  %s -> %s [label="%s", %s];'%(t.source,
                                                             t.destination,
                                                             t.transition_id,
                                                             ', '.join( option ) )

        for state in states:
            if state in end_states:
                print >> io, " %s [color=red];"%state
            else:
                print >> io, "  %s [shape=box ]; "%state
        print >> io, " }"

        return io.getvalue()
       
class WorkflowState(object):
    
    interface.implements(interfaces.IWorkflowState)

    workflow_state_attr = "status"
    
    def __init__(self, context):
        self.context = context
        
    def setState(self, state):
        if state != self.getState():
            setattr( self.context, self.workflow_state_attr, state )
            
    def getState(self):
        try:
            return getattr( self.context, self.workflow_state_attr )
        except AttributeError:
            return None

class WorkflowInfo(object):

    interface.implements(interfaces.IWorkflowInfo)

    def __init__(self, context):
        self.context = context

    def info( self ):
        return interfaces.IWorkflowInfo( self.context )

    def state( self ):
        return interfaces.IWorkflowState( self.context )
    
    def workflow( self ):
        return interfaces.IWorkflow( self.context )

    def _check( self, transition, check_security=False ):
        # check execution against transition condition
        if not transition.condition(self, self.context):
            raise interfaces.ConditionFailedError
        return

    def _setState( self, state_id ):
        # subclass customization hook for changing content state
        pass
    
    def fireTransition(self, transition_id, comment=None, side_effect=None,
                       check_security=True):
        state = self.state()
        wf = self.workflow()
        # this raises InvalidTransitionError if id is invalid for current state
        transition = wf.getTransition(state.getState(), transition_id)

        self._check( transition, check_security )
        transition.action(self, self.context)
        
        if transition.source is None:
            # execute any side effect
            if side_effect is not None:
                side_effect(self.context)

        # change state of context or new object
        state.setState(transition.destination)
        
        # allow workflow info to provide custom behavior for state changes
        self._setState(transition.destination)

        # notify wf event observers
        event = WorkflowTransitionEvent(
            self.context, transition.source,
            transition.destination, transition, comment
            )
        notify(event)
        
        # send modified event for original or new object
        notify(ObjectModifiedEvent(self.context))

    def fireTransitionToward(self, state, comment=None, side_effect=None,
                             check_security=True):
        transition_ids = self.getFireableTransitionIdsToward(state)
        if not transition_ids:
            raise interfaces.NoTransitionAvailableError
        if len(transition_ids) != 1:
            raise interfaces.AmbiguousTransitionError
        return self.fireTransition(transition_ids[0],
                                   comment, side_effect, check_security)
        
    def fireAutomatic(self):
        for transition_id in self.getAutomaticTransitionIds():
            try:
                self.fireTransition(transition_id)
            except interfaces.ConditionFailedError:
                # if condition failed, that's fine, then we weren't
                # ready to fire yet
                pass
            else:
                # if we actually managed to fire a transition,
                # we're done with this one now.
                return
    
    def getManualTransitionIds(self):
        checkPermission = nullCheckPermission
        return [transition.transition_id for transition in
                sorted(self._getTransitions(MANUAL)) if
                transition.condition(self, self.context) and
                checkPermission(transition.permission, self.context)]

    def getSystemTransitionIds(self):
        # ignore permission checks
        return [transition.transition_id for transition in
                sorted(self._getTransitions(SYSTEM)) if
                transition.condition(self, self.context)]

    def getFireableTransitionIds(self):
        return self.getManualTransitionIds() + self.getSystemTransitionIds()
    
    def getFireableTransitionIdsToward(self, state):
        wf = self.workflow()
        result = []
        for transition_id in self.getFireableTransitionIds():
            transition = wf.getTransitionById(transition_id)
            if transition.destination == state:
                result.append(transition_id)
        return result
    
    def getAutomaticTransitionIds(self):
        return [transition.transition_id for transition in
                self._getTransitions(AUTOMATIC)]

    def hasAutomaticTransitions(self):
        return bool(self.getAutomaticTransitionIds())

    def _getTransitions(self, trigger):
        # retrieve all possible transitions from workflow
        wf = self.workflow()
        transitions = wf.getTransitions( self.state().getState() )
        # now filter these transitions to retrieve all possible
        # transitions in this context, and return their ids
        return [transition for transition in transitions if
                transition.trigger == trigger]


class WorkflowTransitionEvent(ObjectEvent):
    interface.implements(interfaces.IWorkflowTransitionEvent)

    def __init__(self, object, source, destination, transition, comment):
        super(WorkflowTransitionEvent, self).__init__(object)
        self.source = source
        self.destination = destination
        self.transition = transition
        self.comment = comment

class AdaptedWorkflowBase( object ):
    pass
    
def AdaptedWorkflow( workflow ):
    """
    wraps a IWorkflow utility into an adapter for use as an adapted workflow
    """

    assert interfaces.IWorkflow.providedBy( workflow )
    
    class AdaptedWorkflow( AdaptedWorkflowBase ):

        def __init__( self, context):
            self.context = context
            self.workflow = workflow

            for m in interfaces.IWorkflow.names():
                setattr( self, m, getattr( workflow, m ) ) 

    interface.classImplements( AdaptedWorkflow, interfaces.IWorkflow )
    interface.directlyProvides(
        AdaptedWorkflow,
        interface.directlyProvidedBy(AdaptedWorkflow ) + interfaces.IAdaptedWorkflow )
                                    
    return AdaptedWorkflow

def ParallelWorkflow( workflow, wf_name, register_for=None):
    """
    wraps an IWorkflow and constructs IWorkflowState and IWorkflowInfo
    adapters, if register_for is specified registers them with the component
    architecture. else registration needs to be done by hand for the given
    name for all three.

    workflow is assumed to be a utility unless it implements IAdaptedWorkflow
    """

    assert interfaces.IWorkflow.providedBy( workflow )
    
    class _ParallelWorkflowState( WorkflowState ):
        workflow_state_attr = "%s_status"%(wf_name)

    class _ParallelWorkflowInfo( ParallelWorkflowInfo ):
        name = wf_name
        
    if not register_for:
        return [ workflow, _ParallelWorkflowState, _ParallelWorkflowInfo ]

    # when you have a few these, zcml registration can be tedious, try to optionally
    # automate some of the pain, even if only for the global site manager
    
    if interfaces.IAdaptedWorkflow.providedBy( workflow ):
        component.provideAdapter( workflow, (register_for,), interfaces.IWorkflow, wf_name )
    else:
        component.provideUtility( workflow, interfaces.IWorkflow, wf_name )

    component.provideAdapter( _ParallelWorkflowInfo,
                              (register_for, ),
                              interfaces.IWorkflowInfo,
                              wf_name )
    
    component.provideAdapter( _ParallelWorkflowState,
                              (register_for, ),
                              interfaces.IWorkflowState,
                              wf_name )

    return [ workflow, _ParallelWorkflowState, _ParallelWorkflowInfo ]

class ParallelWorkflowInfo( WorkflowInfo ):

    name = "ore_workflow"
    
    def info( self ):
        return component.getAdapter( self.context, interfaces.IWorkflowInfo, self.name )

    def state( self ):
        return component.getAdapter( self.context, interfaces.IWorkflowState, self.name )
    
    def workflow( self ):
        return component.queryAdapter( self.context, interfaces.IWorkflow, self.name ) \
               or component.getUtility( interfaces.IWorkflow, self.name )

