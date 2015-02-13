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
    """Checks to see if any random failurs are scheduled, and if so selects a 
    node or edge at random for removal."""
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

def area_sign(poly):
    res = 0.0
    for i in range(0,len(poly)-1):
        p1 = poly[i]
        p2 = poly[i+1]
        res += (p1[0]*p2[1])-(p1[1]*p2[0])
        
    if res < 0: return -1
    elif res > 0: return 1
    elif res == 0: return 0
    else: "Major error. Logic error."

        
def line_intersection(line1,line2):
    
    
    l1p1 = line1[0];l1p2 = line1[1]
    l2p1 = line2[0];l2p2 = line2[1]

    poly=[l1p1,l1p2,l2p1,l1p1]    
    sign1 = area_sign(poly)
    poly=[l1p1,l1p2,l2p2,l1p1]    
    sign2 = area_sign(poly)
    poly=[l2p1,l2p2,l1p1,l2p1]
    sign3 = area_sign(poly)
    poly=[l2p1,l2p2,l1p2,l2p1]
    sign4 = area_sign(poly)
    
    if sign1 <> sign2 and sign3 <> sign4: return 1 #inserect
    else: return 0 #do not intersect
    
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
    #loop through the polygons in the shapefile
    for polygon in polygons:
        #loop through the junctions in the network
        for nd in junctions:
            coords = nd.geom
            x,y = coords[0],coords[1]
            coord = float(x),float(y)
            #find if the junction lies in the polygon
            inside = point_in_poly(coord,polygon)
            if inside == True:
                nodes_inside.append(nd)
                number_inside += 1
    
    #find those edges where at least one of is endpoints have failed
    failed_edges = []
    for eg in net_edges:
        for nd in nodes_inside:
            if eg.start_node == nd or eg.end_node == nd:
                failed_edges.append(eg)
    
    #find all edge segments which intersect with the hazard areas
    #loop thorugh all edge segments(line1)
    lines_inter = 0
    for eg in net_edges:
        line1=eg.start_node.geom,eg.end_node.geom
        for polygon in polygons:
            #loop through edge segments of polygon (line2)
            for i in range(0,len(polygon)-1):
                line2=polygon[i],polygon[i+1]
                #use a line intersection algorithm to check
                intersect = line_intersection(line1,line2)
                if intersect == 1: #lines intersect
                    lines_inter += 1
                    failed_edges.append(eg)

    #find all edge segments which lie within a hazard area
    lines_in = 0
    for eg in net_edges:
        line1=eg.start_node.geom,eg.end_node.geom
        for polygon in polygons:
            inside1 = point_in_poly(line1[0],polygon)
            if inside1 == True:
                inside2 = point_in_poly(line1[1],polygon)
                if inside2 == True:
                    lines_in += 1
                    failed_edges.append(eg)
                
    print 'lines_inter:',lines_inter   
    print 'lines_inside:',lines_in
    #once found a segment, need to remove the whole edge
    #add edge to failed egdes
    
    return number_inside,nodes_inside,failed_edges
    
def geo_failure_comp(NODE_EDGE_RANDOM,FAILURE_TIMES,FLOW_COUNT_TIME,built_network,junctions,edge_set,SHP_FILE,GEO_F_TIME):
    """"""
    for ftime in GEO_F_TIME:
        #if appropriate time
        if ftime >= built_network.time and ftime < built_network.time + built_network.tick_rate:
            #get nodes and edges affecred by hazard area
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
                #
                built_network.Failures.add_edge_fail(edge,ftime)    
                try:
                    edge_set.remove(edge)                
                except:
                    #the edge may have already been removed in another failure process
                    pass
            print 'edge failures added'
    return junctions, edge_set


def load_census_flows(areas,flow_csv,built_network):
    """
    Takes the flow zones and finds the nodes in each, then assigns to each flow
    loaded from  the csv randomly a node which falls in its specified start and 
    end zone. The zones must have the same names as the start and end zones
    specified for the flows i.e. MSOA name.
    """
    #load in census areas
    #get list of nodes which fall in each area
    area_nodes = get_area_nodes(areas,built_network)
    #load in census data
    flows_to_create = create_csv_flows(flow_csv)    
    #assign flows based on random selection of network node in census area
    flow_list = assign_flows_to_nodes(area_nodes,flows_to_create)
    return flow_list
    
def get_area_nodes(areas,G):
    """
    Method to assign a node within the census area for the flows.
    """
    import shapefile
    polygons = []
    name_list=[]
    sf = shapefile.Reader(areas)
    geom = sf.shapeRecords()

    #create list of polygons    
    for shape in geom:
        coords = []
        name_list.append(shape.record[1])
        for p in shape.shape.points: coords.append(p)
        polygons.append(coords)
 
    poly=0
    nodes_per_poly=[]
    node_per_area ={}
    f = 0
    total=0
    while f < len(polygons):
        nodes_per_poly.append([])
        f+=1
    node_list = []
    
    #create a list of nodes
    for nd in G.nodes: node_list.append(nd)

    for polygon in polygons:
        temp = []
        node_count = 0
        #loop thourgh network nodes
        for nd in node_list:
            node_count+=1
            coords = nd.geom
            x,y = coords[0],coords[1]
            coord = float(x),float(y)
            inside = point_in_poly(coord,polygon)
            if inside == True:
                #when find a node which lies in an area, remove node from the network copy
                node_list.remove(nd)
                total+=1
                nodes_per_poly[poly].append(nd)
                temp.append(nd)
            
        #add to a dict based on polygone name thus order does not matter
        node_per_area[str(name_list[poly])]=temp
        poly += 1
    
    return node_per_area

def create_csv_flows(data_file):
    """
    Load from the csv flow data including start and end areas.
    """
    f = open(data_file,'r')    
    #read first line - list of worklocations (first in sequence is empty)
    work_locations = f.readline().split(',')
    flows_to_create = []
    for line in f.readlines():
        #reads all lines of data
        home_locations = line.split(',')
        i = 1
        #loop through the line of data for the from area
        while i < len(home_locations):
            z = 0
            #loop through in case more than one flow from same origin to dest
            while z < int(home_locations[i]):
                #get locations and add to list if all flows
                temp = home_locations[0],work_locations[i]
                flows_to_create.append(temp)
                z += 1
            i += 1
    f.close()
    return flows_to_create

def assign_flows_to_nodes(nodes_per_area,flows_to_create):
    """
    For each flow assign a node randomly whihc lies within its start and end
    area. If no nodes in the area ignore flow. If only one node in area ignore
    flow.
    """
    flow_od = []
    #loop through list of flows
    for flow in flows_to_create:
        #get origin and destination
        origin = flow[0]
        destination = flow[1]
        o = False
        d = False
        #loop through list of areas
        for key in nodes_per_area.keys():
            #if the area is the origin
            if key == origin:
                #shuffle the nodes and select one
                random.shuffle(nodes_per_area[key])
                #if the area has no nodes lying in it
                if len(nodes_per_area[key]) == 0:
                    break
                o = nodes_per_area[key][0]
            #if the area is the destination
            if key == destination:
                random.shuffle(nodes_per_area[key])
                #if the area has no nodes lying it
                if len(nodes_per_area[key])==0:
                    break
                d = nodes_per_area[key][0]
                #re-assign d if same as o
                if o == d:
                    #this will get stuck in only one node in area - need to sort a escape clause
                    if len(nodes_per_area[key]) > 1:
                        d = nodes_per_area[key][1]
                    else:
                        #Cannot assign flow as origin and destination the same"
                        break
            #check if both have been assigned-if so stop looping
            if o <> False and d <> False:
                temp = o,d
                flow_od.append(temp)
                break
            
    print "-------------------------"
    print "Numnber of flows created:",len(flow_od)
    print "Number of flows not possible:",len(flows_to_create)-len(flow_od)
    print "-------------------------"
    #as using network with down to a roads only, some areas don't have any nodes
    return flow_od    