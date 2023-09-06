import time
from typing import Tuple

import aux_functions

from skip_theory import TheoryStrategy


class TheorySolveStrategy:
    def __init__(self, strategy: TheoryStrategy):
        """Set strategy"""
        self.strategy = strategy

    def do_work(self):
        self.strategy.skip_theory()
