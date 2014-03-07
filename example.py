import ncl_visualize
import ncl_network_sim
import datetime 
import random
import math
import matplotlib.pyplot as plt

"""
Current issues:
Major:

Other:

To do/ideas:
-In dense networks, changing colours of edges might be better than line thickness

"""


#define bounding box and canvas width, height calculated from width


#built_network = ncl_network_sim.build_network("networks/tyne_wear_motorways_a_b_roads_v3.shp")
#built_network = ncl_network_sim.build_network("networks/tyne_wear_motorways_a_roads_v2.shp")
built_network = ncl_network_sim.build_network("networks/metro_geo_rail.shp")
junctions = built_network.nodes #previusoly stations
net_edges = built_network.edges

LEFT,BOTTOM, RIGHT,TOP = built_network.bbox
buffer_width = (RIGHT-LEFT)/20
buffer_height = (TOP-BOTTOM)/20
WINDOWWIDTH = 800
canvas = ncl_visualize.Canvas((LEFT-buffer_width,TOP+buffer_height),(RIGHT+buffer_width,BOTTOM-buffer_height) ,WINDOWWIDTH)
canvas.set_background_color((0,0,255))

#Reads in shapefile for land, and converts them to screen coordinates
canvas.LoadStatic.Polygon("static_shps/land.shp",color=(0,0,0))

#Reads in shapefile for river, and converts them to screen coordinates
canvas.LoadStatic.Polygon("static_shps/river_buffer.shp",color=(0,0,255))
       
#Reads in shapefile for buildings, and converts them to screen coordinates
canvas.LoadStatic.Polygon("static_shps/buildings.shp",color=(92,92,92))


#year, month, day, hour
STARTTIME = datetime.datetime(2014,2,2,7,30) #set start start to 7 this morning
SECONDS_PER_FRAME = 30 #set what the frame interval equals in realtime 

#simulation variables
NUMBER_OF_PEOPLE = 1000
HOURS_TO_RUN_FOR = 1

SPEED = 22.35200 # metro_speed  in ms  = 50mph top speed of metros


RECORD = False




#this creates the random people
people = []
for i in range(NUMBER_OF_PEOPLE):
    #ensure end doesn't equal start
    random.shuffle(junctions)
    start = junctions[0]
    end = junctions[1]
    secs = random.randint(0,HOURS_TO_RUN_FOR*3600)
    person_start_time  = STARTTIME + datetime.timedelta(0,secs)
    built_network.add_flow_point(start,end,person_start_time,SPEED)

#year, month, day, hour, minute
EDGE_FAILURE_TIME = [
datetime.datetime(2014,2,2,8,15)
]

random.shuffle(net_edges)

for i,time in enumerate(EDGE_FAILURE_TIME):
    line_to_fail = net_edges[i]
    built_network.Failures.add_edge_fail(line_to_fail,time)

#year, month, day, hour, minute
NODE_FAILURE_TIME = [
datetime.datetime(2014,2,2,8,00),
]

for i,time in enumerate(NODE_FAILURE_TIME):
    node_to_fail = junctions[i]
    built_network.Failures.add_node_fail(node_to_fail,time) 

built_network.time_config(STARTTIME,SECONDS_PER_FRAME)
quit = False
done = False
k = 0
canvas.start_screen()
while not done and not quit:
    
    failure = built_network.Failures.check_fails()
    if failure:
        if failure.edge:
            for i in range(1,50):
                #Terprint failure.statsrible failure animation
                canvas.draw_line(failure.edge.geom,(255,100,0),i)
                canvas.tick()
        if failure.node:
            for i in range(1,20):
                #Terprint failure.statsrible failure animation
                canvas.draw_point(failure.node.geom,(255,0,0),i)
                canvas.tick()
            
        print '----------------------------'
        failure.print_stats()

    quit = canvas.check_quit()
                
    #draw static objects
    canvas.fill_screen()
    canvas.draw_static()

    done = built_network.tick()
    #draws the edges
    for edge in built_network.edges:
        #get flows from last 10 minutes
        num_flows = edge.get_flows(hours=0,mins=10)
        if not edge.failed:
            color = (124,255,91)
            if num_flows:
                weight = int(max(1,num_flows/5))
                canvas.draw_line(edge.geom,color,weight)
        else:
            color = (255,100,0)
            canvas.draw_line(edge.geom,color,2)

    
    #draws network junctions that people have been through their size is changed lateron
    for node in built_network.nodes:
        if not node.failed:
            color = (0,153,0)
            
            num_flows = node.get_flows(hours=0,mins=10)
            if num_flows:
                weight = int(max(2,num_flows/5))
                canvas.draw_point(node.geom,color,weight)
        else:
            color = (255,0,0)
            canvas.draw_point(node.geom,color,4)
    #draws each flow point at its location if it has started and not finished
    for fp in built_network.flow_points:
        if fp.started and not fp.finished:
            canvas.draw_point(fp.loc,(255,255,255),2)         
    canvas.annotate(built_network.time.time(),'BOTTOM_LEFT')

    #increase time by frame rate
    canvas.tick()

# Be IDLE friendly. If you forget this line, the program will 'hang'
# on exit.
canvas.finish()




