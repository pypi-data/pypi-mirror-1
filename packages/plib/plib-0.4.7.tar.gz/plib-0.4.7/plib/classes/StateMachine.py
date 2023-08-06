#!/usr/bin/env python
"""
Module StateMachine
Sub-Package CLASSES of Package PLIB
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the StateMachine class.
"""

class StateMachineException(Exception): pass

class InvalidState(StateMachineException): pass
class InvalidInput(StateMachineException): pass
class InvalidMethod(StateMachineException): pass

class StateMachine(object):
    """
    State machine class, takes a state table and implements
    the code to instantiate a machine based on it.
    
    State table format: a mapping of state names to mappings;
    each value maps input strings to 2-tuples containing:
    (<new state name>, <output>). One of the input string keys
    may be the empty string; if so, this entry will be the
    default if an input string is not in the mapping. If there
    is no default entry present, sending an input string that
    isn't in the mapping for the current state will raise an
    InvalidInput exception.
    
    The new state may be empty; if so, this is equivalent
    to remaining in the current state for that input.
    
    The output may be anything, and if none of the special cases
    below apply, it will be returned unchanged. The special
    cases are:
    
    - If the output is a string and the name of a valid method,
      that method will be called with the old and new states and
      the input to the send_input function as parameters; i.e.,
      its signature must be:
    
          def output_method(self, old_state, new_state, input_data)
    
      The result of the method call will be the output.
    
    - If the output is empty, but the default_output parameter
      was passed to the constructor, default_output will be
      treated as the output (including the possible call of a
      method by the rule just above). Note that "empty" output
      includes *anything* that is considered empty (false) by
      Python; it is not limited to None or an empty string.
    
    - If the output is empty, and there is no default output per
      the above, the new state will be returned as the output.
    
    By default, the machine starts in the first state returned
    from state_table.keys(); however, this is usually not very
    useful since the key ordering depends on the hash table
    implementation. The initial_state parameter to the constructor
    can be used to set a specific state at startup.
    
    Once the machine is instantiated, the send_input method sends
    an input string to the machine and returns the corresponding
    output (see above). When the method returns, the machine will
    be in the new state per the table.
    
    For each named state, two methods can be defined that allow
    arbitrary code to be executed during state transitions:
    
    - enter_<state> will be called when the machine transitions
      into the state;
    
    - exit_<state> will be called when the machine transitions
      out of the state.
    
    The enter method on the initial state is called from the
    constructor. On state transition, the outgoing exit method
    is called first, then the incoming enter method. Each method
    takes the old and new states and the current input as
    parameters.
    
    One other thing to note about all methods called during state
    transitions (state exit, state enter, and output) is that they
    must *not* trigger any further state transitions; thus, they
    must not call the send_input method, either directly or indirectly
    by calling some other function that may do so. This must be
    carefully considered when state transitions trigger side effects;
    if any of the side effects could result in a state change (for
    example, starting an I/O process whose result might trigger
    another state transition), those side effects *must* be delayed
    until the current state transition has been completed and the
    send_input method has returned. (Often this can be accomplished
    by posting the desired side effect to an event queue which will
    not be processed again until after send_input returns.)
    """
    
    def __init__(self, state_table, initial_state='', default_output=""):
        self.state_table = state_table
        self.default_output = default_output
        if not initial_state:
            initial_state = state_table.keys()[0]
        self.current_state = ''
        self.transition(initial_state)
    
    def state_method(self, state, change):
        try:
            return getattr(self, '%s_%s' % (change, state))
        except AttributeError:
            return None
        except TypeError:
            raise InvalidState, "States must be strings."
    
    def exit_state(self, old_state, new_state, input_data=""):
        exit_method = self.state_method(old_state, 'exit')
        if exit_method:
            exit_method(old_state, new_state, input_data)
    
    def enter_state(self, old_state, new_state, input_data=""):
        enter_method = self.state_method(new_state, 'enter')
        if enter_method:
            enter_method(old_state, new_state, input_data)
    
    def transition(self, state, input_data="", output=""):
        curr = self.current_state
        if curr != state:
            if curr:
                self.exit_state(curr, state, input_data)
            self.enter_state(curr, state, input_data)
            self.current_state = state
        if output:
            try:
                meth = getattr(self, output)
            except (AttributeError, TypeError):
                return output
            return meth(curr, state, input_data)
        return state
    
    def send_input(self, input_data):
        try:
            entry = self.state_table[self.current_state]
        except KeyError:
            raise InvalidState, "Current state not in state table."
        try:
            state, output = entry[input_data]
        except KeyError:
            try:
                state, output = entry[""]
            except KeyError:
                raise InvalidInput, "Input not in state table entry for current state."
        if not state:
            state = self.current_state
        if (not output) and self.default_output:
            output = self.default_output
        return self.transition(state, input_data, output)
