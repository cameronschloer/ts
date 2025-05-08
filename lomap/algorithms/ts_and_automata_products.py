import networkx as nx
from itertools import product

from lomap.classes import Ts, Automaton
import lomap.algorithms.graph_search as gs

def get_label_from_ts_node(ts, node):
    return ts.g.nodes[node]['prop']

def combine_state_names(state_name1, state_name2):
    return state_name1 + "-" + state_name2

def build_ts_autonomton_product(ts, automaton, current_node1, current_node2, node_names, edges, labels, init_states):
    new_node_name = combine_state_names(current_node1, current_node2)
    if new_node_name in node_names:
        return
    else:
        next_auto_nodes = automaton.next_states(current_node2, get_label_from_ts_node(ts, current_node1))

        # Check if current state's label changes anything (should only happen on init, because otherwise we made a mistake!)
        if len(next_auto_nodes) != 1 or next_auto_nodes[0] != current_node2:
            print("WARNING: Found transition in current state after arriving. If this is not the initial state, this is not expected! This is assumed to be only on the init state, and the init state will be updated accordingly.")
            for auto_node in next_auto_nodes:
                init_str = combine_state_names(current_node1, auto_node)
                init_states.add(init_str)
                build_ts_autonomton_product(ts, automaton, current_node1, auto_node, node_names, edges, labels, init_states)
            return

        # Add new state to added state names
        node_names.add(new_node_name)

        # Find next possible transitions
        ts_successors = [tup[0] for tup in ts.next_states_of_wts(current_node1, False)]
        automaton_successors = []
        for next_ts_state in ts_successors:
            automaton_successors.append(automaton.next_states(current_node2, get_label_from_ts_node(ts, next_ts_state)))
        
        # Setup next states to visit and continue recursion for each one.
        next_nodes = []
        for i in range(len(ts_successors)):
            for node2 in automaton_successors[i]:
                next_nodes.append((combine_state_names(ts_successors[i], node2), ts_successors[i], node2))
        for combined_state in next_nodes:
            edges.add((new_node_name, combined_state[0]))
            build_ts_autonomton_product(ts, automaton, combined_state[1], combined_state[2], node_names, edges, labels, init_states)

def ts_times_automaton(ts,automaton,visualize=False):
    product = Automaton(name="ts_auto_prod", props=automaton.props, multi=automaton.multi)

    # Get init states and name
    ts_init = next(iter(ts.init))
    automaton_init = next(iter(automaton.init))

    # Create name and edges sets, and label dictionary
    node_names = set()
    edges = set()
    labels = {}
    init_states = set()

    # Build
    build_ts_autonomton_product(ts, automaton, ts_init, automaton_init, node_names, edges, labels, init_states)
    
    if init_states == set():
        init_states.add(combine_state_names(ts_init, automaton_init))

    product.init = init_states
    product.g.add_nodes_from(list(node_names))
    product.g.add_edges_from(list(edges))

    if visualize:
        product.visualize()

    return product
    
    
