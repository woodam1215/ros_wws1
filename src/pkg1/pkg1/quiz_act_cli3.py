# Turtlesim 원 그리기 액션 클라이언트

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from action_msgs.msg import GoalStatus

from interface_pkg1.action import QuizAction1


class CircleActCli1(Node):
    def __init__(self):
        super().__init__('circle_act_cli_node1')

        # Action Client 생성
        self.act_cli = ActionClient(
            self,
            QuizAction1,
            'draw_circle_cmd1'
        )

    def send_goal(self, radius, turns):

        # Action Server 준비 대기
        self.act_cli.wait_for_server()

        # Goal 메시지 생성
        goal_msg = QuizAction1.Goal()

        goal_msg.radius = radius
        goal_msg.turns = turns

        self.get_logger().info(
            f'Goal 전송: '
            f'반지름={radius:.2f}m, '
            f'{turns}바퀴'
        )

        # [Future 1]
        # Goal 전송 후 수락/거절 응답 기다림
        self.goal_future = \
            self.act_cli.send_goal_async(
                goal_msg,
                feedback_callback=self.feedback_callback
            )

        self.goal_future.add_done_callback(
            self.goal_response_callback
        )

    def goal_response_callback(self, future):

        # ClientGoalHandle 받기
        cli_goal_handle = future.result()

        # Goal 수락 여부 확인
        if not cli_goal_handle.accepted:
            self.get_logger().info(
                'Goal 거절됨'
            )
            rclpy.shutdown()
            return

        self.get_logger().info(
            'Goal 승인됨'
        )

        # [Future 2]
        # 최종 Result 요청
        self.result_future = \
            cli_goal_handle.get_result_async()

        self.result_future.add_done_callback(
            self.result_callback
        )

    def feedback_callback(self, feedback_msg):

        # 실제 Feedback 메시지
        feedback = feedback_msg.feedback

        self.get_logger().info(
            f'진행률: {feedback.progress:.1f}%, '
            f'누적각도: '
            f'{feedback.current_angle:.2f} rad'
        )

    def result_callback(self, future):

        # 최종 Action 응답
        result_response = future.result()

        # 실제 Result
        result_final = result_response.result

        # Action 상태
        status_final = result_response.status

        self.get_logger().info(
            f'완료한 바퀴: '
            f'{result_final.completed_turns}'
        )

        self.get_logger().info(
            f'최종 위치: '
            f'x={result_final.final_x:.2f}, '
            f'y={result_final.final_y:.2f}'
        )

        if status_final == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info(
                '결과 상태: SUCCEEDED'
            )

        elif status_final == GoalStatus.STATUS_ABORTED:
            self.get_logger().info(
                '결과 상태: ABORTED'
            )

        elif status_final == GoalStatus.STATUS_CANCELED:
            self.get_logger().info(
                '결과 상태: CANCELED'
            )

        else:
            self.get_logger().info(
                f'결과 상태: {status_final}'
            )

        # 1회성 Client이므로 종료
        rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)

    node1 = CircleActCli1()

    # 반지름 2m, 1바퀴
    node1.send_goal(
        radius=2.0,
        turns=1
    )

    rclpy.spin(node1)

    node1.destroy_node()


if __name__ == '__main__':
    main()