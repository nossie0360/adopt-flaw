from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .function import Function
    from ..agents.i_agent import IAgent

class DFS:
    def getDFS(nodes: list["IAgent"], edges: list[Function]):
        """
        After running addFunciton()
        nodes' indices must be corresponding with agents' xi (id)
        """
        visited = {}
        inTree = {}
        for node in nodes:
            visited[node] = False
            node.depth = 0
        for edge in edges:
            inTree[edge] = False

        def DFS(V:list["IAgent"], E: list[Function], s: "IAgent"):
            visited[s] = True
            for e in E:
                isNotVisitedEdge = False
                if e.sp == s and not visited[e.ep]:
                    w = e.ep
                    isNotVisitedEdge = True
                elif e.ep == s and not visited[e.sp]:
                    w = e.sp
                    isNotVisitedEdge = True

                if isNotVisitedEdge:
                    s.children.append(w)
                    s.neighbor.append(w)
                    s.lower_neighbor.append(w)
                    w.parent = s
                    w.neighbor.append(s)
                    w.ancestors = s.ancestors + [s]
                    w.depth = s.depth + 1
                    inTree[e] = True
                    DFS(V, E, w)

        # create DFS tree
        for node in nodes:
            if not visited[node]:
                DFS(nodes, edges, node)

        # complete pseudo-tree
        for node in nodes:
            processed: list["IAgent"] = []
            if node.parent is None:
                todo = [node]
                while len(todo) > 0:
                    v = todo.pop(0)
                    for child in v.children:
                        todo.append(child)
                    for fn in v.fset:
                        if not inTree[fn]:
                            w = fn.sp
                            if w == v: w = fn.ep
                            v.lower_neighbor.append(w)
                            v.neighbor.append(w)
                            w.neighbor.append(v)
                            inTree[fn] = True
                    processed.insert(0, v)
            for v in processed:
                v.scp = list(set(v.scp).union(set(v.neighbor) - set(v.lower_neighbor)))
                if v.parent is not None:
                    v.parent.scp = list(set(v.parent.scp).union(set(v.scp) - {v.parent}))

        # update depth_tree
        depth_tree = max(nodes, key=lambda v: v.depth).depth
        for node in nodes:
            node.depth_tree = depth_tree

        # sort based on id
        for node in nodes:
            node.children.sort(key=lambda x: x.xi)
            node.neighbor.sort(key=lambda x: x.xi)
            node.lower_neighbor.sort(key=lambda x: x.xi)
            node.ancestors.sort(key=lambda x: x.xi)
            node.scp.sort(key=lambda x: x.xi)