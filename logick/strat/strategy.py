from logick.strat.find_answer_result import ResultStrategy
from logick.strat.question_solve import QuestionStrategy
from logick.strat.skip_theory import TheoryStrategy


class TheorySolveStrategy:
    """Strategy for theory solving"""
    def __init__(self, strategy: TheoryStrategy):
        self.strategy = strategy

    def do_work(self):
        self.strategy.skip_theory()


class QuestionSolveStrategy:
    """Strategy for solving questions"""
    def __init__(self, strategy: QuestionStrategy):
        self.strategy = strategy

    def do_work(self):
        return self.strategy.solve_question()


class AnswerResultStrategy:
    """Strategy for finding question solve result"""

    def __init__(self, strategy: ResultStrategy):
        self.strategy = strategy

    def do_work(self):
        return self.strategy.find_result()
