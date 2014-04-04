import networkx as nx
import shapefile
import math
from classes import NclNetwork,Nodes,Edges,Node,Edge
from tools import truncate_geom as _truncate_geom


def build_network(shp_file, speed_att, length_att):
    sf = shapefile.Reader(shp_file)
    shapes = sf.shapes()

    #create graph
    orig_G=nx.Graph()  
    
    out_nodes = []
    out_nodes_geom_lookup_dict = {} 
    
    all_nodes = []
    all_nodes_geom_lookup_dict = {}
    
    edges = []
    edge_geom_lookup_dict = {}
    
    left = []
    bottom = []
    right = []
    top = []
    
    if speed_att <> None:
        #finds the field number for the speed attribute, if it exists
        speed_field = 0
        while speed_field < len(sf.fields):
            if sf.fields[speed_field][0] == speed_att: 
                speed_field -= 1 #as the first field is not an actual attribute!
                break
            speed_field += 1 #if no speed field, will value will be greater than the number of fields so will get an error
        if speed_field == len(sf.fields):    
            print "Could not find field titled '%s' containing the speed data. Simulation will continue without speed being used." %(speed_att)
            speed_att = None
    
    if length_att <> None:
        #checks to see if length field is an attribute and which record it is
        length_field = 0
        while length_field < len(sf.fields):
            if sf.fields[length_field][0] == length_att: 
                length_field -= 1 #as the first field is not an actual attribute!
                break
            length_field += 1 #if no speed field, will value will be greater than the number of fields so will get an error
        if length_field == len(sf.fields):    
            print "Could not find field titled '%s' containing the length vales. Simulation will calcualte the lengths accordingly." %(speed_att)
            length_att = None
        
    edge_count = 0
    for shape in shapes:
        l,b,r,t = shape.bbox
        left.append(l)
        bottom.append(b)
        right.append(r)
        top.append(t)
        
        stat1 = shape.points[0]
        stat2 = shape.points[-1]
        #create stations out of edge end points. 
        for stat in [stat1,stat2]:
            if _truncate_geom(stat) not in out_nodes_geom_lookup_dict.keys():
                node_class = Node(stat,_truncate_geom(stat))
                
                out_nodes_geom_lookup_dict[node_class._truncated_geom] = node_class
                all_nodes_geom_lookup_dict[node_class._truncated_geom] = node_class
                
                out_nodes.append(node_class)
                all_nodes.append(node_class)
                
        for i in  range(len(shape.points)-1):
            #this creates the simplifed edges to create the network
            #the correct geometry is then stored in a dictionary so that i can go from simplfied geom to real world geom
            p1 = all_nodes_geom_lookup_dict.get(_truncate_geom(shape.points[i]),Node(shape.points[i],_truncate_geom(shape.points[i])))
            p2 = all_nodes_geom_lookup_dict.get(_truncate_geom(shape.points[i+1]),Node(shape.points[i+1],_truncate_geom(shape.points[i+1])))

            for p in [p1,p2]:
                all_nodes_geom_lookup_dict[p._truncated_geom] = p
            edge_class = Edge(p1,p2)
            
            if (p1._truncated_geom,p2._truncated_geom) not in orig_G.edges():
                
                #add the edge straight to the network on the discovery that it has not been added as yet
                if speed_att <> None:
                    #get the speed for the edge                 
                    speed = sf.record(edge_count)[speed_field]
                   
                    if length_att == None:
                        #calculate the length of the edge
                        orig_e,orig_n = p1._truncated_geom
                        dest_e,dest_n = p2._truncated_geom
                        #I know this calculation can be done mch easier, but can't remember how!
                        temp1 = (orig_e-dest_e)
                        temp2 = (orig_n-dest_n)
                        length = math.sqrt((temp1*temp1)+(temp2*temp2))
                    else:
                        length = float(sf.record(edge_count)[length_field])
                    
                    #calculate the time to travel the edge
                    time = length/speed
                    #add the edge and its attributes
                    orig_G.add_edge(p1._truncated_geom,p2._truncated_geom,{'length':length,'speed':speed,'time':time})
                else:
                    #add the edge
                    orig_G.add_edge(p1._truncated_geom,p2._truncated_geom)
                edge_geom_lookup_dict[(p1._truncated_geom,p2._truncated_geom)] = edge_class
                edges.append(edge_class)
        #iterate the edge count - used to get speeds assigned to the edges
        edge_count += 1 
        
    _bbox = (min(left),min(bottom),max(right),max(top))
    
    proper_nodes = Nodes(out_nodes,out_nodes_geom_lookup_dict)
    edges = Edges(edges,edge_geom_lookup_dict)
    print orig_G.number_of_nodes()
    print len(proper_nodes.nodes)
    return NclNetwork(orig_G, proper_nodes, edges, _bbox)



def build_net_from_db(conn, net_name, speed_att, length_att):
    import ogr, sys
    sys.path.append("C:/Users/Craig/Dropbox/GitRepo/nx_pgnet")
    import nx_pgnet
    #get network from database
    conn = ogr.Open(conn)
    orig_G = nx_pgnet.read(conn).pgnet(net_name)
    print orig_G.number_of_nodes()
    print orig_G.nodes()
    print orig_G.edges(data=True)
    #save current set of nodes as the main set of nodes
    proper_nodes = orig_G.nodes
    edges = orig_G.edges

    #add all linestring coords to orig_G network



    #when looping through atts to get coords for line strings, get bounding box stuff as well    
    
    
    #need to create a method which works out the bounding box for the network    
    _bbox = (min(left),min(bottom),max(right),max(top))
    
    return NclNetwork(orig_G, proper_nodes, edges, _bbox)