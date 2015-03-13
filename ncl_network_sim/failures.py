import geo_functions
from flows import FlowPoint
import random


def edge_remove(network, edgefails, reassign_start, reassign_dest, weight):
    """Updates all affected flow points when an edge is removed from the
    network."""
    # find the edge to remove

    failed_edges = []

    for edgefail in edgefails:
        if edgefail.failed:
            continue
        edgefail.failed = True
        start, end = edgefail.start_node, edgefail.end_node
        failed_edges.append((start, end))
        failed_edges.append((end, start))
        network.graph.remove_edge(start._truncated_geom, end._truncated_geom)
    nx_nodes = network.graph.nodes()
    nx_edges = network.graph.edges()
    for node in network.nodes:
        if node.failed:
            continue
        if node._truncated_geom not in nx_nodes:
            node.failed = True
    for edge in network.edges:
        if edge.failed:
            continue
        start, end = edge.start_node, edge.end_node
        if (start._truncated_geom, end._truncated_geom) not in nx_edges:
            edge.failed = True
    # as some edges may have been removed as one of thier end nodes has
    # failed, this is encased in a  try statement
    # remove the edge from the network
    for edgefail in edgefails:
        start, end = edgefail.start_node, edgefail.end_node

    v = 0
    avg_b = network.average_journey_length()
    avg_time_b = network.average_journey_length(length=False)
    reroute, noroute = 0, 0
    while v < len(network.flow_points):
        # if the people have not started traveling yet
        if not network.flow_points[v].finished:
            if not network.flow_points[v].started:
                # loop through all edges in the waypoints
                for edge in network.flow_points[v].waypoints:
                    origin, dest = edge.start_node, edge.end_node
                    # find any possible route uses the edge
                    if (origin, dest) in failed_edges:
                        # get start and end nodes
                        start_waypoint = network.flow_points[
                            v].waypoints[0].start_node
                        end_waypoint = network.flow_points[
                            v].waypoints[-1].end_node
                        # calcualte the new route, if one is possible
                        new_route = network._create_waypoints(
                            start_waypoint,
                            end_waypoint,
                            weight)
                        if not new_route:
                            # if no route is possible - graph has more than
                            # one connected component
                            network.flow_points.remove(network.flow_points[v])
                            v -= 1
                            noroute += 1
                        elif new_route is None:
                            # this will only be used if an unknown error is
                            # generated in the _create_waypoints function
                            print "An error has occured in creating the waypoints"
                            exit()
                        else:
                            reroute += 1
                            # if a route has been sucessfuly found
                            network.flow_points[v] = FlowPoint(
                                network,
                                new_route,
                                network.flow_points[v].start_time)
                        break
            else:

                for edge in network.flow_points[v].waypoints:
                    origin, dest = edge.start_node, edge.end_node
                    # find any possible route uses the edge
                    if (origin, dest) in failed_edges:
                        # get start and end nodes
                        start_waypoint = network.flow_points[
                            v].edge.start_node
                        end_waypoint = network.flow_points[
                            v].waypoints[-1].end_node
                        # calcualte the new route, if one is possible
                        new_route = network._create_waypoints(
                            start_waypoint,
                            end_waypoint,
                            weight)
                        if not new_route:
                            # if no route is possible - graph has more than
                            # one connected component
                            network.flow_points.remove(network.flow_points[v])
                            v -= 1
                            noroute += 1
                        elif new_route is None:
                            # this will only be used if an unknown error is
                            # generated in the _create_waypoints function
                            print "An error has occured in creating the waypoints!"
                            exit()
                        else:
                            reroute += 1
                            # if a route has been sucessfuly found
                            network.flow_points[v].waypoints = [
                                network.flow_points[v].edge]
                            for part in new_route:
                                network.flow_points[v].waypoints.append(part)
                            network.flow_points[v].point = 0
                        break

                # holder for handling those people who need re-routing mid
                # journey
                pass
        v += 1
    # calculatre the average journey length
    avg_a = network.average_journey_length()
    avg_time_a = network.average_journey_length(length=False)
    # print stats on the affect of the edge failure
    # edgefail.fill_stats(reroute,noroute,avg_b,avg_a,avg_time_b,avg_time_a)


def node_remove(network, nodes, reassign_start, reassign_dest, weight):
    """
    """
    failed_nodes = []
    # remove a junction from the network
    for node in nodes:
        if node.failed:
            continue
        node.failed = True
        node_to_remove = node._truncated_geom
        failed_nodes.append(node.geom)
        # remove the failed node from the network

        network.graph.remove_node(node_to_remove)
    nx_nodes = network.graph.nodes()
    nx_edges = network.graph.edges()
    for node in network.nodes:
        if node.failed:
            continue
        if node._truncated_geom not in nx_nodes:
            node.failed = True
    for edge in network.edges:
        if edge.failed:
            continue
        start, end = edge.start_node, edge.end_node
        if (start._truncated_geom, end._truncated_geom) not in nx_edges:
            edge.failed = True

    # calculate the average journey lengths/times
    avg_b = network.average_journey_length()
    avg_time_b = network.average_journey_length(length=False)

    # create parameters to store flow statistics
    v = 0
    noroute, start_rem, dest_rem, journey_rem, inter_node_rem, failed_start_rem, failed_dest_rem, start_rem_no_effect, failed_inter_rem, reroute_start_fail, reroute_dest_fail, reroute_inter_fail, start_is_end = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0

    # loop through all the flows
    while v < len(network.flow_points):
        # if the flow has not finished yet
        if network.flow_points[v].finished == False:

            # get start and end waypoints
            start_junction = network.flow_points[v].waypoints[0].start_node
            dest_junction = network.flow_points[v].waypoints[-1].end_node

            # check if flow origin has failed
            if start_junction.geom in failed_nodes:
                start_rem += 1  # count flow as start being removed
                # if the flow has started
                if network.flow_points[v].started:
                    # it will have passed away from this node already
                    start_rem_no_effect += 1

                # if the flow has not started yet
                elif network.flow_points[v].started == False:
                    # does the user want to assume the flow will reroute to
                    # the nearest node
                    if reassign_start:
                        # get nearest possible junction as a new start node
                        new_start_junction = network._nearest_node(
                            start_junction)
                        print new_start_junction == start_junction
                        if new_start_junction == dest_junction:
                            # remove flow if new start == dest or == failed
                            network.flow_points.remove(network.flow_points[v])
                            failed_start_rem += 1
                            start_is_end += 1
                            v -= 1
                        else:
                            # create a set of waypoints for flow
                            new_route = network._create_waypoints(
                                new_start_junction,
                                dest_junction,
                                weight)
                            if not new_route:
                                # new route not possible
                                noroute += 1
                                failed_start_rem += 1
                                network.flow_points.remove(
                                    network.flow_points[v])
                                v -= 1
                            elif new_route is None or new_route == 'key error on source node' or new_route == 'key error on destnation node':
                                # catch error and stop simulation
                                print "An error occured creating the waypoints! Reason for rerouting was due to failure of start node for flow. Error returned was %s" % new_route
                                exit()
                            else:
                                # new route found
                                reroute_start_fail += 1
                                network.flow_points[v] = FlowPoint(
                                    network,
                                    new_route,
                                    network.flow_points[v].start_time)
                    else:
                        # remove flow as user requested origins not to be
                        # reassigned
                        network.flow_points.remove(network.flow_points[v])
                        failed_start_rem += 1
                        v -= 1
                else:
                    # indicates a major error - stop simulation
                    print "---\nMajor error! (c)\n---"
                    exit()

            # check if flow destination has failed
            elif dest_junction.geom in failed_nodes:
                # record that a flow has had it destination removed
                dest_rem += 1
                # if the user wants the flow to be rerouted to the nearest
                # destination
                if reassign_dest:
                    # find nearest junction to the failed
                    new_dest_junction = network._nearest_node(dest_junction)

                    if new_dest_junction == start_junction or new_dest_junction in failed_nodes:
                        # remove flow if new dest == start or == failed
                        network.flow_points.remove(network.flow_points[v])
                        failed_dest_rem += 1
                        start_is_end += 1
                        v -= 1
                    else:
                        # if flow has started
                        if network.flow_points[v].started:

                            # check new dest is not part of the edge the
                            # flow is currently on
                            if new_dest_junction == network.flow_points[
                                    v].edge.end_node:
                                # if the nearest dest is the end of the edge the flow is on
                                # only need to add the edge as the route
                                network.flow_points[v].waypoints = [
                                    network.flow_points[v].edge]
                                network.flow_points[v].point = 0

                            elif new_dest_junction == network.flow_points[v].edge.start_node:
                                # flow has gone past new destiantion as its the beginning of the edge its currently on
                                # need to find a new route back to this node
                                # add to the new route the current edge its
                                # on
                                comp_route = [network.flow_points[v].edge]
                                # find new route from the end of the
                                # current edge to the eestination, the
                                # beginning of teh current edge
                                new_route = network._create_waypoints(
                                    network.flow_points[v].edge.end_node,
                                    new_dest_junction,
                                    weight)

                                if not new_route:
                                    # new route not possible
                                    noroute += 1
                                    failed_dest_rem += 1
                                    network.flow_points.remove(
                                        network.flow_points[v])
                                    v -= 1
                                elif new_route is None or new_route == 'key error on source node' or new_route == 'key error on destination node':
                                    # if an error is returned from the
                                    # rerouting. Report and exit.
                                    print "An error occured creating the waypoints! Rerouting as the flow destination had failed. Error returned was %s" % new_route
                                    exit()
                                else:
                                    # route found to new destination
                                    reroute_dest_fail += 1
                                    # append new route to the existing
                                    # route - the current edge only
                                    for item in new_route:
                                        comp_route.append(item)
                                    network.flow_points[
                                        v].waypoints = comp_route
                                    network.flow_points[v].point = 0

                            else:
                                # else the new destination is not on the edge the flow is on or its original source
                                # generate new route current edge start and
                                # new destination
                                new_route = network._create_waypoints(
                                    network.flow_points[v].edge.start_node,
                                    new_dest_junction,
                                    weight)
                                if not new_route:
                                    # new route not possible
                                    noroute += 1
                                    failed_dest_rem += 1
                                    network.flow_points.remove(
                                        network.flow_points[v])
                                    v -= 1
                                elif new_route is None or new_route == 'key error on source node' or new_route == 'key error on destination node':
                                    # error returned finding new route.
                                    # Report and exit.
                                    print "An error has occured creating waypoints! Rerouting as the flow destination has failed. Error returned was %s" % new_route
                                    exit()
                                else:
                                    # new route found to new dest
                                    reroute_dest_fail += 1
                                    comp_route = []
                                    for item in new_route:
                                        comp_route.append(item)

                                    network.flow_points[
                                        v].waypoints = comp_route
                                    network.flow_points[v].point = 0

                        # if flow has not started
                        elif network.flow_points[v].started == False:
                            # chose new dest and reroute
                            new_route = network._create_waypoints(
                                start_junction,
                                new_dest_junction,
                                weight)
                            if not new_route:
                                # new route not possible
                                noroute += 1
                                failed_dest_rem += 1
                                network.flow_points.remove(
                                    network.flow_points[v])
                                v -= 1
                            elif new_route is None or new_route == 'key error on source node' or new_route == 'key error on destination node':
                                # error returned finding new route. Report
                                # and exit.
                                print "An error occured creating the waypoints! Rerouting as dest node failed on inactive flow. Error returned was %s" % new_route
                                exit()
                            else:
                                # new route found
                                reroute_dest_fail += 1
                                network.flow_points[v] = FlowPoint(
                                    network,
                                    new_route,
                                    network.flow_points[v].start_time)
                        else:
                            # indicates a major error
                            print "Major error! (a)"
                            exit()
                else:
                    # remove flow as user requested no reassignment of
                    # destinations
                    network.flow_points.remove(network.flow_points[v])
                    failed_dest_rem += 1
                    v -= 1

            # check if part of the flow route has failed
            else:
                # check the route for those which have already started
                if network.flow_points[v].started:
                    # first check if the node at the end of the current
                    # edge has failed
                    if network.flow_points[
                            v].edge.end_node.geom in failed_nodes:
                        # the flow is on an edge with no node at its end,
                        # thus should be removed
                        inter_node_rem += 1
                        failed_inter_rem += 1
                        noroute += 1
                        network.flow_points.remove(network.flow_points[v])
                        v -= 1
                    elif network.flow_points[v].edge.start_node.geom in failed_nodes:
                        # the flow should not be affected by this but need
                        # to catch here
                        pass
                    else:
                        # need to loop through from the edge identified as
                        # the current edge
                        check = False
                        for edg in network.flow_points[v].waypoints:
                            if edg == network.flow_points[
                                    v].edge and check == False:
                                # allows to check only those edges which it
                                # still has to go over
                                check = True
                            # if the flow has yet to go over or on the edge
                            if check:
                                origin, dest = edg.start_node, edg.end_node
                                # check if edge start has failed
                                if origin.geom in failed_nodes:
                                    print 'rerouting node'
                                    inter_node_rem += 1

                                    # if both nodes are the same
                                    if network.flow_points[v].edge.end_node == network.flow_points[
                                            v].waypoints[-1].end_node:
                                        pass
                                    else:
                                        # find new route for flow
                                        new_route = network._create_waypoints(network.flow_points[
                                            v].edge.start_node, network.flow_points[v].waypoints[-1].end_node, weight)

                                        if not new_route:
                                            # new route not possible
                                            noroute += 1
                                            failed_inter_rem += 1
                                            network.flow_points.remove(
                                                network.flow_points[v])
                                            v -= 1
                                        elif new_route is None or new_route == 'key error on source node' or new_route == 'key error on destination node':
                                            # error returned when finding
                                            # new route. Report and exit()
                                            print "An error occured creating the waypoints! Rerouting as node at begining og edge has failed. Error returned was %s" % new_route
                                            exit()
                                        else:
                                            # new route found
                                            reroute_inter_fail += 1
                                            network.flow_points[
                                                v].waypoints = new_route
                                            network.flow_points[v].point = 0
                                        # stop this loop as failure found
                                        # in flow route
                                        break

                                # check if edge end has failed
                                elif dest in failed_nodes:
                                    inter_node_rem += 1
                                    comp_route = [network.flow_points[v].edge]
                                    # if both nodes are the same
                                    if network.flow_points[v].edge.end_node == network.flow_points[
                                            v].waypoints[-1].end_node:
                                        pass
                                    else:
                                        # if the flow is on an edge, then
                                        # need re-route from the end of the
                                        # edge
                                        new_route = network._create_waypoints(network.flow_points[
                                                                              v].edge.end_node, network.flow_points[v].waypoints[-1].end_node, weight)
                                        if not new_route:
                                            # new route not possible
                                            noroute += 1
                                            failed_inter_rem += 1
                                            network.flow_points.remove(
                                                network.flow_points[v])
                                            v -= 1
                                        elif new_route is None or new_route == 'key error on source node' or new_route == 'key error on destination node':
                                            # error returned finding new
                                            # route. Report and exit.
                                            print "An error occured creating the waypoints! Rerouting as the end of an edge in an active route had failed. Error returned was %s" % new_route
                                            exit()
                                        else:
                                            # new route found
                                            reroute_inter_fail += 1
                                            for item in new_route:
                                                comp_route.append(item)
                                            network.flow_points[
                                                v].waypoints = comp_route
                                            network.flow_points[v].point = 0
                                    # stop looping as failure found in flow
                                    # route
                                    break
                                else:
                                    pass
                            else:
                                pass
                # check the route for those which have not started yet
                elif network.flow_points[v].started == False:

                    for edge in network.flow_points[v].waypoints:
                        origin, dest = edge.start_node, edge.end_node
                        # check if edge start or end has failed
                        if origin.geom in failed_nodes or dest.geom in failed_nodes:
                            inter_node_rem += 1
                            # create new route from start node to
                            # destination
                            new_route = network._create_waypoints(network.flow_points[v].waypoints[
                                0].start_node, network.flow_points[v].waypoints[-1].end_node, weight)

                            if not new_route:
                                # new route not possible
                                noroute += 1
                                failed_inter_rem += 1
                                network.flow_points.remove(
                                    network.flow_points[v])
                                v -= 1
                            elif new_route is None or new_route == 'key error on source node' or new_route == 'key error on destination node':
                                # error returned when finding new route.
                                # Report and exit.
                                print "An error has occured creating waypoints. Rerouting a stationary flow due to failure in route. Error returned was %s" % new_route
                                exit()
                            else:
                                # new route found
                                reroute_inter_fail += 1
                                network.flow_points[v] = FlowPoint(
                                    network,
                                    new_route,
                                    network.flow_points[v].start_time)
                            # stop looping as failure found in flow route
                            break
                        else:
                            pass
                else:
                    # major error. exit.
                    print "Major error! (b)"
                    exit()
        v += 1

    # calcaulate the average journey length
    avg_a = network.average_journey_length()
    avg_time_a = network.average_journey_length(length=False)
    # print the stats on the effect of the ndoe being removed
    failed_flows = failed_dest_rem + failed_start_rem + failed_inter_rem
    rerouted_flows = reroute_start_fail + \
        reroute_dest_fail + reroute_inter_fail
    # node_fail.fill_stats(noroute,avg_a,avg_b,avg_time_b,avg_time_a,start_rem,dest_rem,journey_rem,inter_node_rem,failed_dest_rem,failed_start_rem,start_rem_no_effect,failed_inter_rem,reroute_start_fail,reroute_dest_fail,reroute_inter_fail,failed_flows,rerouted_flows,start_is_end)


class NetworkFailure:

    def __init__(self, fail, time, nodes, edges):
        self.time = time

        self.edges = edges
        self.nodes = nodes
        self.fail_attr = fail
        self.done = False
        self.stats = {


        }

    def fail(self, reassign_start, reassign_dest, weight):
        """Run the edge failure code."""

        node_remove(self.fail_attr._network,
                    self.nodes,
                    reassign_start,
                    reassign_dest,
                    weight)

        edge_remove(
            self.fail_attr._network,
            self.edges,
            reassign_start,
            reassign_dest,
            weight)


class Failures:

    """Runs the failure of nodes/edges in the network."""

    def __init__(self, _network):
        self._network = _network
        self.__failures = {}

    def add_failure(self, nodes, edges, time):
        if time in self.__failures.keys():
            self.__failures[time].edges = list(
                set(self.__failures[time].edges + edges))
            self.__failures[time].nodes = list(
                set(self.__failures[time].nodes + nodes))
        else:
            self.__failures[time] = NetworkFailure(self, time, nodes, edges)

    def check_fails(self, reassign_start, reassign_dest, weight):
        """Checks the failures in the list to see if any need to be run at the
        current time."""
        fails = []
        # loop through the failures
        for f in self.__failures.values():
            # if f.node == False:
            if f.done:
                continue
            if f.time >= self._network.time and f.time < self._network.time + \
                    self._network.tick_rate:
                # run node/edge failure
                f.fail(reassign_start, reassign_dest, weight)
                f.done = True
                fails.append(f)

        return fails

    def geographical_failure(self, SHP_FILE, GEO_F_TIME):
        """"""
        GEO_F_TIME
        number_inside, nodes_inside, failed_edges = geo_functions.geo_failure(
            SHP_FILE, self._network)
        self._network.Failures.add_failure(
            nodes_inside,
            failed_edges,
            GEO_F_TIME)

    def random_failure(self, time, type='random'):
        if type not in ['random', 'edge', 'node']:
            raise NameError('Type must be either random,edge,node')

        if type == 'random':
            types = ['edge', 'node']
            random.shuffle(types)
            type = types[0]

        edges = []
        nodes = []
        if type == 'edge':
            net_edges = self._network.edges
            random.shuffle(net_edges)
            edges = [net_edges[0]]
        if type == 'node':
            net_nodes = self._network.nodes
            random.shuffle(net_nodes)
            nodes = [net_nodes[0]]
        self._network.Failures.add_failure(nodes, edges, time)
