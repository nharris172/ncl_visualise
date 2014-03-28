import networkx as nx
import shapefile
import math
from classes import NclNetwork,Nodes,Edges,Node,Edge
from tools import truncate_geom as _truncate_geom


def build_network(shp_file):
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
   
    #calculates the field the speed attribute is in
    speed_field = 0
    while speed_field < len(sf.fields):
        if sf.fields[speed_field][0] == 'speed': 
            speed_field -= 1 #as the first field is not an actual attribute!
            break
        speed_field += 1 #if no speed field, will value will be greater than the number of fields so will get an error
    
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
                #get the speed for the edge 
                speed = sf.record(edge_count)[speed_field]
                #calculate the length of the edge
                orig_e,orig_n = p1._truncated_geom
                dest_e,dest_n = p2._truncated_geom
                #I know this calculation can be done mch easier, but can't remember how!
                temp1 = (orig_e-dest_e)
                temp2 = (orig_n-dest_n)
                length = math.sqrt((temp1*temp1)+(temp2*temp2))
                #calculate the time to travel the edge
                time = length/speed
                #add the edge and its attributes
                orig_G.add_edge(p1._truncated_geom,p2._truncated_geom,{'length':length,'speed':speed,'time':time})
                edge_geom_lookup_dict[(p1._truncated_geom,p2._truncated_geom)] = edge_class
                edges.append(edge_class)
        #iterate the edge count - used to get speeds assigned to the edges
        edge_count += 1 
        
    _bbox = (min(left),min(bottom),max(right),max(top))
    
    proper_nodes = Nodes(out_nodes,out_nodes_geom_lookup_dict)
    edges = Edges(edges,edge_geom_lookup_dict)
    
    return NclNetwork(orig_G,proper_nodes, edges,_bbox)
