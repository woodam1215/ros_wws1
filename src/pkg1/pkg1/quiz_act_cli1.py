# 가상이 컨베이어 벨트 이동하기
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from action_msgs.msg import GoalStatus
from interface_pkg1.action import MyAction4

class ConvetorActCli2(Node):
    def __init__(self):
        super().__init__('quiz_act_cli_node2')

        self.act_cli2 = ActionClient(
            self, 
            MyAction4,
            'act_cmd2'
        )

    def send_goal(self, target_distance, step_distance):
        self.get_logger().info('액션 서버 대기')
        self.act_cli2.wait_for_server()

        goal_msg = MyAction4.Goal()
        goal_msg.target_distance = target_distance
        goal_msg.step_distance = step_distance

        self.get_logger().info(
            f'목표: {target_distance:.1f}cm, '
            f'이동 단위 {step_distance:.1f}cm'
        )

        self.goal_future = self.act_cli2.send_goal_async(
            goal_msg,
            feedback_callback = self.feedback_callback1
        )

        self.goal_future.add_done_callback(
            self.goal_response_callback
        )

    def goal_response_callback(self, future):
        goal_handle = future.result() # 수락 여부

        if not goal_handle.accepted:
            self.get_logger().info('Goal 거절됨')
            rclpy.shutdown()
            return

        self.get_logger().info('Goal 수락됨')
        self.result_future = goal_handle.get_result_async()
        self.result_future.add_done_callback(
            self.result_callback
        )

    def feedback_callback1(self, feedback_msg):
        feedback = feedback_msg.feedback
        self.get_logger().info(
            f'Feedback: 현재 거리 = {feedback.current_distance:.1f}cm, '
            f'남은 거리 = {feedback.remaining_distance:.1f}cm'
        )

    def result_callback(self, future):
        result_resp = future.result()
        result = result_resp.result
        status = result_resp.status

        if status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info(
                f'Result: 최종 거리 = {result.final_distance:.1f}cm, '
            )
        elif status == GoalStatus.STATUS_ABORTED:
            self.get_logger().info(
                '잘못된 Goal로 액션이 불가능'
            )
        else:
            self.get_logger().info(f'액션 종료 상태: {status}')
        rclpy.shutdown()

def main(args=None):
    rclpy.init(args=args)

    node1 = ConvetorActCli2()
    node1.send_goal(100.0, 10.0)

    rclpy.spin(node1)

    node1.destroy_node()

if __name__ == '__main__':
    main()