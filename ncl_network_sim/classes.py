import math
import datetime
from tools import truncate_geom as _truncate_geom
import networkx as nx

class EdgeFailure:
    """Handles the failure of an edge and the associated outcomes."""
    def __init__(self,fail,_geom,_time):
        self.edge = True
        self.node = False
        self.fail_attr = fail
        self.geom = _geom
        self.time = _time
        self.stats = {
            'reroute':{'num':0,'print_str':'number of people re-routed :'},
            'not_pos':{'num':0,'print_str':'number of people whose route was no longer possible :'},
            'avg_b':{'num':0,'print_str':'Average length before :'},
            'avg_a':{'num':0,'print_str':'Average length after :'},
        }
        
    def fail(self):
        """Run the edge failure code."""
        self.fail_attr.network.edge_remove(self)
    
    def fill_stats(self,reroute,not_pos,avg_a,avg_b):
        """Populate the stats dict witht the stats from the affects of the edge
        removal of the flow points."""
        self.stats['reroute']['num'] =reroute
        self.stats['not_pos']['num'] =not_pos
        self.stats['avg_a']['num'] =avg_a
        self.stats['avg_b']['num'] =avg_b
        

    def print_stats(self,):
        """Prints the stats as in the stats dict."""
        for key,val in self.stats.iteritems():
            print val['print_str'],val['num']
            

class NodeFailure:
    """Handles the failure of a node from the network and the associated 
    outcomes."""
    def __init__(self,fail,_geom,_time):
        self.edge = False
        self.node = True
        self.fail_attr = fail
        self.geom = _geom
        self.time = _time
        self.stats = {
            'avg_b':{'num':0,'print_str':'Average length before :'},
            'avg_a':{'num':0,'print_str':'Average length after :'},
            'start_rem':{ 'num':0,'print_str':"number of people who's start node was removed:"},
            'inter_node_rem':{'num':0,'print_str':"number of people who had a intermediate node removed:"},
            'dest_rem':{'num':0,'print_str':"number of people who's destination node was removed:"},
            'reroute':{'num':0,'print_str':'number of people re-routed :'},
            'not_pos':{'num':0,'print_str':'number of people whose route was no longer possible :'},
            'journey_rem':{'num':0,'print_str':"number of people who's start/dest ended up being the same:"},
        }
        
    def fail(self):
        """Runs the failure of node."""
        print 'node'
        self.fail_attr.network.node_remove(self)
        
    def fill_stats(self,reroute,not_pos,avg_a,avg_b,start_rem,dest_rem,journey_rem,inter_node_rem):
        """Populates the stats dict with the required information."""
        self.stats['reroute']['num'] = reroute
        self.stats['not_pos']['num'] = not_pos
        self.stats['avg_a']['num'] = avg_a
        self.stats['avg_b']['num'] = avg_b
        self.stats['start_rem']['num'] = start_rem
        self.stats['dest_rem']['num'] = dest_rem
        self.stats['inter_node_rem']['num'] = inter_node_rem
        self.stats['journey_rem']['num'] = journey_rem

    def print_stats(self,):
        """Prints the stats has in the stats dict."""
        for key,val in self.stats.iteritems():
            print val['print_str'],val['num']

class Failures:
    """Runs the failure of nodes/edges in the network."""
    def __init__(self,_network):
        self.network = _network
        self.failures = []
        
    def add_edge_fail(self,geom,time):
        """Removes an edge and runs the resulting steps required to update 
        everything."""
        self.failures.append(EdgeFailure(self,geom,time))
        
    def add_node_fail(self,geom,time):
        """Removes a node and runs the resulting steps required to update 
        everything."""
        self.failures.append(NodeFailure(self,geom,time))
        
    def check_fails(self,):
        """Checks the failures in the list to see if any need to be run at the 
        current time."""
        for f in self.failures:
            if f.time >= self.network.time and f.time < self.network.time + datetime.timedelta(0,self.network.tick_rate):
                f.fail()
                return f

class FlowPoint:
    """Handles the management of the  flowpoints and thier movement throught 
    the network during the simulation/visualisation."""
    def __init__(self,network,waypoints,speed,start_time):
        self.network = network
        self.waypoints = waypoints
        self.speed = speed
        self.start_time = start_time
        self.loc = waypoints[0][0]
        self.speed
        self.point = 0
        self.finished = False
        self.started = False
        self.edge = waypoints[0]
    
    def move(self,time):
        """Moves the person the correct location. Updates the lists of nodes 
        and edges visited during the time step for the person as well."""
        lines = []
        step = self.speed * time
        ax, ay = self.loc
        bx, by = self.waypoints[self.point][1]
        dist = math.hypot(bx-ax, by-ay)
        while dist < step:
            self.loc = self.waypoints[self.point][1]
            if self.point ==0:
                if self.waypoints[self.point][0] in self.network.nodes:
                    self.network.node_capacity[self.waypoints[self.point][0]] = self.network.node_capacity.get(self.waypoints[self.point][0],0)
                    self.network.node_capacity[self.waypoints[self.point][0]] += 1.0
            if self.waypoints[self.point][1] in self.network.nodes:
                self.network.node_capacity[self.waypoints[self.point][1]] = self.network.node_capacity.get(self.waypoints[self.point][1],0)
                self.network.node_capacity[self.waypoints[self.point][1]] += 1.0
            self.point+=1
            self.network.edge_capacity[self.waypoints[self.point-1]] = self.network.edge_capacity.get(self.waypoints[self.point-1],0)
            self.network.edge_capacity[self.waypoints[self.point-1]] += 1.0
            if self.point== len( self.waypoints):
                self.finished = True
                self.edge = None
                return
            step -= dist
            ax, ay = self.waypoints[self.point][0]
            bx, by = self.waypoints[self.point][1]
            dist = math.hypot(bx-ax, by-ay)
        bearing = math.atan2(by-ay, bx-ax)
        self.loc = (self.loc[0]+ step*math.cos(bearing),self.loc[1] + step * math.sin(bearing))
        self.edge = self.waypoints[self.point]

class NclNetwork:
    """Handler for the generic functions for the analysis and visualisation the
    network."""
    def __init__(self,nx_graph,_nodes,_nodes_trunc,_edges,_edges_trunc):
        self.orig_graph = nx_graph
        self.graph = self.orig_graph.copy()
        self.__nodes_trunc = _nodes_trunc
        self.nodes = _nodes
        self.__edges = _edges
        self.edges = self.__edges.values()
        self.__edges_trunc = _edges_trunc
        self.flow_points = []
        self.Failures = Failures(self,)
        self.edge_capacity = {}
        self.node_capacity = {}
        self.time = None
        self.tick_rate  = None
    
    def add_flow_point(self,start,end,start_time,speed):
        """Adds a new flow point the list."""
        route = self.create_waypoints(start,end)
        if route <> False:
            self.flow_points.append(FlowPoint(self,route,speed,start_time))
            return True
        else:
            return False 
    
    def _shortest_path(self,start,end):
        """Finds the shortest path for a flow point and creates a set of 
        waypoints given this path."""
        route = nx.shortest_path(self.graph,source=self.__nodes_trunc[start], target=self.__nodes_trunc[end])
        waypoints =[]
        for j in range(len(route)-1):
            waypoints.append(self.__edges[(route[j],route[j+1])])
        return waypoints
    
    def create_waypoints(self,start, end):
        """"This creates a set of waypoints for a person if a route is possible"""
        try:
            new_route = self._shortest_path(start,end)
        except nx.NetworkXNoPath:
            #no route possible
            new_route = False
        except nx.NetworkXError:
            #in any other error - likley to be that it could not the node in the network - this is top of the list of bugs
            print 'Could not find node in network. ORIGIN is: %s ; DEST is: %s'%(start,end)
            new_route = None
            #exit the appliocation
            exit()
        return new_route
    
    def edge_remove(self,edgefail):
        """Updates all affected flow points when an edge is removed from the 
        network."""
        #find the edge to remove
        start,end = self.__edges_trunc[edgefail.geom]
        print start,end
        #remove the edge from the network
        self.graph.remove_edge(start,end)
        start,end = edgefail.geom
        v = 0
        avg_b = self.average_journey_length()
        reroute,noroute=0,0
        while v < len(self.flow_points):
            #if the people have not started traveling yet
            if not self.flow_points[v].finished:
                if not self.flow_points[v].started:
                    #loop through all edges in the waypoints
                    for origin,dest in self.flow_points[v].waypoints:
                        #find any possible route uses the edge
                        if start == origin or start == dest or end == origin or end == dest:
                            #get start and end nodes
                            start_waypoint, rubbish = self.flow_points[v].waypoints[0]
                            rubbish, end_waypoint = self.flow_points[v].waypoints[-1]
                            #calcualte the new route, if one is possible
                            new_route = self.create_waypoints(start_waypoint,end_waypoint)
                            if new_route == False:
                                #if no route is possible - graph has more than one connected component
                                self.flow_points.remove(self.flow_points[v])
                                v -= 1
                                noroute +=1
                            elif new_route == None:
                                #this will only be used if an unknown error is generated in the create_waypoints function
                                exit()
                            else:
                                reroute+=1
                                #if a route has been sucessfuly found
                                self.flow_points[v] = FlowPoint(self,new_route,self.flow_points[v].speed,self.flow_points[v].start_time)
                            break
                else:
                    
                    for origin,dest in self.flow_points[v].waypoints:
                        #find any possible route uses the edge
                        if start == origin or start == dest or end == origin or end == dest:
                            #get start and end nodes
                            start_waypoint, rubbish = self.flow_points[v].edge
                            rubbish, end_waypoint = self.flow_points[v].waypoints[-1]
                            #calcualte the new route, if one is possible
                            new_route = self.create_waypoints(start_waypoint,end_waypoint)
                            if new_route == False:
                                #if no route is possible - graph has more than one connected component
                                self.flow_points.remove(self.flow_points[v])
                                v -= 1
                                noroute +=1
                            elif new_route == None:
                                #this will only be used if an unknown error is generated in the create_waypoints function
                                exit()
                            else:
                                reroute+=1
                                #if a route has been sucessfuly found
                                self.flow_points[v].waypoints = [self.flow_points[v].edge]
                                for part in new_route:
                                    self.flow_points[v].waypoints.append(part)
                                self.flow_points[v].point = 0
                            break
                        
                    #holder for handling those people who need re-routing mid journey
                    pass
            v += 1
        #calculatre the average journey length
        avg_a = self.average_journey_length()
        #print stats on the affect of the edge failure
        edgefail.fill_stats(reroute,noroute,avg_b,avg_a)
        
    def node_remove(self,node_fail):
        """Updates for all people their waypoints given the removal of a junction"""
        #remove a junction from the network    
        node_to_remove =self.__nodes_trunc[node_fail.geom]
        self.graph.remove_node(node_to_remove)
        self.nodes.remove(node_fail.geom)
        avg_b = self.average_journey_length()
        v = 0
        reroute,noroute,start_rem,dest_rem,journey_rem,inter_node_rem = 0, 0, 0, 0, 0, 0
        #loop through all people
        while v < len(self.flow_points):
            #if the person has not finished yet
            if not self.flow_points[v].finished:
                #if the person has yet to set off
                if not self.flow_points[v].started:
                    #get start and end waypoints - don't need the others atm
                    start_waypoint, rubbish = self.flow_points[v].waypoints[0]
                    rubbish, end_waypoint =self.flow_points[v].waypoints[-1]
                    #check if the node removed is the start node for the person
                    if start_waypoint == node_fail.geom:
                        #find nearest node
                        new_start_waypoint = self.nearest_node(node_fail.geom)
                        start_rem += 1
                        #calculate new set of waypoints
                        if new_start_waypoint == end_waypoint:
                            #the closest node to the origin is the dest, so no route needed
                            self.flow_points.remove(self.flow_points[v])
                            journey_rem +=1
                            v -= 1
                        else:
                            #find the new route thorugh the function
                            new_route = self.create_waypoints(new_start_waypoint,end_waypoint)
                            #actions depending on the result from the funcation called above
                            if new_route == False:
                                #if no route possible
                                self.flow_points.remove(self.flow_points[v])
                                v -= 1
                                noroute +=1
                            elif new_route == None:
                                #this should never be used, but was used in testing
                                exit()
                            else:
                                #if a new route has been found update for the person
                                reroute +=1
                                self.flow_points[v] = FlowPoint(self,new_route,self.flow_points[v].speed,self.flow_points[v].start_time)
                            
                    #check if the node removed is the destination for the person
                    elif end_waypoint == node_fail.geom:
                        dest_rem += 1
                        new_end_waypoint = self.nearest_node(node_fail.geom)     
                        if start_waypoint == new_end_waypoint:
                            #if closest junction to end same as start - no journey needed
                            journey_rem +=1
                            self.flow_points.remove(self.flow_points[v])
                            v -= 1
                        else:
                            new_route = self.create_waypoints(start_waypoint,new_end_waypoint)
                            if new_route == False:
                                #new route not possible
                                noroute +=1
                                self.flow_points.remove(self.flow_points[v])
                                v -= 1
                            elif new_route == None:
                                #this should never be used
                                exit()
                            else:
                                #new route found
                                reroute +=1
                                self.flow_points[v] = FlowPoint(self,new_route,self.flow_points[v].speed,self.flow_points[v].start_time)
                                
                    else:
                        for origin, dest in self.flow_points[v].waypoints:
                            #search through all the waypoints
                            #only need to check one of the origin or dest
                            if dest == node_fail.geom:
                                inter_node_rem += 1
                                #if a macth is found, try to establish a new route for the person
                                new_route = self.create_waypoints(start_waypoint,end_waypoint)
                                if new_route == False:
                                    #no new route possible
                                    noroute +=1
                                    self.flow_points.remove(self.flow_points[v])
                                    v -= 1
                                elif new_route == None:
                                    #this should never occur
                                    exit()
                                else:
                                    #new route found
                                    reroute +=1
                                    self.flow_points[v] = FlowPoint(self,new_route,self.flow_points[v].speed,self.flow_points[v].start_time)
                                break
                            
                else:
                    #method for handling the circumstance where a feature is removed when the person has is in transit
                    comp_route =[]
                    #get waypoints - the points at either end of the edge the person is on
                    start_waypoint, rubbish = self.flow_points[v].edge
                    rubbish, end_waypoint = self.flow_points[v].waypoints[-1]
                    #if the node where the person started has been removed
                    if start_waypoint== node_fail.geom:
                        #it is allowed to continue
                        comp_route = [self.flow_points[v].edge]
                        start_waypoint = self.flow_points[v].edge[1]
                    #if the end waypoint for the person has been removed
                    elif end_waypoint == node_fail.geom:
                        dest_rem += 1
                        new_end_waypoint = self.nearest_node(node_fail.geom)     
                        if start_waypoint == new_end_waypoint:
                            #if the closest to the end is the start-remove journey
                            journey_rem +=1
                            self.flow_points.remove(self.flow_points[v])
                            v -= 1
                        else:
                            #if new end node found successfully
                            new_route = self.create_waypoints(start_waypoint,new_end_waypoint)
                            if new_route == False:
                                #if no route is possible
                                noroute +=1
                                self.flow_points.remove(self.flow_points[v])
                                v -= 1
                            elif new_route == None:
                                #this should never be used
                                exit()
                            else:
                                #if a new route has been found
                                reroute +=1

                                for part in new_route:
                                    comp_route.append(part)
                                self.flow_points[v].waypoints = comp_route
                                self.flow_points[v].point = 0
                    #if the current edge the person is on is unaffected
                    else:
                        #check the remaining route
                        for origin, dest in self.flow_points[v].waypoints:
                            #search through all the waypoints
                            #only need to check one of the origin or dest
                            if dest == node_fail.geom:
                                inter_node_rem += 1
                                #if a macth is found, try to establish a new route for the person
                                new_route = self.create_waypoints(start_waypoint,end_waypoint)
                                if new_route == False:
                                    #no route has been found
                                    noroute +=1
                                    self.flow_points.remove(self.flow_points[v])
                                    v -= 1
                                elif new_route == None:
                                    #this should never be used
                                    exit()
                                else:
                                    #if a new route has been found
                                    reroute +=1
                                    self.flow_points[v].waypoints = [self.flow_points[v].edge]
                                    for part in new_route:
                                        self.flow_points[v].waypoints.append(part)
                                    self.flow_points[v].point = 0
                                break

            v += 1
        #calcaulate the average journey length
        avg_a = self.average_journey_length()
        #print the stats on the effect of the ndoe being removed
        node_fail.fill_stats(reroute,noroute,avg_a,avg_b,start_rem,dest_rem,journey_rem,inter_node_rem)

    def nearest_node(self,node):
        """Returns the nearest junction in the network to the one removed."""
        node_dist = {}
        dists = []
        #loop though all nodes
        for near in self.nodes:
            #check the node is not the one removed, else calc the dist between them
            if self.__nodes_trunc[near] != self.__nodes_trunc[node]:
                dist = math.hypot(near[0] - node[0], near[1] - node[1]) 
                dists.append(dist)
                node_dist[dist] = near
        dists.sort()
        return node_dist[dists[0]]
        
    def average_journey_length(self,):
        """Calculates the average length of all journeys."""
        peeps_avg = []
        #go through all flow points (people)
        for peeps in self.flow_points:
            peep_total = 0
            #loop through the waypoints to calc the average
            for origin,dest in peeps.waypoints:
                #sum the dist between waypoints
                peep_total += self.orig_graph[self.__nodes_trunc [origin]][self.__nodes_trunc [dest]]['length']
            peeps_avg.append(peep_total)
        if len(peeps_avg) == 0:
            #if no flow points have routes
            return 0
        peeps_avg = sum(peeps_avg)/len(peeps_avg)
        return peeps_avg
    
    def time_config(self,start_time, tick_rate):
        self.time = start_time
        self.tick_rate  = tick_rate
    
    def tick(self,):
        done = True
        for peep in self.flow_points:
            if not(peep.finished):
                done = False # if people are still moving don't finish
                if self.time > peep.start_time:
                    peep.started = True
                    peep.move(self.tick_rate)#move people 
        self.time += datetime.timedelta(0,self.tick_rate)
        return done