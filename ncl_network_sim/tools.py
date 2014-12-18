import random
import datetime


def truncate_geom_funtion_maker(dp=1):

    def truncate_geom_dp(p):
        """Rounds the geometry to nearest 10 this is to ensure the network in topologically correct"""
        return (round(float(p[0]),dp),round(float(p[1]),dp))
    return truncate_geom_dp

def manual_random_edges(EDGE_FAILURE_TIME,net_edges,built_network):
    """Creates a set of failures for edges randomly."""
    for i,time in enumerate(EDGE_FAILURE_TIME):
        line_to_fail = net_edges[i]
        built_network.Failures.add_edge_fail(line_to_fail,time)
        
def manual_random_nodes(NODE_FAILURE_TIME, junctions,built_network):
    """Creates a set of failures for nodes randomly."""
    for i,time in enumerate(NODE_FAILURE_TIME):
        node_to_fail = junctions[i]
        built_network.Failures.add_node_fail(node_to_fail,time)

def generate_failure_times(RANDOM,TIME_INTERVALS,NUMBER_OF_FAILURES,STARTTIME,HOURS_TO_RUN_FOR,built_network):
    """For a targted attack, a set of times are randomly generated or by a 
    defined interval."""
    
    if type(HOURS_TO_RUN_FOR) != int and HOURS_TO_RUN_FOR >= 1:
        print "-------------------------------\nAny time of an hour or longer must be an integer."
        exit()
        
    failure_times = []
    if RANDOM == True:
        while len(failure_times) < NUMBER_OF_FAILURES:
            if HOURS_TO_RUN_FOR < 1:        
                time = datetime.datetime(STARTTIME.year,STARTTIME.month,STARTTIME.day,STARTTIME.hour,random.randint(0,(60*HOURS_TO_RUN_FOR)))
            else: 
                time = datetime.datetime(STARTTIME.year,STARTTIME.month,STARTTIME.day,random.randint(STARTTIME.hour,STARTTIME.hour+HOURS_TO_RUN_FOR-1),random.randint(0,59))
            failure_times.append(time)
    elif TIME_INTERVALS <> None:
        while len(failure_times) < NUMBER_OF_FAILURES:
            secs = (TIME_INTERVALS*60) * (len(built_network.Failures.failures)+1)
            time = STARTTIME + datetime.timedelta(0,secs)
            failure_times.append(time)  
    return failure_times

def get_random_comp(NODE_EDGE_RANDOM, failure_times, built_network, junctions, net_edges):
    """Checks to see if any random failurs are schedules, and if so selects a 
    node or edge at random for removal"""
    for ftime in failure_times:
        #if appropriate time
        if ftime >= built_network.time and ftime < built_network.time + built_network.tick_rate:
            #if simulate either a node or edge failure
            if NODE_EDGE_RANDOM == 'NODE_EDGE' or NODE_EDGE_RANDOM == 'EDGE_NODE':
                NODE_EDGE_RANDOM = random.randint(0,1)
                if NODE_EDGE_RANDOM == 0: NODE_EDGE_RANDOM = 'NODE'
                else: NODE_EDGE_RANDOM = 'EDGE'
            #if simulate a node failure
            if NODE_EDGE_RANDOM == 'NODE':
                random.shuffle(junctions)
                node_to_fail = junctions[0]
                junctions.remove(node_to_fail)
                built_network.Failures.add_node_fail(node_to_fail,ftime)
            #if simulate an edge failure
            elif NODE_EDGE_RANDOM == 'EDGE':
                random.shuffle(net_edges)
                edge_to_fail = net_edges[0]
                net_edges.remove(edge_to_fail)
                built_network.Failures.add_edge_fail(edge_to_fail,ftime)
    
    return junctions, net_edges
    
def get_targted_comp(NODE_EDGE_RANDOM, failure_times,FLOW_COUNT_TIME,built_network,junctions,FLOW,DEGREE):
    """Checks to see if any failures are scheduled. If so selects a component 
    to remove in a targetd way (via flow or a metric) and using the time adds 
    the failure to the Failure set."""
    if FLOW == True and DEGREE == False:
        #check times for failures
        for ftime in failure_times:
            #if appropriate time
            #if ftime >= built_network.time and ftime < built_network.time + datetime.timedelta(0,built_network.tick_rate):
            if ftime >= built_network.time and ftime < built_network.time + built_network.tick_rate:
                max_flow = -99
                meth = None
                if NODE_EDGE_RANDOM == 'NODE_EDGE':
                    meth = random.randint(0,1)
                    if meth==0: meth = 'NODE'
                    else: meth = 'EDGE'
                #if nodes, calc flows and node to remove
                if NODE_EDGE_RANDOM == 'NODE' or meth == 'NODE':                    
                    for node in built_network.nodes:
                         if not node.failed:
                             num_flows = node.get_flows(hours=FLOW_COUNT_TIME[0],mins=FLOW_COUNT_TIME[1])
                             if num_flows > max_flow:
                                 max_flow = num_flows
                                 node_to_fail = node
                    built_network.Failures.add_node_fail(node_to_fail,ftime)
                    junctions.remove(node_to_fail)
                #if edges, calc flows and edge to remove
                elif NODE_EDGE_RANDOM == 'EDGE' or meth == 'EDGE':
                    for edge in built_network.edges:  
                        if not edge.failed:
                            num_flows = edge.get_flows(hours=FLOW_COUNT_TIME[0],mins=FLOW_COUNT_TIME[1])
                            if num_flows > max_flow:
                                max_flow = num_flows
                                edge_to_fail = edge
                    built_network.Failures.add_edge_fail(edge_to_fail,ftime)
        return junctions
    elif FLOW == False and DEGREE == True:        
        #check times for failures
        for ftime in failure_times:
            #if appropriate time
            if ftime >= built_network.time and ftime < built_network.time + datetime.timedelta(0,built_network.tick_rate):
                
                node_degrees = built_network.graph.degree()
                max_degree = max(node_degrees.values())
            
                nodes_w_max=[] #stores all nodes with a equal max degree
                for node in node_degrees:
                    if node_degrees[node] == max_degree:
                        nodes_w_max.append(node)
                
                node_to_fail = None
                while node_to_fail == None:
                    #pick one of the nodes at random
                    item = random.randint(0,len(nodes_w_max)-1)
                    coord = list(nodes_w_max[item])
                    #find the node instance so it can be removed
                    for node in built_network.nodes:
                        tcoord = truncate_geom(node.geom)
                        if tcoord[0]==coord[0] and tcoord[1]==coord[1]:
                            node_to_fail = node
                            break
                    #if node could not be found, remove from the list so not selected again
                    if node_to_fail == None:
                        nodes_w_max.pop(item)
                #add failure intance
                built_network.Failures.add_node_fail(node_to_fail,ftime)
                junctions.remove(node_to_fail)
        return junctions
    else:
        return junctions
        
def write_metadata(META_FILE,net_source_shpfile,shpfile_name,length_att,speed_att,
                   default_speed,STARTTIME,SECONDS_PER_FRAME,NUMBER_OF_PEOPLE,
                   routes_not_pos,HOURS_TO_RUN_FOR,WEIGHT,FLOW_COUNT_TIME):
    """"""
    META_FILE.write("Metadata file file created\n")
    META_FILE.write("Network origin: shapefile- %s\n" %(net_source_shpfile))
    if net_source_shpfile == True:
        META_FILE.write("Network shapefile: %s\n" %(shpfile_name))
    META_FILE.write("Declared length attribute: %s\n" %(length_att))
    META_FILE.write("Declared speed attribute: %s\n" %(speed_att))
    META_FILE.write("Declared default speed: %s\n" %(default_speed))
    META_FILE.write("------------------------------\n")
    META_FILE.write("Simulation start time: %s\n" %(STARTTIME))
    META_FILE.write("Number of seconds per frame: %s\n" %(SECONDS_PER_FRAME))
    META_FILE.write("Number of flow points generated: %s\n" %(NUMBER_OF_PEOPLE))
    META_FILE.write("Number of flows which there journey cannot be completed: %s\n" %(routes_not_pos))
    META_FILE.write("Length of time flows start over: %s\n" %(HOURS_TO_RUN_FOR))
    META_FILE.write("Weight assinged for shortest path assignment: %s\n" %(WEIGHT))
    META_FILE.write("Time frame which flows are counted over for nodes and edges(hours,minutes): %s\n" %(FLOW_COUNT_TIME))
    META_FILE.write("------------------------------\n")
    return
    
def write_failure_data(META_FILE,MANUAL,RANDOM_TIME,TIME_INTERVALS,NUMBER_OF_FAILURES,TARGETED,
                             NODE_EDGE_RANDOM,FLOW,DEGREE,FAILURE_TIMES,EDGE_FAILURE_TIME,NODE_FAILURE_TIME):
    """"""
    META_FILE.write("Failure created\n")    
    META_FILE.write("Failure parameters:\n")
    META_FILE.write("Manualy set times: %s\n"%(MANUAL))    
    META_FILE.write("Failurs use a targted appraoch: %s\n"%(TARGETED))
    if TARGETED == True:
        META_FILE.write("\tFlow set as: %s\n"%(FLOW))
        META_FILE.write("\tDegree set as: %s\n"%(DEGREE))
    META_FILE.write("Components to remove: %s\n"%(NODE_EDGE_RANDOM))    
    if MANUAL == False:
        META_FILE.write("Number of failures to take place: %s\n"%(NUMBER_OF_FAILURES))
        META_FILE.write("Random set as: %s\n"%(RANDOM_TIME))
        META_FILE.write("Time intervals set as: %s\n"%(TIME_INTERVALS))
    else:
        if TARGETED == False:
            META_FILE.write("Number of node failures: %s\n"%(len(NODE_FAILURE_TIME)))
            META_FILE.write("Number of edge failures: %s\n"%(len(EDGE_FAILURE_TIME)))
        else:        
            META_FILE.write("Number of failures: %s\n"%(len(FAILURE_TIMES)))
    META_FILE.write("------------------------------\n")
    return

def point_in_poly(coord,poly):
    x,y = coord
    n = len(poly)
    inside = False

    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xints = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x,p1y = p2x,p2y

    return inside

def geo_failure(shp_file, junctions, net_edges):
    import shapefile
    polygons = []
    sf = shapefile.Reader(shp_file)
    shapes = sf.shapes()
    for shape in shapes:
        coords = []
        for p in  shape.points:
            coords.append(p)
        polygons.append(coords)

    polygon = coords
    nodes_inside = []
    number_inside = 0
    #extract list of coords
    for polygon in polygons:
        for nd in junctions:
            coords = nd.geom
            x,y = coords[0],coords[1]
            coord = float(x),float(y)
            inside = point_in_poly(coord,polygon)
            if inside == True:
                nodes_inside.append(nd)
                number_inside += 1
    
    failed_edges = []
    
    for eg in net_edges:
        for nd in nodes_inside:
            if eg.start_node == nd or eg.end_node == nd:
                failed_edges.append(eg)
    
    return number_inside,nodes_inside,failed_edges
    
def geo_failure_comp(NODE_EDGE_RANDOM,FAILURE_TIMES,FLOW_COUNT_TIME,built_network,junctions,edge_set,SHP_FILE,GEO_F_TIME):
    """"""
    for ftime in GEO_F_TIME:
        #if appropriate time
        if ftime >= built_network.time and ftime < built_network.time + built_network.tick_rate:
 
            number_inside,nodes_inside,failed_edges = geo_failure(SHP_FILE,junctions,edge_set)
            for nd in nodes_inside:
                #add node failure
                built_network.Failures.add_node_fail(nd,ftime)
                
                try:
                    junctions.remove(nd)
                except:
                    #may have already been removed under one of the other failure methods
                    pass
            #add edge failure             
            for edge in failed_edges:
            #   built_network.Failures.add_edge_fail(edge,ftime)    
                try:
                    edge_set.remove(edge)                
                except:
                    #the edge may have already been removed in another failure process
                    pass
                    
    return junctions, edge_set
    
    