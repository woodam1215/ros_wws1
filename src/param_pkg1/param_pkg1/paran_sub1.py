# 1. 원 2. 네모 subscriber
import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32
from geometry_msgs.msg import Twist
import math

class paramsub1(Node):
    def __init__(self):
        super().__init__('param_sub_node1')

        # 파라미터 선언
        self.declare_parameter(
            'linear_x',
            2.0
        )

        self.declare_parameter(
            'angular_z',
            1.0
        )

        # 기본 모양: 원
        self.shape_mode = 1

        # 네모 그리기 상태 
        self.square_state = 'forward'

        self.forward_time = 0.0
        self.turn_angle = 0.0

        # 네모의 한 변을 이용하는 시간
        self.side_time = 2.0

        # timer 추가
        self.dt= 0.1

        # 모양 명령 구독
        self.subber = self.create_subscription(
            Int32,
            '/shape_topic1',
            self.shape_callback,
            10
        )

        # turtlesim 속도 명령 실행
        self.pubber = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            10
        )

        self.timer = self.create_timer(
            self.dt,
            self.timer_callback
        )

        self.get_logger().info("기본 모드: 원 그리기")


    def shape_callback(self, msg):
        if msg.data == 1:
            self.shape_mode = 1
            self.get_logger().info('모드 변경: 원')

        elif msg.data == 2:
            self.shape_mode = 2

            # 네모 동작 초기화
            self.square_state = 'forward'
            self.forward_time = 0.0
            self.turn_angle = 0.0

            self.get_logger().info('모드 변경: 네모')

        elif msg.data == 0:
            self.shape_mode = 0
            self.get_logger().info('모드 정지')

    def timer_callback(self):
        # 현재 파라미터 값 읽기
        linear_x = self.get_parameter('linear_x').value
        angular_z = self.get_parameter('angular_z').value

        msg = Twist()

        # 1. 원 그리기
        if self.shape_mode == 1:
            msg.linear.x = linear_x
            msg.angular.z = angular_z

        # 2. 네모 그리기
        elif self.shape_mode == 2:
            # 직진
            if self.square_state == 'forward':
                msg.linear.x = linear_x
                msg.angular.z = 0.0

                self.forward_time += self.dt

                if self.forward_time >= self.side_time:
                    self.forward_time = 0.0
                    self.square_state = 'turn'

            # 90도 회전
            elif self.square_state == "turn":
                msg.linear.x = 0.0
                msg.angular.z = angular_z

                self.turn_angle += (
                    abs(angular_z) * self.dt
                )

                if self.turn_angle >= math.pi / 2:
                    self.turn_angle = 0.0
                    self.square_state = 'forward'

        elif self.shape_mode == 0:
            msg.linear.x = 0.0
            msg.angular.z = 0.0

        self.pubber.publish(msg)

def main(args=None):
    rclpy.init(args=args)

    node1 = paramsub1()

    try:
        rclpy.spin(node1)
    except:
        pass

    # 종료할 때 거북이 정지
    stop_msg = Twist()
    node1.pubber.publish(stop_msg)

    node1.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()