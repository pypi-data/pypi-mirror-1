"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/issue.py $
$Id: issue.py 27538 2005-10-11 23:00:36Z rmasse $
"""
from datetime import datetime, timedelta
from dulcinea.base import DulcineaPersistent
from dulcinea.sort import function_sort
from dulcinea.spec import mapping, sequence, spec, add_getters, specify
from dulcinea.spec import require, boolean, string
from dulcinea.timestamped import timestamp_sorted, Timestamped
from dulcinea.user import DulcineaUser
from durus.persistent_dict import PersistentDict
from sets import Set

class Issue(DulcineaPersistent, Timestamped):
    """
    An Issue is usually a bug or a feature request.
    """
    title_is = (string, None)
    key_is = (string, None)
    description_is = spec(
        (string, None),
        "A description of the issue and users notes about it.")
    bang_ratings_is = spec(
        mapping({DulcineaUser:(int,None)}, PersistentDict),
        "The bang ratings given by users.")
    buck_ratings_is = spec(
        mapping({DulcineaUser:(int,None)}, PersistentDict),
        "The buck ratings given by users.")
    approvals_is = spec(
        sequence(DulcineaUser, Set),
        "The users who agree the issue is resolved.")

    BANG_OPTIONS = (None, 1, 2, 3, 4, 5)
    BANG_DESCRIPTIONS = ('No Opinion',
                         'Minor',
                         'Valuable',
                         'Very Valuable',
                         'Major Advance',
                         'Essential')
    BUCK_OPTIONS = (None, 1, 2, 3, 4, 5)
    BUCK_DESCRIPTIONS = ('No Opinion',
                         'Trivial',
                         'Easy',
                         'Moderate',
                         'Tough',
                         'Extremely Difficult')

    def __init__(self):
        Timestamped.__init__(self)
        specify(self, title='', key=None, description=None,
                bang_ratings=PersistentDict(),
                buck_ratings=PersistentDict(),
                approvals=Set())

    def set_key(self, key):
        assert self.key is None
        specify(self, key=key)

    def set_title(self, title):
        specify(self, title=title)

    def set_description(self, description):
        specify(self, description=description)

    def set_bang(self, user, rating):
        require(user, DulcineaUser)
        require(rating, (int, None))
        if not rating in self.BANG_OPTIONS:
            raise TypeError, 'invalid rating: %r, rating must be one of %r' % (
                rating, self.BANG_OPTIONS)
        self.bang_ratings[user] = rating

    def get_individual_bang(self, user):
        require(user, DulcineaUser)
        return self.bang_ratings.get(user, None)

    def get_combined_bang(self):
        cumulative_bang = 0.0
        number_of_ratings = 0
        for rating in self.bang_ratings.values():
            if rating is not None:
                cumulative_bang += rating
                number_of_ratings += 1
        if number_of_ratings == 0:
            return None
        else:
            return cumulative_bang / number_of_ratings

    def get_bang_description(self, rating):
        for index, option in enumerate(self.BANG_OPTIONS):
            if rating <= option:
                return self.BANG_DESCRIPTIONS[index]

    def set_buck(self, user, rating):
        require(user, DulcineaUser)
        require(rating, (int, None))
        if rating not in self.BUCK_OPTIONS:
            raise TypeError, 'invalid rating: %r, rating must be one of %r' % (
                rating, self.BUCK_OPTIONS)
        self.buck_ratings[user] = rating

    def get_individual_buck(self, user):
        require(user, DulcineaUser)
        return self.buck_ratings.get(user, None)

    def get_combined_buck(self):
        cumulative_buck = 0.0
        number_of_ratings = 0
        for rating in self.buck_ratings.values():
            if rating is not None:
                cumulative_buck += rating
                number_of_ratings += 1
        if number_of_ratings == 0:
            return None
        else:
            return cumulative_buck / number_of_ratings

    def get_buck_description(self, rating):
        for index, option in enumerate(self.BUCK_OPTIONS):
            if rating <= option:
                return self.BUCK_DESCRIPTIONS[index]

    def get_priority(self):
        bang = self.get_combined_bang()
        if bang is None:
            return None
        buck = self.get_combined_buck()
        if buck is None:
            return None
        return bang / buck

    def get_inverted_priority(self):
        priority = self.get_priority()
        if priority is None:
            return 0
        else:
            return 1 / priority

    def set_approval(self, user, approval):
        require(user, DulcineaUser)
        require(approval, boolean)
        self._p_note_change()
        if approval:
            self.approvals.add(user)
        elif user in self.approvals:
            self.approvals.remove(user)

    def awaits_approval_by(self, user):
        require(user, DulcineaUser)
        return (self.approvals and
                user in self.bang_ratings.keys() and
                user not in self.approvals)

    def is_approved_by(self, user):
        require(user, DulcineaUser)
        return user in self.approvals

    def get_voters(self):
        return self.bang_ratings.keys()

    def is_resolved(self):
        for user in self.bang_ratings.keys():
            if user not in self.approvals:
                return False
        return True

    def get_approvers(self):
        return self.approvals

add_getters(Issue)

def _sort_issue_list(issues):
    def issue_info(issue):
        return (len(issue.get_approvers()), issue.get_inverted_priority())
    return function_sort(issues, issue_info)


class IssueDatabase(DulcineaPersistent):

    issues_is = spec(
        mapping({string:Issue}, PersistentDict),
        "Mapping of issue IDs to issues.")
    issues_in_progress_is = spec(
        mapping({DulcineaUser:Issue}, PersistentDict),
        "Mapping of users to the issues they are working on.")
    _next_issue_id_is = spec(
        int,
        "Internal counter used for allocating issue IDs")

    def __init__(self):
        specify(self,
                issues=PersistentDict(),
                issues_in_progress=PersistentDict(),
                _next_issue_id=1)

    def get_issue(self, issue_id):
        return self.issues.get(issue_id)

    def __getitem__(self, issue_id):
        return self.issues[issue_id]

    def _generate_issue_id(self):
        issue_id = self._next_issue_id
        self._next_issue_id += 1
        return 'I%04d' % issue_id

    def add_issue(self, issue):
        require(issue, Issue)
        assert issue.get_key() is None, 'Issue already has id'
        issue_id = self._generate_issue_id()
        assert not self.issues.has_key(issue_id)
        issue.set_key(issue_id)
        self.issues[issue_id] = issue

    def remove_issue(self, issue):
        issue_id = issue.get_key()
        assert issue_id is not None, 'Issue has no ID'
        del self.issues[issue_id]
        for user, issue_in_progress in self.issues_in_progress.items():
            if issue is issue_in_progress:
                del self.issues_in_progress[user]

    def get_issues(self):
        return _sort_issue_list(self.issues.values())

    def set_issue_in_progress(self, user, issue):
        require(user, DulcineaUser)
        require(issue, Issue)
        self.issues_in_progress[user] = issue

    def clear_issue_in_progress(self, user, issue):
        require(user, DulcineaUser)
        require(issue, Issue)
        if self.issues_in_progress.get(user) is issue:
            del self.issues_in_progress[user]

    def get_issue_in_progress(self, user):
        require(user, DulcineaUser)
        return self.issues_in_progress.get(user)

    def get_issues_in_progress(self):
        return _sort_issue_list(Set(self.issues_in_progress.values()))

    def is_issue_in_progress(self, issue):
        require(issue, Issue)
        return issue in self.issues_in_progress.values()

    def get_users_on_issue(self, issue):
        require(issue, Issue)
        return [user
                for user, issue_in_progress in self.issues_in_progress.items()
                if issue is issue_in_progress]

    def get_issues_for_approval(self, user):
        require(user, DulcineaUser)
        return _sort_issue_list([issue
                                 for issue in self.issues.values()
                                 if issue.awaits_approval_by(user)])

    def get_recent_issues(self, days):
        minimum_time = datetime.now() - timedelta(days=days)
        issues = [issue for issue in self.issues.values()
                  if issue.get_timestamp() > minimum_time]
        return timestamp_sorted(issues)
