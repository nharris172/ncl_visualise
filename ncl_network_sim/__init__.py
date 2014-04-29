import networkx as nx
import shapefile
import math
from classes import NclNetwork,Nodes,Edges,Node,Edge
from tools import truncate_geom as _truncate_geom


def build_network(shp_file, speed_att=None,default_speed=1, length_att=None):
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
   
        #get coordinates     
        stat1 = shape.points[0]
        stat2 = shape.points[-1]
        
        #create stations out of edge end points
        
        #need to figure out exactly how this works
        for stat in [stat1,stat2]:
        #takes every node and adds if not already added it to the list of nodes
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
            
            info ={}
            if (p1._truncated_geom,p2._truncated_geom) not in orig_G.edges():
                
                #add the edge straight to the network on the discovery that it has not been added as yet
                speed = default_speed
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
                if speed == 0:
                    speed = default_speed
                time = length/speed
                #add the edge and its attributes
                info = {'length':length,'speed':speed,'time':time}
                orig_G.add_edge(p1._truncated_geom,p2._truncated_geom,info)

                edge_class = Edge(p1,p2,info)
                edge_geom_lookup_dict[(p1._truncated_geom,p2._truncated_geom)] = edge_class
                edges.append(edge_class)
        #iterate the edge count - used to get speeds assigned to the edges
        edge_count += 1 
    _bbox = (min(left),min(bottom),max(right),max(top))

    proper_nodes = Nodes(out_nodes,out_nodes_geom_lookup_dict)
    edges = Edges(edges,edge_geom_lookup_dict)
    print '---------------------'
    print 'nodes in network:',orig_G.number_of_nodes()
    print 'station nodes:',len(proper_nodes.nodes)
    print '---------------------'
    return NclNetwork(orig_G, proper_nodes, edges, _bbox)

def build_net_from_db(conn, net_name,speed_att=None,default_speed=1, length_att=None):
    import ogr, sys
    sys.path.append("C:/Users/Craig/Dropbox/GitRepo/nx_pgnet")
    import nx_pgnet
    #get network from database
    conn = ogr.Open(conn)
    db_G = nx_pgnet.read(conn).pgnet(net_name)

    #needed for the classes
    out_nodes = []
    out_nodes_geom_lookup_dict = {} 
      
    all_nodes = []
    all_nodes_geom_lookup_dict = {}
    
    edges = []
    edge_geom_lookup_dict = {}     
        
    #add all linestring coords to orig_G network
    orig_G= nx.Graph()
    e_list = []
    n_list = []
    #reads the network and create a new one with all nodes and egdes for real vis
    
    #adds all stations to the lists for the class
    for nd in db_G.nodes_iter():
        #loop through stations(nodes)
        #find the start of the coordinate        
        char = 0
        while str(db_G.node[nd]['Wkt'])[char] <> '(':  char += 1

        #get the coordinate from the string
        coord = str(db_G.node[nd]['Wkt'])[char+1:-1]
        
        #split the coordinate on the space
        char = 0
        while coord[char] <> ' ': char += 1
        coord = [float(coord[:char]),float(coord[char+1:])]

        #add the node to the class lists
        if _truncate_geom(coord) not in out_nodes_geom_lookup_dict.keys():
            node_class = Node(coord,_truncate_geom(coord))
   
            out_nodes_geom_lookup_dict[node_class._truncated_geom] = node_class
            all_nodes_geom_lookup_dict[node_class._truncated_geom] = node_class
            
            out_nodes.append(node_class)
            all_nodes.append(node_class)
                   
    #loop through the edges in the db network
    for o,d in db_G.edges_iter():
        #get the list of coordinates which make the linestring
        coordlist = db_G[o][d]['Wkt']
        coordlist = coordlist[12:-1]
        coordlist = coordlist.split(',')

        #convert coordinates to a tuples
        coordlist_tuples = []
        for coord in coordlist:
            char = 0
            while coord[char] <> ' ': char += 1
            coordlist_tuples.append([float(coord[:char]),float(coord[char+1:])])
            
        coordlist = coordlist_tuples        
        #to get bounds for bounding box, add to make a list of eastings and northings
        for coord in coordlist:
            e,n = coord
            e_list.append(e)
            n_list.append(n)
            
        #loop through the list of coordinates for the linestring
        j = 0         
        while j < len(coordlist)-1:

            p1 = all_nodes_geom_lookup_dict.get(_truncate_geom(coordlist[j]),Node(coordlist[j],_truncate_geom(coordlist[j])))
            p2 = all_nodes_geom_lookup_dict.get(_truncate_geom(coordlist[j+1]),Node(coordlist[j+1],_truncate_geom(coordlist[j+1])))
                      
            for p in [p1,p2]:
                all_nodes_geom_lookup_dict[p._truncated_geom] = p
            
            info = {}
            if (p1._truncated_geom,p2._truncated_geom) not in orig_G.edges():
                
                #add the edge straight to the network on the discovery that it has not been added as yet
                
                #code to check attributes in db_G             
                if length_att == None:
                    #calculate the length of the edge
                    orig_e,orig_n = p1._truncated_geom
                    dest_e,dest_n = p2._truncated_geom
                    #I know this calculation can be done mch easier, but can't remember how!
                    temp1 = (orig_e-dest_e)
                    temp2 = (orig_n-dest_n)
                    length = math.sqrt((temp1*temp1)+(temp2*temp2))
                else:
                    #get length attribute from db_G
                    length = db_G[o][d][length_att]                                      

                #get the speed for the edge                    
                if speed_att == None:
                    speed = default_speed
                else:
                    speed = db_G[o][d][speed_att]
                    
                #calculate the time to travel the edge
                time = float(length)/float(speed)

                #add the edge and its attributes
                info = {'length':length,'speed':speed,'time':time}
                orig_G.add_edge(p1._truncated_geom,p2._truncated_geom,info)
                
                edge_class = Edge(p1,p2,info)
                edge_geom_lookup_dict[(p1._truncated_geom,p2._truncated_geom)] = edge_class
                edges.append(edge_class)
            j += 1
    
    proper_nodes = Nodes(out_nodes, out_nodes_geom_lookup_dict)
    edges = Edges(edges, edge_geom_lookup_dict)
            
    print '---------------------'
    print 'nodes in network:',orig_G.number_of_nodes()
    print 'station nodes:',len(proper_nodes.nodes)
    print '---------------------'
     
    _bbox = (min(e_list),min(n_list),max(e_list),max(n_list))
    return NclNetwork(orig_G, proper_nodes, edges, _bbox)
    
    