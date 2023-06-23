import unittest

from src.module.agents.adopt.original_agent import OriginalAgent
from tests.test_algorithms_solve_dcop.exec_dcop.adopt_example_graph.adopt_example_graph_exec import AdoptExampleGraphExec
from tests.test_algorithms_solve_dcop.exec_dcop.util.execution_manager_for_test import ExecutionManagerForTest
from tests.test_algorithms_solve_dcop.exec_dcop.complete_graph.complete_graph_exec import CompleteGraphExec

class TestOriginalAgentSolveDcop(unittest.TestCase):
    def setUp(self):
        self.agent_class = OriginalAgent

    def test_complete_graph(self):
        exec_collection = CompleteGraphExec(self.agent_class)
        exec_manager = ExecutionManagerForTest(
            exec_collection.init_agents,
            exec_collection.init_functions,
            exec_collection.exec_cycle
        )
        ret_solution, ret_cost = exec_manager.exec()
        expected_solution = exec_collection.optimal_solution
        expected_cost = exec_collection.optimal_cost
        self.assertEqual(ret_solution, expected_solution)
        self.assertEqual(ret_cost, expected_cost)

    def test_adopt_example_graph(self):
        exec_collection = AdoptExampleGraphExec(self.agent_class)
        exec_manager = ExecutionManagerForTest(
            exec_collection.init_agents,
            exec_collection.init_functions,
            exec_collection.exec_cycle
        )
        ret_solution, ret_cost = exec_manager.exec()
        expected_solution = exec_collection.optimal_solution
        expected_cost = exec_collection.optimal_cost
        self.assertEqual(ret_solution, expected_solution)
        self.assertEqual(ret_cost, expected_cost)

if __name__ == "__main__":
    unittest.main()