# 큰 원 작은 원 번갈아 그리기: subscriber
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import math

class Subcriber(Node):
    def __init__(self):
        super().__init__('circle_subscriber')

        # 가장 최근에 받은 메시지 저장요 함수
        self.latest_msg = None

        # 1. subscriber 생성
        self.subber1 = self.create_subscription(
            Twist,
            '/turtle1/cmd_vel',
            self.cmd_callback,
            10
        )

        # 2. 출력용 타이머 생성
        # 너무 빠르지 않도록 1초마다 출력
        self.timer = self.create_timer(
            1.0,
            self.timer_callback
        )

    def cmd_callback(self, msg):
        self.latest_msg = msg

    def timer_callback(self):
        if self.latest_msg is None:
            return 

        linear = self.latest_msg.linear.x
        angular = self.latest_msg.angular.z

        # 원의 반지름 계산
        if angular != 0.0:
            radius = linear / angular
        else:
            radius = 0.0

        # 큰 원 / 작은 원 판단
        if abs(angular - 0.5) < 0.01:
            circle_type = "큰 원"

        elif abs(angular - 1.0) < 0.01:
            circle_type = '작은 원'
        else: 
            circle_type = ''

        self.get_logger().info(
            f'{circle_type} | '
            f'linear= {linear:.2f}'
            f'angular= {angular:.2f}'
            f'radius = {radius:.2f}'
        )

def main(args=None):
    rclpy.init(args=args)
    node1 = Subcriber()
    rclpy.spin(node1)

    node1.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()