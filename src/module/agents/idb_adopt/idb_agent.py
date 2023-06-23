import numpy as np

from ..adopt.original_agent import OriginalAgent
from ..adopt.messages_origin import Threshold

class IdbAgent(OriginalAgent):
    def initialize_root(self, root_threshold: int):
        self._exec_terminate = False
        self._terminate = False
        self._threshold = root_threshold
        if root_threshold < 0:
            self._threshold = 0
        self._b = 0
        self._CurrentContext = []
        self._lb = {}; self._ub = {}; self._t = {}; self._context = {}
        for d in self._D:
            self._lb[d] = {}; self._ub[d] = {}; self._t[d] = {}; self._context[d] = {}
            for child in self._children:
                xl = child.xi
                self._lb[d][xl] = 0
                self._ub[d][xl] = np.inf
                self._t[d][xl] = 0
                self._context[d][xl] = []
        self._di = self.argminLB_d()
        self.backTrack()

    # For the counterexamle to termination without redundant messages,
    # children loop is reversed from the original ADOPT.
    # This modification does not affect the algorithm itself essentially.
    def maintainAllocationInvariant(self):
        delta = self.delta(self._di)
        sum_t = 0
        for child in self._children:
            sum_t = sum_t + self._t[self._di][child.xi]

        while self._threshold > delta + sum_t:
            for child in reversed(self._children):
                if self._ub[self._di][child.xi] > self._t[self._di][child.xi]:
                    self._t[self._di][child.xi] = self._t[self._di][child.xi] + 1
                    sum_t = sum_t + 1      # because t++
                    break
        while self._threshold < delta + sum_t:
            for child in reversed(self._children):
                if self._t[self._di][child.xi] > self._lb[self._di][child.xi]:
                    self._t[self._di][child.xi] = self._t[self._di][child.xi] - 1
                    sum_t = sum_t - 1      # because t--
                    break
        for dst in self._children:
            self.send(Threshold(self._t[self._di][dst.xi], self._CurrentContext), dst)