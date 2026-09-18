import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from action_msgs.msg import GoalStatus
from interface_pkg1.action import MyAction3

class SumClient(Node):
    def __init__(self):
        super().__init__('quiz_Act_cli_node1')

        # 액션 클라 생성
        self._act_cli1 = ActionClient(
            self,
            MyAction3,
            'act_cmd3'
        )

    def send_goal(self, target_num):
        self.get_logger().info('액션 서버 대기')
        self._act_cli1.wait_for_server()
        goal_msg = MyAction3.Goal()
        goal_msg.target_num =target_num

        self.get_logger().info(f'goal 전송: target_num = {target_num}')

        self.goal_future = self._act_cli1.send_goal_async(
                goal_msg,
                feedback_callback=self.feedback_callback1
        )

        self.goal_future.add_done_callback(
            self.goal_response_callback
        )

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('골 거절됨')
            return

        self.get_logger().info('골 수락됨')
        self.result_future = goal_handle.get_result_async()

        self.result_future.add_done_callback(
            self.result_callback
        )

    def feedback_callback1(self, feedback_msg):

        feedback = feedback_msg.feedback
        self.get_logger().info(
            f'feedback current num = {feedback.current_num}' 
            f'square = {feedback.square}'
        )

    def result_callback(self, future):
        result_resp = future.result()
        result = result_resp.result
        status = result_resp.status

        if status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info(
                f'Result: 제곱의 합 = {result.total}'
            )
        else:
            self.get_logger().info(
                f'액션이 비정상 종료됨'
            )

        rclpy.shutdown()

def main(args=None):
    rclpy.init(args=args)
    node1 = SumClient()
    node1.send_goal(6)
    rclpy.spin(node1)

if __name__ == '__main__':
    main()