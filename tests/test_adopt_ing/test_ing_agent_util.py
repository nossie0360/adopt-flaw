import unittest

from src.module.agents.adopt_ing.empty_vn_ca import EmptyCostAssessment, EmptyValuedNogood
from src.module.agents.adopt_ing.ing_agent_util import IngAgentUtil
from src.module.agents.adopt_ing.cost_assessment import CostAssessment
from src.module.agents.adopt_ing.valued_nogood import ValuedNogood
from src.module.agents.adopt_ing.messages_ing import AddLink, Nogood, Ok
from src.module.agents.util.message_queue import MessageQueue
from src.module.agents.i_agent import IAgent
from src.module.util.assignment import Assignment
from src.module.util.assignment_with_timestamp import AssignmentWithTimestamp
from src.module.util.function import Function, IdCounter
from src.module.util.abstract_messages import Message

class IngAgentUtilWrapper(IngAgentUtil):
    def __init__(self, xi: int, di: int, D: int, disp: bool = True):
        super().__init__(xi, di, D, disp)

    def initialize(self):
        pass

    def receive(self, msg: Message) -> None:
        pass

class TestIngAgentUtil(unittest.TestCase):
    def setUp(self):
        self._ing_agent_util = IngAgentUtilWrapper(0, 0, [0, 1, 2], False)

    def testGetAgent(self):
        agent_1 = IngAgentUtilWrapper(1, 0, [0, 1, 2], False)
        agent_2 = IngAgentUtilWrapper(2, 0, [0, 1, 2], False)
        agent_3 = IngAgentUtilWrapper(3, 0, [0, 1, 2], False)
        agent_list = [agent_1, agent_2, agent_3]
        ret = self._ing_agent_util.getAgent(2, agent_list)
        self.assertEqual(ret, agent_2)

    def testGetAssignment(self):
        asg_list = [AssignmentWithTimestamp(0, 1, 1),
                    AssignmentWithTimestamp(1, 3, 2),
                    AssignmentWithTimestamp(2, 5, 3)]
        ret = self._ing_agent_util.getAssignment(asg_list, 1)
        self.assertEqual(ret, 3)

    def testIsNewAssignmentTrue(self):
        asg_list = [AssignmentWithTimestamp(0, 1, 1),
                    AssignmentWithTimestamp(1, 3, 2),
                    AssignmentWithTimestamp(2, 5, 3)]
        asg = AssignmentWithTimestamp(0, 2, 2)
        ret = self._ing_agent_util.isNewAssignment(asg, asg_list)
        self.assertTrue(ret)

    def testIsNewAssignmentFalse(self):
        asg_list = [AssignmentWithTimestamp(0, 1, 1),
                    AssignmentWithTimestamp(1, 3, 2),
                    AssignmentWithTimestamp(2, 5, 3)]
        asg = AssignmentWithTimestamp(1, 2, 1)
        ret = self._ing_agent_util.isNewAssignment(asg, asg_list)
        self.assertFalse(ret)

    def testIsNewAssignmentTrueNotIn(self):
        asg_list = [AssignmentWithTimestamp(0, 1, 1),
                    AssignmentWithTimestamp(1, 3, 2),
                    AssignmentWithTimestamp(2, 5, 3)]
        asg = AssignmentWithTimestamp(3, 2, 2)
        ret = self._ing_agent_util.isNewAssignment(asg, asg_list)
        self.assertTrue(ret)

    def testRemoveAssignment(self):
        asg_list = [AssignmentWithTimestamp(0, 1, 1),
                    AssignmentWithTimestamp(1, 3, 2),
                    AssignmentWithTimestamp(2, 5, 3)]
        ret = self._ing_agent_util.removeAssignment(asg_list, 0)
        expected = [AssignmentWithTimestamp(1, 3, 2),
                    AssignmentWithTimestamp(2, 5, 3)]
        self.assertEqual(ret, expected)

    def testAddToAgentView(self):
        self._ing_agent_util._agent_view = []
        asg = AssignmentWithTimestamp(0, 1, 2)
        self._ing_agent_util.addToAgentView(asg)
        self.assertEqual(self._ing_agent_util._agent_view, [asg])

    def testIsCompatibleTrue(self):
        view_one = [AssignmentWithTimestamp(0, 1, 1),
                    AssignmentWithTimestamp(1, 3, 2),
                    AssignmentWithTimestamp(2, 5, 3)]
        view_two = [AssignmentWithTimestamp(0, 1, 3),
                    AssignmentWithTimestamp(1, 3, 1),
                    AssignmentWithTimestamp(3, 2, 4)]
        ret = self._ing_agent_util.isCompatible(view_one, view_two)
        self.assertTrue(ret)

    def testIsCompatibleFalse(self):
        view_one = [AssignmentWithTimestamp(0, 1, 1),
                    AssignmentWithTimestamp(1, 3, 2),
                    AssignmentWithTimestamp(2, 5, 3)]
        view_two = [AssignmentWithTimestamp(0, 1, 3),
                    AssignmentWithTimestamp(1, 3, 1),
                    AssignmentWithTimestamp(2, 2, 4)]
        ret = self._ing_agent_util.isCompatible(view_one, view_two)
        self.assertFalse(ret)

    def testIsEmptyCostAssessmentTrue(self):
        ca = EmptyCostAssessment(0)
        ret = self._ing_agent_util.isEmpty(ca)
        self.assertTrue(ret)

    def testIsEmptyCostAssessmentFalse(self):
        ca = CostAssessment({1, 2}, 0, False, 0, set())
        ret = self._ing_agent_util.isEmpty(ca)
        self.assertFalse(ret)

    def testIsEmptyNogoodTrue(self):
        vn = EmptyValuedNogood()
        ret = self._ing_agent_util.isEmpty(vn)
        self.assertTrue(ret)

    def testIsEmptyNogoodFalse(self):
        vn = ValuedNogood({1, 2}, False, 0, set())
        ret = self._ing_agent_util.isEmpty(vn)
        self.assertFalse(ret)

    def testTargetIdCostAssessment(self):
        asg_set = {AssignmentWithTimestamp(0, 1, 1),
                    AssignmentWithTimestamp(1, 3, 2),
                    AssignmentWithTimestamp(2, 5, 3)}
        ca = CostAssessment({1, 2, 3}, 0, False, 0, asg_set)
        ret = self._ing_agent_util.targetId(ca)
        self.assertEqual(ret, 2)

    def testTargetIdCostAssessmentEmpty(self):
        asg_set = set()
        ca = CostAssessment({1, 2, 3}, 0, False, 0, asg_set)
        ret = self._ing_agent_util.targetId(ca)
        self.assertEqual(ret, -1)

    def testTargetIdNogood(self):
        asg_set = {AssignmentWithTimestamp(0, 1, 1),
                    AssignmentWithTimestamp(1, 3, 2),
                    AssignmentWithTimestamp(2, 5, 3)}
        vn = ValuedNogood({1, 2, 3}, False, 0, asg_set)
        ret = self._ing_agent_util.targetId(vn)
        self.assertEqual(ret, 2)

    def testTargetIdNogoodEmpty(self):
        asg_set = set()
        vn = ValuedNogood({1, 2, 3}, False, 0, asg_set)
        ret = self._ing_agent_util.targetId(vn)
        self.assertEqual(ret, -1)

    def testTargetIdCostAssessmentTrue(self):
        asg_set = {AssignmentWithTimestamp(0, 1, 1),
                    AssignmentWithTimestamp(1, 3, 2),
                    AssignmentWithTimestamp(2, 5, 3)}
        ca = CostAssessment({1, 2, 3}, 0, False, 0, asg_set)
        ret = self._ing_agent_util.targetId(ca)
        self.assertEqual(ret, 2)

    def testGetAgentsIdInSameSubtree(self):
        self._ing_agent_util._subtree = {0: 1, 1: 2, 2: 1}
        ret = self._ing_agent_util.getAgentsIdInSameSubtree(1)
        self.assertEqual(ret, [0, 2])

    def testGetCost(self):
        ca = CostAssessment(set(), 0, False, 10, set())
        ret = self._ing_agent_util.getCost(ca)
        self.assertEqual(ret, 10)

    def testTransformToValuedNogood(self):
        src = {1, 2}
        value = 10
        exact = False
        cost = 5
        asg_set = {AssignmentWithTimestamp(0, 1, 1)}
        ca = CostAssessment(src, value, exact, cost, asg_set)
        ret = self._ing_agent_util.transformToValuedNogood(ca, 1, 3)
        expect_asg_set = {AssignmentWithTimestamp(0, 1, 1),
                          AssignmentWithTimestamp(1, 10, 3)}
        expect = ValuedNogood(src, exact, cost, expect_asg_set)
        self.assertEqual(ret, expect)

    def testTransformToValuedNogoodEmpty(self):
        ca = EmptyCostAssessment(1)
        ret = self._ing_agent_util.transformToValuedNogood(ca, 1, 3)
        expect = EmptyValuedNogood()
        self.assertEqual(ret, expect)

    def testTransformToCostAssessment(self):
        src = {1, 2}
        exact = False
        cost = 5
        asg_set = {AssignmentWithTimestamp(0, 1, 1),
                   AssignmentWithTimestamp(1, 10, 3)}
        ca = ValuedNogood(src, exact, cost, asg_set)
        ret = self._ing_agent_util.transformToCostAssessment(ca, 1, 10)
        expect_asg_set = {AssignmentWithTimestamp(0, 1, 1)}
        expect = CostAssessment(src, 10, exact, cost, expect_asg_set)
        self.assertEqual(ret, expect)

    def testTransformToCostAssessmentEmpty(self):
        ca = EmptyValuedNogood()
        ret = self._ing_agent_util.transformToCostAssessment(ca, 1, 10)
        expect = EmptyCostAssessment(10)
        self.assertEqual(ret, expect)

    def testTransformToCostAssessmentDifferentValue(self):
        src = {1, 2}
        exact = False
        cost = 5
        asg_set = {AssignmentWithTimestamp(0, 1, 1),
                   AssignmentWithTimestamp(1, 10, 3)}
        ca = ValuedNogood(src, exact, cost, asg_set)
        ret = self._ing_agent_util.transformToCostAssessment(ca, 1, 5)
        expect = EmptyCostAssessment(5)
        self.assertEqual(ret, expect)

    def testArgminCostAssessment(self):
        ca_0 = CostAssessment({1, 2}, 0, False, 10, {AssignmentWithTimestamp(0, 1, 1)})
        ca_1 = CostAssessment({1, 2}, 0, False, 1, {AssignmentWithTimestamp(0, 1, 1)})
        ca_dict = {0: ca_0, 1: ca_1}
        ret = self._ing_agent_util.argminCostAssessment(ca_dict)
        self.assertEqual(ret, 1)

    def testMinCostAssessment(self):
        ca_0 = CostAssessment({1, 2}, 0, False, 10, {AssignmentWithTimestamp(0, 1, 1)})
        ca_1 = CostAssessment({1, 2}, 0, False, 1, {AssignmentWithTimestamp(0, 1, 1)})
        ca_dict = {0: ca_0, 1: ca_1}
        ret = self._ing_agent_util.minCostAssessment(ca_dict)
        self.assertEqual(ret, ca_1)

    def testGetLocalCostAssessment(self):
        f_set = [Function(self._ing_agent_util,
                          IngAgentUtilWrapper(1, 1, [1, 2], False),
                          lambda x, y: x + y),
                 Function(self._ing_agent_util,
                          IngAgentUtilWrapper(2, 1, [1, 2], False),
                          lambda x, y: x + y)]
        agent_view = [AssignmentWithTimestamp(1, 1, 2),
                      AssignmentWithTimestamp(2, 1, 2)]
        self._ing_agent_util._fset = f_set
        self._ing_agent_util._agent_view = agent_view
        ret = self._ing_agent_util.getLocalCostAssessment(2)
        expect = CostAssessment({1, 2}, 2, True, 6, set(agent_view))
        self.assertEqual(ret, expect)

    def testGetLocalCostAssessmentExactFalse(self):
        f_set = [Function(self._ing_agent_util,
                          IngAgentUtilWrapper(1, 1, [1, 2], False),
                          lambda x, y: x + y),
                 Function(self._ing_agent_util,
                          IngAgentUtilWrapper(2, 1, [1, 2], False),
                          lambda x, y: x + y)]
        agent_view = [AssignmentWithTimestamp(1, 1, 2)]
        self._ing_agent_util._fset = f_set
        self._ing_agent_util._agent_view = agent_view
        ret = self._ing_agent_util.getLocalCostAssessment(2)
        expect = CostAssessment({1}, 2, False, 3, set(agent_view))
        self.assertEqual(ret, expect)

    def testGetPartialLocalCostFunctions(self):
        agent_1 = IngAgentUtilWrapper(1, 1, [1, 2], False)
        agent_2 = IngAgentUtilWrapper(2, 1, [1, 2], False)
        agent_3 = IngAgentUtilWrapper(3, 1, [1, 2], False)
        func_1 = Function(self._ing_agent_util, agent_1, lambda x, y: x + y)
        func_2 = Function(self._ing_agent_util, agent_2, lambda x, y: x + y)
        func_3 = Function(self._ing_agent_util, agent_3, lambda x, y: x + y)
        f_set = [func_1, func_2, func_3]
        self._ing_agent_util._fset = f_set
        considered_agents = [agent_1, agent_2]
        ret = self._ing_agent_util.getPartialLocalCostFunctions(considered_agents)
        self.assertEqual(ret, [func_1, func_2])

    def getPartialAgentView(self, agent_view: list[AssignmentWithTimestamp],\
                            considered_agents: list[IAgent]):
        considered_id = [agent.xi for agent in considered_agents]
        return [asg for asg in agent_view if asg.xi in considered_id]

    def testGetPartialAgentView(self):
        agent_1 = IngAgentUtilWrapper(1, 1, [1, 2], False)
        agent_3 = IngAgentUtilWrapper(3, 1, [1, 2], False)
        agent_view = [AssignmentWithTimestamp(1, 1, 1),
                      AssignmentWithTimestamp(2, 2, 2),
                      AssignmentWithTimestamp(3, 3, 3)]
        considered_agents = [agent_1, agent_3]
        ret = self.getPartialAgentView(agent_view, considered_agents)
        expect = [AssignmentWithTimestamp(1, 1, 1),
                    AssignmentWithTimestamp(3, 3, 3)]
        self.assertEqual(ret, expect)

    def testGetPartialLocalCostAssessment(self):
        agent_1 = IngAgentUtilWrapper(1, 1, [1, 2], False)
        agent_2 = IngAgentUtilWrapper(2, 1, [1, 2], False)
        agent_3 = IngAgentUtilWrapper(3, 1, [1, 2], False)
        f_set = [Function(self._ing_agent_util,
                          agent_1,
                          lambda x, y: x + y),
                 Function(self._ing_agent_util,
                          agent_2,
                          lambda x, y: x + y),
                 Function(self._ing_agent_util,
                          agent_3,
                          lambda x, y: x + y)]
        agent_view = [AssignmentWithTimestamp(1, 1, 2),
                      AssignmentWithTimestamp(2, 1, 2),
                      AssignmentWithTimestamp(3, 1, 2)]
        considered_agents = [agent_1, agent_2]
        self._ing_agent_util._fset = f_set
        self._ing_agent_util._agent_view = agent_view
        ret = self._ing_agent_util.getPartialLocalCostAssessment(2, considered_agents)
        expect_agent_view = [AssignmentWithTimestamp(1, 1, 2),
                            AssignmentWithTimestamp(2, 1, 2)]
        expect = CostAssessment({1, 2}, 2, True, 6, set(expect_agent_view))
        self.assertEqual(ret, expect)

    def testGetPartialLocalCostAssessmentExactFalse(self):
        agent_1 = IngAgentUtilWrapper(1, 1, [1, 2], False)
        agent_2 = IngAgentUtilWrapper(2, 1, [1, 2], False)
        agent_3 = IngAgentUtilWrapper(3, 1, [1, 2], False)
        f_set = [Function(self._ing_agent_util,
                          agent_1,
                          lambda x, y: x + y),
                 Function(self._ing_agent_util,
                          agent_2,
                          lambda x, y: x + y),
                 Function(self._ing_agent_util,
                          agent_3,
                          lambda x, y: x + y)]
        agent_view = [AssignmentWithTimestamp(1, 1, 2),
                      AssignmentWithTimestamp(3, 1, 2)]
        considered_agents = [agent_1, agent_2]
        self._ing_agent_util._fset = f_set
        self._ing_agent_util._agent_view = agent_view
        ret = self._ing_agent_util.getPartialLocalCostAssessment(2, considered_agents)
        expect_agent_view = [AssignmentWithTimestamp(1, 1, 2)]
        expect = CostAssessment({1}, 2, False, 3, set(expect_agent_view))
        self.assertEqual(ret, expect)

    def testIsComposedOnlyOfConsideredAgentCostAssessmentTrue(self):
        agent_1 = IngAgentUtilWrapper(1, 1, [1, 2], False)
        agent_2 = IngAgentUtilWrapper(2, 1, [1, 2], False)
        agent_3 = IngAgentUtilWrapper(3, 1, [1, 2], False)
        asg_set = {AssignmentWithTimestamp(1, 0, 1),
                   AssignmentWithTimestamp(2, 0, 2)}
        ca = CostAssessment({1, 2}, 0, False, 1, asg_set)
        considered_agents = [agent_1, agent_2]
        ret = self._ing_agent_util.isComposedOnlyOfConsideredAgents(ca, considered_agents)
        self.assertTrue(ret)

    def testIsComposedOnlyOfConsideredAgentCostAssessmentFalse(self):
        agent_1 = IngAgentUtilWrapper(1, 1, [1, 2], False)
        agent_2 = IngAgentUtilWrapper(2, 1, [1, 2], False)
        agent_3 = IngAgentUtilWrapper(3, 1, [1, 2], False)
        asg_set = {AssignmentWithTimestamp(1, 0, 1),
                   AssignmentWithTimestamp(2, 0, 2)}
        ca = CostAssessment({1, 2}, 0, False, 1, asg_set)
        considered_agents = [agent_1, agent_3]
        ret = self._ing_agent_util.isComposedOnlyOfConsideredAgents(ca, considered_agents)
        self.assertFalse(ret)

    def testIsComposedOnlyOfConsideredAgentValuedNogoodTrue(self):
        agent_1 = IngAgentUtilWrapper(1, 1, [1, 2], False)
        agent_2 = IngAgentUtilWrapper(2, 1, [1, 2], False)
        agent_3 = IngAgentUtilWrapper(3, 1, [1, 2], False)
        asg_set = {AssignmentWithTimestamp(1, 0, 1),
                   AssignmentWithTimestamp(2, 0, 2)}
        vn = ValuedNogood({1, 2}, False, 1, asg_set)
        considered_agents = [agent_1, agent_2]
        ret = self._ing_agent_util.isComposedOnlyOfConsideredAgents(vn, considered_agents)
        self.assertTrue(ret)

    def testIsComposedOnlyOfConsideredAgentValuedNogoodFalse(self):
        agent_1 = IngAgentUtilWrapper(1, 1, [1, 2], False)
        agent_2 = IngAgentUtilWrapper(2, 1, [1, 2], False)
        agent_3 = IngAgentUtilWrapper(3, 1, [1, 2], False)
        asg_set = {AssignmentWithTimestamp(1, 0, 1),
                   AssignmentWithTimestamp(2, 0, 2)}
        vn = ValuedNogood({1, 2}, False, 1, asg_set)
        considered_agents = [agent_1, agent_3]
        ret = self._ing_agent_util.isComposedOnlyOfConsideredAgents(vn, considered_agents)
        self.assertFalse(ret)

    def testGetPrefixAgents(self):
        agent_1 = IngAgentUtilWrapper(1, 1, [1, 2], False)
        agent_2 = IngAgentUtilWrapper(2, 1, [1, 2], False)
        agent_3 = IngAgentUtilWrapper(3, 1, [1, 2], False)
        agent_4 = IngAgentUtilWrapper(4, 1, [1, 2], False)
        agents_list = [agent_1, agent_4, agent_3, agent_2]
        ret = self._ing_agent_util.getPrefixAgents(agents_list, agent_3)
        expect = [agent_1, agent_2, agent_3]
        self.assertEqual(ret, expect)

    def tearDown(self):
        IdCounter.resetId()

if __name__ == "__main__":
    unittest.main()