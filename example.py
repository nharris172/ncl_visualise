import ncl_visualize
import ncl_network_sim
import datetime 
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





#define bounding box and canvas width, height calculated from width
TOPLEFT = (418046.80,572753.35)  
BOTTOMRIGHT = (440224.21,556052.84)
WINDOWWIDTH = 900

canvas = ncl_visualize.Canvas(TOPLEFT,BOTTOMRIGHT ,WINDOWWIDTH)
canvas.set_background_color((0,0,255))



metro_network = ncl_network_sim.build_network("networks/metro_geo_rail.shp")
stations = metro_network.nodes
metro_lines = metro_network.edges


STARTTIME = datetime.datetime(2014,2,2,7) #set start start to 7 this morning
SECONDS_PER_FRAME = 30 #set what the frame interval equals in realtime 

#simulation variables
NUMBER_OF_PEOPLE = 3000
HOURS_TO_RUN_FOR = 2



RECORD = False


#Reads in shapefile for land,  and  converts them to screen coordinates
canvas.LoadStatic.Polygon("static_shps/land.shp",color=(0,0,0))

#Reads in shapefile for river,  and  converts them to screen coordinates
canvas.LoadStatic.Polygon("static_shps/river_buffer.shp",color=(0,0,255))
       
#Reads in shapefile for buildings,  and  converts them to screen coordinates
canvas.LoadStatic.Polygon("static_shps/buildings.shp",color=(92,92,92))


#this creates 1000 random metro users
people = []
for i in range(NUMBER_OF_PEOPLE):
    start,end = False,False
    while start == end:
        #ensure end doesn't equal start
        random.shuffle(stations)
        start = stations[0]
        end = stations[1]
        secs = random.randint(0,HOURS_TO_RUN_FOR*3600)
        speed = 22.35200 # metro_speed  in ms  = 50mph top speed of metros
        person_start_time  = STARTTIME + datetime.timedelta(0,secs)
        metro_network.add_flow_point(start,end,person_start_time,speed)

#failure varaibles


EDGE_FAILURE_TIME = [
datetime.datetime(2014,2,2,7,11),
datetime.datetime(2014,2,2,7,13),
datetime.datetime(2014,2,2,8),
datetime.datetime(2014,2,2,8,15)
]

random.shuffle(metro_lines)

for i,time in enumerate(EDGE_FAILURE_TIME):
    line_to_fail = metro_lines[i]
    metro_network.Failures.add_edge_fail(line_to_fail,time)


NODE_FAILURE_TIME = [
datetime.datetime(2014,2,2,7,10),
datetime.datetime(2014,2,2,7,20),
datetime.datetime(2014,2,2,7,35),
]
  
for i,time in enumerate(NODE_FAILURE_TIME):
    node_to_fail = stations[i]
    metro_network.Failures.add_node_fail(node_to_fail,time)  

metro_network.time_config(STARTTIME,SECONDS_PER_FRAME)
quit = False
done = False
k = 0
removed_edges = []
removed_nodes = []
while not done and not quit:
    
    failure = metro_network.Failures.check_fails()
    if failure:
        if failure.edge:
            for i in range(1,50):
                #Terprint failure.statsrible failure animation
                canvas.draw_line(failure.geom,(255,255,0),i)
                canvas.tick()
            removed_edges.append(failure.geom)
        if failure.node:
            for i in range(1,20):
                #Terprint failure.statsrible failure animation
                canvas.draw_point(failure.geom,(255,255,0),i)
                canvas.tick()
            removed_nodes.append(failure.geom)
            
        print '----------------------------'
        failure.print_stats()
    quit = canvas.check_quit()
                
    #draw static objects
    canvas.draw_static()

    done = metro_network.tick()
    
    for line,weight in metro_network.edge_capacity.iteritems():
        color = (255,0,0)
        weight = max(1,int(math.floor(weight/20)))
        canvas.draw_line(line,color,weight)
    
    for line in removed_edges:
        canvas.draw_line(line,(255,255,0),3)
    
    #draws metro stations that people have been through their size is changed lateron
    for station,weight in metro_network.node_capacity.iteritems():
        weight = max(2,int(math.floor(weight/20)))
        color = (0,255,0)
        canvas.draw_point(station,color,weight)
        
    for node in removed_nodes:
        canvas.draw_point(node,(255,255,0),5)
    
    for fp in metro_network.flow_points:
        if fp.started and not fp.finished:
            canvas.draw_point(fp.loc,(255,255,255),2)         
            
    canvas.annotate(metro_network.time.time(),'BOTTOM_LEFT')      
    
    if RECORD:
        pygame.image.save(screen, "frames/frame_%s.jpeg" %(str(frame),))
    
    #increase time by frame rate
    canvas.tick()


# Be IDLE friendly. If you forget this line, the program will 'hang'
# on exit.
canvas.finish()
