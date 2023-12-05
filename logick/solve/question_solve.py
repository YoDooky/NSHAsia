from typing import Type, Union
from logick.strat.question_solve import (
    QuestionStrategy,
    QuestionSolveStrategy,
    QuestionStrategyB,
    QuestionStrategyA
)


class QuestionSolve:
    def __init__(self, strategy: Union[Type[QuestionStrategy], None]):
        self.strategy = strategy

    def solve_question(self) -> Type[QuestionStrategy]:
        if self.strategy is None:
            self.define_strategy()
        QuestionSolveStrategy(self.strategy).do_work()
        return self.strategy

    def define_strategy(self):
        """Find demand question solve strategy for current topic depending on founded xpath (current_score)"""
        try:
            if QuestionStrategyB().get_result_data() is None:
                self.strategy = QuestionStrategyA
            self.strategy = QuestionStrategyB
        except IndexError:
            self.strategy = QuestionStrategyA
