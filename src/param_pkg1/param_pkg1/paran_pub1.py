# 1. 원 2. 네모 
import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32

class parampub1(Node):
    def __init__(self):
        super().__init__('param_pub_node1')

        self.pubber = self.create_publisher(
            Int32,
            '/shape_topic1',
            10
        )

        self.get_logger().info('모양 선택: 0=정지, 1=원, 2=네모')

    def publish_shape(self, shape):
        msg1 = Int32()
        msg1.data = shape

        self.pubber.publish(msg1)

        if shape == 1:
            self.get_logger().info('원 그리기 방향 선택')
        elif shape == 2:
            self.get_logger().info('네모 그리기 방향 선택')
        elif shape == 0:
            self.get_logger().info('정지')

def main(args=None):
    rclpy.init(args=args)

    node1 = parampub1()
    try:
        while rclpy.ok():
            user_input= input(
                '모양 선 [1: 원, 2: 네모, 0: 정지] >'
            )

            if user_input == "1":
                node1.publish_shape(1)
            elif user_input == "2":
                node1.publish_shape(2)
            elif user_input == "0":
                node1.publish_shape(0)
            else:
                print('입력 불가')
    except KeyboardInterrupt:
        pass
    finally:
        node1.destroy_node()
        rclpy.shutdown()