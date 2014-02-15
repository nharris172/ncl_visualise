import pygame
import ncl_visualize
import datetime 
import shapefile
import networkx as nx
import random
import math

"""
Current issues:
Major:

Other:
-Develop node failure methods for failure at any time step
-It may be just me, but some nodes don't show until they have been traveled to, even though they have been travelled from - not 100% of this though

To do/ideas:
-Flow through nodes based on a set time ie. last two hours
-In dense networks, changing colours of edges might be better than line thickness
-Failure at different times (not just at the bginning)
"""
# my class designed so that i can interpolate locations of people when given waypoints,speed and starttime
class flow_point:
	def __init__(self,waypoints,speed,start_time):
		self.waypoints = waypoints
		self.speed = speed
		self.start_time = start_time
		self.loc = waypoints[0][0]
		self.speed
		self.point = 0
		self.finished = False
		self.started = False
	def move(self,time):
		"""moves the person the correct location"""
		lines = []
		step = self.speed*time
		ax, ay = self.loc
		bx, by = self.waypoints[self.point][1]
		dist = math.hypot(bx-ax, by-ay)
		while dist<step:
			self.loc = self.waypoints[self.point][1]
			self.point+=1
			lines.append(self.waypoints[self.point-1])
			if self.point== len( self.waypoints):
				self.finished = True
				return lines
			step -= dist
			ax, ay = self.waypoints[self.point][0]
			bx, by = self.waypoints[self.point][1]
			dist = math.hypot(bx-ax, by-ay)
		bearing = math.atan2(by-ay, bx-ax)
		self.loc = (self.loc[0]+ step*math.cos(bearing),self.loc[1] + step*math.sin(bearing))
		return lines

def truncate_geom(p):
	"""Rounds the geometry to nearest 10 this is to ensure the network in topologically correct"""
	return (int(10 * round(float(p[0])/10)),int(10 * round(float(p[1])/10)))

def node_removed(G, NODE_TO_REMOVE, counts, speed):
    """Updates for all people their waypoints given the removal of a station/node"""
    count_new_routes,count_start_node_removed,count_end_node_removed,count_no_route_possible,count_no_route_needed = counts
    #remove a station from the network    
    node_to_remove = truncate_geom(stations[NODE_TO_REMOVE])
    G.remove_node(node_to_remove)
    #shorten coords into a shorter format    
    node_to_remove = truncate_geom(stations[NODE_TO_REMOVE])
    v = 0
    #loop through all people
    while v < len(people):
        #if the people have yet to set off
        if vis_time <= people[v].start_time:
            #get start and end waypoints - don't need the others atm
            start_waypoint, rubbish = people[v].waypoints[0]
            rubbish, end_waypoint = people[v].waypoints[len(people[v].waypoints)-1]
            
            start = truncate_geom(start_waypoint)
            end = truncate_geom(end_waypoint)
            #check if the node removed is the start node for the person
            if start == node_to_remove:
                count_start_node_removed += 1
                #find nearest node
                new_start_waypoint = nearest_node(G, NODE_TO_REMOVE)            
                #calculate new set of waypoints
                if new_start_waypoint == end:
                    #the closest node to the origin is the dest, so no route needed
                    count_no_route_needed += 1
                    people.remove(people[v])
                    v -= 1
                else:
                    #find the new route thorugh the function
                    new_route = create_waypoints(G, truncate_geom(new_start_waypoint), end)
                    #actions depending on the result from the funcation called above
                    if new_route == False:
                        #if no route possible
                        count_no_route_possible += 1
                        people.remove(people[v])
                        v -= 1
                    elif new_route == None:
                        #this should never be used, but was used in testing
                        pass
                    else:
                        #if a new route has been found update for the person
                        people[v] = (flow_point(new_route,speed,people[v].start_time))
                        count_new_routes += 1
                    
            #check if the node removed is the destination for the person
            elif end == node_to_remove:
                count_end_node_removed += 1
                new_end_waypoint = nearest_node(G, NODE_TO_REMOVE)
                if start == new_end_waypoint:
                    count_no_route_needed += 1
                    people.remove(people[v])
                    v -= 1
                else:
                    new_route = create_waypoints(G, start, truncate_geom(new_end_waypoint))
                    if new_route == False:
                        count_no_route_possible += 1
                        people.remove(people[v])
                        v -= 1
                    elif new_route == None:
                        pass
                    else:
                        people[v] = (flow_point(new_route,speed,people[v].start_time))
                        count_new_routes += 1
                        
            else:
                for origin, dest in people[v].waypoints:
                    #search through all the waypoints
                    #only need to check one of the origin or dest
                    if truncate_geom(dest) == node_to_remove:
                        #if a macth is found, try to establish a new route for the person
                        new_route = create_waypoints(G, start, end)
                        if new_route == False:
                            count_no_route_possible += 1
                            people.remove(people[v])
                            v -= 1
                        elif new_route == None:
                            pass
                        else:
                            people[v] = (flow_point(new_route,speed,people[v].start_time))
                            count_new_routes += 1
                        break
            v += 1        
        else:
            #method for handling the circumstance where people are traveling and thier destination is removed
            #need to identify if they have passed the removed nodes/edges. If so, or are doung so, allow them to
            #if they have yet to get to the affected location, reroute them from the next station in their route
            exit()
            pass
            
    counts = count_new_routes,count_start_node_removed,count_end_node_removed,count_no_route_possible,count_no_route_needed
    return G, counts

def edge_removed(G, edge_to_remove, counts, speed):
    """Handles an instance when an edge is removed"""
    count_new_routes,count_start_node_removed,count_end_node_removed,count_no_route_possible,count_no_route_needed = counts

    #find the edge to remove
    start,end = metro_graph_edges[edge_to_remove]
    #remove the edge from the network
    G.remove_edge(start,end)
  
    v = 0
    while v < len(people):
        #if the people have not started traveling yet
        if vis_time <= people[v].start_time:
            #loop through all edges in the waypoints
            for origin,dest in people[v].waypoints:
                origin = truncate_geom(origin)
                dest = truncate_geom(dest)
                #find any possible route uses the edge
                if start == origin or start == dest or end == origin or end == dest:
                    #get start and end nodes
                    start_waypoint, rubbish = people[v].waypoints[0]
                    rubbish, end_waypoint = people[v].waypoints[len(people[v].waypoints)-1]
                    #calcualte the new route, if one is possible
                    new_route = create_waypoints(G, truncate_geom(start_waypoint), truncate_geom(end_waypoint))
                    if new_route == False:
                        #if no route is possible - graph has more than one connected component
                        count_no_route_possible += 1
                        people.remove(people[v])
                        v -= 1
                    elif new_route == None:
                        #this will only be used if an unknown error is generated in the create_waypoints function
                        exit()
                    else:
                        #if a route has been sucessfuly found
                        people[v] = (flow_point(new_route,speed,people[v].start_time))
                        count_new_routes += 1
                    break
        else:
            #holder for handling those people who need re-routing mid journey
            pass
        v += 1
    
    counts = count_new_routes,count_start_node_removed,count_end_node_removed,count_no_route_possible,count_no_route_needed
    return G, counts

def nearest_node(G, NODE_TO_REMOVE):
    """Find the nearest station to NODE_TO_REMOVE"""
    #this will be geogrpahical as best arrpoximator for a pedestrian rather than track length
    updated_stations=[]
    for item in stations_truncated:        
        updated_stations.append(item)
    #updated_stations.remove(stations[station_removed])
    e_removed, n_removed = stations_truncated[NODE_TO_REMOVE]
    mindiff = 9999999999999999999.0
    u = 0
    #for each of the stations in updated stations
    for e_station,n_station in updated_stations:
        if e_station == e_removed and n_station == n_removed:
            #if the station is the one which has been been removed
            pass
        else:
            #calc the distance between the subject and the removed node
            e_diff = e_removed - e_station
            n_diff = n_removed - n_station
            e_diff = e_diff * e_diff
            n_diff = n_diff * n_diff
            diff = math.sqrt(e_diff+n_diff)
            if diff < mindiff and diff > 0:
                u_closest = u
                mindiff = diff
        u += 1
    
    #check station is in correct format - i.e is it in the network nodes
    good = False
    nde = stations_truncated[u_closest]
    for nd in G.nodes():
        if nd == nde:
            good = True
            break

    #if node is not the same as any of those in the network        
    if good == False:
        print 'could not find node in network - unknown cause'
        exit()
    return nde
       
def create_waypoints(G, start, end):
    """"This creates a set of waypoints for a person if a route is possible"""
    try:
        route = nx.shortest_path(G,source=start, target=end)
        #if path found create the waypoint set
        #this is copied from the original code used for creating the people
        path =[]
        for j in range(len(route)-1):
            path.append(metro_links[(route[j],route[j+1])])
        new_route = path
    except nx.NetworkXNoPath:
        #no route possible
        new_route = False
    except nx.NetworkXError:
        #in any other error - likley to be that it could not the node in the network - this is top of the list of bugs
        print 'Could not find node in network'
        new_route = None
        print 'start=', start
        print 'end=', end
        route = nx.shortest_path(G,source=start, target=end)#this is so I can see the error until I sort it out finally
        #exit the appliocation
        exit()
    return new_route

def get_avg_pathlength(G):
    #loop through the people
    peeps_avg = []
    for peeps in people:
        peep_total = 0
        #loop through the waypoints to calc the average
        for origin,dest in peeps.waypoints:
            peep_total += G[truncate_geom(origin)][truncate_geom(dest)]['length']
        peeps_avg.append(peep_total)
    peeps_avg = sum(peeps_avg)/len(peeps_avg)
    return peeps_avg


#define bounding box and canvas width, height calculated from width
TOPLEFT = (418046.80,572753.35)  
BOTTOMRIGHT = (440224.21,556052.84)
WINDOWWIDTH = 900

#failure varaibles
NODE_FAILURE = True
EDGE_FAILURE = False
NODE_TO_REMOVE = 15
EDGE_TO_REMOVE = random.randint(0,265) #radomly select an edge to remove
#can only cope on initial interation
TIME_TO_REMOVE_FEATURE = 0 #with respect to interations at the minute rather than time


#simulation variables
NUMBER_OF_PEOPLE = 1000
HOURS_TO_RUN_FOR = 4

STARTTIME = datetime.datetime(2014,2,2,7) #set start start to 7 this morning
SECONDS_PER_FRAME = 240 #set what the frame interval equals in realtime 

RECORD = False

#create Canvas
canvas = ncl_visualize.Canvas(TOPLEFT,BOTTOMRIGHT ,WINDOWWIDTH)
pygame.init()
#create pygame screen
screen = pygame.display.set_mode(canvas.size)
clock = pygame.time.Clock()
done = False

#stats collecting - only as values currently as only one node removed
count_new_routes = 0
count_start_node_removed = 0
count_end_node_removed = 0
count_no_route_posssible = 0
count_no_route_needed = 0
counts = count_new_routes,count_start_node_removed,count_end_node_removed,count_no_route_posssible,count_no_route_needed 

#Reads in shapefile for river,  and  converts them to screen coordinates
river_polys = []
sf = shapefile.Reader("static_shps/river_buffer.shp")
shapes = sf.shapes()
for shape in shapes:
	river_shape = []
	for p in  shape.points:
		river_shape.append(canvas.RW_to_screen(p))
	river_polys.append(river_shape)
	
#Reads in shapefile for land,  and  converts them to screen coordinates
land_polys = []
sf = shapefile.Reader("static_shps/land.shp")
shapes = sf.shapes()
for shape in shapes:
	land_shape = []
	for p in  shape.points:
		land_shape.append(canvas.RW_to_screen(p))
	land_polys.append(land_shape)
	
#Reads in shapefile for buildings,  and  converts them to screen coordinates
build_polys = []
sf = shapefile.Reader("static_shps/buildings.shp")
shapes = sf.shapes()
for shape in shapes:
	build_shape = []
	for p in  shape.points:
		build_shape.append(canvas.RW_to_screen(p))
	build_polys.append(build_shape)

#THIS BIT IS PROBABLY DONE HORRIBLY
#read in metros
sf = shapefile.Reader("networks/metro_geo_rail.shp")
shapes = sf.shapes()

#create graph
G=nx.Graph()

stations = []
metro_links ={}
metro_graph_edges = []
for shape in shapes:
	metro_line_points = []
	stat1 = shape.points[0]
	stat2 = shape.points[-1]
	#create stations out of edge end points. 
	if stat1 not in stations:
		stations.append(stat1)
	if stat2 not in stations:
		stations.append(stat2)
		
	for i in  range(len(shape.points)-1):
		#this creates the simplifed edges to create the network
		#the correct geometry is then stored in a dictionary so that i can go from simplfied geom to real world geom
		p1 = shape.points[i]
		p2 = shape.points[i+1]
		p1_rounded = truncate_geom(p1)
		p2_rounded = truncate_geom(p2)
		metro_links[p1_rounded,p2_rounded] = (p1,p2 )
		metro_links[p2_rounded,p1_rounded] = (p2,p1 )
		metro_graph_edges.append((p1_rounded,p2_rounded))

#adds all simple edges to graph
G.add_edges_from(metro_graph_edges)

#coarsly add and calc a length for all the edges and add as an attribute
for origin, dest in G.edges():
    e_origin, n_origin = origin
    e_dest, n_dest = dest
    e_diff =  e_origin- e_dest
    n_diff = n_origin - n_dest
    e_diff = e_diff * e_diff
    n_diff = n_diff * n_diff
    diff = math.sqrt(e_diff+n_diff)
    G[origin][dest]['length'] = diff

#create a duplicate list of station with truncated geom
stations_truncated = []
for items in stations:
    stations_truncated.append(truncate_geom(items))

#this creates 1000 random metro users
people = []
for i in range(NUMBER_OF_PEOPLE):
	start,end = False,False
	while start == end:
		#ensure end doesn't equal start
		random.shuffle(stations)
		start = truncate_geom(stations[0])
		end = truncate_geom(stations[1])
	#calculates route
	route = nx.shortest_path(G,source=start, target=end)
	#creates list of waypoints
	waypoints =[]
	for j in range(len(route)-1):
		waypoints.append(metro_links[(route[j],route[j+1])])
	speed = 22.35200 # metro_speed  in ms  = 50mph top speed of metros
	secs = random.randint(0,HOURS_TO_RUN_FOR*3600)
	#creates random starttime
	person_start_time  = STARTTIME + datetime.timedelta(0,secs)
	#adds person to list
	people.append(flow_point(waypoints,speed,person_start_time))

lines_been = {}
stations_been = {}
vis_time = STARTTIME
quit = False
k = 0
while not done and not quit:
    
    if k == TIME_TO_REMOVE_FEATURE:
        #compute the average of the length of the waypoints - in terms of geo length
        peeps_avg = get_avg_pathlength(G)
        print 'Avg path length at begining is:', peeps_avg
        get = metro_graph_edges[EDGE_TO_REMOVE]
        #call either of the removal handlers if required      
        if NODE_FAILURE == True and EDGE_FAILURE == False:
            G, counts = node_removed(G, NODE_TO_REMOVE, counts, speed)
            peeps_avg = get_avg_pathlength(G)
            print 'Avg path length after removal of node:', peeps_avg 
        elif EDGE_FAILURE == True and NODE_FAILURE == False:
            G, counts = edge_removed(G, EDGE_TO_REMOVE, counts, speed)
            peeps_avg = get_avg_pathlength(G)
            print 'Avg path length after removal of edge:', peeps_avg 
        else:
            #this for the case where either might occur - if this is chosen to be implimented
            pass
        
    for event in pygame.event.get(): # User did something
    		if event.type == pygame.QUIT: # If user clicked close
    			quit = True # Flag that we are done so we exit this loop
    screen.fill((0,0,255))
    #draw static objects
    # these have alreasy been converted
    for land_points in land_polys:
    		pygame.draw.polygon(screen,(0,0,0),land_points)
    	
    for river_points in river_polys:
    		pygame.draw.polygon(screen,(0,0,255),river_points)
    		
    for build_points in build_polys:
    		pygame.draw.polygon(screen,(92,92,92),build_points)
    
    #draws metro lines their thickness is changed lateron
    for key,weight in lines_been.iteritems():
    		pygame.draw.line(screen,(255,0,0),canvas.RW_to_screen(key[0]),canvas.RW_to_screen(key[1]),int(math.floor(weight)))
    		
    #draws metro stations that people have been through their size is changed lateron
    for station,weight in stations_been.iteritems():
    		pygame.draw.circle(screen,  (0,255,0), canvas.RW_to_screen(station), int(math.floor(weight)))
    
    done = True
    for peep in people:
         if not(peep.finished):
             done = False # if people are still moving don't finish
             if vis_time > peep.start_time:
                 lines = peep.move(SECONDS_PER_FRAME)#move people 
                 if lines: #if they're travelled a complete segment 
                     for line in lines:#for each segment they completed in this move
						if line[1] in stations:#have they been through a station
							stations_been[line[1]] = stations_been.get(line[1],2)
							stations_been[line[1]] += 0.05 #increase the size size are rounded down to the nearest int so it takes 20 visits to increse the size displayed
						n_line = (min(line[0],line[1]),max(line[0],line[1]))
						lines_been[n_line] = lines_been.get(n_line,1)
						lines_been[n_line] +=0.05 #increase the size size are rounded down to the nearest int so it takes 20 visits to increse the size displayed
                 pygame.draw.circle(screen,  (255,255,255), canvas.RW_to_screen(peep.loc), 2)#draw circles at peoples locations         
    
    #setup font
    myfont = pygame.font.SysFont("arial", 25)
    myfont.set_bold(True)
    #display time in bottom left
    label = myfont.render(str(vis_time.time()), 1, (255,0,0))
    screen.blit(label, (10, canvas.height-30))		
    
    if RECORD:
            pygame.image.save(screen, "frames/frame_%s.jpeg" %(str(frame),))
    
    #increase time by frame rate
    vis_time += datetime.timedelta(0,SECONDS_PER_FRAME)
    pygame.display.flip()
    clock.tick(20)#this try to draw 20 frames a second
    k += 1

count_new_routes,count_start_node_removed,count_end_node_removed,count_no_route_posssible,count_no_route_needed = counts			
print "number of people re-routed:", count_new_routes
if NODE_FAILURE == True:
    print "number of people who's start node was removed:", count_start_node_removed
    print "number of people who's destination node was removed:", count_end_node_removed
    print "number of people who's start/dest ended up being the same:", count_no_route_needed
print "number of routes not possible:", count_no_route_posssible
print "from", str(NUMBER_OF_PEOPLE), "people who should have traveled,", str(len(people)), "did so"

#this is purely to check it is still working correctly
if NODE_FAILURE == True:
    print "number of times removed station was visited:", stations_been.get(stations[NODE_TO_REMOVE])
if EDGE_FAILURE == True:
    print "number of times removed edge was traversed:", lines_been.get(metro_graph_edges[EDGE_TO_REMOVE])

# Be IDLE friendly. If you forget this line, the program will 'hang'
# on exit.
pygame.quit ()