import math
import datetime
import networkx as nx
import numpy as np
from scipy.spatial import KDTree
import pickle
from failures import Failures
from flows import FlowPoint


class Node:

    """Network Node"""

    def __init__(self, geom, truncated_geom):
        self.geom = geom
        self._truncated_geom = truncated_geom
        self.failed = False
        self.network = None
        self.flows = {}

    def add_flow(self, time):
        """store flows at each time step"""
        self.flows[time] = self.flows.get(time, 0.0)
        self.flows[time] += 1.0

    def get_flows(self, hours=0, mins=0, secs=0):
        """gets the number of flows in a given epoch"""
        tot_secs = secs + (mins * 60) + (hours * 60 * 60)
        cutoff = self.network.time - datetime.timedelta(0, tot_secs)
        num_flows = 0
        for time, flow in self.flows.iteritems():
            if time > cutoff:
                num_flows += flow
        return num_flows


class Nodes:

    """Network nodes"""

    def __init__(self, nodes, truncated_geom_lookup):
        self.nodes = nodes
        self.truncated_geom_lookup = truncated_geom_lookup

    def add_network(self, network):
        """Add network to each node"""
        for node in self.nodes:
            node.network = network


class Edge:

    """Network Edge"""

    def __init__(self, start_node, end_node, info):
        self.start_node = start_node
        self.end_node = end_node
        self.geom = (self.start_node.geom, self.end_node.geom)

        ax, ay = self.start_node.geom
        bx, by = self.end_node.geom

        if 'length' in info.keys():
            self.length = info['length']
        else:
            self.length = math.hypot(bx - ax, by - ay)
        if 'speed' in info.keys():
            self.speed = info['speed']
        else:
            self.speed = None
        if 'time' in info.keys():
            self.time = info['time']
        else:
            self.time = None
        self.failed = False
        self.network = None
        self.flows = {}

        self.reversed = Edge_reversed(self)

    def add_flow(self, time):
        """store flows at each time step"""
        self.flows[time] = self.flows.get(time, 0.0)
        self.flows[time] += 1.0

    def get_flows(self, hours=0, mins=0, secs=0):
        """gets the number of flows in a given epoch"""
        tot_secs = secs + (mins * 60) + (hours * 60 * 60)
        cutoff = self.network.time - datetime.timedelta(0, tot_secs)
        num_flows = 0
        for time, flow in self.flows.iteritems():
            if time > cutoff:
                num_flows += flow
        return num_flows


class Edge_reversed:

    """create a reversed copy of the edge but still store flow with the original edge"""

    def __init__(self, edge):
        self.edge = edge
        self.start_node = self.edge.end_node
        self.end_node = self.edge.start_node
        self.length = self.edge.length
        self.speed = self.edge.speed
        self.time = self.edge.time
        self.failed = self.edge.length
        self.network = self.edge.network

    def add_flow(self, time):
        """add flow to orig edge"""
        self.edge.flows[time] = self.edge.flows.get(time, 0.0)
        self.edge.flows[time] += 1.0


class Edges:

    """Handler for the network edges"""

    def __init__(self, edges, truncated_geom_lookup):
        self.edges = edges
        self.__truncated_geom_lookup = truncated_geom_lookup

    def __getitem__(self, trunc_geom):
        """fetchs the edge given a truncated geometry"""
        flipped_trunc_geom = (trunc_geom[1], trunc_geom[0])
        if trunc_geom in self.__truncated_geom_lookup.keys():
            return self.__truncated_geom_lookup[trunc_geom]
        # if the start and end node and the other way round fetches the revered
        # edge
        return self.__truncated_geom_lookup[flipped_trunc_geom].reversed

    def add_network(self, network):
        """adds the network class as an attribute to all edges"""
        for edge in self.edges:
            edge.network = network


class NclNetwork:

    """Handler for the generic functions for the analysis and visualisation the
    network."""

    def __init__(self, nx_graph, _nodes, _edges, _bbox):
        self.orig_graph = nx_graph
        self.graph = self.orig_graph.copy()

        self.__nodes_class = _nodes
        self.nodes = self.__nodes_class.nodes
        self._kd_tree = None

        self.node_class_array = []
        self.__nodes_class.add_network(self)

        self.__edges_class = _edges
        self.edges = self.__edges_class.edges

        self.__edges_class.add_network(self)

        self.bbox = _bbox

        self.flow_points = []
        self.Failures = Failures(self,)
        self.time = None
        self.tick_rate = None

    def __make_kdtree(self,):
        node_array = []
        for node in self.nodes:
            if not node.failed:
                node_array.append([node.geom[0], node.geom[1]])
                self.node_class_array.append(node)
        node_array = np.array(node_array)

        self._kd_tree = KDTree(node_array)

    def save(self, fname):
        self.kd_tree = None
        graph_obj = {
            'nx_graph': self.orig_graph,
            'node': self.__nodes_class,
            'edges': self.__edges_class,
            'bbox': self.bbox
        }
        pickle.dump(self, open(fname, "wb"))

    def find_nearest_node(self, coords):
        self.__make_kdtree()
        distance, point_index = self._kd_tree.query([coords[0], coords[1]])
        return self.node_class_array[point_index]

    def add_flow_point(self, start, end, start_time, WEIGHT, end_time=False):
        """Adds a new flow point the list."""
        route = self._create_waypoints(start, end, WEIGHT)
        if route:
            if end_time:
                time = (end_time - start_time).total_seconds()
                distance = 0
                for edge in route:
                    distance += edge.length
                speed = distance / time
            else:
                speed = False
            self.flow_points.append(
                FlowPoint(
                    self,
                    route,
                    start_time,
                    speed=speed))
            return True
        else:
            return False

    def __shortest_path(self, start, end, WEIGHT):
        """Finds the shortest path for a flow point and creates a set of
        waypoints given this path."""
        source = start._truncated_geom
        target = end._truncated_geom

        route = nx.shortest_path(self.graph, source, target, WEIGHT)

        waypoints = []
        for j in range(len(route) - 1):
            if self.__edges_class[
                (route[j],
                 route[
                    j +
                    1])].start_node.failed or self.__edges_class[
                (route[j],
                 route[
                    j +
                    1])].end_node.failed:
                print 'route contains failure!'
            waypoints.append(self.__edges_class[(route[j], route[j + 1])])
        return waypoints

    def _create_waypoints(self, start, end, WEIGHT):
        """"This creates a set of waypoints for a person if a route is possible"""
        try:
            # find shortest path
            new_route = self.__shortest_path(start, end, WEIGHT)
            if new_route == 'key error on source node' or new_route == 'key error on destination node':
                return new_route

        except nx.NetworkXNoPath:
            # no route possible
            new_route = False

        return new_route

    def _nearest_node(self, node):
        """Returns the nearest junction in the network to the one removed."""
        node_dist = {}
        dists = []
        # loop though all nodes

        for near in self.nodes:
            # check the node is not the one removed, else calc the dist between
            # them
            if near != node and not near.failed:
                dist = math.hypot(
                    near.geom[0] -
                    node.geom[0],
                    near.geom[1] -
                    node.geom[1])
                dists.append(dist)
                node_dist[dist] = near
        dists.sort()
        return node_dist[dists[0]]

    def average_journey_length(self, active=False, length=True):
        """Calculates the average length of journeys."""
        peeps_avg = []
        # go through all flow points (people)
        for peeps in self.flow_points:
            if active:
                if peeps.finished or peeps.started == False:
                    continue
            peep_total = 0
            # loop through the waypoints to calc the average
            for edge in peeps.waypoints:
                # sum the dist between waypoints
                if length:
                    peep_total += edge.length
                else:
                    peep_total += edge.time
            peeps_avg.append(peep_total)
        if len(peeps_avg) == 0:
            # if no flow points have routes
            return 0
        peeps_avg = sum(peeps_avg) / len(peeps_avg)
        return peeps_avg

    def average_journey_left(self, active=False):
        """Calculates the average length of journeys parts left"""
        peeps_avg = []
        # go through all flow points (people)
        for peeps in self.flow_points:
            if active:
                if peeps.finished or peeps.started == False:
                    continue
            peep_total = 0
            # loop through the waypoints to calc the average
            for edge in peeps.waypoints[peeps.point:len(peeps.waypoints)]:
                # sum the dist between waypoints
                peep_total += edge.length
            peeps_avg.append(peep_total)
        if len(peeps_avg) == 0:
            # if no flow points have routes
            return 0
        peeps_avg = sum(peeps_avg) / len(peeps_avg)
        return peeps_avg

    def number_flows(self, active):
        num = 0
        for peeps in self.flow_points:
            if active:
                if peeps.finished or peeps.started == False:
                    continue
            num += 1
        return num

    def time_config(self, start_time, tick_rate):

        self.tick_rate = datetime.timedelta(seconds=tick_rate)
        self.time = start_time - self.tick_rate

    def tick(self,):
        done = True
        for peep in self.flow_points:
            if not(peep.finished):
                done = False  # if people are still moving don't finish
                if self.time > peep.start_time:
                    peep.started = True
                    peep.move(self.tick_rate.total_seconds())  # move people
        self.time += self.tick_rate
        return done
