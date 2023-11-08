from typing import Type

from logick import strat


class CourseSolveStrategy:
    """Strategy for solving course"""

    def __init__(self, strategy: Type[strat.CourseStrategy]):
        self.strategy = strategy

    def do_work(self):
        return self.strategy().main()


class TopicSolveStrategy:
    """Strategy for solving topic"""

    def __init__(self, strategy: Type[strat.TopicStrategy]):
        self.strategy = strategy

    def do_work(self):
        return self.strategy().main()


class TheorySolveStrategy:
    """Strategy for theory solving"""

    def __init__(self, strategy: strat.TheoryStrategy):
        self.strategy = strategy

    def do_work(self):
        self.strategy.skip_theory()


class QuestionSolveStrategy:
    """Strategy for solving questions"""

    def __init__(self, strategy: Type[strat.QuestionStrategy]):
        self.strategy = strategy

    def do_work(self):
        return self.strategy().solve_question()
