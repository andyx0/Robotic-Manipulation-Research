from util import generate_instance, construct_DG
from show_arrangement import show_arrangement

import math
import networkx as nx
import matplotlib.pyplot as plt
import gurobipy as grb


def Labeled_Experiment(nx_graph, numObjs, Density, Height=1000, Width=1000, layers=1, verbose=False):
    '''
    Args:
    numObjs: number of objects in this problem
    Density: S(occupied area)/S(environment)
    Height, Width: Environment size
    layers: number of layers in this problem
    '''
    # disc radius
    RAD = math.sqrt((Height*Width*Density)/(math.pi*numObjs))

    # Load instance (start arrangement, goal arrangement)
    start_arr, goal_arr = generate_instance(numObjs, Density)

    # Generate the dependency graph
    Digraph = construct_DG(start_arr, goal_arr, RAD, layers)
    nx_graph = nx.DiGraph(Digraph)
    action_sequence = optimal_sequence(nx_graph, verbose)
    for action in action_sequence:
        print(action)
    # show_Digraph(nx_graph, "Final Graph")

    # show instance
    show_arrangement(numObjs, Density, start_arr, goal_arr)


def optimal_sequence(Digraph, verbose):
    action_sequence = []
    if verbose:
        show_digraph(Digraph, "Original Graph")
    edges = Digraph.edges(data=True)
    layer_edges = list(x for x in edges if 'layer' in x[-1])
    layer_graph = nx.DiGraph()
    layer_graph.add_nodes_from(Digraph)
    layer_graph.add_edges_from(layer_edges)
    if verbose:
        show_digraph(layer_graph, "Layer Graph")

    # Use Tarjan's SCC decomposition algo to find SCCs in reverse topological order
    partition = list(nx.strongly_connected_components(Digraph))

    for SCC in partition:
        SCC_list = list(SCC)
        if len(SCC_list) == 1:
            action_sequence.append((SCC_list[0], 'g'))
        if len(SCC_list) > 1:
            print("SCC (" + str(len(SCC_list)) + "): " + str(SCC_list))
            new_Graph = Digraph.subgraph(SCC_list).copy()  # construct the strongly connected component
            mfvs, layer_independent_nodes = ILP_MFVS(new_Graph, layer_graph.subgraph(SCC_list))
            if verbose:
                show_digraph(new_Graph, "Strongly Connected Component")
            # subgraph of only weighted edges
            mfvs_graph = layer_graph.subgraph(mfvs)
            mfvs = list(reversed(list(nx.topological_sort(mfvs_graph))))
            for v in mfvs:
                if v in layer_independent_nodes:
                    action_sequence.append((v, 'b'))
                else:
                    action_sequence.append((v, 'g'))
                new_Graph.remove_node(v)
            assert(nx.is_directed_acyclic_graph(new_Graph))
            rev_list = list(reversed(list(nx.topological_sort(new_Graph))))
            if verbose:
                print("Reverse Topological (without MFVS): " + str(rev_list))
            for item in rev_list:
                action_sequence.append((item, 'g'))
            for v in mfvs:
                if v in layer_independent_nodes:
                    action_sequence.append((v, 'g'))
    return action_sequence


def ILP_MFVS(subgraph, layer_graph):
    env = grb.Env(empty=True)
    env.setParam("OutputFlag", 0)
    env.start()
    model = grb.Model("mip1", env=env)
    layer_independent_nodes = set()
    for x in subgraph.nodes:
        model.addVar(vtype=grb.GRB.BINARY, name=str(x))
        if subgraph.out_degree(x) > layer_graph.out_degree(x) or subgraph.in_degree(x) > layer_graph.in_degree(x):
            layer_independent_nodes.add(x)
    model.update()
    model.setObjective(grb.quicksum(model.getVarByName(str(graphNode)) for graphNode in layer_independent_nodes), grb.GRB.MAXIMIZE)
    for cycle in nx.simple_cycles(subgraph):
        model.addConstr((grb.quicksum(model.getVarByName(str(graphNode)) for graphNode in cycle)) <= len(cycle) - 1)
    edges = subgraph.edges(data='layer')
    for edge in edges:
        is_layer_edge = edge[-1]
        if is_layer_edge:
            sourceNode = str(edge[0])
            targetNode = str(edge[1])
            # targetNode must be moved before sourceNode moves
            model.addConstr(model.getVarByName(sourceNode) >= model.getVarByName(targetNode))

    model.optimize()
    mfvs = set()
    for v in model.getVars():
        if not v.x:
            mfvs.add(int(v.varName))
    print("Gurobi ILP MFVS: " + str(mfvs))
    return mfvs, layer_independent_nodes


def show_digraph(Digraph, window_title=''):
    pos = nx.spring_layout(Digraph)
    nx.draw_networkx(Digraph, pos)
    labels = nx.get_edge_attributes(Digraph, 'layer')
    nx.draw_networkx_edge_labels(Digraph, pos, edge_labels=labels)
    if window_title:
        plt.get_current_fig_manager().set_window_title(window_title)
    plt.show()


if __name__ == '__main__':
    # test 1 (no cycles)
    graph_1 = nx.DiGraph()
    graph_1.add_edge(2, 1, layer=True)
    graph_1.add_edge(3, 4, layer=True)
    graph_1.add_edge(1, 0)
    graph_1.add_edge(2, 3)
    # test 2 (cycles)
    graph_2 = nx.DiGraph()
    graph_2.add_edge(0, 1, layer=True)
    graph_2.add_edge(2, 3, layer=True)
    graph_2.add_edge(3, 0)
    graph_2.add_edge(1, 2)
    graph_2.add_edge(0, 2)
    graph_2.add_edge(2, 0)
    # test 2.5 (cycles)
    graph_2_5 = nx.DiGraph()
    graph_2_5.add_edge(0, 1, layer=True)
    graph_2_5.add_edge(2, 3, layer=True)
    graph_2_5.add_edge(3, 2)
    graph_2_5.add_edge(1, 2)
    graph_2_5.add_edge(0, 2)
    graph_2_5.add_edge(2, 0)
    # test 3 (cycles)
    graph_3 = nx.DiGraph()
    graph_3.add_edge(0, 1, layer=True)
    graph_3.add_edge(1, 2)
    graph_3.add_edge(0, 2)
    graph_3.add_edge(2, 0)
    # test 4 (cycles)
    graph_4 = nx.DiGraph()
    graph_4.add_edge(0, 1, layer=True)
    graph_4.add_edge(2, 4, layer=True)
    graph_4.add_edge(1, 2)
    graph_4.add_edge(4, 2)
    graph_4.add_edge(0, 3)
    graph_4.add_edge(2, 3)
    graph_4.add_edge(3, 0)
    # test 4_5 (cycles with 3 layers)
    graph_4_5 = nx.DiGraph()
    graph_4_5.add_edge(0, 1, layer=True)
    graph_4_5.add_edge(1, 2, layer=True)
    graph_4_5.add_edge(2, 3, layer=True)
    graph_4_5.add_edge(1, 0)
    graph_4_5.add_edge(3, 0)
    # test 5 (cycles)
    graph_5 = nx.DiGraph()
    graph_5.add_edge(4, 1, layer=True)
    graph_5.add_edge(4, 0)
    graph_5.add_edge(0, 4)
    graph_5.add_edge(4, 2)
    graph_5.add_edge(2, 4)
    graph_5.add_edge(4, 3)
    graph_5.add_edge(3, 4)
    # test 6 (demo)
    graph_6 = nx.DiGraph()
    graph_6.add_edge(1, 4, layer=True)
    graph_6.add_edge(2, 4, layer=True)
    graph_6.add_edge(4, 3, layer=True)
    graph_6.add_edge(3, 5)
    # Labeled_Experiment(graph_1, 100, 0.4)
    # Labeled_Experiment(graph_2, 30, 0.4)
    # Labeled_Experiment(graph_2_5, 30, 0.4)
    # Labeled_Experiment(graph_3, 30, 0.4)
    # Labeled_Experiment(graph_4, 30, 0.4)
    Labeled_Experiment(graph_4_5, 120, 0.4, layers=2)
