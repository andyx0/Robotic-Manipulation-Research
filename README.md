# Robotic Manipulation of Many Objects with Multiple Layers

## Dependencies
* [Python](https://www.python.org/)
* [NumPy](https://numpy.org/)
* [Matplotlib](https://matplotlib.org/)
* [NetworkX](https://networkx.org/)
* [Gurobi](https://pypi.org/project/gurobipy/)

## Run
* Single Layer Labeled Instance: `python ./Labeled_Case/Labeled_Experiment_Single_Layer.py`
* Multiple Layer Labeled Instance: `python ./Labeled_Case/Labeled_Experiment_Multi_Layer.py`

## Introduction
In nearly all aspects of our everyday lives, be it work related, at home, or for play, objects are to be grasped and rearranged, e.g., tidying up a messy desk, cleaning the table after dinner, or solving a jigsaw puzzle. Similarly, many industrial and logistics applications require repetitive rearrangements of many objects, e.g., the sorting and packaging of products on conveyors with robots, and doing so efficiently is of critical importance to boost the competitiveness of the stakeholders. However, even without the challenge of grasping, **deciding the sequence of objects for optimally solving a pick-n-place based rearrangement task** is non-trivial.

For the example below, perhaps we want to arrange the sodas from the configuraiton on the left to the neater configuration on the right. Let us assume the robot will use overhand grasps: it will pick up an object, lift it above all other objects, move it around, and drop it off at a place on the table that is collision-free. A natural question to ask here is, **how many** such pick-n-place operations are needed to solve a given problem?

![setup](https://user-images.githubusercontent.com/35314983/124187803-59b14b00-da8c-11eb-8160-7b3af0f1c4a2.png)

In solving the problem, we first make the following observation: the Coke occupies the Pepsi's goal and vice versa, which means that one of them must be moved to a temporary location before the problem can be solved. This creates a **two-way** constraint. The Coke also occupies the goal of the Fanta, but this constraint is a **one-way** constraint. From the observation, we may fully capture the constraints in a tabletop pick-n-place rearrangement problem using **dependency graphs**, as shown on the right side of the figure below. Dependency graphs can be computed easily by extracting the the pairwise object constraints.

![labeled](https://user-images.githubusercontent.com/35314983/124187832-633ab300-da8c-11eb-9a6f-1cd623ac30b1.png)

The above dependency graph structure is induced by labeled (distinguishable) objects. When the objects are unlabeled, dependency graphs can also be defined. In this case, the dependency graphs are undirected and bipartite.

![unlabeled](https://user-images.githubusercontent.com/35314983/124187844-6766d080-da8c-11eb-9178-2313de59bda7.png)

As it turns out, minimizing the **total number** of objects to place at temporary locations, or **buffers**, is a difficult problem to solve at scale, because it is essentially the same as the *feedback vertex set* problem on the corresponding dependency graph, which is one of the [first batch of problems proven to be NP-hard](https://en.wikipedia.org/wiki/Karp%27s_21_NP-complete_problems). This aspect of the tabletop rearrangement problem is studied by [Han et al.](https://journals.sagepub.com/doi/pdf/10.1177/0278364918780999) a few years back. 
