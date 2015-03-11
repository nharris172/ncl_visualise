import random
import datetime


def get_targted_comp(
        NODE_EDGE_RANDOM,
        failure_times,
        FLOW_COUNT_TIME,
        built_network,
        junctions,
        FLOW,
        DEGREE):
    """Checks to see if any failures are scheduled. If so selects a component
    to remove in a targetd way (via flow or a metric) and using the time adds
    the failure to the Failure set."""
    if FLOW and DEGREE == False:
        # check times for failures
        for ftime in failure_times:
            # if appropriate time
            # if ftime >= built_network.time and ftime < built_network.time +
            # datetime.timedelta(0,built_network.tick_rate):
            if ftime >= built_network.time and ftime < built_network.time + \
                    built_network.tick_rate:
                max_flow = -99
                meth = None
                if NODE_EDGE_RANDOM == 'NODE_EDGE':
                    meth = random.randint(0, 1)
                    if meth == 0:
                        meth = 'NODE'
                    else:
                        meth = 'EDGE'
                # if nodes, calc flows and node to remove
                if NODE_EDGE_RANDOM == 'NODE' or meth == 'NODE':
                    for node in built_network.nodes:
                        if not node.failed:
                            num_flows = node.get_flows(
                                hours=FLOW_COUNT_TIME[0],
                                mins=FLOW_COUNT_TIME[1])
                            if num_flows > max_flow:
                                max_flow = num_flows
                                node_to_fail = node
                    built_network.Failures.add_node_fail(node_to_fail, ftime)
                    junctions.remove(node_to_fail)
                # if edges, calc flows and edge to remove
                elif NODE_EDGE_RANDOM == 'EDGE' or meth == 'EDGE':
                    for edge in built_network.edges:
                        if not edge.failed:
                            num_flows = edge.get_flows(
                                hours=FLOW_COUNT_TIME[0],
                                mins=FLOW_COUNT_TIME[1])
                            if num_flows > max_flow:
                                max_flow = num_flows
                                edge_to_fail = edge
                    built_network.Failures.add_edge_fail(edge_to_fail, ftime)
        return junctions
    elif FLOW == False and DEGREE == True:
        # check times for failures
        for ftime in failure_times:
            # if appropriate time
            if ftime >= built_network.time and ftime < built_network.time + \
                    datetime.timedelta(0, built_network.tick_rate):

                node_degrees = built_network.graph.degree()
                max_degree = max(node_degrees.values())

                nodes_w_max = []  # stores all nodes with a equal max degree
                for node in node_degrees:
                    if node_degrees[node] == max_degree:
                        nodes_w_max.append(node)

                node_to_fail = None
                while node_to_fail is None:
                    # pick one of the nodes at random
                    item = random.randint(0, len(nodes_w_max) - 1)
                    coord = list(nodes_w_max[item])
                    # find the node instance so it can be removed
                    for node in built_network.nodes:
                        tcoord = truncate_geom(node.geom)
                        if tcoord[0] == coord[0] and tcoord[1] == coord[1]:
                            node_to_fail = node
                            break
                    # if node could not be found, remove from the list so not
                    # selected again
                    if node_to_fail is None:
                        nodes_w_max.pop(item)
                # add failure intance
                built_network.Failures.add_node_fail(node_to_fail, ftime)
                junctions.remove(node_to_fail)
        return junctions
    else:
        return junctions
