import math
import datetime
import networkx as nx



class EdgeFailure:
    """Handles the failure of an edge and the associated outcomes."""
    def __init__(self,fail,_edge_class,_time):
        self.node = False
        self.done = False
        self.fail_attr = fail
        self.edge = _edge_class
        self.time = _time
        self.stats = {
            'reroute':{'num':0,'print_str':'Number of flows re-routed:'},
            'not_pos':{'num':0,'print_str':'Number of failed flows:'},
            'avg_b':{'num':0,'print_str':'Average length before:'},
            'avg_a':{'num':0,'print_str':'Average length after:'},
            'avg_time_b':{'num':0,'print_str':'Average travel time before:'},
            'avg_time_a':{'num':0,'print_str':'Average travel time after:'},
        }
        
    def fail(self,reassign_start,reassign_dest,weight):
        """Run the edge failure code."""
        self.edge.failed = True
        self.fail_attr.network.edge_remove(self,reassign_start,reassign_dest,weight)
    
    def fill_stats(self,reroute,not_pos,avg_a,avg_b,avg_time_b,avg_time_a):
        """Populate the stats dict witht the stats from the affects of the edge
        removal of the flow points."""
        self.stats['reroute']['num'] =reroute
        self.stats['not_pos']['num'] =not_pos
        self.stats['avg_a']['num'] =avg_a
        self.stats['avg_b']['num'] =avg_b
        self.stats['avg_time_b']['num'] =avg_time_b
        self.stats['avg_time_a']['num'] =avg_time_a

    def print_stats(self,):
        """Prints the stats as in the stats dict."""
        print '----------------------------'
        for key,val in self.stats.iteritems():
            print val['print_str'],val['num']
    
    def write_stats(self,FILE):
        """Write stats on the failure to the metadata file."""
        FILE.write("Edge Failure\n")
        FILE.write("Time of failure: %s\n"%(self.time))
        FILE.write("Edge removed: %s\n"%(str(self.edge.geom)))
        FILE.write("Stats relating to the failure:\n")
        for key, val in self.stats.iteritems():
            FILE.write(val['print_str']+" "+str(val['num'])+"\n")
        FILE.write("------------------------------\n")
            

class NodeFailure:
    """Handles the failure of a node from the network and the associated 
    outcomes."""
    def __init__(self,fail,_node_class,_time):
        self.edge = False
        self.done = False
        self.fail_attr = fail
        self.node = _node_class
        self.time = _time
        self.stats = {
            'avg_b':{'num':0,'print_str':'Average length before:'},
            'avg_a':{'num':0,'print_str':'Average length after:'},
            'avg_time_b':{'num':0,'print_str':'Average travel time before:'},
            'avg_time_a':{'num':0,'print_str':'Average travel time after:'},
            'start_rem':{ 'num':0,'print_str':"Number of flows where the start failed:"},
            'inter_node_rem':{'num':0,'print_str':"Number of flows where a waypoint failed:"},
            'dest_rem':{'num':0,'print_str':"Number of flows where the destination has failed:"},
            'journey_rem':{'num':0,'print_str':"Number of flows who's start/dest ended up being the same:"},
            'failure_start_rem':{'num':0,'print_str':"Number of flows failed as start failed:"},
            'failure_dest_rem':{'num':0,'print_str':"Number of flows failed as destination failed:"},
            'start_rem_no_effect':{'num':0,'print_str':"Number of flows unaffected where their start has failed:"},
            'failed_inter_rem':{'num':0,'print_str':"Number of failed flows as a waypoint failed:"},
            'reroute_start_fail': {'num':0,'print_str':"Number of flows rerouted as start failed:"},
            'reroute_dest_fail':{'num':0,'print_str':"Number of flows rerouted as destination failed:"},
            'reroute_inter_fail':{'num':0,'print_str':"Number of flows rerouted as a waypoint failed:"},
            'start_is_end':{'num':0,'print_str':"Number of failures where reassigned start/end clashed:"},
            'failed_flows':{'num':0,'print_str':"Number of failed flows:"},
            'rerouted_flows':{'num':0,'print_str':"Number of flows rerouted:"},
            'noroute':{'num':0,'print_str':"Number of failed flows as no route possible:"},
            }
        
    def fail(self,reassign_start,reassign_dest,weight):
        """Runs the failure of node."""
        self.node.failed = True
        self.fail_attr.network.node_remove(self,reassign_start,reassign_dest,weight)
        
    #def fill_stats(self,reroute,not_pos,avg_a,avg_b,avg_time_b,avg_time_a,start_rem,dest_rem,journey_rem,inter_node_rem,failure_start_rem,failure_dest_rem,start_rem_no_effect,failed_inter_rem,reroute_start_fail,reroute_dest_fail,reroute_inter_fail):
    def fill_stats(self,noroute,avg_a,avg_b,avg_time_b,avg_time_a,start_rem,dest_rem,journey_rem,inter_node_rem,failed_dest_rem,failed_start_rem,start_rem_no_effect,failed_inter_rem,reroute_start_fail,reroute_dest_fail,reroute_inter_fail,failed_flows,rerouted_flows,start_is_end):

        """Populates the stats dict with the required information."""
        #self.stats['avg_a']['num'] = avg_a
        #self.stats['avg_b']['num'] = avg_b
        #self.stats['avg_time_a']['num'] = avg_time_a
        #self.stats['avg_time_b']['num'] = avg_time_b
        self.stats['start_rem']['num'] = start_rem
        self.stats['failure_start_rem']['num'] = failed_start_rem
        self.stats['start_rem_no_effect']['num'] = start_rem_no_effect
        self.stats['reroute_start_fail']['num'] = reroute_start_fail
        self.stats['dest_rem']['num'] = dest_rem
        self.stats['failure_dest_rem']['num'] = failed_dest_rem
        self.stats['reroute_dest_fail']['num'] = reroute_dest_fail
        self.stats['inter_node_rem']['num'] = inter_node_rem
        self.stats['failed_inter_rem']['num'] = failed_inter_rem
        self.stats['reroute_inter_fail']['num'] = reroute_inter_fail
        self.stats['journey_rem']['num'] = journey_rem
        self.stats['rerouted_flows']['num'] = rerouted_flows
        self.stats['failed_flows']['num'] = failed_flows 
        self.stats['start_is_end']['num'] = start_is_end
        self.stats['noroute']['num'] = noroute
        
    def print_stats(self,):
        """Prints the stats has in the stats dict."""
        print '----------------------------'
        for key,val in self.stats.iteritems():
            print val['print_str'],val['num']
    
    def write_stats(self,FILE):
        """Write stats on the failure to the metadata file."""
        FILE.write("Node Failure\n")
        FILE.write("Time of failure: %s\n"%(self.time))
        FILE.write("Node removed: %s\n"%(self.node.geom))
        FILE.write("Stats relating to the failure:\n")
        for key, val in self.stats.iteritems():
            FILE.write(val['print_str']+" "+str(val['num'])+"\n")
        FILE.write("------------------------------\n")

class Failures:
    """Runs the failure of nodes/edges in the network."""
    def __init__(self,_network):
        self.network = _network
        self.failures = []
        
    def add_edge_fail(self,edge,time):
        """Removes an edge and runs the resulting steps required to update 
        everything."""
        self.failures.append(EdgeFailure(self,edge,time))
        
    def add_node_fail(self,node,time):
        """Removes a node and runs the resulting steps required to update 
        everything."""
        self.failures.append(NodeFailure(self,node,time))
        
    def check_fails(self,reassign_start,reassign_dest,weight):
        """Checks the failures in the list to see if any need to be run at the 
        current time."""
        fails = []
        #loop through the failures
        for f in self.failures:
            #if f.node == False:
                if f.done:
                    continue
                if f.time >= self.network.time and f.time < self.network.time + self.network.tick_rate:
                    #run node/edge failure
                    f.fail(reassign_start,reassign_dest,weight)
                    f.done = True
                    fails.append(f)
        #for f in self.failures:
        #    if f.edge == False:
        #       if f.done:
        #           continue
        #       if f.time >= self.network.time and f.time < self.network.time + self.network.tick_rate:
        #           #run node/edge failure
        #           f.fail()
        #           f.done = True
        #           fails.append(f)
                
        return fails

class FlowPoint:
    """Handles the management of the  flowpoints and thier movement throught 
    the network during the simulation/visualisation."""
    def __init__(self,network,waypoints,start_time,speed = False):
        self.network = network
        self.waypoints = waypoints
        self.start_time = start_time
        self.speed = speed
        self.point = 0
        self.loc = waypoints[0].start_node.geom
        self.finished = False
        self.started = False
        self.edge = waypoints[0]
    
    def move(self,time):
        """Moves the person the correct location. Updates the lists of nodes 
        and edges visited during the time step for the person as well."""
        if not self.speed:
            step = self.edge.speed * time
        else:
            step = self.speed * time
        ax, ay = self.loc
        bx, by = self.edge.end_node.geom
        dist = math.hypot(bx-ax, by-ay)
        while dist < step:
            self.loc = self.edge.end_node.geom
            if self.point == 0:
                try:
                    if self.waypoints[self.point].start_node in self.network.nodes:
                        self.waypoints[self.point].start_node.add_flow(self.network.time)
                except:
                    print self.point
                    print len(self.waypoints)
                    
            if self.waypoints[self.point].end_node in self.network.nodes:
                self.waypoints[self.point].end_node.add_flow(self.network.time)
            self.waypoints[self.point].add_flow(self.network.time)
            self.point +=1
            
            if self.point == len( self.waypoints): 
                self.finished = True
                self.edge = None
                return
            
            self.edge = self.waypoints[self.point]
            step -= dist
            self.loc = self.edge.start_node.geom
            ax, ay = self.waypoints[self.point].start_node.geom
            bx, by = self.waypoints[self.point].end_node.geom
            dist = math.hypot(bx-ax, by-ay)
        bearing = math.atan2(by-ay, bx-ax)
        self.loc = (self.loc[0]+ step*math.cos(bearing),self.loc[1] + step * math.sin(bearing))
        self.edge = self.waypoints[self.point]



class Node:
    """Network Node"""
    def __init__(self,geom,truncated_geom):
        self.geom = geom 
        self._truncated_geom = truncated_geom
        self.failed = False
        self.network = None
        self.flows ={}
        
    def add_flow(self,time):
        """store flows at each time step"""
        self.flows[time] = self.flows.get(time,0.0)
        self.flows[time] += 1.0
        
    def get_flows(self,hours=0,mins=0,secs=0):
        """gets the number of flows in a given epoch"""
        tot_secs = secs + (mins*60) + (hours*60*60)
        cutoff = self.network.time - datetime.timedelta(0,tot_secs)
        num_flows = 0
        for time,flow in self.flows.iteritems():
            if time > cutoff:
                num_flows += flow
        return num_flows
        
class Nodes:
    """Network nodes"""
    def __init__(self,nodes,truncated_geom_lookup):
        self.nodes = nodes
        self.truncated_geom_lookup = truncated_geom_lookup
        
    def add_network(self,network):
        """Add network to each node"""
        for node in self.nodes:
            node.network = network


class Edge:
    """Network Edge"""
    def __init__(self,start_node,end_node,info):
        self.start_node = start_node 
        self.end_node = end_node
        self.geom = (self.start_node.geom,self.end_node.geom)
           
        ax, ay = self.start_node.geom
        bx, by = self.end_node.geom
            
        if 'length' in info.keys():
            self.length = info['length']
        else:
            self.length = math.hypot(bx-ax, by-ay)
        if 'speed' in info.keys():
            self.speed = info['speed']
        else:
            self.speed= None
        if 'time' in info.keys():
            self.time = info['time']
        else:
            self.time = None
        self.failed = False
        self.network = None
        self.flows = {}
        
        self.reversed =  Edge_reversed(self)
        
    def add_flow(self,time):
        """store flows at each time step"""
        self.flows[time] = self.flows.get(time,0.0)
        self.flows[time] += 1.0
        
    def get_flows(self,hours=0,mins=0,secs=0):
        """gets the number of flows in a given epoch"""
        tot_secs = secs + (mins*60) + (hours*60*60)
        cutoff = self.network.time - datetime.timedelta(0,tot_secs)
        num_flows = 0
        for time,flow in self.flows.iteritems():
            if time > cutoff:
                num_flows += flow
        return num_flows
    
class Edge_reversed:
    """create a reversed copy of the edge but still store flow with the original edge"""
    def __init__(self,edge):
        self.edge = edge
        self.start_node= self.edge.end_node
        self.end_node = self.edge.start_node
        self.length = self.edge.length
        self.speed = self.edge.speed
        self.time = self.edge.time
        self.failed = self.edge.length
        self.network = self.edge.network
        
        
    def add_flow(self,time):
        """add flow to orig edge"""
        self.edge.flows[time] = self.edge.flows.get(time,0.0)
        self.edge.flows[time] += 1.0

        

class Edges:
    """Handler for the network edges"""
    def __init__(self,edges,truncated_geom_lookup):
        self.edges = edges
        self.truncated_geom_lookup = truncated_geom_lookup
    
    def __getitem__(self,trunc_geom):
        """fetchs the edge given a truncated geometry"""
        flipped_trunc_geom = (trunc_geom[1],trunc_geom[0])
        if trunc_geom in self.truncated_geom_lookup.keys():
            return self.truncated_geom_lookup[trunc_geom]
        #if the start and end node and the other way round fetches the revered
        #edge
        return self.truncated_geom_lookup[flipped_trunc_geom].reversed
    
    def add_network(self,network):
        """adds the network class as an attribute to all edges"""
        for edge in self.edges:
            edge.network = network

class NclNetwork:
    """Handler for the generic functions for the analysis and visualisation the
    network."""
    def __init__(self,nx_graph,_nodes,_edges,_bbox):
        self.orig_graph = nx_graph
        self.graph = self.orig_graph.copy()
        
        self.__nodes_class = _nodes
        self.nodes = self.__nodes_class.nodes
        
        self.__nodes_class.add_network(self)
        
        self.__edges_class = _edges
        self.edges = self.__edges_class.edges
        
        self.__edges_class.add_network(self)
        
        self.bbox= _bbox
        
        self.flow_points = []
        self.Failures = Failures(self,)
        self.time = None
        self.tick_rate  = None
    
    def add_flow_point(self, start, end, start_time, WEIGHT,end_time=False):
        """Adds a new flow point the list."""
        route = self.create_waypoints(start,end, WEIGHT)
        if route <> False:
            if end_time:
                time = (end_time - start_time).total_seconds()
                distance = 0
                for edge in route:
                    distance += edge.length
                speed = distance/time
            else:
                speed=False
            self.flow_points.append(FlowPoint(self,route,start_time,speed=speed))
            return True
        else:
            return False 
    
    def _shortest_path(self, start, end, WEIGHT):
        """Finds the shortest path for a flow point and creates a set of 
        waypoints given this path."""
        source = start._truncated_geom
        target = end._truncated_geom
    
        try:
            route = nx.shortest_path(self.graph, source, target, WEIGHT)
        except KeyError:
            try:
                print self.graph[source]
            except:
                return 'key error on source node'
            try:
                print self.graph[target]
            except:
                return 'key error on destination node'
    
        waypoints =[]
        for j in range(len(route)-1):
            if self.__edges_class[(route[j],route[j+1])].start_node.failed or \
            self.__edges_class[(route[j],route[j+1])].end_node.failed:
                print 'route contains failure!'
            waypoints.append(self.__edges_class[(route[j],route[j+1])])
        return waypoints
    
    def create_waypoints(self, start, end, WEIGHT):
        """"This creates a set of waypoints for a person if a route is possible"""
        try:
            #find shortest path
            new_route = self._shortest_path(start, end, WEIGHT)
            if new_route == 'key error on source node' or new_route == 'key error on destination node':
                return new_route
                
        except nx.NetworkXNoPath:
            #no route possible
            new_route = False
        
        return new_route
        
    def edge_remove(self,edgefail,reassign_start,reassign_dest,weight):
        """Updates all affected flow points when an edge is removed from the 
        network."""
        #find the edge to remove
        start,end = edgefail.edge.start_node,edgefail.edge.end_node
             
        try:        
            self.graph.remove_edge(start._truncated_geom,end._truncated_geom)
            #remove the edge from the network
            print "Removed edge(",start._truncated_geom,",",end._truncated_geom,")"      
            v = 0
            avg_b = self.average_journey_length()
            avg_time_b = self.average_journey_length(length=False)
            reroute,noroute=0,0
            while v < len(self.flow_points):
                #if the people have not started traveling yet
                if not self.flow_points[v].finished:
                    if not self.flow_points[v].started:
                        #loop through all edges in the waypoints
                        for edge in self.flow_points[v].waypoints:
                            origin,dest = edge.start_node,edge.end_node
                            #find any possible route uses the edge
                            if start == origin or start == dest or end == origin or end == dest:
                                #get start and end nodes
                                start_waypoint = self.flow_points[v].waypoints[0].start_node
                                end_waypoint = self.flow_points[v].waypoints[-1].end_node
                                #calcualte the new route, if one is possible
                                new_route = self.create_waypoints(start_waypoint,end_waypoint,weight)
                                if new_route == False:
                                    #if no route is possible - graph has more than one connected component
                                    self.flow_points.remove(self.flow_points[v])
                                    v -= 1
                                    noroute +=1
                                elif new_route == None:
                                    #this will only be used if an unknown error is generated in the create_waypoints function
                                    print "An error has occured in creating the waypoints"
                                    exit()
                                else:
                                    reroute+=1
                                    #if a route has been sucessfuly found
                                    self.flow_points[v] = FlowPoint(self,new_route,self.flow_points[v].start_time)
                                break
                    else:
                        
                        for edge in self.flow_points[v].waypoints:
                            origin,dest = edge.start_node,edge.end_node
                            #find any possible route uses the edge
                            if start == origin or start == dest or end == origin or end == dest:
                                #get start and end nodes
                                start_waypoint = self.flow_points[v].edge.start_node
                                end_waypoint = self.flow_points[v].waypoints[-1].end_node
                                #calcualte the new route, if one is possible
                                new_route = self.create_waypoints(start_waypoint,end_waypoint,weight)
                                if new_route == False:
                                    #if no route is possible - graph has more than one connected component
                                    self.flow_points.remove(self.flow_points[v])
                                    v -= 1
                                    noroute +=1
                                elif new_route == None:
                                    #this will only be used if an unknown error is generated in the create_waypoints function
                                    print "An error has occured in creating the waypoints!"
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
            avg_time_a = self.average_journey_length(length=False)
            #print stats on the affect of the edge failure
            edgefail.fill_stats(reroute,noroute,avg_b,avg_a,avg_time_b,avg_time_a)        
        
        except:
            pass
        
        
  
    def node_remove(self,node_fail,reassign_start, reassign_dest, weight):
        """
        """
        #remove a junction from the network
        node_to_remove = node_fail.node._truncated_geom
        print "Removed node(",node_fail.node._truncated_geom,")"
        #remove the failed node from the network
        try:
            self.graph.remove_node(node_to_remove)
        except nx.NetworkXError:
            print "Could not remove node with geom ", node_to_remove, " as it could not be found in the network"
        
        #calculate the average journey lengths/times
        avg_b = self.average_journey_length()
        avg_time_b = self.average_journey_length(length=False)
        
        #create parameters to store flow statistics
        v = 0       
        noroute,start_rem,dest_rem,journey_rem,inter_node_rem,failed_start_rem,failed_dest_rem,start_rem_no_effect,failed_inter_rem,reroute_start_fail,reroute_dest_fail,reroute_inter_fail,start_is_end = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
        
        #loop through all the flows
        while v < len(self.flow_points):

            #if the flow has not finished yet        
            if self.flow_points[v].finished == False:
                
                #get start and end waypoints
                start_junction = self.flow_points[v].waypoints[0].start_node
                dest_junction =self.flow_points[v].waypoints[-1].end_node
                
                #check if flow origin has failed
                if start_junction == node_fail.node:
                    start_rem += 1 #count flow as start being removed
                    #if the flow has started        
                    if self.flow_points[v].started == True:
                        #it will have passed away from this node already
                        start_rem_no_effect += 1
                        
                    #if the flow has not started yet
                    elif self.flow_points[v].started == False:
                        #does the user want to assume the flow will reroute to the nearest node
                        if reassign_start == True:
                            #get nearest possible junction as a new start node
                            new_start_junction = self.nearest_node(node_fail.node)
                            
                            if new_start_junction == dest_junction:
                                #remove flow if new start == dest or == failed
                                self.flow_points.remove(self.flow_points[v])
                                failed_start_rem += 1
                                start_is_end += 1
                                v -= 1
                            else:
                                #create a set of waypoints for flow
                                new_route = self.create_waypoints(new_start_junction,dest_junction,weight)
                                if new_route == False:
                                    #new route not possible
                                    noroute += 1
                                    failed_start_rem += 1
                                    self.flow_points.remove(self.flow_points[v])
                                    v -= 1
                                elif new_route == None or new_route == 'key error on source node' or new_route == 'key error on destnation node':
                                    #catch error and stop simulation
                                    print "An error occured creating the waypoints! Reason for rerouting was due to failure of start node for flow. Error returned was %s" %new_route
                                    exit()
                                else:
                                    #new route found
                                    reroute_start_fail += 1
                                    self.flow_points[v] = FlowPoint(self,new_route,self.flow_points[v].start_time)
                        else:
                            #remove flow as user requested origins not to be reassigned
                            self.flow_points.remove(self.flow_points[v])
                            failed_start_rem += 1
                            v -= 1
                    else:
                        #indicates a major error - stop simulation
                        print "---\nMajor error! (c)\n---"
                        exit()
                        
                #check if flow destination has failed
                elif  dest_junction == node_fail.node:
                    #record that a flow has had it destination removed
                    dest_rem += 1
                    #if the user wants the flow to be rerouted to the nearest destination
                    if reassign_dest == True:
                        #find nearest junction to the failed
                        new_dest_junction = self.nearest_node(node_fail.node)
                        
                        if new_dest_junction == start_junction or new_dest_junction == node_fail.node:
                            #remove flow if new dest == start or == failed
                            self.flow_points.remove(self.flow_points[v])
                            failed_dest_rem += 1
                            start_is_end += 1
                            v -= 1
                        else:
                            #if flow has started
                            if self.flow_points[v].started == True:

                                #check new dest is not part of the edge the flow is currently on                                
                                if  new_dest_junction == self.flow_points[v].edge.end_node:
                                    #if the nearest dest is the end of the edge the flow is on
                                    #only need to add the edge as the route
                                    self.flow_points[v].waypoints = [self.flow_points[v].edge]
                                    self.flow_points[v].point = 0
                                    
                                elif new_dest_junction == self.flow_points[v].edge.start_node:
                                    #flow has gone past new destiantion as its the beginning of the edge its currently on
                                    #need to find a new route back to this node
                                    #add to the new route the current edge its on
                                    comp_route = [self.flow_points[v].edge]
                                    #find new route from the end of the current edge to the eestination, the beginning of teh current edge
                                    new_route = self.create_waypoints(self.flow_points[v].edge.end_node,new_dest_junction,weight)
                                        
                                    if new_route == False:
                                        #new route not possible
                                        noroute +=1
                                        failed_dest_rem += 1
                                        self.flow_points.remove(self.flow_points[v])
                                        v -= 1
                                    elif new_route == None or new_route == 'key error on source node' or new_route == 'key error on destination node':
                                        #if an error is returned from the rerouting. Report and exit.
                                        print "An error occured creating the waypoints! Rerouting as the flow destination had failed. Error returned was %s" %new_route
                                        exit()
                                    else:
                                        #route found to new destination
                                        reroute_dest_fail += 1
                                        #append new route to the existing route - the current edge only
                                        for item in new_route: comp_route.append(item)
                                        self.flow_points[v].waypoints = comp_route
                                        self.flow_points[v].point = 0
                                    
                                else:
                                    #else the new destination is not on the edge the flow is on or its original source
                                    #generate new route current edge start and new destination
                                    new_route = self.create_waypoints(self.flow_points[v].edge.start_node,new_dest_junction,weight)
                                    if new_route == False:
                                        #new route not possible
                                        noroute +=1
                                        failed_dest_rem += 1
                                        self.flow_points.remove(self.flow_points[v])
                                        v -= 1
                                    elif new_route == None or new_route == 'key error on source node' or new_route == 'key error on destination node':
                                        #error returned finding new route. Report and exit.
                                        print "An error has occured creating waypoints! Rerouting as the flow destination has failed. Error returned was %s" %new_route
                                        exit()
                                    else:
                                        #new route found to new dest
                                        reroute_dest_fail += 1
                                        comp_route = []
                                        for item in new_route: comp_route.append(item)
                                        
                                        self.flow_points[v].waypoints = comp_route
                                        self.flow_points[v].point = 0
                                
                            #if flow has not started
                            elif self.flow_points[v].started == False:
                                #chose new dest and reroute
                                new_route = self.create_waypoints(start_junction,new_dest_junction,weight)
                                if new_route == False:
                                    #new route not possible
                                    noroute +=1
                                    failed_dest_rem += 1
                                    self.flow_points.remove(self.flow_points[v])
                                    v -= 1
                                elif new_route == None or new_route == 'key error on source node' or new_route == 'key error on destination node':
                                    #error returned finding new route. Report and exit.
                                    print "An error occured creating the waypoints! Rerouting as dest node failed on inactive flow. Error returned was %s" %new_route
                                    exit()
                                else:
                                    #new route found
                                    reroute_dest_fail += 1
                                    self.flow_points[v] = FlowPoint(self,new_route,self.flow_points[v].start_time)
                            else:
                                #indicates a major error
                                print "Major error! (a)"
                                exit() 
                    else:
                        #remove flow as user requested no reassignment of destinations    
                        self.flow_points.remove(self.flow_points[v])
                        failed_dest_rem += 1
                        v -= 1
                        
                #check if part of the flow route has failed
                else:
                    #check the route for those which have already started
                    if self.flow_points[v].started == True:
                        #first check if the node at the end of the current edge has failed
                        if self.flow_points[v].edge.end_node == node_fail.node:
                            #the flow is on an edge with no node at its end, thus should be removed
                            inter_node_rem += 1
                            failed_inter_rem += 1
                            noroute +=1
                            self.flow_points.remove(self.flow_points[v])
                            v -= 1
                        elif self.flow_points[v].edge.start_node == node_fail.node:
                            #the flow should not be affected by this but need to catch here
                            pass
                        else:
                            #need to loop through from the edge identified as the current edge  
                            check = False
                            for edg in self.flow_points[v].waypoints:
                                if edg == self.flow_points[v].edge and check == False:
                                    #allows to check only those edges which it still has to go over
                                    check = True 
                                #if the flow has yet to go over or on the edge
                                if check == True:
                                    origin, dest = edg.start_node,edg.end_node
                                    #check if edge start has failed
                                    if origin == node_fail.node:
                                        inter_node_rem += 1
                                        
                                        #if both nodes are the same
                                        if self.flow_points[v].edge.end_node == self.flow_points[v].waypoints[-1].end_node:
                                            pass
                                        else:
                                            #find new route for flow
                                            new_route = self.create_waypoints(self.flow_points[v].edge.start_node,self.flow_points[v].waypoints[-1].end_node,weight)
                                            
                                            if new_route == False:
                                                #new route not possible
                                                noroute +=1
                                                failed_inter_rem += 1
                                                self.flow_points.remove(self.flow_points[v])
                                                v -= 1
                                            elif new_route == None or new_route == 'key error on source node' or new_route == 'key error on destination node':
                                                #error returned when finding new route. Report and exit()
                                                print "An error occured creating the waypoints! Rerouting as node at begining og edge has failed. Error returned was %s" %new_route
                                                exit()
                                            else:
                                                #new route found
                                                reroute_inter_fail += 1
                                                self.flow_points[v].waypoints = new_route
                                                self.flow_points[v].point = 0
                                            #stop this loop as failure found in flow route
                                            break
                                    
                                    #check if edge end has failed
                                    elif dest == node_fail.node:
                                        inter_node_rem += 1
                                        comp_route = [self.flow_points[v].edge]
                                        #if both nodes are the same
                                        if self.flow_points[v].edge.end_node == self.flow_points[v].waypoints[-1].end_node:
                                            pass
                                        else:
                                            #if the flow is on an edge, then need re-route from the end of the edge
                                            new_route = self.create_waypoints(self.flow_points[v].edge.end_node,self.flow_points[v].waypoints[-1].end_node,weight)
                                            if new_route == False:
                                                #new route not possible
                                                noroute +=1
                                                failed_inter_rem += 1
                                                self.flow_points.remove(self.flow_points[v])
                                                v -= 1
                                            elif new_route == None or new_route == 'key error on source node' or new_route == 'key error on destination node':
                                                #error returned finding new route. Report and exit.
                                                print "An error occured creating the waypoints! Rerouting as the end of an edge in an active route had failed. Error returned was %s" %new_route
                                                exit()
                                            else:
                                                #new route found
                                                reroute_inter_fail += 1
                                                for item in new_route: comp_route.append(item)
                                                self.flow_points[v].waypoints = comp_route
                                                self.flow_points[v].point = 0
                                        #stop looping as failure found in flow route
                                        break
                                    else: pass
                                else: pass
                    #check the route for those which have not started yet
                    elif self.flow_points[v].started == False:
                        
                        for edge in self.flow_points[v].waypoints:
                            origin, dest = edge.start_node,edge.end_node
                            #check if edge start or end has failed
                            if origin == node_fail.node or dest == node_fail.node:
                                inter_node_rem += 1
                                #create new route from start node to destination
                                new_route = self.create_waypoints(self.flow_points[v].waypoints[0].start_node,self.flow_points[v].waypoints[-1].end_node,weight)
                                    
                                if new_route == False:
                                    #new route not possible
                                    noroute +=1
                                    failed_inter_rem += 1
                                    self.flow_points.remove(self.flow_points[v])
                                    v -= 1
                                elif new_route == None or new_route == 'key error on source node' or new_route == 'key error on destination node':
                                    #error returned when finding new route. Report and exit.
                                    print "An error has occured creating waypoints. Rerouting a stationary flow due to failure in route. Error returned was %s" %new_route
                                    exit()
                                else:
                                    #new route found
                                    reroute_inter_fail += 1
                                    self.flow_points[v] = FlowPoint(self,new_route,self.flow_points[v].start_time)
                                #stop looping as failure found in flow route
                                break
                            else: pass
                    else: 
                        #major error. exit.
                        print "Major error! (b)"
                        exit()     
            v += 1
        
        #calcaulate the average journey length
        avg_a = self.average_journey_length()
        avg_time_a = self.average_journey_length(length=False)
        #print the stats on the effect of the ndoe being removed
        failed_flows = failed_dest_rem+failed_start_rem+failed_inter_rem
        rerouted_flows = reroute_start_fail+reroute_dest_fail+reroute_inter_fail
        node_fail.fill_stats(noroute,avg_a,avg_b,avg_time_b,avg_time_a,start_rem,dest_rem,journey_rem,inter_node_rem,failed_dest_rem,failed_start_rem,start_rem_no_effect,failed_inter_rem,reroute_start_fail,reroute_dest_fail,reroute_inter_fail,failed_flows,rerouted_flows,start_is_end)

        
    def nearest_node(self,node):
        """Returns the nearest junction in the network to the one removed."""
        node_dist = {}
        dists = []
        #loop though all nodes
        
        for near in self.nodes:
            #check the node is not the one removed, else calc the dist between them
            if near != node and not near.failed:
                dist = math.hypot(near.geom[0] - node.geom[0], near.geom[1] - node.geom[1]) 
                dists.append(dist)
                node_dist[dist] = near
        dists.sort()
        return node_dist[dists[0]]
        
    def average_journey_length(self,active=False,length=True):
        """Calculates the average length of journeys."""
        peeps_avg = []
        #go through all flow points (people)
        for peeps in self.flow_points:
            if active:
                if peeps.finished or peeps.started == False:
                    continue
            peep_total = 0
            #loop through the waypoints to calc the average
            for edge in peeps.waypoints:
                #sum the dist between waypoints
                if length==True:
                    peep_total += edge.length
                else:
                    peep_total += edge.time
            peeps_avg.append(peep_total)
        if len(peeps_avg) == 0:
            #if no flow points have routes
            return 0
        peeps_avg = sum(peeps_avg)/len(peeps_avg)
        return peeps_avg
    
    def average_journey_left(self,active=False):
        """Calculates the average length of journeys parts left"""
        peeps_avg = []
        #go through all flow points (people)
        for peeps in self.flow_points:
            if active:
                if peeps.finished or peeps.started == False:
                    continue
            peep_total = 0
            #loop through the waypoints to calc the average
            for edge in peeps.waypoints[peeps.point:len(peeps.waypoints)]:
                #sum the dist between waypoints
                peep_total += edge.length
            peeps_avg.append(peep_total)
        if len(peeps_avg) == 0:
            #if no flow points have routes
            return 0
        peeps_avg = sum(peeps_avg)/len(peeps_avg)
        return peeps_avg
    
    def number_flows(self,active):
        num = 0
        for peeps in self.flow_points:
            if active:
                if peeps.finished or peeps.started == False:
                    continue
            num+=1
        return num
    
    def time_config(self,start_time, tick_rate):
        
        self.tick_rate  = datetime.timedelta(seconds =tick_rate)
        self.time = start_time - self.tick_rate
    
    def tick(self,):
        done = True
        for peep in self.flow_points:
            if not(peep.finished):
                done = False # if people are still moving don't finish
                if self.time > peep.start_time:
                    peep.started = True
                    peep.move(self.tick_rate.total_seconds())#move people 
        self.time += self.tick_rate
        return done