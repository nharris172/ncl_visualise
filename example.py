import ncl_visualize
import ncl_network_sim
import datetime
import random
from ncl_network_sim import tools
import os 
"""
To do/ideas:
-Need to look at adding edge failure visualisation to the geo failure method
-In dense networks, changing colours of edges might be better than line 
thickness.
-For geo failure, produce stats on the accumulative effect rather/as well as
for the individual failures.

"""

def run_sim():
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
    path =  os.path.dirname(os.path.realpath(__file__))
    if net_source_shpfile == True:
        
        #print os.path.join(path,"networks","%s.shp" % shpfile_name) == '/home/neil/git_rep/ncl_visualise/networks/metro_geo_rail.shp'
        built_network = ncl_network_sim.build_network(os.path.join(path,"networks","%s.shp" % shpfile_name) , speed_att=speed_att, default_speed=default_speed, length_att=length_att)
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
    canvas.LoadStatic.Polygon(os.path.join(path,"static_shps","land.shp"),color=(0,0,0))
    #canvas.LoadStatic.Polygon("static_shps/leeds_background.shp",color=(0,0,0))
    #canvas.LoadStatic.Polygon("static_shps/greatbritain",color=(0,0,0))
    #canvas.LoadStatic.Polygon("static_shps/london_background.shp",color=(0,0,0))
    
    #Reads in shapefile for river, and converts them to screen coordinates
    canvas.LoadStatic.Polygon(os.path.join(path,"static_shps","river_buffer.shp"),color=(0,0,255))
    #canvas.LoadStatic.Polygon("static_shps/leeds_river_buffer.shp",color=(0,0,255))
    #canvas.LoadStatic.Polygon("static_shps/london_rivers.shp",color=(0,0,255)) 
    
    #Reads in shapefile for buildings, and converts them to screen coordinates
    #canvas.LoadStatic.Polygon("static_shps/buildings.shp",color=(92,92,92))
    canvas.LoadStatic.Polygon(os.path.join(path,"static_shps","buildings.shp"),color=(92,92,92))
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
    NUMBER_OF_FLOWS = 1000
    HOURS_TO_RUN_FOR = 0.5 #time which start times are spread over
    WEIGHT = 'time'
    FLOW_COUNT_TIME = [0,10]#HOURS,MINUTES
    
    #outputs
    PRINT_STATS = False
    RECORD = False
    #FILE_PATH = "C:\\Users\\Craig\\network_vis_tool\\vis_sim\\temp_%s-%s-%s.jpg"
    FILE_PATH = "C:\\Users\\Craig\\network_vis_tool\\vis_sim - TW\\temp%s.jpg"
    if RECORD == True: META_FILE = open("C:\\Users\\Craig\\network_vis_tool\\vis_sim - TW\\metadata.txt","w")
    
    #------------------------------------------------------------------------------
    
    #this creates the random people
    routes_not_pos = 0
    for i in range(NUMBER_OF_FLOWS):
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
                         NUMBER_OF_FLOWS,routes_not_pos,HOURS_TO_RUN_FOR,WEIGHT,FLOW_COUNT_TIME)
    
    #------------------------------------------------------------------------------
    #Variables to tailor failure analysis
    MANUAL = False #define times and failure methods (set as True)
    RANDOM_TIME = True #if failure times to be randomly generated (set as True)
    TIME_INTERVALS = None #set an interval(mins) between failures.
    NUMBER_OF_FAILURES = 5 #the number of failures which are to occur.
    
    RANDOM_F = False
    TARGETED = True #if selecting nodes by their flow value - will also add degree - may be able to get rid of this
    FLOW = True #removes the node which the greatest number of flows have passed through in the last 10mins for example
    DEGREE = False #does not yet work
    NODE_EDGE_RANDOM = 'NODE_EDGE' #should be NODE, EDGE or NODE_EDGE
   
    #geo failure
    GEO_FAILURE = False
    SHP_FILE = "C:\\Users\\Craig\\GitRepo\\ncl_visualise\\static_shps\\PiP\\polygon_coastal_flood_eg.shp"
 
    #junction re-assignment - only checks the closest as an alternative
    REASSIGN_START = True
    REASSIGN_DEST = True
       
    #------------------------------------------------------------------------------
    
    
    random.shuffle(net_edges)
    EDGE_FAILURE_TIME=None;NODE_FAILURE_TIME=None;FAILURE_TIMES=None
    
    if MANUAL == False:
        if TARGETED == False: #random time(s), random component selection
            RANDOM_F = True
            RANDOM_FAILURE_TIMES = tools.generate_failure_times(RANDOM_TIME,
                        TIME_INTERVALS,NUMBER_OF_FAILURES,STARTTIME,HOURS_TO_RUN_FOR,built_network)
        elif TARGETED == True: #random time(s), targeted component selection
            TARGETED_FAILURE_TIMES = tools.generate_failure_times(RANDOM_TIME,
                        TIME_INTERVALS,NUMBER_OF_FAILURES,STARTTIME,HOURS_TO_RUN_FOR,built_network)  
        
    elif MANUAL == True:
        EDGE_FAILURE_TIME=None;NODE_FAILURE_TIME=None;TARGETED_FAILURE_TIMES=None;RANDOM_FAILURE_TIMES=None
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
            TARGETED_FAILURE_TIMES = [
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
    GEO_F_TIME = []
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
    
    #need to make a copy of junctions so do not try and remove the same node twice
    failure_junctions = [] 
    for junc in junctions: failure_junctions.append(junc)
    failure_edges = []
    for edge in net_edges: failure_edges.append(edge)
    
    while not done and not quit:
        
        #check if any tageted failures are scheduled
        if TARGETED == True:
            failure_junctions = tools.get_targted_comp(NODE_EDGE_RANDOM, TARGETED_FAILURE_TIMES,
                                   FLOW_COUNT_TIME,built_network, failure_junctions,
                                   FLOW,DEGREE)
        #check if any random failures are scheduled
        elif RANDOM_F == True:
            failure_junctions, failure_edges = tools.get_random_comp(NODE_EDGE_RANDOM, RANDOM_FAILURE_TIMES,
                                   built_network, failure_junctions, failure_edges)
        #check if a geo failure is scheduled
        if GEO_FAILURE == True:
            failure_junctions, failure_edges = tools.geo_failure_comp(NODE_EDGE_RANDOM, FAILURE_TIMES, FLOW_COUNT_TIME,
                                   built_network, failure_junctions, failure_edges, SHP_FILE, GEO_F_TIME)
            #failure_edges = []
            #for edge in built_network.edges:failure_edges.append(edge)
                
        #load polygon onto map for visualisation
        for ftime in GEO_F_TIME:
            if ftime == built_network.time:
                canvas.LoadStatic.Polygon(SHP_FILE,color=(0,0,255))
     
        #check if any failures are due and reroute flows
        fails = built_network.Failures.check_fails(REASSIGN_START,REASSIGN_DEST,WEIGHT)
        
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
                if PRINT_STATS: failure.print_stats()
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
