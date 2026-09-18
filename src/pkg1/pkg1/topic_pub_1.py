# 큰 원 작은 원 번갈아 그리기
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import math

class Publi(Node):
    def __init__(self):
        super().__init__("circle_pub_node1")

        # 1. publisher
        self.pubber1 = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            10
        )

        # 2. 속도 명령
        self.linear_speed = 1.0

        # 큰 원
        self.big_angular = 0.5

        # 작은 원
        self.small_angular = 1.0

        # 원 교차 플래그: 처음에는ㄴ 큰 원
        self.is_big = True

        # 현재 원 그리기 시작 시간
        self.start_time = self.get_clock().now()

        # 타이머 생성 0.1 초마다 속도 명령 발행
        self.timer = self.create_timer(
            0.1,
            self.timer_callback
        )

        self.get_logger().info("큰 원부터 시작")

    def timer_callback(self):
        # 1. 현재 원에 맞는 각속도 선택
        if self.is_big:
            angular_speed = self.big_angular
        else:
            angular_speed = self.small_angular

        # 2. 한 바퀴 도는 체 걸리는 시간
        circle_time = 2.0 * math.pi / angular_speed

        # 3. 현재까지 지난 시간
        now1 = self.get_clock().now()

        elapsed_time = (
            now1 - self.start_time
        ).nanoseconds / 1e9

        # 4. 한 바퀴가 끝나면 큰 원  <=> 작은 원 변경
        if elapsed_time >= circle_time:
            self.is_big = not self.is_big
            self.start_time = now1

            if self.is_big:
                self.get_logger().info('큰 원 시작')
            else:
                self.get_logger().info('작은 원 시작')

            # 변경된 원의 angular 값
            if self.is_big:
                angular_speed = self.big_angular
            else:
                angular_speed = self.small_angular

        # 5. Twist 메시지 생성 
        msg = Twist()

        msg.linear.x = self.linear_speed
        msg.angular.z = angular_speed

        # 6. 발행 
        self.pubber1.publish(msg)

    # 프로그램 종료 전 거북이 멈춤
    def stop(self):
        msg = Twist()

        msg.linear.x = 0.0
        msg.angular.z = 0.0

        self.pubber1.publish(msg)

def main(args=None):
        rclpy.init(args=args)
        node1 = Publi()

        try:
            rclpy.spin(node1)
        except KeyboardInterrupt:
            pass
        finally:
            node1.stop()
            node1.destroy_node()
            rclpy.shutdown()

if __name__ == '__main__':
    main()