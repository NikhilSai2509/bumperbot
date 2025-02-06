import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TwistStamped
import sys
import termios
import tty

# Instructions for keyboard controls
instructions = """
Control Your Robot!
---------------------------
Moving around:
   w    
a  s  d

w/a/s/d: Move forward/left/backward/right
q/e: Rotate counter-clockwise/clockwise
space: Stop the robot
CTRL+C: Quit
"""

# Default linear and angular speed
LINEAR_SPEED = 0.3
ANGULAR_SPEED = 0.25


class KeyboardTwistStamped(Node):
    def __init__(self):
        super().__init__('keyboard_twist_stamped')

        # Publisher for TwistStamped messages
        self.publisher = self.create_publisher(TwistStamped, '/bumperbot_controller/cmd_vel', 10)

        # Initialize speeds
        self.linear_speed = 0.0
        self.angular_speed = 0.0

        # Print instructions
        print(instructions)

    def get_key(self):
        """Capture keyboard input without requiring Enter."""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            key = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return key

    def publish_twist_stamped(self):
        """Publish a TwistStamped message based on the current speed settings."""
        twist_stamped = TwistStamped()

        # Add timestamp and frame ID
        twist_stamped.header.stamp = self.get_clock().now().to_msg()
        twist_stamped.header.frame_id = "base_link"

        # Set velocities
        twist_stamped.twist.linear.x = self.linear_speed
        twist_stamped.twist.angular.z = self.angular_speed

        # Publish the message
        self.publisher.publish(twist_stamped)

    def run(self):
        """Main loop to read keyboard input and publish TwistStamped messages."""
        try:
            while rclpy.ok():
                key = self.get_key()

                # Map keyboard input to motion
                if key == 'w':
                    self.linear_speed = LINEAR_SPEED
                    self.angular_speed = 0.0
                elif key == 's':
                    self.linear_speed = -LINEAR_SPEED
                    self.angular_speed = 0.0
                elif key == 'a':
                    self.linear_speed = 0.0
                    self.angular_speed = ANGULAR_SPEED
                elif key == 'd':
                    self.linear_speed = 0.0
                    self.angular_speed = -ANGULAR_SPEED
                elif key == 'q':
                    self.linear_speed = LINEAR_SPEED
                    self.angular_speed = ANGULAR_SPEED
                elif key == 'e':
                    self.linear_speed = LINEAR_SPEED
                    self.angular_speed = -ANGULAR_SPEED
                elif key == ' ':  # Stop
                    self.linear_speed = 0.0
                    self.angular_speed = 0.0
                elif key == '\x03':  # CTRL+C
                    break
                else:
                    continue

                # Publish the TwistStamped message
                self.publish_twist_stamped()

        except Exception as e:
            self.get_logger().error(f"Error in keyboard control: {e}")
        finally:
            # Stop the robot before exiting
            self.linear_speed = 0.0
            self.angular_speed = 0.0
            self.publish_twist_stamped()


def main(args=None):
    rclpy.init(args=args)
    node = KeyboardTwistStamped()
    try:
        node.run()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
