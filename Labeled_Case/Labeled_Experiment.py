from util import generate_instance, construct_DG
from show_arrangement import show_arrangement

import math
import networkx as nx
import matplotlib.pyplot as plt
from itertools import combinations
import gurobipy as grb


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
    buffer_sequence = []
    show_digraph(Digraph, "Original Graph")

    # SCC decomposition
    partition = nx.strongly_connected_components(Digraph.copy())  # copy to avoid dictionary size changed error

    for SCC in partition:
        SCC_list = list(SCC)
        if len(SCC_list) > 1:
            print("SCC (" + str(len(SCC_list)) + "): " + str(SCC_list))
            # construct the strongly connected component
            new_Graph = Digraph.subgraph(SCC)
            mfvs = ILP_MFVS(new_Graph)
            show_digraph(new_Graph, "Strongly Connected Component")
            for v in mfvs:
                action_sequence.append((v, 'b'))
                buffer_sequence.append((v, 'g'))
                Digraph.remove_node(v)
    if nx.is_directed_acyclic_graph(Digraph):
        rev_list = list(reversed(list(nx.topological_sort(Digraph))))
        print("Reverse Topological (without MFVS): " + str(rev_list))
        for item in rev_list:
            action_sequence.append((item, 'g'))
    else:
        print("Not a DAG!")
    return action_sequence + buffer_sequence


def ILP_MFVS(subgraph):
    model = grb.Model()
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


def show_digraph(Digraph, window_title=''):
    nx.draw_networkx(Digraph)
    if window_title:
        plt.get_current_fig_manager().set_window_title(window_title)
    plt.show()


if __name__ == '__main__':
    Labeled_Experiment(120, 0.4)
