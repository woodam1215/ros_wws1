# 터틀십  
import rclpy
from rclpy.node import Node
from std_srvs.srv import SetBool

class CirclesCli1(Node):
    def __init__(self):
        super().__init__('circles_cli_node1')

        # 1. service Client
        self.cli1 = self.create_client(
            SetBool,
            'draw_circle1'
        )

        # 2. 서버가 실행될 때까지 대기
        while not self.cli1.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('서버 기다리는 중')

    def send_request(self, is_big):
        request = SetBool.Reaquest()

        # 3. 객체 생성
        request.data = is_big

        # 4. 비 동기 서비스 요청
        future = self.cli1.call_async(request)

        # 5. 응답이 올 때까지 기다림
        rclpy.spin_utill_future_complete(self, future)

        return future.result()

def main(args=Node):
    rclpy.init(args=args)

    node1 = CirclesCli1()

    # 처음에는 큰 원
    is_big = True

    try:
        while rclpy.ok():
            # 1. 현재 요청 종류 출력
            if is_big:
                node1.get_logger().info("큰 원 요청")
            else:
                node1.get_logger().info("작은 원 요청")

            # 2. 서비스 요청 
            response = node1.send_request(is_big)

            # 3. 응답 확인
            if response is not None:
                node1.get_logger().info(
                    f'Server 응답: {response.message}'
                )

            # 4. 큰 원 < = > 작은 원 변경
            is_big = not is_big

    except KeyboardInterrupt:
        pass
    finally:
        node1.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()