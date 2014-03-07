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
    graph_edges = []
    
    
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
    for shape in shapes:
        l,b,r,t = shape.bbox
        left.append(l)
        bottom.append(b)
        right.append(r)
        top.append(t)
        metro_line_points = []
        
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
            if (p1._truncated_geom,p2._truncated_geom) not in graph_edges:
                graph_edges.append((p1._truncated_geom,p2._truncated_geom))
                edge_geom_lookup_dict[(p1._truncated_geom,p2._truncated_geom)] = edge_class
                edges.append(edge_class)
                
    #adds all simple edges to graph

    orig_G.add_edges_from(graph_edges)
        
    _bbox = (min(left),min(bottom),max(right),max(top))
    
    proper_nodes = Nodes(out_nodes,out_nodes_geom_lookup_dict)
    edges = Edges(edges,edge_geom_lookup_dict)
    
    return NclNetwork(orig_G,proper_nodes, edges,_bbox)
