from lomap.classes import Ts, Automaton
from collections import deque

import copy


def source_to_accepting_dijkstra(product, init_state=None):
    edges = product.g.edges(data=True)
    if init_state is None:
        init_state = list(product.init)[0]
    queue = deque([(init_state, [])])
    visited = set()  # Track visited nodes to avoid cycles

    while queue:
        current_state, current_path = queue.popleft()
        current_path.append(current_state)
        visited.add(current_state)  # Mark as visited

        if current_state.find("accept") != -1:
            return current_path
        
        for edge in edges:
            if edge[0] == current_state and edge[1] not in current_path and edge[1] not in visited:
                queue.append((edge[1], copy.deepcopy(current_path)))
            if edge[1] == current_state and edge[0] not in current_path and edge[0] not in visited:
                queue.append((edge[0], copy.deepcopy(current_path)))
    
    print("WARNING: No path found to target insource_to_accepting_dijkstra")
    return None

def find_path_to_label_in_original_ts(ts, node_mapping, target_simplified_state, start_state=None):
    edges = ts.g.edges(data=True)
    if start_state is None:
        start_state = list(ts.init)[0]
    queue = deque([(start_state, [])])
    visited = set()  # Track visited nodes to avoid cycles

    while queue:
        current_state, current_path = queue.popleft()
        current_path.append(current_state)
        visited.add(current_state)  # Mark as visited

        if node_mapping[current_state] == target_simplified_state:
            return current_path
        
        for edge in edges:
            if edge[0] == current_state and edge[1] not in current_path and edge[1] not in visited:
                queue.append((edge[1], copy.deepcopy(current_path)))
            if edge[1] == current_state and edge[0] not in current_path and edge[0] not in visited:
                queue.append((edge[0], copy.deepcopy(current_path)))
    
    print("WARNING: No path found to target find_path_to_label_in_original_ts")
    return None