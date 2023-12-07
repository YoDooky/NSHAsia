from app_types import TopicData
from logick.strat.topic_solve import TopicSolveStrategy, TopicStrategyA


class TopicSolve:

    @staticmethod
    def main(topic_data: TopicData):
        TopicSolveStrategy(TopicStrategyA).do_work(topic_data)
