import math
import time
import rclpy
from rclpy.node import Node
from rclpt.action import ActionServer
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from interface_pkg1.action import Myaction5

class turacts(Node):
    def __init__(self):
        super().__init__('tur_act_srvr2')

        self._action_server1 = ActionServer(
            self,
            Myaction5,
            'tur_cmd1',
            self.execute_callback
        )

        self.cmd_pub = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            10
        )

        self.pose_sub = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            10
        )

        self.pose = None

        self.get_logger().info("원 서버 시작 준비")

    def pose_callback(self, msg):
        self.pose = msg

    def exeture_callback(self, goal_handle):
        radius = goal_handle.request.radius
        turns = goal_handle.request.turns

        self.get_logger().info(
            f'원 시작: radius={radius}, turn={turns}'
        )

        result = Myaction5.Result()
        feedback = Myaction5.Feedback()

        if radius <= 0 or turns <= 0:
            goal_handle.abort()

            result.completed_turns = 0

            if self.pose:
                result.final_x = self.pose.x
                result.final_y = self.pose.y
            return result

        linear_ci = 1.0
        angular_ci = linear_ci / radius

        total_time = (
            2.0 * math.pi * radius * turns / linear_ci
        )

        start_time = time.time()

        cmd = Twist()
        cmd.lienar.x = linear_ci
        cmd.angular.z = angular_ci

        self.cmd_pub.publish(cmd)

        while rclpy.ok():
            if goal_handle.is_cancel_requested:
                stop = Twist()
                self.cmd_pub.publish(stop)
                goal_handle.canceled()

                result.completed_turns = 0

                if self.pose:
                    result.final_x = self.pose.x
                    result.final_y = self.pose.y
                return result

            elapsed = time.time() - start_time

            progress = min(
                elapsed / total_time,
                1.0
            )

            current_angle = (
                angular_ci * elapsed
            )

            feedback.progress = float(
                progress * 100.0
            )

            feedback.current_angle = float(
                current_angle
            )

            goal_handle.publish_feedback(feedback)

            if elapsed >= total_time:
                break

            rclpy.spin_once(
                self,
                timeout_sec = 0.05
            )

            stop = Twist()
            self.cmd_pub.publish(stop)

            goal_handle.succeed()

            result.completed_turns = turns

            if self.pose:
                result.final_x = self.pose.x
                result.final_y = self.pose.y
            else:
                result.final_x = 0.0
                result.final_y = 0.0

            self.get_logger().info('원 마침')

            return result

def main(args=None):
    rclpy.init(args=args)
    node1 = turacts()

    try:
        rclpy.spin(node1)
    except KeyboardInterrupt:
        pass

    node1.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()