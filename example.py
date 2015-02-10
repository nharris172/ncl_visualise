import ncl_visualize
import ncl_network_sim
import datetime
import random
from ncl_network_sim import tools
import os 

def run_sim():
    
    
    #-------------------------------------------------------------------------#
    #network based variables
    
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
    db_parameters = {'dbname':'lightrail',
                     'net_name':'tyne_wear_metro_geo_w_shortcuts',
                     'host':'localhost','user':'postgres','port':'5433','password':'aaSD2011'}
                     
    #------------------------------------------------------------------------------
    #visualisation varaibles
    
    #year, month, day, hour
    STARTTIME = datetime.datetime(2014,2,2,7,00) #set start start to 7 this morning
    SECONDS_PER_FRAME = 30 #set what the frame interval equals in realtime
    
    #factors at which the nodes/edges are scaled at based on their flow value
    NODE_SCALE_FACTOR = 2
    EDGE_SCALE_FACTOR = 5

    #sizes generic
    FLOW_SIZE = 2 #active flow size
    FAILED_NODE_SIZE = 4 #size of failed nodes
    FAILED_EDGE_SIZE = 2 #width of failed edges
    MIN_NODE_SIZE = 2 #minimum size of active node    
    MIN_EDGE_SIZE = 1 #minimum width of an active edge
    
    #size of failure visualisation for nodes and edges
    NODE_FAILURE_SCALE_RANGE = 20
    EDGE_FAILURE_SCALE_RANGE = 50
    
    #active colours for flows, nodes and edges
    FLOW_COLOUR = (255,255,255) #white
    NODE_ACTIVE_COLOUR = (0,153,0) #green
    EDGE_ACTIVE_COLOUR = (124,255,91) #green        
    
    #failure colours
    NODE_FAILED_COLOUR = (255,0,0) #red
    EDGE_FAILED_COLOUR = (255,100,0) #orange 
    GEO_FAILURE_COLOUR = (0,0,255) #blue
    
    #colours generic
    BACKGROUND_COLOUR = (0,0,255) #blue
    LAND_COLOUR = (0,0,0) #black
    BUILDINGS_COLOUR = (92,92,92) #grey
    RIVER_COLOUR = (0,0,255) #blue
    #------------------------------------------------------------------------------
    #flow variables
    
    RANDOM_FLOWS = True
    #file paths for flow origin/destination areas and flow data csv
    ZONE_FILE_NAME = "tyne_wear_msoas"
    FLOW_CSV_NAME = "ne_cummute_by_car_msoa_edited"
    #for random flows        
    NUMBER_OF_FLOWS = 1000
    #for the routing of all flows
    WEIGHT = 'time'
    
    HOURS_TO_RUN_FOR = 0.5 #time which start times are spread over    
    FLOW_COUNT_TIME = [0,10]#HOURS,MINUTES
    
    #outputs
    PRINT_STATS = False
    RECORD = False
    #FILE_PATH = "C:\\Users\\Craig\\network_vis_tool\\vis_sim\\temp_%s-%s-%s.jpg"
    FILE_PATH = "C:\\Users\\Craig\\network_vis_tool\\vis_sim - TW\\temp%s.jpg"
    if RECORD == True: META_FILE = open("C:\\Users\\Craig\\network_vis_tool\\vis_sim - TW\\metadata.txt","w")

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
    GEO_FAILURE = True
    GEO_SHP_NAMES = ["polygon_coastal_flood_eg","spatial_hazards_tw_roads"
                    ]
 
    #junction re-assignment - only checks the closest as an alternative
    REASSIGN_START = True
    REASSIGN_DEST = True
    
    #-----------------------------------------------------------------------------
    #for non targeted approach's
    if MANUAL == True:
        EDGE_FAILURE_TIME = [
            datetime.datetime(2014,2,2,7,45),
            ]        
        NODE_FAILURE_TIME = [
            datetime.datetime(2014,2,2,7,40),
            ]
    
    #for targeted appraoch (nodes only)
    if TARGETED == True:
        TARGETED_FAILURE_TIMES = [
            #datetime.datetime(2014,2,2,7,5),
            ]
    if GEO_FAILURE == True:
        #is running a geo failure
        #requires a seperate time for each shapefile
        GEO_F_TIME = [
            datetime.datetime(2014,2,2,7,04) ,
            datetime.datetime(2014,2,2,7,14) 
            ]
            
    #-----------------------------------------------------------------------------
    #build network
    path =  os.path.dirname(os.path.realpath(__file__))
    if net_source_shpfile == True:
        #print os.path.join(path,"networks","%s.shp" % shpfile_name) == '/home/neil/git_rep/ncl_visualise/networks/metro_geo_rail.shp'
        built_network = ncl_network_sim.build_network(os.path.join(path,"networks","%s.shp" % shpfile_name) , speed_att=speed_att, default_speed=default_speed, length_att=length_att)
    elif net_source_shpfile == False:
        conn = "PG: host='%s' dbname='%s' user='%s' password='%s' port='%s'" % (db_parameters['host'], db_parameters['dbname'], db_parameters['user'], db_parameters['password'], db_parameters['port'])
        built_network = ncl_network_sim.build_net_from_db(conn, db_parameters['net_name'],speed_att=speed_att,default_speed=default_speed, length_att=length_att)
    
    #------------------------------------------------------------------------------
    junctions = built_network.nodes
    net_edges = built_network.edges
    
    #define bounding box and canvas width, height calculated from width
    LEFT,BOTTOM, RIGHT,TOP = built_network.bbox
    buffer_width = (RIGHT-LEFT)/20
    buffer_height = (TOP-BOTTOM)/20
    WINDOWWIDTH = 800
    canvas = ncl_visualize.Canvas((LEFT-buffer_width,TOP+buffer_height),(RIGHT+buffer_width,BOTTOM-buffer_height) ,WINDOWWIDTH)
    canvas.set_background_color(BACKGROUND_COLOUR)
    
    #------------------------------------------------------------------------------
    #Reads in shapefile for land, and converts them to screen coordinates
    #canvas.LoadStatic.Polygon("static_shps/land.shp",color=(0,0,0))
    canvas.LoadStatic.Polygon(os.path.join(path,"static_shps","land.shp"),LAND_COLOUR)
    #canvas.LoadStatic.Polygon("static_shps/leeds_background.shp",color=(0,0,0))
    #canvas.LoadStatic.Polygon("static_shps/greatbritain",color=(0,0,0))
    #canvas.LoadStatic.Polygon("static_shps/london_background.shp",color=(0,0,0))
    
    #Reads in shapefile for river, and converts them to screen coordinates
    canvas.LoadStatic.Polygon(os.path.join(path,"static_shps","river_buffer.shp"),RIVER_COLOUR)
    #canvas.LoadStatic.Polygon("static_shps/leeds_river_buffer.shp",color=(0,0,255))
    #canvas.LoadStatic.Polygon("static_shps/london_rivers.shp",color=(0,0,255)) 
    
    #Reads in shapefile for buildings, and converts them to screen coordinates
    #canvas.LoadStatic.Polygon("static_shps/buildings.shp",color=(92,92,92))
    canvas.LoadStatic.Polygon(os.path.join(path,"static_shps","buildings.shp"),BUILDINGS_COLOUR)
    #canvas.LoadStatic.Polygon("static_shps/tw_urban_areas.shp",color=(92,92,92))
    #canvas.LoadStatic.Polygon("static_shps/Leeds_roads_buildings.shp",color=(92,92,92))
    #canvas.LoadStatic.Polygon("static_shps/greatbritain",color=(92,92,92))
    #canvas.LoadStatic.Polygon("static_shps/london_dlr_buildings.shp",color=(92,92,92))
    
    #SHP_FILE = "C:\\Users\\Craig\\Dropbox\\polygon_multiple_failures_testing.shp"
    #canvas.LoadStatic.Polygon(SHP_FILE,color=(92,92,92))

    #------------------------------------------------------------------------------
    
    #this creates the random flows
    routes_not_pos = 0
    if RANDOM_FLOWS:
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
    else:
        #loads flows and assigns start and end nodes within census zone (AREAS)
        loaded_flows = tools.load_census_flows(os.path.join(path,"static_shps","%s.shp" % ZONE_FILE_NAME),
                        os.path.join(path,"flow_data","%s.csv" % FLOW_CSV_NAME),built_network)
        for f in loaded_flows:
            secs = random.randint(0,HOURS_TO_RUN_FOR*3600)
            person_start_time  = STARTTIME + datetime.timedelta(0,secs)
            done = built_network.add_flow_point(f[0],f[1],person_start_time,WEIGHT)
            if done == False: routes_not_pos += 1
              
    print "number of people who's route is not possible:", routes_not_pos 
    if RECORD: tools.write_metadata(META_FILE,net_source_shpfile,shpfile_name,length_att,
                         speed_att,default_speed,STARTTIME,SECONDS_PER_FRAME,
                         NUMBER_OF_FLOWS,routes_not_pos,HOURS_TO_RUN_FOR,WEIGHT,FLOW_COUNT_TIME)
          
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
            tools.manual_random_edges(EDGE_FAILURE_TIME,net_edges,built_network)
            tools.manual_random_edges(NODE_FAILURE_TIME,junctions,built_network)
    
    if RECORD: tools.write_failure_data(META_FILE,MANUAL,RANDOM_TIME,TIME_INTERVALS,NUMBER_OF_FAILURES,TARGETED,
                                 NODE_EDGE_RANDOM,FLOW,DEGREE,FAILURE_TIMES,EDGE_FAILURE_TIME,NODE_FAILURE_TIME)
    
    #------------------------------------------------------------------------------
    #run simulation
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
        
        #check if a geo failure is scheduled and a file exists
        if GEO_FAILURE == True and len(GEO_SHP_NAMES) > 0:
            GEO_SHP = os.path.join(path,"static_shps/hazard_areas","%s.shp" % GEO_SHP_NAMES[0])
            failure_junctions, failure_edges = tools.geo_failure_comp(NODE_EDGE_RANDOM, FAILURE_TIMES, FLOW_COUNT_TIME,
                                   built_network, failure_junctions, failure_edges, GEO_SHP, GEO_F_TIME)

            #load polygon onto map for visualisation
            for ftime in GEO_F_TIME:
                if ftime == built_network.time:
                    canvas.LoadStatic.Polygon(GEO_SHP,GEO_FAILURE_COLOUR)
                    GEO_SHP_NAMES.pop(0) #remove the first in list as used above
     
        #check if any failures are due and reroute flows
        fails = built_network.Failures.check_fails(REASSIGN_START,REASSIGN_DEST,WEIGHT)
        
        #if there is a failure
        for failure in fails:
            if failure:
                if failure.edge:
                    for i in range(1,EDGE_FAILURE_SCALE_RANGE):
                        #Terprint failure.statsrible failure animation
                        canvas.draw_line(failure.edge.geom,EDGE_FAILED_COLOUR,i)
                        canvas.tick()
                if failure.node:
                    for i in range(1,NODE_FAILURE_SCALE_RANGE):
                        #Terprint failure.statsrible failure animation
                        canvas.draw_point(failure.node.geom,NODE_FAILED_COLOUR,i)
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
                if num_flows:
                    weight = int(max(MIN_EDGE_SIZE,num_flows/EDGE_SCALE_FACTOR))
                    canvas.draw_line(edge.geom,EDGE_ACTIVE_COLOUR,weight)
            else:
                canvas.draw_line(edge.geom,EDGE_FAILED_COLOUR,FAILED_EDGE_SIZE)
        
        #draws network junctions that people have been through their size is changed lateron
        for node in built_network.nodes:
            if not node.failed:
                
                num_flows = node.get_flows(hours=FLOW_COUNT_TIME[0],mins=FLOW_COUNT_TIME[1])
                
                if num_flows:
                    weight = int(max(MIN_NODE_SIZE,num_flows/NODE_SCALE_FACTOR))
                    canvas.draw_point(node.geom,NODE_ACTIVE_COLOUR,weight)
            else:
                canvas.draw_point(node.geom,NODE_FAILED_COLOUR,FAILED_NODE_SIZE)   
        
        #draws each flow point at its location if it has started and not finished
        for fp in built_network.flow_points:
            if fp.started and not fp.finished:
                canvas.draw_point(fp.loc,FLOW_COLOUR,FLOW_SIZE)         
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
run_sim()