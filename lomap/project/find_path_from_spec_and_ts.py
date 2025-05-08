#!/usr/bin/env python3

import spot
import argparse
import networkx as nx
from collections import deque
import copy
import yaml
import os

from lomap.classes import Buchi, Ts, Automaton, Fsa
from lomap.algorithms import ts_and_automata_products as tsap
from lomap.algorithms import dijkstra as dj



def ltl_to_automata(formula, output_file=None):
    """
    Convert an LTL formula to a Büchi automaton and optionally save to file if specified.
    
    Args:
        formula (str): The LTL formula
        output_file (str, optional): Path to output file. If None, it won't save the automaton generated.
        
    Returns:
        buchi_automaton: A Buchi automaton object from lomap capturing the LTL specification.
        fsa: A finite state automaton object from lomap capturing the LTL specification.
    """
    # Decide whether to keep file after use
    delete_file_after_use = False if output_file else True

    # Parse the LTL formula and convert to Büchi automaton
    f = spot.formula(formula)
    aut = f.translate('BA')  # BA = Büchi Automaton
    only_buchi = False
    try: 
        never_claim = aut.to_str('spin')
    except RuntimeError as e:
        only_buchi = True
        print(f"Error converting LTL to automaton: {e}. Trying iwth hoa.")
        never_claim = aut.to_str('hoa')

    # print("\n", never_claim)

    if delete_file_after_use:
        output_file = 'temp_never_claim.txt'
    
    # Write to file
    with open(output_file, 'w') as file:
        file.write(never_claim)
    
    # Create Buchi and Fsa objects from lomap so either can be used
    buchi_automaton = Buchi()
    buchi_automaton.from_formula(formula, output_file)
    if not only_buchi:
        fsa = Fsa()
        fsa.from_formula(formula, output_file)
        fsa.visualize()
    else:
        fsa = None
        buchi_automaton.visualize()
    
    
    
    # Remove file or notify of where it was written to
    if delete_file_after_use:
        os.remove(output_file)
    else:
        print(f"\nBüchi automaton for '{formula}' written to {output_file}\n")
    
    return buchi_automaton, fsa
    

def estimate_product_size(ts, automaton, size_threshold, print_info=True):
    """
    Estimate the size of the product of a transition system and an automaton.
    
    Args:
        ts (Ts): Transition system
        automaton (Automaton): Büchi automaton
        size_threshold (int): The maximum number of nodes the product of the TS and Automaton can have before simplifying the TS occurs
        
    Returns:
        int: Estimated size of the product
        bool: Whether the product is too large to handle (True if too large)
    """
    ts_size = len(ts.g.nodes())
    automaton_size = len(automaton.g.nodes())
    estimated_product_size = ts_size * automaton_size
    
    # Define a threshold for "too large" - adjust based on your system's capabilities
    # This is a parameter you might want to tune based on your specific application
    
    if print_info: 
        print(f"Transition system size: {ts_size} nodes")
        print(f"Automaton size: {automaton_size} nodes")
        print(f"Estimated product size: {estimated_product_size} nodes")
    
    return estimated_product_size, estimated_product_size > size_threshold


def simplify_transition_system(ts):
    """
    Simplify a transition system by collapsing adjacent nodes with the same label
    into connected components.
    
    Args:
        ts (Ts): Original transition system
        
    Returns:
        Ts: Simplified transition system
        dict: Mapping from original nodes to simplified nodes
    """
    # Create a new transition system
    simplified_ts = Ts(name='Simplified_' + ts.name, multi=ts.multi, directed=ts.directed)
    simplified_ts.init = set()
    
    # Group nodes by their labels first
    label_to_nodes = {}
    node_to_label = {}
    
    for node in ts.g.nodes():
        node_props = frozenset(ts.g.nodes[node]['prop'])
        node_to_label[node] = node_props
        if node_props not in label_to_nodes:
            label_to_nodes[node_props] = []
        label_to_nodes[node_props].append(node)
    
    # Create a mapping of nodes to their connected components
    node_mapping = {}  # Original node -> Simplified node
    simplified_idx = 0
    
    # Process each label group separately
    for label, nodes_with_label in label_to_nodes.items():
        # Create a subgraph only containing nodes with this label
        subgraph = nx.Graph() if not ts.directed else nx.DiGraph()
        subgraph.add_nodes_from(nodes_with_label)
        
        # Add edges only between nodes with this same label
        for u, v in ts.g.edges():
            if u in nodes_with_label and v in nodes_with_label:
                subgraph.add_edge(u, v)
        
        # Find connected components within this label's subgraph
        connected_components = nx.connected_components(subgraph) if not ts.directed else nx.weakly_connected_components(subgraph)
        
        # Create a simplified node for each connected component
        for component in connected_components:
            simplified_node = f"{list(label)[0]}_s{simplified_idx}"
            simplified_idx += 1
            
            # Map all nodes in this component to the simplified node
            for original_node in component:
                node_mapping[original_node] = simplified_node
            
            # Add node to simplified TS with original properties
            simplified_ts.g.add_node(simplified_node)
            simplified_ts.g.nodes[simplified_node]['prop'] = dict.fromkeys(label, None)
            
            # Handle initial states
            if any(node in ts.init for node in component):
                simplified_ts.init.add(simplified_node)
    
    # Add edges between different simplified nodes
    for u, v in ts.g.edges():
        simplified_u = node_mapping[u]
        simplified_v = node_mapping[v]
        
        # Add edge between simplified nodes (avoid duplicates)
        if simplified_u != simplified_v and not simplified_ts.g.has_edge(simplified_u, simplified_v):
            simplified_ts.g.add_edge(simplified_u, simplified_v, weight=1)
    
    print(f"Simplified TS: {len(simplified_ts.g.nodes())} nodes (from {len(ts.g.nodes())})")
    simplified_ts.visualize()
    return simplified_ts, node_mapping


def extract_ts_path_from_product_path(ts, product_path, is_simplified=False, node_mapping=None):
    """
    Extract the transition system path from a product path.
    
    Args:
        ts (Ts): Transition system
        product_path (list): Path in the product automaton
        is_simplified (bool): Whether the path is from a simplified TS product
        node_mapping (dict): Mapping from original TS nodes to simplified nodes (if simplified)
        
    Returns:
        list: Path in the original transition system
    """
    # Extract TS states from product states
    ts_path = []
    for state in product_path:
        # Product states are in the format "ts_state-aut_state". This removes the automaton part and keeps the TS state.
        ts_state = state.split('-')[0]
        ts_path.append(ts_state)
    
    # If not working with simplified TS, just return the extracted path
    if not is_simplified or not node_mapping:
        return ts_path
    
    # Working with simplified TS, need to find path through original TS
    complete_path = []
    current_state = list(ts.init)[0]  # Start from an initial state
    
    # Process each simplified state in the path
    for simplified_state in ts_path:
        # Find path segment to this simplified state
        path_segment = dj.find_path_to_label_in_original_ts(ts, node_mapping, simplified_state, current_state)
        
        if path_segment is None:
            print(f"Failed to find path segment to simplified state {simplified_state}, this should not happen if a path was found in the product automaton.")
            # Try to continue from the last known position
            if current_state is not None:
                continue
            else:
                return complete_path  # Return whatever we have so far
        
        # Add segment to the complete path (avoid duplicate states between segments)
        if not complete_path:
            complete_path.extend(path_segment)
        else:
            # Skip the first state in the segment as it should be the same as the last state in complete_path
            if path_segment[0] == complete_path[-1]:
                complete_path.extend(path_segment[1:])
            else:
                print("Warning: Path segments do not connect properly, this should not happen if the product path is valid.")
                complete_path.extend(path_segment)
        
        # Update current state to the last state in this segment
        current_state = path_segment[-1]
    
    return complete_path
    


def process_ltl_specification(ts, ltl_formula, output_file=None, size_threshold=1000):
    """
    Process an LTL specification with a transition system and find a satisfying path.
    
    Args:
        ts (Ts): Transition system
        ltl_formula (str): LTL formula
        output_file (str, optional): Path to output file for the automaton
        
    Returns:
        list: Path in the transition system that satisfies the LTL formula
    """
    # Convert LTL to Büchi automaton
    buchi, fsa = ltl_to_automata(ltl_formula, output_file)
    if fsa is None:
        print("Failed to create automaton.")
        return None
    
    # Estimate product size
    _, is_too_large = estimate_product_size(ts, fsa, size_threshold)
    
    if is_too_large:
        print("Product would be too large. Simplifying transition system...")
        
        # Simplify the transition system
        simplified_ts, node_mapping = simplify_transition_system(ts)

        # Print new product size
        estimated_size, _ = estimate_product_size(simplified_ts, fsa, size_threshold, print_info=False)
        print(f"Estimated product size after simplification: {estimated_size} nodes")
        
        # Create product with simplified TS
        product = tsap.ts_times_automaton(simplified_ts, fsa, True)
        
        # Find a path in the product
        product_path = dj.source_to_accepting_dijkstra(product)
        print(f"Simplified product path: {product_path}")
        
        if product_path:
            # Extract TS path from product path and map back to original TS
            return extract_ts_path_from_product_path(ts, product_path, is_simplified=True, node_mapping=node_mapping)
        else:
            print("No satisfying path found in simplified product.")
            return None
    else:
        print("Product size is manageable. Creating direct product...")
        
        # Create direct product
        product = tsap.ts_times_automaton(ts, fsa, True)
        
        # Find a path in the product
        product_path = dj.source_to_accepting_dijkstra(product)
        print(f"Product path: {product_path}")
        
        if product_path:
            # Extract TS path from product path
            return extract_ts_path_from_product_path(ts, product_path)
        else:
            print("No satisfying path found in product.")
            return None

    
def main():
    parser = argparse.ArgumentParser(description='Process LTL specification with a transition system.')
    parser.add_argument('ts_file', help='Transition system YAML file')
    parser.add_argument('ltl_formula', help='LTL formula')
    parser.add_argument('-o', '--output', help='Output file for Büchi automaton')
    parser.add_argument('-p', '--path_output', help='Output file for the resulting path')
    parser.add_argument('-s', '--size_threshold', help='The maximum amount of nodes in the TS and Automaton product before simulating the TS', default=1000)
    
    args = parser.parse_args()
    
    # Load transition system
    ts = Ts.load(args.ts_file)
    ts.visualize()
    
    # Process LTL specification
    ts_path = process_ltl_specification(ts, args.ltl_formula, args.output, int(args.size_threshold))
    
    if ts_path:
        print(f"Found satisfying path: {ts_path}")
        
        # Save path to file if requested
        if args.path_output:
            with open(args.path_output, 'w') as f:
                yaml.dump(ts_path, f)
            print(f"Path saved to {args.path_output}")
    else:
        print("Failed to find a satisfying path.") 
    

if __name__ == "__main__":
    main()