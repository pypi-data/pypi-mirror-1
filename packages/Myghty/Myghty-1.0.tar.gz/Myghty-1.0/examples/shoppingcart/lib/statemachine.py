__all__ = ['StateMachine', 'StateTransition', 'AbortTransition', 'Transition']

class StateMachine:
    def do_transition(self, state, transition):
        trans = self.__class__.transitions[state + "_" + transition]
        trans.function(self)
        return trans.tostate

class StateTransition:
    def __init__(self, fromstate, tostate, transition, function):
        self.fromstate = fromstate
        self.tostate = tostate
        self.transition = transition
        self.function = function
        self.key = fromstate + "_" + transition

class AbortTransition(Exception):
    pass

def Transition(fromstate, tostate, transition, function):
    trans = StateTransition(fromstate, tostate, transition, function)
    return (trans.key, trans)
    
        