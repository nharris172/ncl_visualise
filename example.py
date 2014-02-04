import pygame
import ncl_visualize
import datetime 
import shapefile
import networkx as nx
import random
import math
import datetime

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



#define bounding box and canvas width, height calculated from width
TOPLEFT=(418046.80,572753.35)
BOTTOMRIGHT =(440224.21,556052.84)
WINDOWWIDTH=900

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

#this creates 1000 random metro users
people = []
for i in range(1000):
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
	secs = random.randint(0,57600)
	#creates random starttime
	person_start_time  = STARTTIME + datetime.timedelta(0,secs)
	#adds person to list
	people.append(flow_point(waypoints,speed,person_start_time))


lines_been = {}
stations_been = {}
vis_time = STARTTIME
quit = False
while not done and not quit:
	
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
		if not(peep.finished) :
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
			
# Be IDLE friendly. If you forget this line, the program will 'hang'
# on exit.
pygame.quit ()