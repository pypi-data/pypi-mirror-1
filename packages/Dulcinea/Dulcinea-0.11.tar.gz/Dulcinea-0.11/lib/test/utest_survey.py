"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/test/utest_survey.py $
$Id: utest_survey.py 27590 2005-10-18 17:11:46Z dbinger $
"""
from dulcinea.survey import Question, TextQuestion, SelectQuestion, Surveyable
from dulcinea.survey import QuestionDatabase, TextAnswer, SelectAnswer, Survey
from dulcinea.survey import SurveysAndQuestions, SurveysAndQuestionsDatabase
from dulcinea.user import DulcineaUser
from sancho.utest import UTest


class SurveyTest (UTest):

    class TestSurveyable(Surveyable):

        def __init__(self, question_db=None):
            Surveyable.__init__(self)
            self.question_db = question_db

        def get_new_survey(self):
            return Survey(self.question_db.get_answers([1,2,3]))

    class BadQuestion(Question):
        pass

    def _pre(self):
        self.user = DulcineaUser('u')
        self.questions = [
            TextQuestion("text1 title", sub_title="text sub title"),
            SelectQuestion("select1 title", column_headings=['Yes', 'No']),
            SelectQuestion("select2 title",
                           sub_title="check-all-that-apply question",
                           row_headings=["using machining",
                                         "using bulk ",
                                         "using substrate",
                                         "using substrate",
                                         "equipment supplier",
                                         "material supplier",
                                         "service supplier",
                                         "Other (please specify):"],
                           last_row_has_text=True),
            SelectQuestion("select3 title",
                           sub_title="This example uses a numbered radio set",
                           column_headings=map(str, range(1,10)),
                           row_headings=["Material type",
                                         "Thickness",
                                         "Thickness uniformity",
                                         "Resistivity",
                                         "Flatness",
                                         "Defect level"]),
            SelectQuestion("select4 title",
                           sub_title="This example uses 'range labels'",
                           range_labels = ["Not Important",
                                           "Very Important"],
                           column_headings=map(str, range(1,10)),
                           row_headings=["Material type",
                                         "Thickness",
                                         "Thickness uniformity",
                                         "Resistivity",
                                         "Flatness",
                                         "Defect level"])]
        self.question_db = QuestionDatabase()
        for question in self.questions:
            self.question_db.add(question)

    def check_bad_question(self):
        b1 = self.BadQuestion('bad')
        try:
            b1.get_new_answer()
            assert 0
        except NotImplementedError: pass

    def check_text_question(self):
         t1 = self.question_db.get(1)
         assert t1.get_new_answer().__class__ == TextAnswer
         assert t1.get_title() == "text1 title"
         assert t1.get_sub_title() == 'text sub title'

    def check_select_question(self):
         s1 = self.question_db.get(2)
         assert s1.get_new_answer().__class__ == SelectAnswer
         assert s1.get_title() == "select1 title"
         assert s1.get_sub_title() == None
         assert s1.get_column_headings() == ['Yes', 'No']
         assert s1.get_row_headings() == []
         assert s1.get_range_labels() == []
         s2 = self.question_db.get(3)
         assert s2.get_sub_title() == "check-all-that-apply question"
         assert s2.get_row_headings() == [
             "using machining",
             "using bulk ",
             "using substrate",
             "using substrate",
             "equipment supplier",
             "material supplier",
             "service supplier",
             "Other (please specify):"]
         s4 = self.question_db.get(5)
         assert s4.get_range_labels() == ["Not Important", "Very Important"]

    def check_text_answer(self):
         self.t1 = self.question_db.get(1)
         assert self.t1.get_new_answer().__class__ == TextAnswer
         a1 = self.t1.get_new_answer()
         assert a1.get_question() == self.t1
         assert a1.get_answer() == None
         assert a1.has_answer() == False
         a1.set_answer('the answer')
         assert a1.get_answer() == 'the answer'
         assert a1.has_answer() == True

    def check_select_answer(self):
         self.s1 = self.question_db.get(2)
         assert self.s1.get_new_answer().__class__ == SelectAnswer
         a2 = self.s1.get_new_answer()
         assert a2.get_question() == self.s1
         assert a2.get_answer() == None
         assert a2.has_answer() == False
         a2.set_answer(['1','2','3'])
         assert a2.get_answer() == ['1','2','3']
         assert a2.has_answer() == True
         assert a2.get_other_text() == None
         a2.set_other_text('other')
         assert a2.get_other_text() == 'other'

    def check_survey(self):
        s1 = Survey(self.question_db.get_answers([1,2,3,4,5]))
        str(s1)
        assert len(s1) == 5
        assert len(s1.get_questions()) == 5
        assert len(s1.get_answers()) == 5
        timestamp = s1.get_timestamp()
        s1.set_timestamp()
        assert s1.get_timestamp() != timestamp
        assert s1.get_user() == None
        s1.set_user(self.user)
        assert s1.get_user().get_id() == 'u'
        assert not s1.has_answers()
        a1 = s1.get_answers()[0]
        a1.set_answer('the answer')
        assert s1.has_answers()
        s1.set_answers(s1.get_answers(), self.user)

    def check_surveyable(self):
        sv = self.TestSurveyable(question_db=self.question_db)
        assert sv.get_surveys() == []
        sv.add_survey(Survey(self.question_db.get_answers([1,2,3])))
        sv.get_survey(0)
        sv.get_new_survey()
        sv2 = Surveyable()
        try:
            sv2.get_new_survey()
            assert 0
        except NotImplementedError: pass

    def check_surveys_and_questions(self):
        questions = [TextQuestion(
            "Do you wish to be included?",
            sub_title=("If you wish to be entered, please "
                       "enter your contact information below so you can be "
                       "notified.")),
                     SelectQuestion(
            "Are there factors more critical "
            "than hypothetical issues?", column_headings=['Yes', 'No']),
                     SelectQuestion(
            "Please choose one or more of the following categories to "
            "represent your club's activities.",
            row_headings=["maker using dirt",
                          "maker using glass",
                          "maker using metal",
                          "maker using wood",
                          "equipment supplier",
                          "material supplier",
                          "service supplier",
                          "Other (please specify):"],
            sub_title="This is a 'check-all-that-apply' style question",
            last_row_has_text=True),
                     SelectQuestion(
            "What are the key  issues?",
            sub_title="This example uses a numbered radio set",
            column_headings=map(str, range(1,10)),
            row_headings=["type", "ness", "uniformity",
                          "blah", "Flatness", "level"]),
                     SelectQuestion(
            "What are the key?",
            sub_title="This example uses 'range labels' in addition to numbers",
            range_labels = ["Not Important", "Very Important"],
            column_headings=map(str, range(1,10)),
            row_headings=["type", "ness", "uniformity",
                          "blah", "Flatness", "level"])]

        sq = SurveysAndQuestions('test', questions)
        assert sq.get_id() == 'test'
        assert len(sq.get_new_survey().get_questions()) == len(questions)
        sq_db = SurveysAndQuestionsDatabase()
        sq_db.add(sq)
        assert sq_db.get('test') is sq
        sq_db.get_mapping()['test'] is sq

if __name__ == "__main__":
    SurveyTest()
