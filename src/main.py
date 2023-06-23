from module.exec.execution_manager import ExecutionManager
from module.agents.adopt.modified_agent import ModifiedAgent
from module.agents.adopt.original_agent import OriginalAgent
from module.agents.adopt_plus.plus_agent import PlusAgent
from module.agents.idb_adopt.idb_agent import IdbAgent
from module.agents.bnb_adopt.bnb_agent import BnbAgent
from module.agents.bnb_adopt_plus.bnb_plus_agent import BnbPlusAgent
from module.agents.adopt_k.k_agent import KAgent
from module.agents.bd_adopt.bd_agent import BdAgent
from module.agents.adopt_ing.ing_agent import IngAgent

from module.exec.counterexample.optimality_initialization.optimality_initialization_exec \
    import OptimalityInitializationExec
from module.exec.counterexample.optimality_terminate.optimality_terminate_exec \
    import OptimalityTerminateExec
from module.exec.counterexample.termination.termination_exec import TerminationExec
from module.exec.counterexample.termination_without_redundant.termination_without_redundant_exec \
    import TerminationWithoutRedundantExec

if __name__ == "__main__":

    agent_class = IdbAgent
    exec_collection = TerminationWithoutRedundantExec(agent_class)
    obj = ExecutionManager(exec_collection.init_agents,
                        exec_collection.init_functions,
                        exec_collection.exec_cycle)
    obj.exec()