#!/usr/bin/env python
"""
    pyfse.Controller module
    
    @author: Jean-Lou Dupont
"""
__author__  = "Jean-Lou Dupont"
__version__ = "$Id: controller.py 27 2009-03-26 10:51:05Z jeanlou.dupont $"

__all__ = ['pyfseException', 'Controller',]

from types import *



class pyfseException(Exception):
    """ Exception base class 
    """
    def __init__(self, msg, params = None):
        Exception.__init__(self, msg)
        self.params = params
        
    def __str__(self):
        """
        Human readable representation
        
        Usually, a client of this library would use the
        `msg` parameter to lookup a human readable message.
        The parameters `params` would be used to clarify the
        error message.
        """
        return "msg[%s] params[%s]" % (self.message, self.params)



class Controller(object):
    """

    **Transition Table**
        
    Dictionary consisting of:
    
        { (current_state, event): record }
        
    where `record` can be of the form:
    
    1. (next_state, action_method)
    2. (next_state,)
    3. (next_state, None)
    4. next_state
        
    Upon leaving the current_state, the method 'leave_STATE'
    will be called. Upon entering the next_state, the method
    'enter_STATE' will be called.
    
    The type of the parameter 'event' is a `string`.
    
    A 'wildcard' match on any event can be obtained using:
        
        **(current_state, None): (next_state, action_method)**
        
    An initialization sequence can be obtained using:
        
        **('', None): record**
        
    An 'attractor' match: an event X can direct the
    next_state from whatever current_state:
    
        **(None, 'event'): record**
    
    **Precedence**
        
    The precedence algorithm goes as follows:
    
    1. Exact match first / Initialization match
    2. Wildcard match
    3. Attractor match
    
    **Attractor Match**
    
    Care should be exercised when using this matching pattern.
    
    **Action Method**
    
    The `action method` need not to be present: it can take
    the value `None`. The `action method` can be:
    
    1. a callable function
    2. a method name of the `actions` object instance (if provided)
    3. a method name local to the controller.
 
    string representing a local attribute + method name
    
    For case 1, the function will be called with the `event` parameter.
    For case 2, the method will be called with the `event` parameter.
    For case 3, assuming the `actions` object is provided, the
    method will be called with the `event` parameter.
    
    Precedence order is as listed. 
    
    The `enter_STATE` will be called prior to the `action method`.
    """
    
    
    _enter_prefix = "enter_"
    _leave_prefix = "leave_"
    
    def __init__(self, transition_table, actions = None):
        self.transition_table = transition_table
        self.current_state = ''
        self.actions = actions
        self._debug = False
    
    def default_enter(self, event, *pargs):
        """ Default `enter` method
            Should be subclassed
        """
        if self._debug:
            print "default_enter"
    
    def default_leave(self):
        """ Default `leave` method
            Should be subclassed
        """
        if self._debug:
            print "default_leave"
    
    def __call__(self, event, *pargs):
        """ Event Handler entry point
        
            1. Call the leave_X method where X is the current_state
            2. Look-up [next_state;action] based on [current_state;input]            
            3. Call the enter_Y method where Y is the next_state
            4. Call action method
            5. current_state <- next_state
        """

        #1
        leave_method_name = "%s%s" % (self._leave_prefix, self.current_state)
        leave_method = getattr(self, leave_method_name, self.default_leave)
        leave_method()
        
        #2
        #next_state, action = self._lookup(event)
        record = self._lookup(event)
        next_state, action = self._decodeRecord(record)
        
        #3
        enter_method_name = "%s%s" % (self._enter_prefix, next_state)
        enter_method = getattr(self, enter_method_name, self.default_enter)
        enter_method(event, pargs)

        #4
        if action is not None:
            self._handleActionMethod(action, event)
        
        #5
        self.current_state = next_state
    
    def _decodeRecord(self, record):
        """ Extracts `next_state` and `action`
        
            **Cases**
            
            1. ('next_state', action)
            2. ('next_state', None)
            3. ('next_state', )
            4. 'next_state'
        """
        if type(record) is TupleType:
            try:    next_state = record[0]
            except: next_state = record
            
            try:    action = record[1]
            except: action = None
        else:
            next_state = record
            action = None
            
        return next_state, action
     
    def _handleActionMethod(self, action, event):
        """ Handles the `action method`
        
            1. String consisting of only a `method name`
            2. Callable function
            3. String representing `attribute.method_name`
        """
        # String? if YES, then try local method
        if type(action) is StringType:
            self._handleStringAction(action, event)
            return
        
        # Callable? This is the last resort.
        if callable(action):
            action(event)
            return
        
        self._raiseException('error_action_method', event)

    def _handleStringAction(self, action, event):
        """ Handles the `action` when it is provided through a string
        """
        if self.actions is not None:
            self._handleActionFromActions(action, event)
            return
        
        action_method = getattr(self, action, None)
        if action_method is not None:
            action_method(event)
            
    def _handleActionFromActions(self, action, event):
        try:
            method = getattr(self.actions, action)
            method(event)            
        except:
            self._raiseException('error_action_method_not_found', event)
            

    def _lookup(self, event):
        """ Look up the next_state based on [current_state;event]
        
            @return: next_state
        """
        # precedence 1. direct match
        tuple_dm = (self.current_state, event)        
        dm = self.transition_table.get( tuple_dm, None )
        if dm is not None:
            return dm
        
        # precedence 2. wildcard match
        tuple_wm = (self.current_state, None)
        wm = self.transition_table.get(tuple_wm, None)
        if wm is not None:
            return wm
        
        # precedence 3. attractor match
        tuple_am = (None, event)
        am = self.transition_table.get(tuple_am, None)
        if am is not None:
            return am
        
        self._raiseException('error_transition_missing', event)

    def _raiseException(self, msg, event = None):
        """ Raises an exception.
            Convenience method.
        """
        params = {'current_state':self.current_state, 'event':event}
        raise pyfseException(msg, params)

