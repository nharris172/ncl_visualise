import ncl_visualize
import ncl_network_sim
import datetime 
import random
from ncl_network_sim import tools

"""
Current issues:
Major:
-Neils hardcoded the use of the speed attribute for the visualisation. Need to 
look at turning this into a variable.
-Neils alterations mean speed is used for the visualisation only, not for the 
routing(ie. time to traverse an edge) for the creation if the flowpoint.


Other:

To do/ideas:
-Do we want to check for a pre-exisitng length field?
-In dense networks, changing colours of edges might be better than line thickness

"""

net_source_shpfile = True

#attribute name in shapefile/datatable - set as None if they are not in the shapefile
length_att = 'length' #None #default value
speed_att = None #'speed' #None #default value
default_speed = 22

if net_source_shpfile == True:
    #built_network = ncl_network_sim.build_network("networks/tw_m_a_b_w_speeds_TEMPfixONLY.shp", speed_att = 'speed', default_speed=20.0)
    #built_network = ncl_network_sim.build_network("networks/tyne_wear_motorways_a_roads_v2.shp", default_speed=30, length_att=length_att)
    built_network = ncl_network_sim.build_network("networks/metro_geo_rail.shp", speed_att=speed_att, default_speed=default_speed, length_att=length_att)
    #built_network = ncl_network_sim.build_network("networks/metro_geo_rail_w_shortcuts.shp", speed_att=speed_att, length_att=length_att)
elif net_source_shpfile == False:
    host = 'localhost'; user = 'postgres'; port = '5433'
    password = 'aaSD2011'
    dbname = 'lightrail'
    #net_name = 'tyne_wear_metro'
    net_name = 'tyne_wear_metro_geo_w_shortcuts'
    conn = "PG: host='%s' dbname='%s' user='%s' password='%s' port='%s'" % (host, dbname, user, password, port)
    built_network = ncl_network_sim.build_net_from_db(conn, net_name,speed_att=speed_att,default_speed=default_speed, length_att=length_att)


junctions = built_network.nodes
net_edges = built_network.edges

#define bounding box and canvas width, height calculated from width
LEFT,BOTTOM, RIGHT,TOP = built_network.bbox
buffer_width = (RIGHT-LEFT)/20
buffer_height = (TOP-BOTTOM)/20
WINDOWWIDTH = 800
canvas = ncl_visualize.Canvas((LEFT-buffer_width,TOP+buffer_height),(RIGHT+buffer_width,BOTTOM-buffer_height) ,WINDOWWIDTH)
canvas.set_background_color((0,0,255))

#Reads in shapefile for land, and converts them to screen coordinates
#canvas.LoadStatic.Polygon("static_shps/land.shp",color=(0,0,0))
canvas.LoadStatic.Polygon("static_shps/land_tw2.shp",color=(0,0,0))

#Reads in shapefile for river, and converts them to screen coordinates
canvas.LoadStatic.Polygon("static_shps/river_buffer.shp",color=(0,0,255))
       
#Reads in shapefile for buildings, and converts them to screen coordinates
canvas.LoadStatic.Polygon("static_shps/buildings.shp",color=(92,92,92))
#canvas.LoadStatic.Polygon("static_shps/buildings_tw2.shp",color=(92,92,92))
#canvas.LoadStatic.Polygon("static_shps/tw_urban_areas.shp",color=(92,92,92))

#year, month, day, hour
STARTTIME = datetime.datetime(2014,2,2,7,00) #set start start to 7 this morning
SECONDS_PER_FRAME = 30 #set what the frame interval equals in realtime 

#simulation variables
NUMBER_OF_PEOPLE = 1000
HOURS_TO_RUN_FOR = 1 #time which start times are spread over

FLOW_COUNT_TIME = [0,10]#HOURS,MINUTES

RECORD = False

#this creates the random people
people = []
routes_not_pos = 0
for i in range(NUMBER_OF_PEOPLE):
    #ensure end doesn't equal start
    random.shuffle(junctions)
    start = junctions[0]
    end = junctions[1]
    secs = random.randint(0,HOURS_TO_RUN_FOR*3600)
    person_start_time  = STARTTIME + datetime.timedelta(0,secs)
    done = built_network.add_flow_point(start,end,person_start_time)
    if done == False:
        routes_not_pos += 1

print "number of people who's route is not possible:", routes_not_pos 

#Variables to tailor failure analysis
MANUAL = True #define times our have them generated
RANDOM_TIME = False #if want to create times at random
TIME_INTERVALS = None #set an interval(mins) between failures.
NUMBER_OF_FAILURES = 1 #the number of failures which are to occur. 

TARGETED = True #if selecting nodes by their flow value - will also add degree - may be able to get rid of this
NODE_EDGE_RANDOM = 'EDGE' #should be NODE,EDGE or NODE_EDGE
FLOW = True #removes the node which the greatest number of flows have passed through in the last 10mins for example
DEGREE = False #does not yet work

random.shuffle(net_edges)

if MANUAL == False:
    if TARGETED == False: #random time(s), random component selection
        tools.random_failures(TIME_INTERVALS,NUMBER_OF_FAILURES,STARTTIME,NODE_EDGE_RANDOM,built_network,junctions,net_edges)
    elif TARGETED == True: #random time(s), targeted removal
         FAILURE_TIMES = tools.targeted_times(RANDOM_TIME,TIME_INTERVALS,NUMBER_OF_FAILURES,STARTTIME,built_network)
            
elif MANUAL == True:
    if TARGETED == False:
        #manual time setting, random component selection
        #year, month, day, hour, minut
        EDGE_FAILURE_TIME = [
        datetime.datetime(2014,2,2,7,45)
        ]        
        NODE_FAILURE_TIME = [
        datetime.datetime(2014,2,2,7,40),
        ]
        
        tools.manual_random_edges(EDGE_FAILURE_TIME,net_edges,built_network)
        tools.manual_random_edges(NODE_FAILURE_TIME,junctions,built_network)
         
    elif TARGETED == True:
        FAILURE_TIMES = [
        datetime.datetime(2014,2,2,7,30)
        ]

built_network.time_config(STARTTIME,SECONDS_PER_FRAME)
quit = False
done = False
k = 0
canvas.start_screen()

while not done and not quit:   
    
    #check if any tageted failures are due and create full instance if so
    if TARGETED == True:
        tools.get_targted_comp(NODE_EDGE_RANDOM, FAILURE_TIMES,FLOW_COUNT_TIME,built_network,FLOW,DEGREE)
    
    #check if any failures are due
    failure = built_network.Failures.check_fails()
    
    #if there is a failure
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
                
        #print stats following the failure
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
        num_flows = edge.get_flows(hours=FLOW_COUNT_TIME[0],mins=FLOW_COUNT_TIME[1])
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
            
            num_flows = node.get_flows(hours=FLOW_COUNT_TIME[0],mins=FLOW_COUNT_TIME[1])
            
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
    if RECORD:
        canvas.record("C:\\Users\\Craig\\vis_temp\\temp_%s-%s-%s.jpg", built_network.time.time())
       
# Be IDLE friendly. If you forget this line, the program will 'hang'
# on exit.
canvas.finish()