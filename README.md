# ADOPT-Flaw
This repository provides the implementation of
counterexamples to ADOPT-based algorithms
and the modified version of ADOPT,
both of which are shown in the following paper.
See the paper for more details.
> Koji Noshiro and Koji Hasebe. Flaws of Termination and Optimality in ADOPT-based Algorithms, 32nd International Joint Conference on Artificial Intelligence (IJCAI-23), 8 pages, August 2023.

## Prequisities
* Python 3.9.13 or later

## Getting Started
1. Clone this repository.
    ```
    $ git clone https://github.com/nossie0360/adopt-flaw.git
    ```

1. Move to the cloned directory.
    ```
    $ cd adopt-flaw
    ```

1. Install the required packages.
    ```
    $ pip install -r requirements.txt
    ```

## Usage
`src/main.py` executes the selected algorithm
using the trace of the selected counterexample.
The algorithm and counterexample can be set by modifying
the classes given to `agent_class` and `exec_collection`, respectively.
```python
agent_class = ModifiedAgent # The algorithm to run
exec_collection = TerminationExec(agent_class) # The counterexample to run
```

The classes for `agent_class` correspond to the implemented algorithm as follows:

|`agent_class`|Algorithm|
|:-|:-|
|`ModifiedAgent`|Modified version of ADOPT|
|`OriginalAgent`|Original ADOPT [1]|
|`PlusAgent`|ADOPT+ [2]|
|`IdbAgent`|IDB-ADOPT [3]|
|`BnbAgent`|BnB-ADOPT [4]|
|`BnbPlusAgent`|BnB-ADOPT+ [3]|
|`KAgent`|ADOPT-k [5]|
|`BdAgent`|BD-ADOPT [6]|
|`IngAgent`|ADOPT-ing [7]|

The classes for `exec_collection` correspond to the counterexamples as follows:

|`exec_collection`|Counterexample|
|:-|:-|
|`TerminationExec`|to Termination|
|`TerminationWithoutRedundantExec`|to Termination (without Redundant Messages)|
|`OptimalityInitializationExec`|to Optimality Caused by Initialization|
|`OptimalityTerminateExec`|to Optimality Caused by TERMINATE Messages|

After setting the classes, run `src/main.py`.
```
$ python3 src/main.py
```

### Bounded-Error Approximation of ADOPT
If you want to enable the bounded-error approximation of ADOPT
(including the modified version),
you must change the value of error bound `self._b`
in `OriginalAgent` (or `ModifiedAgent`).
The definition is in
`src/module/agents/adopt/original_agent.py (or modified_agent.py)`.

### Change for Cost Functions
You can modify the cost functions of the DCOPs,
which especially needs for running ADOPT-ing.
The class `InitFunctions` in each
`src/module/counterexample/<Counterexample Type>/init_functions.py`
defines the cost functions in the corresponding counterexample.
If you want to add constant values to all costs,
it is enough just to change the value of `c`
in the class.

## License
The source code is licensed MIT, see `LICENSE`.

## References
* [1] P. J. Modi, W.-M. Shen, M. Tambe, M. Yokoo, Adopt: Asynchronous distributed constraint optimization with
quality guarantees, Artificial Intelligence 161 (1-2) (2005) 149–180. doi:10.1016/j.artint.2004.09.003.

* [2] P. Gutierrez, P. Meseguer, Saving messages in ADOPT-based algorithms, in: AAMAS 2010 Workshop: Distributed Constraint Reasoning, Toronto, Canada, 2010, pp. 53–64.

* [3] W. Yeoh, A. Felner, S. Koenig, IDB-ADOPT: A depth-first search DCOP algorithm, in: A. Oddi, F. Fages,
F. Rossi (Eds.), Recent Advances in Constraints, Vol. 5655 of Lecture Notes in Artificial Intelligence, Springer,
Rome, Italy, 2009, pp. 132–146. doi:10.1007/978-3-642-03251-6_9.

* [4] W. Yeoh, A. Felner, S. Koenig, BnB-ADOPT: An asynchronous branch-and-bound DCOP algorithm, Journal
of Artificial Intelligence Research 38 (2010) 85–133. doi:10.1613/jair.2849.

* [5] P. Gutierrez, P. Meseguer, W. Yeoh, Generalizing ADOPT and BnB-ADOPT, in: T. Walsh (Ed.), Proceedings
of the 22nd International Joint Conference on Artificial Intelligence, Barcelona, Catalonia, Spain, 2011, pp.
554–559. doi:10.5591/978-1-57735-516-8/IJCAI11-100.

* [6] Z. Chen, C. He, Z. He, M. Chen, BD-ADOPT: A hybrid DCOP algorithm with best-first and depth-first search
strategies, Artificial Intelligence Review 50 (2) (2018) 161–199. doi:10.1007/s10462-017-9540-z.

* [7] M. C. Silaghi, M. Yokoo, ADOPT-ing: Unifying asynchronous distributed optimization with asyn-
chronous backtracking, Autonomous Agents and Multi-Agent Systems 19 (2) (2009) 89–123. doi:10.1007/
s10458-008-9069-2.
