"""

some things we add on

 - custom events

 - state security manipulations
"""

import amara
import logging

from zope.dottedname.resolve import resolve
from ore.workflow import Workflow, Transition, interfaces
from zope.i18nmessageid import Message

class EventDispatcher( object ):

    def __init__( self ):
        self.event_transition_map = {}

class StatePermissions

class ImportContext( object ):

    def __init__( self ):
        self.log = logging.getLogger('ore.workflow xml')
        self.transitions = []

def load( uri ):
    doc = parse( uri )
    return _load( doc.workflow )

#def save( ):

def parse( uri ):
    doc = amara.parse( uri )

trigger_value_map = {
    'manual':interfaces.MANUAL,
    'automatic':interfaces.AUTOMATIC,
    'system':interfaces.SYSTEM
    }

def _load( workflow ):
    transitions = []

    domain = getattr( workflow, 'domain', None )
    
    for t in workflow.transition:
        try:
            kw = dict( id=t.id,
                       title=Message( t.title, domain),
                       source = t.source,
                       )
        except AttributeError:
            raise SyntaxError( t.toxml() )

        # optionals
        for i in ('trigger', 'order', 'permission'):
            val = getattr( t,i,None )
            if not val:
                continue
            kw[i] = val

        if 'trigger' in kw:
            k = kw['trigger']
            v = trigger_value_map[ k ]
            kw['trigger'] = v

        # optional python resolvables
        for i in('condition', 'action', 'trigger'):
            val = getattr( t,i,None)
            if not val:
                continue
            val = resolve( val ) # raises importerror/nameerror
            kw[i] = val
            
        transitions.append( Transition( **kw ) )

    return Workflow( transitions )
        
if __name__ == '__main__':
    import sys
    workflow = load( sys.argv[1] )
    for t in workflow.transitions:
        print  t.transition_id, t.source, t.destination, t.permission, t.condition
