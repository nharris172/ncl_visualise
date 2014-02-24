import networkx as nx
import shapefile
import math
from classes import NclNetwork
from tools import truncate_geom as _truncate_geom

def build_network(shp_file):
    sf = shapefile.Reader(shp_file)
    shapes = sf.shapes()

    #create graph
    orig_G=nx.Graph()

    nodes_truncated = {}
    edges_truncated ={}
    edges = {}
    graph_edges = []
    out_nodes_dict = {} 
    node_check = {}
    for shape in shapes:
        metro_line_points = []
        stat1 = shape.points[0]
        stat2 = shape.points[-1]
        #create stations out of edge end points. 
        for stat in [stat1,stat2]:
            if stat not in out_nodes_dict.keys():
                if _truncate_geom(stat) not in out_nodes_dict.values():
                    out_nodes_dict[stat] = _truncate_geom(stat)
                    node_check[_truncate_geom(stat)] = stat
        for i in  range(len(shape.points)-1):
            #this creates the simplifed edges to create the network
            #the correct geometry is then stored in a dictionary so that i can go from simplfied geom to real world geom
            p1 = node_check.get(_truncate_geom(shape.points[i]),shape.points[i])
            p2 = node_check.get(_truncate_geom(shape.points[i+1]),shape.points[i+1])
            for p in [p1,p2]:
                node_check[p] = _truncate_geom(p)
                nodes_truncated[p] = _truncate_geom(p)
            p1_rounded = _truncate_geom(p1)
            p2_rounded = _truncate_geom(p2)
            if (p1_rounded,p2_rounded) not in graph_edges:
                graph_edges.append((p1_rounded,p2_rounded))
                edges_truncated[(p1,p2)]=(p1_rounded,p2_rounded)
                edges_truncated[(p2,p1)]=(p1_rounded,p2_rounded)
                edges[(p1_rounded,p2_rounded)] = (p1,p2)
                edges[(p2_rounded,p1_rounded)] = (p2,p1)
    #adds all simple edges to graph

    orig_G.add_edges_from(graph_edges)
    
    
    for origin, dest in orig_G.edges():
        e_origin, n_origin = origin
        e_dest, n_dest = dest
        e_diff =  e_origin- e_dest
        n_diff = n_origin - n_dest
        e_diff = e_diff * e_diff
        n_diff = n_diff * n_diff
        diff = math.sqrt(e_diff+n_diff)
        orig_G[origin][dest]['length'] = diff
    
        
    return NclNetwork(orig_G,out_nodes_dict.keys(),nodes_truncated,edges,edges_truncated)
