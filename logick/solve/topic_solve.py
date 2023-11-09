from logick.strat.topic_solve import TopicSolveStrategy, TopicStrategyA


class TopicSolve:

    @staticmethod
    def main(topic_name: str):
        TopicSolveStrategy(TopicStrategyA).do_work(topic_name)
