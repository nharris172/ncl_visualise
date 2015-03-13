from rtree import index


def truncate_geom_funtion_maker(dp=1):

    def truncate_geom_dp(p):
        """Rounds the geometry to nearest 10 this is to ensure the network in topologically correct"""
        return (round(float(p[0]), dp), round(float(p[1]), dp))
    return truncate_geom_dp


def area_sign(poly):
    res = 0.0
    for i in range(0, len(poly) - 1):
        p1 = poly[i]
        p2 = poly[i + 1]
        res += (p1[0] * p2[1]) - (p1[1] * p2[0])

    if res < 0:
        return -1
    elif res > 0:
        return 1
    elif res == 0:
        return 0
    else:
        "Major error. Logic error."


def line_intersection(line1, line2):

    l1p1 = line1[0]
    l1p2 = line1[1]
    l2p1 = line2[0]
    l2p2 = line2[1]

    poly = [l1p1, l1p2, l2p1, l1p1]
    sign1 = area_sign(poly)
    poly = [l1p1, l1p2, l2p2, l1p1]
    sign2 = area_sign(poly)
    poly = [l2p1, l2p2, l1p1, l2p1]
    sign3 = area_sign(poly)
    poly = [l2p1, l2p2, l1p2, l2p1]
    sign4 = area_sign(poly)

    if sign1 != sign2 and sign3 != sign4:
        return 1  # inserect
    else:
        return 0  # do not intersect


def point_in_poly(coord, poly):
    x, y = coord
    n = len(poly)
    inside = False

    p1x, p1y = poly[0]
    for i in range(n + 1):
        p2x, p2y = poly[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xints = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside


def geo_failure(shp_file, sim_network):
    import shapefile
    polygons = []
    sf = shapefile.Reader(shp_file)
    shapes = sf.shapes()
    idx = index.Index()
    polygon_dict = {}
    i = 0
    for shape in shapes:
        idx.insert(i, shape.bbox)
        coords = []
        for p in shape.points:
            coords.append(p)
        polygon_dict[i] = coords
        i += 1
        polygons.append(coords)

    junctions = sim_network.nodes
    net_edges = sim_network.edges
    nodes_inside = []
    number_inside = 0
    # extract list of coords
    # loop through the polygons in the shapefile
    for nd in junctions:
        print nd
        coords = nd.geom
        x, y = coords[0], coords[1]
        coord = float(x), float(y)
        polgon_indexs = list(
            idx.intersection(
                (float(x), float(y), float(x), float(y))))
        for pindex in polgon_indexs:
            # find if the junction lies in the polygon
            inside = point_in_poly(coord, polygon_dict[pindex])
            if inside:
                nodes_inside.append(nd)
                number_inside += 1
    print number_inside
    failed_edges = []
    # find all edge segments which lie within a hazard area
    lines_in = 0
    for eg in net_edges:

        line1 = eg.start_node.geom, eg.end_node.geom

        polgon_indexs = list(
            set(
                list(
                    idx.intersection(
                        (line1[0][0],
                         line1[0][1],
                            line1[0][0],
                            line1[0][1]))) +
                list(
                    idx.intersection(
                        ([1][0],
                         line1[1][1],
                            line1[1][0],
                            line1[1][1])))))

        for pindex in polgon_indexs:

            inside1 = point_in_poly(line1[0], polygon_dict[pindex])
            if inside1:
                inside2 = point_in_poly(line1[1], polygon_dict[pindex])
                if inside2:
                    lines_in += 1
                    failed_edges.append(eg)
    print lines_in
    # find those edges where at least one of is endpoints have failed

    for eg in net_edges:
        if eg in failed_edges:
            continue
        for nd in nodes_inside:
            if eg.start_node == nd or eg.end_node == nd:
                failed_edges.append(eg)

    # find all edge segments which intersect with the hazard areas
    # loop thorugh all edge segments(line1)
    lines_inter = 0
    for eg in net_edges:
        if eg in failed_edges:
            continue

        line1 = eg.start_node.geom, eg.end_node.geom
        line_bbox = (
            min(line1[0][0], line1[1][0]),
            min(line1[0][1], line1[1][1]),
            max(line1[0][0], line1[1][0]),
            max(line1[0][1], line1[1][1]),
        )
        polgon_indexs = list(idx.intersection(line_bbox))
        for pindex in polgon_indexs:
            # loop through edge segments of polygon (line2)
            for i in range(0, len(polygon_dict[pindex]) - 1):
                line2 = polygon_dict[pindex][i], polygon_dict[pindex][i + 1]
                # use a line intersection algorithm to check
                intersect = line_intersection(line1, line2)
                if intersect == 1:  # lines intersect
                    lines_inter += 1
                    failed_edges.append(eg)

    print 'lines_inter:', lines_inter
    print 'lines_inside:', lines_in
    # once found a segment, need to remove the whole edge
    # add edge to failed egdes

    return number_inside, list(set(nodes_inside)), list(set(failed_edges))
