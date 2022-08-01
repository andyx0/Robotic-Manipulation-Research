import numpy as np
import os
import random
import math
import json


def constrained_sum_sample(n, total):
    """Return a randomly chosen list of n positive integers summing to total.
    Each such list is equally likely to occur."""

    dividers = sorted(random.sample(range(1, total), n - 1))
    return sorted([a - b for a, b in zip(dividers + [total], [0] + dividers)], reverse=True)


def generate_instance(numObjs, Density):
    '''
    Args:
    numObjs: number of objects in this problem
    Density: S(occupied area)/S(environment)
    Returns:
    start_arr: start arrangement. key: int obj ID, value: (x,y) coordinate
    goal_arr: goal arrangement. key: int obj ID, value: (x,y) coordinate
    '''
    instance_num = 20
    arrangement_choices = np.random.choice(range(instance_num), size=2, replace=False)
    my_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__))) + "/arrangements"

    # randomly assign obj IDs to discs
    start_list = list(range(numObjs))
    goal_list = list(range(numObjs))
    random.shuffle(start_list)
    random.shuffle(goal_list)

    # Construct start and goal arrangements
    start_arr = {}
    goal_arr = {}

    ### start arr ###
    with open(
            os.path.join(
                my_path,
                "D="+str(round(Density, 1)),
                "n="+str(numObjs),
                str(arrangement_choices[0])+"_"+str(numObjs)+"_"+str(round(Density, 1))+".json"
            )) as f:
        data_dict = json.load(f)
        point_list = data_dict['point_list']
        start_arr = {start_list[i]: tuple(p) for i, p in enumerate(point_list)}

    ### goal arr ###
    with open(
            os.path.join(
                my_path,
                "D="+str(round(Density, 1)),
                "n="+str(numObjs),
                str(arrangement_choices[1])+"_"+str(numObjs)+"_"+str(round(Density, 1))+".json"
            )) as f:
        data_dict = json.load(f)
        point_list = data_dict['point_list']
        goal_arr = {goal_list[i]: tuple(p) for i, p in enumerate(point_list)}

    return start_arr, goal_arr


def construct_DG(start_arr, goal_arr, radius, layers=1):
    '''
    Args:
    start_arr: start arrangement. key: int obj ID, value: (x,y) coordinate
    goal_arr: goal arrangement. key: int obj ID, value: (x,y) coordinate
    radius: disc radius
    Returns:
    dependency graph DG: DG[objID]=set(obj1, obj2, ...)
    '''
    layer_arr = []
    if layers > 1:
        layer_size_arr = constrained_sum_sample(layers, len(start_arr))
        layer_index_arr = layer_size_arr.copy()
        for i in range(1, len(layer_index_arr)):
            layer_index_arr[i] = layer_index_arr[i - 1] + layer_index_arr[i]
        # print("layer_size_arr: " + str(layer_size_arr))
        # print("layer_index_arr: " + str(layer_index_arr))
        # create each layer one at a time, assign layer dependencies, and set coords
        base_layer_obj_id = 0
        curr_layer_obj_id = layer_index_arr[0]
        for layer in range(1, layers):
            # print("layer: " + str(layer))
            # print("base_layer_obj_id: " + str(base_layer_obj_id))
            # print("curr_layer_obj_id: " + str(curr_layer_obj_id))
            for i in range(layer_size_arr[layer]):
                start_arr[curr_layer_obj_id + i] = start_arr[base_layer_obj_id + i]
                layer_arr.append((base_layer_obj_id + i, curr_layer_obj_id + i))
                # print((base_layer_obj_id + i, curr_layer_obj_id + i))
            base_layer_obj_id = curr_layer_obj_id
            curr_layer_obj_id = layer_index_arr[layer]
            
    DG = {}
    for goal_obj, goal_center in goal_arr.items():
        DG[goal_obj] = {}
        for start_obj, start_center in start_arr.items():
            if start_obj == goal_obj:
                continue
            if (math.sqrt((start_center[0]-goal_center[0])**2 + (start_center[1]-goal_center[1])**2) <= 2*radius):
                DG[goal_obj][start_obj] = {}
    # print(layer_arr)
    for lower_obj, higher_obj in layer_arr:
        DG[lower_obj][higher_obj] = {'layer': True}
    return DG


def set2tuple(s):
    '''
    Args:
    set: number set
    
    Return:
    tuple: ordered number tuple
    '''
    return tuple(sorted(list(s)))
