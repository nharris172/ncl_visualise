import ncl_visualize
import ncl_network_sim
import datetime 
import random
from ncl_network_sim import tools

"""
Current issues:
Major:
-WEIGHT varaible used for the inital creation of the flow points, though not 
when they fail at the moment (uses a default which is set as time). Needs to be
sorted so is varaible, i.e. can be set to cost for example.
-Would be good to be able to add the flow/degree value for a node/edge removed 
in a targeted failure.

Other:

To do/ideas:
-Do we want to check for a pre-exisitng length field?
-In dense networks, changing colours of edges might be better than line 
thickness.

"""

net_source_shpfile = True

#attribute name in shapefile/datatable - set as None if they are not in the shapefile
length_att = 'length' #None
speed_att = 'speed' #None #speed should be in meters per second, otherwise results may be miss-representative
default_speed = 42

#shpfile_name = "tw_m_a_b_w_speeds_TEMPfixONLY"
shpfile_name = "metro_geo_rail"
#shpfile_name = "leeds_m_a_b_w_travel_time"
#shpfile_name = "uk_internal_routes"
#shpfile_name = "london_dlr_lines"

if net_source_shpfile == True:
    built_network = ncl_network_sim.build_network("networks/%s.shp" %(shpfile_name), speed_att=speed_att, default_speed=default_speed, length_att=length_att)
elif net_source_shpfile == False:
    host = 'localhost'; user = 'postgres'; port = '5433'
    password = 'aaSD2011'
    dbname = 'lightrail'
    #net_name = 'tyne_wear_metro'
    net_name = 'tyne_wear_metro_geo_w_shortcuts'
    conn = "PG: host='%s' dbname='%s' user='%s' password='%s' port='%s'" % (host, dbname, user, password, port)
    built_network = ncl_network_sim.build_net_from_db(conn, net_name,speed_att=speed_att,default_speed=default_speed, length_att=length_att)

#------------------------------------------------------------------------------
junctions = built_network.nodes
net_edges = built_network.edges

#define bounding box and canvas width, height calculated from width
LEFT,BOTTOM, RIGHT,TOP = built_network.bbox
buffer_width = (RIGHT-LEFT)/20
buffer_height = (TOP-BOTTOM)/20
WINDOWWIDTH = 800
canvas = ncl_visualize.Canvas((LEFT-buffer_width,TOP+buffer_height),(RIGHT+buffer_width,BOTTOM-buffer_height) ,WINDOWWIDTH)
canvas.set_background_color((0,0,255))

#------------------------------------------------------------------------------
#Reads in shapefile for land, and converts them to screen coordinates
#canvas.LoadStatic.Polygon("static_shps/land.shp",color=(0,0,0))
canvas.LoadStatic.Polygon("static_shps/land_tw2.shp",color=(0,0,0))
#canvas.LoadStatic.Polygon("static_shps/leeds_background.shp",color=(0,0,0))
#canvas.LoadStatic.Polygon("static_shps/greatbritain",color=(0,0,0))
#canvas.LoadStatic.Polygon("static_shps/london_background.shp",color=(0,0,0))

#Reads in shapefile for river, and converts them to screen coordinates
canvas.LoadStatic.Polygon("static_shps/river_buffer.shp",color=(0,0,255))
#canvas.LoadStatic.Polygon("static_shps/leeds_river_buffer.shp",color=(0,0,255))
#canvas.LoadStatic.Polygon("static_shps/london_rivers.shp",color=(0,0,255)) 

#Reads in shapefile for buildings, and converts them to screen coordinates
#canvas.LoadStatic.Polygon("static_shps/buildings.shp",color=(92,92,92))
canvas.LoadStatic.Polygon("static_shps/TyneWear_roads_buildings.shp",color=(92,92,92))
#canvas.LoadStatic.Polygon("static_shps/tw_urban_areas.shp",color=(92,92,92))
#canvas.LoadStatic.Polygon("static_shps/Leeds_roads_buildings.shp",color=(92,92,92))
#canvas.LoadStatic.Polygon("static_shps/greatbritain",color=(92,92,92))
#canvas.LoadStatic.Polygon("static_shps/london_dlr_buildings.shp",color=(92,92,92))

#SHP_FILE = "C:\\Users\\Craig\\Dropbox\\polygon_multiple_failures_testing.shp"
#canvas.LoadStatic.Polygon(SHP_FILE,color=(92,92,92))

#------------------------------------------------------------------------------
#year, month, day, hour
STARTTIME = datetime.datetime(2014,2,2,7,00) #set start start to 7 this morning
SECONDS_PER_FRAME = 30 #set what the frame interval equals in realtime 

#simulation variables
NUMBER_OF_PEOPLE = 1000
HOURS_TO_RUN_FOR = 1 #time which start times are spread over
WEIGHT = 'time'
FLOW_COUNT_TIME = [0,10]#HOURS,MINUTES

RECORD = False
#FILE_PATH = "C:\\Users\\Craig\\network_vis_tool\\vis_sim\\temp_%s-%s-%s.jpg"
FILE_PATH = "C:\\Users\\Craig\\network_vis_tool\\vis_sim - TW\\temp%s.jpg"
if RECORD == True: META_FILE = open("C:\\Users\\Craig\\network_vis_tool\\vis_sim - TW\\metadata.txt","w")

#------------------------------------------------------------------------------

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
    done = built_network.add_flow_point(start,end,person_start_time,WEIGHT)
    if done == False:
        routes_not_pos += 1

print "number of people who's route is not possible:", routes_not_pos 
if RECORD: tools.write_metadata(META_FILE,net_source_shpfile,shpfile_name,length_att,
                     speed_att,default_speed,STARTTIME,SECONDS_PER_FRAME,
                     NUMBER_OF_PEOPLE,routes_not_pos,HOURS_TO_RUN_FOR,WEIGHT,FLOW_COUNT_TIME)

#------------------------------------------------------------------------------
#Variables to tailor failure analysis
MANUAL = True #define times our have them generated
RANDOM_TIME = True #if want to create times at random
TIME_INTERVALS = None #set an interval(mins) between failures.
NUMBER_OF_FAILURES = 10 #the number of failures which are to occur. 

TARGETED = True #if selecting nodes by their flow value - will also add degree - may be able to get rid of this
FLOW = True #removes the node which the greatest number of flows have passed through in the last 10mins for example
DEGREE = False #does not yet work
NODE_EDGE_RANDOM = 'NODE' #should be NODE,EDGE or NODE_EDGE

GEO_FAILURE = True
SHP_FILE = "C:\\Users\\Craig\\Dropbox\\vis_tool_data\\PiP\\polygon_multiple_failures_testing.shp"
'''
if GEO_FAILURE:
    canvas.LoadStatic.Polygon("C:\\Users\\Craig\\Dropbox\\vis_tool_data\\PiP\\polygon_multiple_failures_testing.shp",color=(0,0,255))
'''
#------------------------------------------------------------------------------


random.shuffle(net_edges)
EDGE_FAILURE_TIME=None;NODE_FAILURE_TIME=None;FAILURE_TIMES=None

if MANUAL == False:
    if TARGETED == False: #random time(s), random component selection
        tools.random_failures(TIME_INTERVALS,NUMBER_OF_FAILURES,STARTTIME,NODE_EDGE_RANDOM,built_network,junctions,net_edges)
    elif TARGETED == True: #random time(s), targeted removal
         FAILURE_TIMES = tools.targeted_times(RANDOM_TIME,TIME_INTERVALS,NUMBER_OF_FAILURES,STARTTIME,built_network)
    
    
elif MANUAL == True:
    EDGE_FAILURE_TIME=None;NODE_FAILURE_TIME=None;FAILURE_TIMES=None
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
        #datetime.datetime(2014,2,2,7,5),
        #datetime.datetime(2014,2,2,7,11),
        #datetime.datetime(2014,2,2,7,14),
        #datetime.datetime(2014,2,2,7,32),
        #datetime.datetime(2014,2,2,7,33),
        #datetime.datetime(2014,2,2,7,43),
        #datetime.datetime(2014,2,2,7,49),
        #datetime.datetime(2014,2,2,7,53),
        #datetime.datetime(2014,2,2,7,28),
        #datetime.datetime(2014,2,2,7,15),
        ]
    
if GEO_FAILURE == True:
    GEO_F_TIME = [
    datetime.datetime(2014,2,2,7,04)  
    ]
    
if RECORD: tools.write_failure_data(META_FILE,MANUAL,RANDOM_TIME,TIME_INTERVALS,NUMBER_OF_FAILURES,TARGETED,
                             NODE_EDGE_RANDOM,FLOW,DEGREE,FAILURE_TIMES,EDGE_FAILURE_TIME,NODE_FAILURE_TIME)

#------------------------------------------------------------------------------
built_network.time_config(STARTTIME,SECONDS_PER_FRAME)
quit = False
done = False
k = 0
canvas.start_screen()

while not done and not quit:
    
    #check if any tageted failures are due and create full instance if so
    if TARGETED == True:
        tools.get_targted_comp(NODE_EDGE_RANDOM, FAILURE_TIMES,FLOW_COUNT_TIME,built_network,FLOW,DEGREE)

    #check for geo failure
    if GEO_FAILURE == True:
        tools.geo_failure_comp(NODE_EDGE_RANDOM, FAILURE_TIMES,FLOW_COUNT_TIME,built_network,FLOW,DEGREE,SHP_FILE,GEO_F_TIME)
    
    for ftime in GEO_F_TIME:
        if ftime == built_network.time:
            canvas.LoadStatic.Polygon("C:\\Users\\Craig\\Dropbox\\vis_tool_data\\PiP\\polygon_multiple_failures_testing.shp",color=(0,0,255))
 
    #check if any failures are due and reroute flows
    fails = built_network.Failures.check_fails()
    
    #if there is a failure
    for failure in fails:
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
            if RECORD: failure.write_stats(META_FILE)

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
        canvas.record(FILE_PATH, built_network.time.time(),k)

    k+=1
if RECORD: META_FILE.close()
# Be IDLE friendly. If you forget this line, the program will 'hang'
# on exit.
canvas.finish()