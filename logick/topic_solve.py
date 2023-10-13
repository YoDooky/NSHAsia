from logick.strat.strategy import TopicSolveStrategy
from logick.strat.topic_solve import TopicStrategyA


class TopicSolve:

    @staticmethod
    def main():
        TopicSolveStrategy(TopicStrategyA).do_work()
