#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
import rclpy.time
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import OccupancyGrid, MapMetaData
from tf2_ros import Buffer, TransformListener
from tf2_ros import LookupException
from tf_transformations import euler_from_quaternion
import math

class Pose():
    def __init__(self, px=0,py=0):
        self.x = px
        self.y = py

def coordinatesToPose(px , py, map:MapMetaData):
    pose = Pose()
    pose.x = round((px - map.origin.position.x)/map.resolution)
    pose.y = round((py - map.origin.position.y)/map.resolution)
    return pose

def poseonMap(pose: Pose, map:MapMetaData):
    return pose.x < map.width and pose.x >=0 and pose.y < map.height and  pose.y >=0

def poseToCell(pose: Pose,map:MapMetaData):
    return map.width * pose.x + pose.y
    
class Mappingwihtpose(Node):
    def __init__(self, name):
        super().__init__(name)

        self.declare_parameter('width',50.0)
        self.declare_parameter('height', 50.0)
        self.declare_parameter('resolution', 0.1)

        width_m = self.get_parameter('width').value  #This is the dimensions of map in meters 
        height_m = self.get_parameter('height').value
        resolution = self.get_parameter('resolution').value

        self.map = OccupancyGrid()
        self.map.info.resolution = resolution
        self.map.info.height = round(height_m/resolution) #This refers to height and width in terms of CELLS
        self.map.info.width = round(width_m/resolution)
        self.map.info.origin.position.x = float(-round(height_m/2))##
        self.map.info.origin.position.y = float(-round(width_m/2))##
        self.map.header.frame_id = 'odom'
        self.map.data = [-1] * (self.map.info.height*self.map.info.width)

        self.map_pub = self.create_publisher(OccupancyGrid,'map',1)
        self.scan_sub = self.create_subscription(LaserScan,'scan',self.scan_callback,10) ##
        self.timer = self.create_timer(1.0,self.timer_callback)

        self.tf_buffer = Buffer()
        self.tf_listenere = TransformListener(self.tf_buffer,self)

    def scan_callback(self, scan:LaserScan):
        try:
            t = self.tf_buffer.lookup_transform(self.map.header.frame_id,scan.header.frame_id, rclpy.time.Time())
        except LookupException:
            self.get_logger().error('Unable to tarnsform between /odom and /basfootprint')
            return

        robot_p = coordinatesToPose(t.transform.translation.x,t.transform.translation.y, self.map.info)
        if not poseonMap(robot_p, self.map.info):
            self.get_logger().error('The robot is out of the map')
            return
        
        robot_cell = poseToCell(robot_p , self.map.info) ##
        self.map.data[robot_cell] = 100

    def timer_callback(self):
        self.map.header.stamp = self.get_clock().now().to_msg()
        self.map_pub.publish(self.map)


def main():
    rclpy.init()
    MapNode = Mappingwihtpose('map_with_pose')
    rclpy.spin(MapNode)
    MapNode.destroy_node()
    rclpy.shutdown()

if __name__=='__main__':
    main()