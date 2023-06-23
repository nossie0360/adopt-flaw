import copy

from .empty_vn_ca import EmptyCostAssessment, EmptyValuedNogood
from .ing_agent_util import IngAgentUtil
from .messages_ing import AddLink, Nogood, Ok, Message
from .cost_assessment import CostAssessment
from .valued_nogood import ValuedNogood
from ..i_agent import IAgent
from ...util.assignment_with_timestamp import AssignmentWithTimestamp

class IngAgent(IngAgentUtil):
    """
    This is ADOPT-D agent (see the paper of ADOPT-ing)
    """
    def __init__(self, xi: int, di: int, D: int, disp: bool = True):
        super().__init__(xi, di, D, disp)

    def initialize(self):
        self._time_stamp = 0
        self._received_terminate = False
        self._outgoing_links = copy.copy(self._lower_neighbor)
        for i, child in enumerate(self._children):
            self._subtree[child.xi] = i
        self._l: dict[int, CostAssessment] = {}
        self._ca: dict[int, dict[int, CostAssessment]] = {}
        self._th: dict[int, ValuedNogood] = {}
        self._h: dict[int, CostAssessment] = {}
        self._lr: dict[int, ValuedNogood] = {}
        self._last_sent: dict[int, ValuedNogood] = {}
        for d in self._D:
            self._ca[d] = {}
            for agent in set(self._all_agents) - set(self._ancestors) - set([self]):
                self._ca[d][agent.xi] = EmptyCostAssessment(d)
            self._l[d] = self.getLocalCostAssessment(d)
            self._h[d] = self.getLocalCostAssessment(d)
        self._di = self.argminCostAssessment(self._h)
        for agent_dst in self._outgoing_links:
            asg = AssignmentWithTimestamp(self._xi, self._di, self._time_stamp)
            tvn = EmptyValuedNogood()
            terminate = False
            self.send(Ok(asg, tvn, terminate), agent_dst)

    def getHeuristicCostAssessment(self, d: int, considered_agents: list[IAgent])\
            -> CostAssessment:
        """
        return a heuristic cost assessment (an element of h[d]) for a variable value d.
        This procedure follows Remark 8 in the paper of ADOPT-ing.
        """
        h = EmptyCostAssessment(d)
        tmp: dict[int, CostAssessment] =\
            { s:EmptyCostAssessment(d) for s in self._subtree.values()}
        for s in tmp:
            for xj in self.getAgentsIdInSameSubtree(s):
                tmp[s] = self.sumInference(tmp[s], self._ca[d][xj])
        for s in tmp:
            h = self.sumInference(h, tmp[s])
        h = self.sumInference(h, self._l[d])
        for child in self._children:
            if self.isEmpty(self._ca[d][child.xi]):
                h.exact = False
        for xj in self._th:
            ca_th = self.transformToCostAssessment(self._th[xj], self._xi, d)
            h = self.sumInference(h, ca_th)
        return h

    def checkAgentVeiew(self):
        for agent_j in sorted(self._ancestors, key=lambda agent: agent.xi):
            for d in self._D:
                prefix_agents = self.getPrefixAgents(self._ancestors, agent_j)
                self._l[d] = self.getPartialLocalCostAssessment(d, prefix_agents)
                self._h[d] = self.getHeuristicCostAssessment(d, prefix_agents)
            if agent_j == self._parent\
                or all([self._h[d].cost > 0 for d in self._D]):
                vn = self.minResolution(agent_j)
                if agent_j.xi not in self._last_sent or vn != self._last_sent[agent_j.xi]:
                    if self.targetId(vn) == agent_j.xi or agent_j == self._parent:
                        ancestors_id = [agent.xi for agent in self._ancestors]
                        self.send(Nogood(vn, self._xi, ancestors_id), agent_j)
                        self._last_sent[agent_j.xi] = vn
        pre_di = self._di
        self._di = self.argminCostAssessment(self._h)
        exact = self._h[self._di].exact
        terminate = exact and (self._received_terminate or self._parent is None)
        if pre_di != self._di or terminate:
            self._time_stamp += 1
            for agent_k in self._outgoing_links:
                self.send(Ok(AssignmentWithTimestamp(self._xi, self._di, self._time_stamp),\
                                self.transformToValuedNogood(\
                                self._ca[self._di][agent_k.xi], self._xi, self._time_stamp),\
                                terminate), agent_k)
            if terminate:
                self._exec_terminate = True

    def discardValuedNogood(self, vn_dict: dict[int, CostAssessment],\
                               asg: AssignmentWithTimestamp) -> dict[int, CostAssessment]:
        """
        discard elements in the given vn_dict based on incompatible assignments with asg.
        The discarded ones are replaced with empty nogoods.
        """
        ret_vn_dict = copy.copy(vn_dict)
        for key in vn_dict:
            if not self.isCompatible([asg], list(vn_dict[key].asg_set)):
                ret_vn_dict[key] = EmptyValuedNogood()
        return ret_vn_dict

    def integrate(self, asg: AssignmentWithTimestamp):
        self._th = self.discardValuedNogood(self._th, asg)
        self._last_sent = self.discardValuedNogood(self._last_sent, asg)
        self._lr = self.discardValuedNogood(self._lr, asg)
        for d in self._D:
            for key in self._ca[d]:
                if not self.isCompatible([asg], list(self._ca[d][key].asg_set)):
                    self._ca[d][key] = \
                        self.transformToCostAssessment(self._lr[key], self.xi, d)
        self.addToAgentView(asg)

    def sumInference(self, ca_one: CostAssessment, ca_two: CostAssessment) -> CostAssessment:
        if ca_one.cost == 0 or ca_two.cost == 0:
            if ca_two.cost == 0:
                ca_ret = ca_one
            else:
                ca_ret = ca_two
            if isinstance(ca_ret, EmptyCostAssessment):
                return EmptyCostAssessment(ca_ret.value)
            else:
                return CostAssessment(ca_ret.src, ca_ret.value, ca_ret.exact,\
                                      ca_ret.cost, ca_ret.asg_set)

        elif ca_one.src.isdisjoint(ca_two.src):
            if self.isCompatible(list(ca_one.asg_set), list(ca_two.asg_set))\
                and ca_one.value == ca_two.value:
                src = ca_one.src.union(ca_two.src)
                value = ca_one.value
                exact = ca_one.exact and ca_two.exact
                cost = ca_one.cost + ca_two.cost
                asg_set = ca_one.asg_set.union(ca_two.asg_set)
                return CostAssessment(src, value, exact, cost, asg_set)
            else:
                return CostAssessment(ca_one.src, ca_one.value, False,\
                                  ca_one.cost, ca_one.asg_set)

        elif ca_one.cost != ca_two.cost:
            return ca_two if ca_one.cost < ca_two.cost else ca_one
        elif self.targetId(ca_one) != self.targetId(ca_two):
            target_one = self.targetId(ca_one)
            target_two = self.targetId(ca_two)
            return ca_two if target_one > target_two else ca_one
        else:
            return ca_one

    def sumInferenceForValuedNogood(self, vn_one: ValuedNogood, vn_two: ValuedNogood):
        ca_one = self.transformToCostAssessment(vn_one, self._xi, self._di)
        ca_two = self.transformToCostAssessment(vn_two, self._xi, self._di)
        ca_ret = self.sumInference(ca_one, ca_two)
        return self.transformToValuedNogood(ca_ret, self._xi, self._time_stamp)

    def minResolution(self, agent_j: IAgent) -> ValuedNogood:
        considered_agents = self.getPrefixAgents(self._ancestors, agent_j)
        considered_h = [ca for ca in self._h.values()\
                        if self.isComposedOnlyOfConsideredAgents(ca, considered_agents)]
        for ca_one in considered_h:
            for ca_two in considered_h:
                if not self.isCompatible(list(ca_one.asg_set), list(ca_two.asg_set)):
                    return EmptyValuedNogood()
        if len(considered_h) > 0:
            src = set()
            exact = False
            cost = min([ca.cost for ca in considered_h])
            asg_set = set()
            for ca in considered_h:
                src = src.union(ca.src)
                asg_set = asg_set.union(ca.asg_set)
                if ca.cost == cost:
                    exact = exact or ca.exact
            return ValuedNogood(src, exact, cost, asg_set)
        else:
            return EmptyValuedNogood()

    def receiveOk(self, ok_msg: Ok):
        if self.isNewAssignment(ok_msg.asg, self._agent_view):
            self.integrate(ok_msg.asg)
        if not self.isEmpty(ok_msg.tvn)\
            and self.isCompatible(self._agent_view, list(ok_msg.tvn.asg_set)):
            k = self.targetId(ok_msg.tvn)
            self._th[k] = self.sumInferenceForValuedNogood(ok_msg.tvn, self._th[k])\
                            if k in self._th else ok_msg.tvn
        if ok_msg.from_xi == self._parent.xi and ok_msg.terminate:
            self._received_terminate = True
        self.checkAgentVeiew()

    def receiveAddLink(self, add_link_msg: AddLink):
        new_agent = self.getAgent(add_link_msg.from_xi, self._all_agents)
        self._outgoing_links.append(new_agent)
        my_asg = AssignmentWithTimestamp(self._xi, self._di, self._time_stamp)
        if not self.isCompatible([my_asg], [add_link_msg.asg]):
            tvn = EmptyValuedNogood()
            terminate = False
            self.send(Ok(my_asg, tvn, terminate), new_agent)

    def receiveNogood(self, nogood_msg: Nogood):
        if nogood_msg.xi not in self._subtree.keys():   # update the list of subtree
            for child in self.children:
                if child.xi in nogood_msg.induced_links:
                    self._subtree[nogood_msg.xi] = self._subtree[child.xi]
        view_updated = False
        for asg in nogood_msg.rvn.asg_set:
            if self.isNewAssignment(asg, self._agent_view) and asg.xi != self._xi:
                self.integrate(asg)
                view_updated = True
        self._lr[nogood_msg.xi] = copy.deepcopy(nogood_msg.rvn)
        if not self.isCompatible(self._agent_view, list(nogood_msg.rvn.asg_set)):
            if view_updated:
                self.checkAgentVeiew()
            return
        for asg in nogood_msg.rvn.asg_set:
            if asg.xi not in [agent.xi for agent in self._neighbor]\
                and asg.xi != self._xi:
                dst_agent = self.getAgent(asg.xi, self._all_agents)
                self.send(AddLink(asg), dst_agent)       # need the agent object
        for d in self._D:
            rca = self.transformToCostAssessment(nogood_msg.rvn, self._xi, d)
            if not self.isEmpty(rca):
                pre_ca = copy.deepcopy(self._ca[d][nogood_msg.xi])
                self._ca[d][nogood_msg.xi] =\
                    self.sumInference(rca, self._ca[d][nogood_msg.xi])
                h = self.getHeuristicCostAssessment(d, self._ancestors)
                if h.cost >= self._h[d].cost:
                    self._h[d] = h
                else:
                    self._ca[d][nogood_msg.xi] = pre_ca
        self.checkAgentVeiew()

    def receive(self, msg: Message):
        if isinstance(msg, Ok):
            if self._disp:       # <DISP>
                print("{} receives [Ok]".format(self._xi))
                print(msg)  ####
            return self.receiveOk(msg)
        if isinstance(msg, AddLink):
            if self._disp:       # <DISP>
                print("{} receives [AddLink]".format(self._xi))
                print(msg)  ####
            return self.receiveAddLink(msg)
        if isinstance(msg, Nogood):
            if self._disp:       # <DISP>
                print("{} receives [Nogood]".format(self._xi))
                print(msg)  ####
            return self.receiveNogood(msg)