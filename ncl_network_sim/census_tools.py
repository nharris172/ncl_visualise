import random
def load_census_flows(areas, flow_csv, built_network):
    """
    Takes the flow zones and finds the nodes in each, then assigns to each flow
    loaded from  the csv randomly a node which falls in its specified start and
    end zone. The zones must have the same names as the start and end zones
    specified for the flows i.e. MSOA name.
    """
    # load in census areas
    # get list of nodes which fall in each area
    area_nodes = get_area_nodes(areas, built_network)
    # load in census data
    flows_to_create = create_csv_flows(flow_csv)
    # assign flows based on random selection of network node in census area
    flow_list = assign_flows_to_nodes(area_nodes, flows_to_create)
    return flow_list


def get_area_nodes(areas, G):
    """
    Method to assign a node within the census area for the flows.
    """
    import shapefile
    polygons = []
    name_list = []
    sf = shapefile.Reader(areas)
    geom = sf.shapeRecords()

    # create list of polygons
    for shape in geom:
        coords = []
        name_list.append(shape.record[1])
        for p in shape.shape.points:
            coords.append(p)
        polygons.append(coords)

    poly = 0
    nodes_per_poly = []
    node_per_area = {}
    f = 0
    total = 0
    while f < len(polygons):
        nodes_per_poly.append([])
        f += 1
    node_list = []

    # create a list of nodes
    for nd in G.nodes:
        node_list.append(nd)

    for polygon in polygons:
        temp = []
        node_count = 0
        # loop thourgh network nodes
        for nd in node_list:
            node_count += 1
            coords = nd.geom
            x, y = coords[0], coords[1]
            coord = float(x), float(y)
            inside = point_in_poly(coord, polygon)
            if inside:
                # when find a node which lies in an area, remove node from the
                # network copy
                node_list.remove(nd)
                total += 1
                nodes_per_poly[poly].append(nd)
                temp.append(nd)

        # add to a dict based on polygone name thus order does not matter
        node_per_area[str(name_list[poly])] = temp
        poly += 1

    return node_per_area


def create_csv_flows(data_file):
    """
    Load from the csv flow data including start and end areas.
    """
    f = open(data_file, 'r')
    # read first line - list of worklocations (first in sequence is empty)
    work_locations = f.readline().split(',')
    flows_to_create = []
    for line in f.readlines():
        # reads all lines of data
        home_locations = line.split(',')
        i = 1
        # loop through the line of data for the from area
        while i < len(home_locations):
            z = 0
            # loop through in case more than one flow from same origin to dest
            while z < int(home_locations[i]):
                # get locations and add to list if all flows
                temp = home_locations[0], work_locations[i]
                flows_to_create.append(temp)
                z += 1
            i += 1
    f.close()
    return flows_to_create


def assign_flows_to_nodes(nodes_per_area, flows_to_create):
    """
    For each flow assign a node randomly whihc lies within its start and end
    area. If no nodes in the area ignore flow. If only one node in area ignore
    flow.
    """
    flow_od = []
    # loop through list of flows
    for flow in flows_to_create:
        # get origin and destination
        origin = flow[0]
        destination = flow[1]
        o = False
        d = False
        # loop through list of areas
        for key in nodes_per_area.keys():
            # if the area is the origin
            if key == origin:
                # shuffle the nodes and select one
                random.shuffle(nodes_per_area[key])
                # if the area has no nodes lying in it
                if len(nodes_per_area[key]) == 0:
                    break
                o = nodes_per_area[key][0]
            # if the area is the destination
            if key == destination:
                random.shuffle(nodes_per_area[key])
                # if the area has no nodes lying it
                if len(nodes_per_area[key]) == 0:
                    break
                d = nodes_per_area[key][0]
                # re-assign d if same as o
                if o == d:
                    # this will get stuck in only one node in area - need to
                    # sort a escape clause
                    if len(nodes_per_area[key]) > 1:
                        d = nodes_per_area[key][1]
                    else:
                        # Cannot assign flow as origin and destination the
                        # same"
                        break
            # check if both have been assigned-if so stop looping
            if o and d:
                temp = o, d
                flow_od.append(temp)
                break

    print "-------------------------"
    print "Numnber of flows created:", len(flow_od)
    print "Number of flows not possible:", len(flows_to_create) - len(flow_od)
    print "-------------------------"
    # as using network with down to a roads only, some areas don't have any
    # nodes
    return flow_od
