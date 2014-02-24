def truncate_geom(p):
    """Rounds the geometry to nearest 10 this is to ensure the network in topologically correct"""
    return (int(10 * round(float(p[0])/10)),int(10 * round(float(p[1])/10)))
