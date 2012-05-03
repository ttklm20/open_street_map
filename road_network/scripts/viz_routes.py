#!/usr/bin/python
# Software License Agreement (BSD License)
#
# Copyright (C) 2012, Jack O'Quin
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#  * Neither the name of the author nor of other contributors may be
#    used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# Revision $Id$

"""
Create route network messages for geographic information maps.
"""

from __future__ import print_function

PKG_NAME = 'road_network'
import roslib; roslib.load_manifest(PKG_NAME)
import rospy

import sys
import itertools
import geodesy.wu_point

from geographic_msgs.msg import RouteNetwork
from geographic_msgs.msg import RouteSegment
from geometry_msgs.msg import Point
from geometry_msgs.msg import Quaternion
from geometry_msgs.msg import Vector3
from std_msgs.msg import ColorRGBA
from visualization_msgs.msg import Marker
from visualization_msgs.msg import MarkerArray

class RouteVizNode():

    def __init__(self):
        """ROS node to publish the route network graph for a GeographicMap.
        """
        rospy.init_node('viz_routes')
        self.msg = None
        self.marks = None

        # advertise visualization marker topic
        self.pub = rospy.Publisher('visualization_marker_array',
                                   MarkerArray, latch=True)

        # subscribe to route network
        self.sub = rospy.Subscriber('route_network', RouteNetwork,
                                    self.graph_callback)

    def graph_callback(self, msg):
        """Publish visualization markers for a RouteNetwork graph.

        :param msg: RouteNetwork message

        :post: self.marks = visualization markers message.
        :post: self.msg = RouteNetwork message.
        """
        self.msg = msg
        self.marks = MarkerArray()
        self.points = geodesy.wu_point.WuPointSet(msg.points)

        self.mark_way_points(ColorRGBA(r=1., g=1., b=0., a=0.8))

        self.pub.publish(self.marks)

    def mark_way_points(self, color):
        """Create slightly transparent disks for way-points.

        :param color: disk RGBA value
        """
        cylinder_size = Vector3(x=2., y=2., z=0.2)
        null_quaternion = Quaternion(x=0., y=0., z=0., w=1.)
        index = 0
        for wp in self.points:
            marker = Marker(header = self.msg.header,
                            ns = "route_waypoints",
                            id = index,
                            type = Marker.CYLINDER,
                            action = Marker.ADD,
                            scale = cylinder_size,
                            color = color,
                            lifetime = rospy.Duration())
            index += 1
            # use easting and northing coordinates (ignoring altitude)
            marker.pose.position = wp.toPointXY()
            marker.pose.orientation = null_quaternion
            self.marks.markers.append(marker)
    
def main():
    node_class = RouteVizNode()
    try:
        rospy.spin()            # wait for messages
    except rospy.ROSInterruptException: pass

if __name__ == '__main__':
    # run main function and exit
    sys.exit(main())
