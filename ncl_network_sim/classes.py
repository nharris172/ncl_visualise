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
            'reroute':{'num':0,'print_str':'number of people re-routed :'},
            'not_pos':{'num':0,'print_str':'number of people whose route was no longer possible :'},
            'avg_b':{'num':0,'print_str':'Average length before :'},
            'avg_a':{'num':0,'print_str':'Average length after :'},
            'avg_time_b':{'num':0,'print_str':'Average travel time before :'},
            'avg_time_a':{'num':0,'print_str':'Average travel time after :'},
        }
        
    def fail(self):
        """Run the edge failure code."""
        self.edge.failed = True
        self.fail_attr.network.edge_remove(self)
    
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
            'avg_b':{'num':0,'print_str':'Average length before :'},
            'avg_a':{'num':0,'print_str':'Average length after :'},
            'avg_time_b':{'num':0,'print_str':'Average travel time before :'},
            'avg_time_a':{'num':0,'print_str':'Average travel time after :'},
            'start_rem':{ 'num':0,'print_str':"number of people who's start node was removed:"},
            'inter_node_rem':{'num':0,'print_str':"number of people who had a intermediate node removed:"},
            'dest_rem':{'num':0,'print_str':"number of people who's destination node was removed:"},
            'reroute':{'num':0,'print_str':'number of people re-routed :'},
            'not_pos':{'num':0,'print_str':'number of people whose route was no longer possible :'},
            'journey_rem':{'num':0,'print_str':"number of people who's start/dest ended up being the same:"},
        }
        
    def fail(self,):
        """Runs the failure of node."""
        self.node.failed = True
        self.fail_attr.network.node_remove(self,)
        
    def fill_stats(self,reroute,not_pos,avg_a,avg_b,avg_time_b,avg_time_a,start_rem,dest_rem,journey_rem,inter_node_rem):
        """Populates the stats dict with the required information."""
        self.stats['reroute']['num'] = reroute
        self.stats['not_pos']['num'] = not_pos
        self.stats['avg_a']['num'] = avg_a
        self.stats['avg_b']['num'] = avg_b
        self.stats['avg_time_a']['num'] = avg_time_a
        self.stats['avg_time_b']['num'] = avg_time_b
        self.stats['start_rem']['num'] = start_rem
        self.stats['dest_rem']['num'] = dest_rem
        self.stats['inter_node_rem']['num'] = inter_node_rem
        self.stats['journey_rem']['num'] = journey_rem

    def print_stats(self,):
        """Prints the stats has in the stats dict."""
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
        
    def check_fails(self,):
        """Checks the failures in the list to see if any need to be run at the 
        current time."""
        fails = []
        for f in self.failures:
            if f.done:
                continue
            if f.time >= self.network.time and f.time < self.network.time + self.network.tick_rate:
                #print "FOUND A FAILURE"
                f.fail()#this is where the re-routing is done - goes to node failure class then network class
                f.done= True
                #print "F is:",f
                fails.append(f)
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
            if self.point ==0:
                if self.waypoints[self.point].start_node in self.network.nodes:
                    self.waypoints[self.point].start_node.add_flow(self.network.time)
                    
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
        #print self.graph.edge[self.graph.edges()[0][0]][self.graph.edges()[0][1]]
        #weighted shortest path
        #print "looking for route - origin = %s, dest = %s" %(source,target)
        try:
            route = nx.shortest_path(self.graph, source, target, WEIGHT)

        except:            
            #print self.graph.nodes()
            #makes the error happen again so can see a print out
            route = nx.shortest_path(self.graph, source, target, WEIGHT)
            print 'MAJOR ERROR', source, target, route
        
        waypoints =[]
        for j in range(len(route)-1):
            if self.__edges_class[(route[j],route[j+1])].start_node.failed or \
            self.__edges_class[(route[j],route[j+1])].end_node.failed:
                print 'route contains failure!'
            waypoints.append(self.__edges_class[(route[j],route[j+1])])
        return waypoints
    
    def create_waypoints(self, start, end, WEIGHT='time'):
        """"This creates a set of waypoints for a person if a route is possible"""
        try:
            #find shortest path
            new_route = self._shortest_path(start, end, WEIGHT)
        except nx.NetworkXNoPath:
            #no route possible
            new_route = False
        except nx.NetworkXError:
            #in any other error - likley to be that it could not the node in the network - this is top of the list of bugs
            print 'Could not find node in network. ORIGIN is: %s ; DEST is: %s'%(start.geom,end.geom)
            new_route = False
        return new_route
    
    def edge_remove(self,edgefail):
        """Updates all affected flow points when an edge is removed from the 
        network."""
        #find the edge to remove
        start,end = edgefail.edge.start_node,edgefail.edge.end_node
        #remove the edge from the network
        

        self.graph.remove_edge(start._truncated_geom,end._truncated_geom)
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
        avg_time_a = self.average_journey_length(length=False)
        #print stats on the affect of the edge failure
        edgefail.fill_stats(reroute,noroute,avg_b,avg_a,avg_time_b,avg_time_a)
        
    def node_remove(self,node_fail):
        """Updates for all people their waypoints given the removal of a junction"""
        errors_caught = 0
        #remove a junction from the network
        node_to_remove =node_fail.node._truncated_geom
        
        try:
            self.graph.remove_node(node_to_remove)
        except nx.NetworkXError:
            print '--------------!!!!!!!!!!!----------------------------------'
            print 'Could not remove node with geom ', node_to_remove, ' as if could not be found in the network'
            print '--------------!!!!!!!!!!!----------------------------------'
                
        avg_b = self.average_journey_length()
        avg_time_b = self.average_journey_length(length=False)
        v = 0
        reroute,noroute,start_rem,dest_rem,journey_rem,inter_node_rem = 0, 0, 0, 0, 0, 0
        #loop through all the flows
        
        while v < len(self.flow_points):

            #if the flow has not finished yet        
            if self.flow_points[v].finished == False:

                #if the flow has not started
                if self.flow_points[v].started == False:

                    #get start and end waypoints - don't need the others atm
                    start_waypoint = self.flow_points[v].waypoints[0].start_node
                    end_waypoint =self.flow_points[v].waypoints[-1].end_node
                    
                    #check if the node removed is the start node for the person
                    if start_waypoint == node_fail.node:
                        #find nearest node
                        new_start_waypoint = self.nearest_node(node_fail.node)
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
                            else:
                                #if a new route has been found update for the flow
                                reroute +=1
                                self.flow_points[v] = FlowPoint(self,new_route,self.flow_points[v].start_time)
                            
                    #check if the node removed is the destination for the flow
                    elif end_waypoint == node_fail.node:
                        dest_rem += 1
                        new_end_waypoint = self.nearest_node(node_fail.node)     
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
                            else:
                                #new route found
                                reroute +=1
                                self.flow_points[v] = FlowPoint(self,new_route,self.flow_points[v].start_time)
                    
                    #check all waypoints on all flows for failed nodes
                    else:
                        for edge in self.flow_points[v].waypoints:
                            #search through all the waypoints
                            #only need to check one of the origin or dest
                            origin, dest = edge.start_node,edge.end_node
                            if dest == node_fail.node:
                                inter_node_rem += 1
                                #if a macth is found, try to establish a new route for the person
                                new_route = self.create_waypoints(start_waypoint,end_waypoint)
                                if new_route == False:
                                    #no new route possible
                                    noroute +=1
                                    self.flow_points.remove(self.flow_points[v])
                                    v -= 1
                                else:
                                    #new route found
                                    reroute +=1
                                    self.flow_points[v] = FlowPoint(self,new_route,self.flow_points[v].start_time)
                                break
                            elif origin == node_fail.node:
                                inter_node_rem += 1
                                #if a macth is found, try to establish a new route for the person
                                new_route = self.create_waypoints(start_waypoint,end_waypoint)
                                if new_route == False:
                                    #no new route possible
                                    noroute +=1
                                    self.flow_points.remove(self.flow_points[v])
                                    v -= 1
                                else:
                                    #new route found
                                    reroute +=1
                                    self.flow_points[v] = FlowPoint(self,new_route,self.flow_points[v].start_time)
                                break
                    
                #if the flow has already started, but it not finished yet
                elif self.flow_points[v].started == True:
                    
                    comp_route =[]
                    #get waypoints - the points at either end of the edge the flow is on
                    start_waypoint = self.flow_points[v].edge.start_node
                    end_waypoint = self.flow_points[v].waypoints[-1].end_node
                    
                    #if the node where the flow last went through has been removed
                    if start_waypoint== node_fail.node:
                        #it is allowed to continue
                        comp_route = [self.flow_points[v].edge]
                        start_waypoint = self.flow_points[v].edge.start_node

                    #if the destination for the flow has been removed
                    elif end_waypoint == node_fail.node:
                        dest_rem += 1
                        new_end_waypoint = self.nearest_node(node_fail.node)     
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
                            else:
                                #if a new route has been found
                                reroute +=1
                                for part in new_route:
                                    comp_route.append(part)
                                self.flow_points[v].waypoints = comp_route
                                self.flow_points[v].point = 0
                    
                    #if the current edge the flow is on is unaffected
                    #checks the waypoints on the rest of the route
                    else:
                        #loops through the waypoints
                        for edge in self.flow_points[v].waypoints:
                            #check node at either end of edge
        
                            origin, dest = edge.start_node,edge.end_node
                           
                            if origin == node_fail.node:
                                if self.flow_points[v].started == True:
                                    pass
                                else:
                                    inter_node_rem += 1
                                    new_route = self.create_waypoints(start_waypoint,end_waypoint)
                                    if new_route == False:
                                        noroute +=1
                                        self.flow_points.remove(self.flow_points[v])
                                        v -= 1
                                    else:
                                        #if a new route has been found
                                        reroute +=1
                                        self.flow_points[v].waypoints = [self.flow_points[v].edge]
                                        for part in new_route:
                                            self.flow_points[v].waypoints.append(part)
                                            self.flow_points[v].point = 0
                                        break
                                    
                            elif dest == node_fail.node:
                                inter_node_rem += 1
                                new_route = self.create_waypoints(start_waypoint,end_waypoint)
                                if new_route == False:
                                    noroute +=1
                                    self.flow_points.remove(self.flow_points[v])
                                    v -= 1
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
        avg_time_a = self.average_journey_length(length=False)
        #print the stats on the effect of the ndoe being removed
        node_fail.fill_stats(reroute,noroute,avg_a,avg_b,avg_time_b,avg_time_a,start_rem,dest_rem,journey_rem,inter_node_rem)
        
        """Below stops the errors which occur sometimes -some routes contain 
        the failed node for some reason still.
        Should only be a temp fix!!!! Not recorded in stats as a result."""        
        """
        #check flows for failed node - no paths should have it in i think
        v = 0
        while v < len(self.flow_points):
            if self.flow_points[v].finished == True:
                break
            start_waypoint = self.flow_points[v].waypoints[0].start_node
            end_waypoint = self.flow_points[v].waypoints[-1].end_node
            
            if start_waypoint == node_fail.node:
                if self.flow_points[v].started == False:
                    self.flow_points.remove(self.flow_points[v])
                    errors_caught += 1
                    v -= 1
            elif end_waypoint == node_fail.node:
                if self.flow_points[v].finished == False:
                    self.flow_points.remove(self.flow_points[v])
                    errors_caught += 1
                    v -= 1
            else:
                for edge in self.flow_points[v].waypoints:
                    origin, dest = edge.start_node,edge.end_node
                    if origin == node_fail.node:
                        if self.flow_points[v].started == True:
                            pass
                        else:
                            #print "Inter origin waypoint = failed node;",self.flow_points[v].started, ". Finshed:", self.flow_points[v].finished
                            self.flow_points.remove(self.flow_points[v])
                            errors_caught += 1
                            v -= 1
                    elif dest == node_fail.node:
                        #print "Inter dest waypoint = failed node;", self.flow_points[v].started, ". Finshed:", self.flow_points[v].finished
                        self.flow_points.remove(self.flow_points[v])
                        errors_caught += 1
                        v -= 1
            v+=1
        
        if errors_caught > 0:
            print "------ Potential errors caught:",errors_caught,"------"
            exit()
        """ 
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