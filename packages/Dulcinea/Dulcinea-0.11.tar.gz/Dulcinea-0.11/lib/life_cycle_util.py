"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/life_cycle_util.py $
$Id: life_cycle_util.py 27538 2005-10-11 23:00:36Z rmasse $
"""
from dulcinea.sort import lexical_sort
from dulcinea.metaclass import ClassMethodsClass

class TransitionClass (ClassMethodsClass):
    """This class is here so that we have a distinctive type for Transitions.

    Instance attributes: none
    """

    def __init__ (self, class_name, bases, namespace):
        super(TransitionClass, self).__init__(class_name, bases, namespace)
        # provide default values for attributes
        for attr in ['_progressive', '_require_comment', '_suppress_comment']:
            if not hasattr(self, attr):
                setattr(self, attr, 0)


class StateClass (ClassMethodsClass):
    """This class is here so that we have a distinctive type for States.

    Instance attributes: 
      _name : string
      _transitions : [TransitionClass]
    """

    def __init__ (self, class_name, bases, namespace):
        super(StateClass, self).__init__(class_name, bases, namespace)
        # compute _transitions list
        self._transitions = lexical_sort(
            [ value for value in namespace.values()
              if isinstance(value, TransitionClass) ])

class PlainState:

    """
    Subclasses of PlainState are states of Statefuls. !

    Instance attributes: none
    """

    __metaclass__ = StateClass
    _name = "PlainState"
    _transitions = []
    
    def __init__ (self):
        """
        No instances of PlainState should ever exist.
        Subclasses are used directly as if they were instances.
        """
        raise RuntimeError

    def get_name (klass):
        """() -> string
        A pretty label for the state.
        """
        return klass._name

    def get_transitions (klass):
        """() -> sequence [ Transition ]
        Generates the list of Transitions in this class.
        """
        return klass._transitions

    def get_transition (klass, action):
        """() -> Transition
        Return the Transition with the given action,
        or None if no such transition is present.
        """
        for transition in klass.get_transitions():
            if action == transition.get_action():
                return transition
        return None

    def validate (*klasses):
        """
        Look for coding mistakes in this class.
        """
        for klass in klasses:
            assert type(klass.get_name()) is str
            actions = []
            for transition in klass.get_transitions():
                action = transition.get_action()
                assert action not in actions
                actions.append(action)
                transition.validate()

    def format (klass):
        """() -> string
        Return a plain text dump of this class.
        """
        s = 'State %s\n' % klass
        s += '    name=%r\n' % klass.get_name()
        s += '    '
        for transition in klass.get_transitions():
            s += transition.format().replace('\n','\n    ')
        s += '\n'
        return  s


class PlainTransition:
    """
    Subclasses of this class are defined within subclasses of State.

    Instance attributes: none
    """

    __metaclass__ = TransitionClass
    _action = _description = _hint = ''
    _next_state = PlainState

    def __init__ (self):
        """
        No instances of PlainTransition should ever exist.
        Subclasses are used directly as if they were instances.
        """
        raise RuntimeError

    def get_action (klass):
        """() -> string

        Return the string that is used to identify this transition.
        """
        return klass._action

    def get_description (klass):
        """() -> string
        """
        return klass._description

    def get_hint (klass):
        """() -> string

        A hint to users about this transition.
        """
        return klass._hint

    def get_next_state (klass):
        """() -> State
        Return the state that the run should be in after this transition
        is executed.
        """
        return klass._next_state

    def disallowed (klass, stateful, user):
        """(stateful : Stateful, user : User) ->  string | None
        Return an explanation of any problem (that the user can't correct)
        that prevents the user from executing this transition for the stateful.
        If this returns a string, this transition should not be offered.

        Subclasses will override this method.
        """
        return ("The %s.%s transition isn't allowed for anyone." %
                (stateful.state, klass))

    def get_warnings (klass, stateful, user, comment):
        """(stateful : Stateful, user : User) -> [ string ]
        Return a list of explanations of any problems (that the user could
        possibly correct) that prevent the user from executing this transition
        for the stateful.  If this returns any strings, this transition may be
        shown in some disabled form to the user, along with the explanation of
        why it is not currently available.

        Subclasses will override this method.
        """
        return []

    def prepare (klass, stateful, user, comment):
        """(stateful : Stateful, user : User, comment : string=None)
            -> string | None
        Assuming that disallowed() and get_warnings() return no reasons
        to stop, the transition may be attempted.  Sometimes there is something
        destructive that should be done just prior to the actual change
        of state, and the change may not produce the conditions that
        are required for the actual change of state to occur.
        This method executes those destructive operations and
        reports any final reason why the actual state change
        should not happen.

        Subclasses will override this method.
        """
        return None

    def change_state (klass, stateful, user, comment):
        """(stateful : Stateful, user : User, comment : string)
            -> [ string ] | None
        Try to execute this transition.
        Make the necessary history records,
        send the necessary email,
        perform the necessary data modifications,
        and assign a State to the stateful's 'state' attribute.

        If there are some reasons that the transition can't be completed,
        return a string containing the reasons, otherwise return None.
        """
        errors  = (klass.disallowed(stateful, user) or
                   klass.get_warnings(stateful, user, comment) or
                   klass.prepare(stateful, user, comment))
        if errors:
            if type(errors) is str:
                errors = [ errors ]
            klass.mail_on_errors(stateful, user, comment, errors)
            return errors
        else:
            stateful.set_state(klass.get_next_state(), user)
            klass.mail_on_success(stateful, user, comment)
            return None

    def is_progressive (klass, stateful=None, user=None):
        """(stateful : Stateful, user : User) -> boolean
        Is this a transition that moves the stateful toward completion?
        """
        return klass._progressive

    def require_comment (klass, stateful=None, user=None):
        """(stateful : Stateful, user : User) -> boolean
        Should the user be required to provide a comment when executing
        this transition?
        """
        return klass._require_comment

    def suppress_comment (klass, stateful=None, user=None):
        """(stateful : Stateful, user : User) -> boolean
        Should the user be offered a chance to comment when executing
        this transition?
        """
        return klass._suppress_comment

    def mail_on_errors (klass, stateful, user, comment, errors):
        """(stateful : Stateful, user : User, comment : string, errors: [ string ])
            -> (non_fab_message : string, fab_message : string)
        Deliver notification about this failed transition to the
        appropriate parties.  Subclasses will override this
        if they want any require any notification.

        Return a pair of strings that report the messages
        sent.  The first string describes the message that would
        be sent to all except fab staff.  The second string
        describes the message that would be sent to fab staff.
        The difference exists because we don't identify the
        customer to fab staff.
        """
        return ('No mail\n', '')

    def mail_on_success (klass, stateful, user, comment):
        """(stateful : Stateful, user : User, comment : string)
            -> (non_fab_message : string, fab_message : string)
        Deliver notification about this successful transition to the
        appropriate parties.  Subclasses will override this
        if they want any require any notification.

        Return a pair of strings that report the messages
        sent.  The first string describes the message that would
        be sent to all except fab staff.  The second string
        describes the message that would be sent to fab staff.
        The difference exists because we don't identify the
        customer to fab staff.
        """
        return ('No mail\n', '')

    def validate (*klasses):
        """
        Look for coding mistakes in this class.
        """
        for klass in klasses:
            assert issubclass(klass, PlainTransition)
            assert type(klass.get_action()) is str
            assert type(klass.get_description()) is str
            assert type(klass.get_hint()) is str
            assert issubclass(klass.get_next_state(), PlainState)
            assert callable(klass.require_comment)
            assert callable(klass.suppress_comment)
            assert callable(klass.is_progressive)
            assert callable(klass.disallowed)
            assert callable(klass.get_warnings)
            assert callable(klass.prepare)
            assert callable(klass.mail_on_errors)
            assert callable(klass.mail_on_success)
            assert callable(klass.change_state)

    def format (klass):
        """() -> string

        Return a plain text dump of this class.
        """
        s =  'Transition %s (%s) to State %s' % (klass,
                                                 klass.get_action(),
                                                 klass.get_next_state())
        s += '\n'
        s += '    description=%r\n' % klass.get_description()
        s += '    hint=%r\n' % klass.get_hint()
        s += '    is_progressive=%s\n' % klass.is_progressive()
        s += '    disallowed=%s\n' % klass.disallowed.func_name
        s += '    require_comment=%s\n' % klass.require_comment()
        s += '    suppress_comment=%s\n' % klass.suppress_comment()
        return s

class Stateful:

    """Stateful objects have a state attribute.

    Instance attributes:
       state : StateClass
    """
    state_is = StateClass

    def __init__ (self, state):
        self.state = state

    def is_ready_for_user (self, user):
        """(user : User) -> boolean

        Return true if user is able to move the run forward in its life cycle.
        """
        for transition in self.state.get_transitions():
            if (transition.is_progressive(self, user) and
                transition.disallowed(self, user) is None):
                return 1
        return 0

    def get_available_actions (self, user):
        """(user:User) -> [(action,description,hint)]
        Returns a list of the actions that can be successfully taken
        by the given user.
        """
        return [ (transition.get_action(),
                  transition.get_description(),
                  transition.get_hint())
                 for transition in self.state.get_transitions()
                 if transition.disallowed(self, user) is None ]

    def get_transition (self, user, action):
        """(user : User, action : string) -> PlainTransition

        Look up the FSM transition for this user and action.  Return None if
        the transition does not exist or if it is not valid for this user.
        """
        transition = self.state.get_transition(action)
        if transition is None or transition.disallowed(self, user):
            return None
        else:
            return transition

    def change_state (self, user, action, comment=None):
        """(user : User, action : string, comment : string) -> [ string ]

        Change the run's state depending on the provided acting user
        and action.  If anything prevents the transition from happening,
        return a list of reasons.
        """
        transition = self.state.get_transition(action)
        if transition is None:
            return [ "No %s action available from %s."
                     % (action, self.get_state()) ]
        return transition.change_state(self, user, comment)

    def set_state (self, state, user):
        self.state = state

    def get_state (self):
        return self.state

def find_states (namespace):
    """
    Return a sorted list of states defined in the namespace
    and update the _next_state attributes. 

    A module that defines a life cycle should call this after
    defining states, with a line, for example, like this:

    states = find_states(globals())
    
    """
    state_dict = {}
    for name, value in namespace.items():
        if isinstance(value, StateClass):
            state_dict[name] = value
    # connect transitions to states
    for state in state_dict.values():
        for transition in state.get_transitions():
            transition._next_state = state_dict[transition._next_state_name]
    return lexical_sort(state_dict.values())




