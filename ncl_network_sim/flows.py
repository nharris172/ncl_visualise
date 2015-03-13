import math


class FlowPoint:

    """Handles the management of the  flowpoints and thier movement throught
    the network during the simulation/visualisation."""

    def __init__(self, network, waypoints, start_time, speed=False):
        self.network = network
        self.waypoints = waypoints
        self.start_time = start_time
        self.speed = speed
        self.point = 0
        self.loc = waypoints[0].start_node.geom
        self.finished = False
        self.started = False
        self.edge = waypoints[0]

    def move(self, time):
        """Moves the person the correct location. Updates the lists of nodes
        and edges visited during the time step for the person as well."""
        if not self.speed:
            step = self.edge.speed * time
        else:
            step = self.speed * time
        ax, ay = self.loc
        bx, by = self.edge.end_node.geom
        dist = math.hypot(bx - ax, by - ay)
        while dist < step:
            self.loc = self.edge.end_node.geom
            if self.point == 0:
                try:
                    if self.waypoints[
                            self.point].start_node in self.network.nodes:
                        self.waypoints[
                            self.point].start_node.add_flow(
                            self.network.time)
                except:
                    print self.point
                    print len(self.waypoints)

            if self.waypoints[self.point].end_node in self.network.nodes:
                self.waypoints[self.point].end_node.add_flow(self.network.time)
            self.waypoints[self.point].add_flow(self.network.time)
            self.point += 1

            if self.point == len(self.waypoints):
                self.finished = True
                self.edge = None
                return

            self.edge = self.waypoints[self.point]
            step -= dist
            self.loc = self.edge.start_node.geom
            ax, ay = self.waypoints[self.point].start_node.geom
            bx, by = self.waypoints[self.point].end_node.geom
            dist = math.hypot(bx - ax, by - ay)
        bearing = math.atan2(by - ay, bx - ax)
        self.loc = (
            self.loc[0] +
            step *
            math.cos(bearing),
            self.loc[1] +
            step *
            math.sin(bearing))
        self.edge = self.waypoints[self.point]
