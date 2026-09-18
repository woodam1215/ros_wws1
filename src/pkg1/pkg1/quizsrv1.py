# 터틀 십: 큰 원 작은원 교대로 그리기 서버
import math
import time
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_srvs.srv import SetBool

class CirclesSrvr1(Node):
    def __init__(self):
        super().__init__('circles_srvr_node1')

        # 1. 거북이 속도 publisher
        self.pubber1 = self.create_publisher(
            Twist,
            '/tuetle1/cmd_vel',
            10
        )

        # 2. Service 서버 생성
        self.srvr1 = self.create_service(
            SetBool,
            '/draw_circle1',
            self.service_callback
        )

        self.linear.speed = 1.0
        self.big_angular = 0.5
        self.small_angular = 1.0

        self.get_logger().info(
            '/draw_circle1 서비스 서버 시작'
        )

    def service_callback(self, req, resp):
        # 1. Request 확인
        # 2. True: 큰 원, False: 작은 원
        if req.data:
            circle_name = '큰 원'
            angular_speed = self.big_angular
        else:
            circle_name = '작은 원'
            angular_speed = self.small_angular

        self.get_logger().info(
            f'{circle_name} 요청 받음'
        )

        # 2. 한 바퀴 도는 시간 계산
        circle_time = (
            2.0 * math.pi / angular_speed
        )

        # 3. Twist 메시지
        msg = Twist()

        msg.linear.x = self.linear_speed
        msg.angular.z = angular_speed

        # 4. 한 바퀴 돌기 실행
        start_time = time.monotonic() # 프로그램 실행 중 증가 시간

        while(time.monotonic() - start_time < circle_time):
            self.pubber1.publish(msg)
            # 약 20Hz
            time.sleep(0.05)

        # 5. 한 바퀴 후 정지
        stop_msg = Twist()
        stop_msg.linear.x = 0.0
        stop_msg.angular.z = 0.0

        self.pubber1.publish(stop_msg)

        # 6. Client 에게 결과 응답 보냄
        resp.success = True

        resp.message = (
            f'{circle_name} 한 바퀴 완료'
        )

        self.get_logger().info(
            resp.message
        )
        return resp

def main(args=None):
    rclpy.init(args=args)

    node1 = CirclesSrvr1()
    try:
        rclpy.spin(node1)
    except KeyboardInterrupt:
        pass
    finally:
        node1.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()        