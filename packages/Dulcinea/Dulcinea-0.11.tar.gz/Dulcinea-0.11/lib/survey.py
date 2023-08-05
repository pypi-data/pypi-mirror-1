"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/survey.py $
$Id: survey.py 27528 2005-10-07 20:50:40Z dbinger $
"""
from dulcinea.address import ContactAddress
from dulcinea.base import DulcineaBase, DulcineaPersistent
from dulcinea.keyed import Keyed, KeyedMap
from dulcinea.spec import either, sequence, mapping, require, init, specify
from dulcinea.spec import spec, boolean, add_getters_and_setters, add_getters
from dulcinea.spec import string
from dulcinea.timestamped import Timestamped
from dulcinea.user import DulcineaUser
from durus.persistent_dict import PersistentDict
from durus.persistent_list import PersistentList


class Question(Keyed, DulcineaPersistent):

    title_is = (string, None)
    sub_title_is = (string, None)

    def __init__(self, title, sub_title=None):
        assert self.__class__ is not Question, "abstract class"
        Keyed.__init__(self)
        specify(self, title=title, sub_title=sub_title)

    def __str__(self):
        if self.sub_title:
            return self.title + "\n" + self.sub_title
        return self.title

    def get_new_answer(self):
        raise NotImplementedError, "abstract method"

add_getters(Question)


class TextQuestion(Question):

    dimensions_is = (int, int)

    def __init__(self, title, sub_title=None, rows=5, cols=80):
        Question.__init__(self, title, sub_title)
        self.dimensions = (rows, cols)

    def get_new_answer(self):
        return TextAnswer(self)

    def get_dimensions(self):
        # Fix with update_db.
        return getattr(self, 'dimensions', (5, 80))


class ContactAddressQuestion(Question):

    def get_new_answer(self):
        return ContactAddressAnswer(self)


class SelectQuestion(Question):
    """
    A SelectQuestion is an abstract class for representing selections
    from either checkboxes or radio buttons
    """
    column_headings_is = spec(
        [(string, None)],
        "text to place above each column")
    row_headings_is = spec(
        [(string, None)],
        "text that preceeds each row")
    range_labels_is = spec(
        [string],
        "labels to be placed in a row above column headings at the right and "
        "left")
    last_row_has_text_is = spec(
        boolean,
        "flag to tell the widget to display a TextWidget after the last row "
        "label")

    def __init__(self, title, sub_title=None,
                 column_headings=None, row_headings=None,
                 range_labels=None, last_row_has_text=False):
        Question.__init__(self, title, sub_title=sub_title)
        specify(self,
                column_headings=column_headings or [],
                row_headings=row_headings or [],
                range_labels=range_labels or [],
                last_row_has_text = last_row_has_text)
        assert len(self.range_labels) in (0,2), "must have two range labels"

    def __str__(self):
        question = self.title
        if len(self.column_headings) > 1: # Radioset
            if len(self.column_headings) > 4:
                headings = '(%s ... %s)' % (self.column_headings[0],
                                            self.column_headings[-1])
            else:
                headings = '(%s)' % (', '.join(self.column_headings))
            question += "\n" + headings
            if self.range_labels:
                question += "\n  ...where %s is %s and %s is %s" % (
                    self.column_headings[0], self.range_labels[0],
                    self.column_headings[-1], self.range_labels[-1])
        if self.sub_title:
            question += "\n" + self.sub_title
        return question

    def get_new_answer(self):
        return SelectAnswer(self)

add_getters(SelectQuestion)


class Answer(DulcineaBase):

    question_is = Question

    def __init__(self, question):
        assert self.__class__ is not Answer, "abstract class"
        self.question = question

    def get_question(self):
        return self.question



class ContactAddressAnswer(Answer):

    answer_is = ContactAddress

    def __init__(self, question):
        Answer.__init__(self, question)
        self.answer = ContactAddress()

    def __str__(self):
        return self.answer.format()

    def has_answer(self):
        return self.answer != ContactAddress()

add_getters_and_setters(ContactAddressAnswer)


class TextAnswer(Answer):

    answer_is = string

    def __init__(self, question):
        Answer.__init__(self, question)
        self.answer = None

    def __str__(self):
        return self.answer

    def get_answer(self):
        return self.answer

    def set_answer(self, answer):
        specify(self, answer=answer)

    def has_answer(self):
        return self.answer is not None

add_getters_and_setters(TextAnswer)


class SelectAnswer(Answer):

    selected_is = spec(
        [either(string, boolean)],
        "list of selected row answers")
    other_text_is = spec(
        string,
        "contents of the filled in 'last_row_has_text' textfield")

    def __init__(self, question):
        Answer.__init__(self, question)
        init(self)

    def __str__(self):
        if self.question.row_headings:
            def format_heading_answer(heading, answer):
                if answer:
                    return "%s: %s" % (heading, answer)
                return ''
            return "\n".join([format_heading_answer(*heading_answer) for
                              heading_answer in
                              zip(self.question.row_headings, self.selected)])
        return ", ".join(self.selected)

    def set_other_text(self, other_text):
        specify(self, other_text=other_text)

    def get_other_text(self):
        return self.other_text

    def set_answer(self, selected):
        specify(self, selected=selected)

    def get_answer(self):
        return self.selected

    def has_answer(self):
        return self.selected is not None


class Survey(DulcineaPersistent, Timestamped):
    """A set of Questions and Answers attached to a single object.
    """
    user_is = spec(
        (DulcineaUser, None),
        "user taking the survey")
    answers_is = spec(
        [Answer],
        "answers to the questions that comprise the object's survey")

    def __init__(self, answers):
        """(answers:[Answer])
        """
        Timestamped.__init__(self)
        init(self, answers=answers)

    def __str__(self):
        return "By %s on %s: %d answers" % (
            self.user, self.get_timestamp(), len(self.answers))

    def __len__(self):
        return len(self.answers)

    def get_questions(self):
        return [answer.get_question() for answer in self.answers]

    def get_answer_for_question_key(self, question_key):
        for answer in self.answers:
            if answer.get_question().get_key() == question_key:
                return answer
        return None

    def set_user(self, user):
        """(user : DulcineaUser)
        """
        specify(self, user=user)

    def set_answers(self, answers, user):
        """(answers : [Answer], user : DulcineaUser)
        """
        specify(self, answers=answers, user=user)
        self.set_timestamp()

    def has_answers(self, omit_questions=None):
        """(omit_questions : [int] | None) -> boolean

        Return true if any answers have been answered for this survey
        ignoring omitted questions if specified
        """
        for answer in self.answers:
            if answer.get_question().get_key() in (omit_questions or []):
                continue
            if answer.has_answer():
                return True
        return False

add_getters(Survey)


class Surveyable:
    """A mixin for objects that have Surveys
    """
    surveys_is = (None, sequence(Survey, PersistentList))

    def __init__(self):
        self.surveys = None

    def get_surveys(self):
        """() -> [Survey]
        """
        return self.surveys or []

    def get_survey(self, index):
        return self.surveys and self.surveys[index]

    def get_new_survey(self):
        """() -> Survey
        """
        raise NotImplementedError, "abstract method"

    def add_survey(self, survey):
        if self.surveys is None:
            self.surveys = PersistentList()
        self.surveys.append(survey)


class QuestionDatabase(KeyedMap, DulcineaPersistent):

    def __init__(self):
        KeyedMap.__init__(self, value_spec=Question)

    def get_answers(self, question_keys=None):
        """(question_keys: [int]) -> [Answer]
        """
        if not question_keys:
            question_keys = self.get_mapping().keys()
            question_keys.sort()
        return [self.get(question_key).get_new_answer()
                for question_key in question_keys]


class SurveysAndQuestions(Surveyable, QuestionDatabase):

    id_is = string
    title_is = string
    description_is = string

    def __init__(self, id, questions):
        """(id : string, questions : [Question])
        """
        Surveyable.__init__(self)
        QuestionDatabase.__init__(self)
        for question in questions:
            self.add(question)
        specify(self, id=id, title='', description='')

    def get_new_survey(self):
        return Survey(self.get_answers())

add_getters_and_setters(SurveysAndQuestions)


class SurveysAndQuestionsDatabase(DulcineaPersistent):

    surveys_and_questions_is = mapping({string:SurveysAndQuestions},
                                       PersistentDict)

    def __init__(self):
        self.surveys_and_questions = PersistentDict()

    def add(self, surveys_and_questions):
        require(surveys_and_questions, SurveysAndQuestions)
        id = surveys_and_questions.get_id()
        assert id not in self.surveys_and_questions, id
        self.surveys_and_questions[id] = surveys_and_questions

    def get(self, id):
        return self.surveys_and_questions.get(id)

    def get_mapping(self):
        return self.surveys_and_questions

