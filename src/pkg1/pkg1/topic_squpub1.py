import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Int32, Bool
import time, math

class turpub1(Node):
    def __init__(self):
        super().__init__('tur_pub_node1')
        self.cmd_pub = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            10
        )

        # 거북이 이동 명령
        self.side_pub = self.create_publisher(
            Int32,
            '/sq/cur_side1',
            10
        )

        # 네모 그리기 완료 여부
        self.done_pub = self.create_publisher(
            Bool,
            '/sq/done1',
            10
        )

    # 네모 그리기 함수
    def square(self, side_length):
        for i in range(4):
            # 현재 변 번호 발행
            side_msg = Int32()
            side_msg.data = i + 1
            self.side_pub.publish(side_msg)

            self.get_logger().info(
                f'{i + 1} 번재 변'
            )

            # 직진
            self.move_straight(side_length)

            # 90 도 회전 = (~ 1.57 라디안)
            self.rotate_90()

        # 완료 메시지
        done_msg = Bool()
        done_msg.data = True

        self.done_pub.publish(done_msg)

        self.get_logger().info('square 완료')

    # 직진하기
    def move_straight(self, distance):
        speed = 1.0
        move_time = distance / speed

        msg = Twist()
        msg.linear.x = speed

        start_time = time.monotonic()

        while time.monotonic() - start_time < move_time:
            self.cmd_pub.publish(msg)
            time.sleep(0.05)

        self.stop()

    # 90도 회전하기
    def rotate_90(self):
        angular_speed = 1.0
        rotate_time = (math.pi / 2) / angular_speed

        msg = Twist()
        msg.angular.z = angular_speed

        start_time = time.monotonic()

        while time.monotonic() - start_time < rotate_time:
            self.cmd_pub.publish(msg)

            time.sleep(0.05)

        self.stop()

    # 정지 하기
    def stop(self):
        msg = Twist()
        self.cmd_pub.publish(msg) # 디폴트가 0.0이다 
        time.sleep(0.1)

def main(args=None):
    rclpy.init(args=args)

    node1 = turpub1()

    # 한 변의 길이
    side_length = 2.0

    # 네모 그리기
    node1.square(side_length)

    node1.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()