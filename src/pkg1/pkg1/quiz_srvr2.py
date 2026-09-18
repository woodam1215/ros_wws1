# 목표 수자까지 제곱값 계산
import time
import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer
from interface_pkg1.action import MyAction3

class SumServer(Node):
    def __init__(self):
        super().__init__('quiz_act_sevr_node1')

        # 액션 서버 생성
        self._action_server1 = ActionServer(
            self,
            MyAction3,
            'act_cmd3',
            self.execute_callback
        )

        self.get_logger().info('제곱 합계 액션 서버 시작')

    def execute_callback(self, goal_handle):
        target_num = goal_handle.request.target_num

        self.get_logger().info(
            f'goal 수신: 1부터 {target_num} 까지 계산'
        )

        feedback_msg = MyAction3.Feedback()

        total = 0

        for num in range(1, target_num + 1):
            square = num ** 2
            total += square

            feedback_msg.current_num = num
            feedback_msg.square = square

            goal_handle.publish_feedback(feedback_msg)

            self.get_logger().info(
                f'Feedback 전송: {num}의 제곱 = {square}'
            )

            time.sleep(0.5)

            goal_handle.succeed()

            result = MyAction3.Result()
            result.total = total

            self.get_logger().info(f'Result: total = {total}')
            return result

def main(args=None):
    rclpy.init(args=args)
    node1 = SumServer()
    rclpy.spin(node1)

    node1.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()