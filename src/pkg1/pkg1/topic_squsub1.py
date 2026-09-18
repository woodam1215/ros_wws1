import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose
from std_msgs.msg import Int32, Bool


class turSub1(Node):
    def __init__(self):
        super().__init__('tur_sub_node1')

        # 현재 거북이 위치 구독
        self.pose_sub = self.create_subscription(
            Pose,
            'turtle1/cmd_vel',
            self.pose_callback1,
            10
        )

        # 현재 몇 번째 변인지 아는 법
        self.side_sub = self.create_subscription(
            Int32,
            '/sq/cur_side1',
            self.side_callback,
            10
        )

        # 완료 여부
        self.done_sub = self.create_subscription(
            Bool,
            '/sq/done1',
            self.done_callback,
            10
        )

    def pose_callback1(self, msg):
        self.get_logger().info(
            f'pose: x: {msg.x:.2f}, '
            f'y: {msg.y:.2f}, theta: {msg.theta:.2f}'
        )

    def side_callback(self, msg):
        self.get_logger().info(
            f'현재 변: {msg.data}번째'
        )

    def done_callback(self, msg):
        if msg.data:
            self.get_logger().info(
                '네모 그리기 완료'
            )

def main(args=None):
    rclpy.init(args=args)

    node1 = turSub1()
    rclpy.spin(node1)

    node1.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()