from util import generate_instance, construct_DG
from show_arrangement import show_arrangement

import math
import networkx as nx
from itertools import combinations
import gurobipy as grb
from Labeled_Experiment_Multi_Layer import show_digraph

def Labeled_Experiment(numObjs, Density, Height=1000, Width=1000):
    '''
    Args:
    numObjs: number of objects in this problem
    Density: S(occupied area)/S(environment)
    Height, Width: Environment size
    '''
    # disc radius
    RAD = math.sqrt((Height*Width*Density)/(math.pi*numObjs))

    # Load instance (start arrangement, goal arrangement)
    start_arr, goal_arr = generate_instance(numObjs, Density)

    # Generate the dependency graph
    Digraph = construct_DG(start_arr, goal_arr, RAD)
    nx_graph = nx.DiGraph(Digraph)
    action_sequence = optimal_sequence(nx_graph)
    for action in action_sequence:
        print(action)
    # show_Digraph(nx_graph, "Final Graph")

    # show instance
    show_arrangement(numObjs, Density, start_arr, goal_arr)


def optimal_sequence(Digraph):
    action_sequence = []
    show_digraph(Digraph, "Original Graph")

    # Use Tarjan's SCC decomposition algo to find SCCs in reverse topological order
    partition = nx.strongly_connected_components(Digraph)

    for SCC in partition:
        SCC_list = list(SCC)
        if len(SCC_list) == 1:
            action_sequence.append((SCC_list[0], 'g'))
        if len(SCC_list) > 1:
            print("SCC (" + str(len(SCC_list)) + "): " + str(SCC_list))
            # construct the strongly connected component
            new_Graph = Digraph.subgraph(SCC).copy()
            mfvs = ILP_MFVS(new_Graph)
            show_digraph(new_Graph, "Strongly Connected Component")
            for v in mfvs:
                action_sequence.append((v, 'b'))
                new_Graph.remove_node(v)
            assert(nx.is_directed_acyclic_graph(new_Graph))
            rev_list = list(reversed(list(nx.topological_sort(new_Graph))))
            print("Reverse Topological (without MFVS): " + str(rev_list))
            for item in rev_list:
                action_sequence.append((item, 'g'))
            for v in mfvs:
                action_sequence.append((v, 'g'))
    return action_sequence


def ILP_MFVS(subgraph):
    env = grb.Env(empty=True)
    env.setParam("OutputFlag", 0)
    env.start()
    model = grb.Model("mip1", env=env)
    for x in subgraph.nodes():
        model.addVar(vtype=grb.GRB.BINARY, name=str(x))
    model.update()
    model.setObjective(grb.quicksum(model.getVars()), grb.GRB.MAXIMIZE)
    for cycle in nx.simple_cycles(subgraph):
        model.addConstr((grb.quicksum(model.getVarByName(str(graphNode)) for graphNode in cycle)) <= len(cycle) - 1)

    model.optimize()
    mfvs = set()
    for v in model.getVars():
        if not v.x:
            mfvs.add(int(v.varName))
    print("Gurobi ILP MFVS: " + str(mfvs))
    return mfvs


def brute_force_MFVS(subgraph):
    for r in range(subgraph.number_of_nodes()):
        combos = list(combinations(subgraph.nodes(), r))
        for combo in combos:
            temp = subgraph.copy()  # copy to avoid modifying original graph

            for i in combo:  # remove possible mfvs vertices
                temp.remove_node(i)
            if nx.is_directed_acyclic_graph(temp):
                # print("Brute Force MFVS: " + str(set(combo)))
                print("Brute Force MFVS: {" + ', '.join(map(str, combo)) + "}")
                return combo


if __name__ == '__main__':
    Labeled_Experiment(10, 0.4)
