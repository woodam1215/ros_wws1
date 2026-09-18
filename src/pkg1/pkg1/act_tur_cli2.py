import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from interface_pkg1.action import Myaction5

class turactc(Node):
    def __init__(self):
        super().__init__('tur_act_cli2')
        self.cli = ActionClient(
            self,
            Myaction5,
            'tur_cmd1'
        )

    def send_goal(self, radius, turns):
        self.get_logger().info(
            '액션 서버 기다림'
        )

        self.cli.wait_for_server()

        goal_msg = Myaction5.Goal()

        goal_msg.radius = radius
        goal_msg.turns = turns

        self.get_logger().info(
            f'sending Goal: radius={radius}, turns={turns}'
        )

        future = self.cli.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )

        future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()

        if not goal_handle.accepted:
            self.get_logger().info('골 거절')
            return

        self.get_logger().info('골 수락')

        future = goal_handle.get_result_async()

        future.add_done_callback(
            self.result_callback
        )

    def feedback_callback(self, feedback_msg):
        feedback = feedback_msg.feedback
        self.get_logger().info(
            f'progress: {feedback.progress:.1f}%'
            f'angle: {feedback.angle:.1f} rad'
        )

    def result_callback(self, future):
        result = future.result().result

        self.get_logger().info(
            f'completed turns: {result.completed_turns}'
        )

        self.get_logger().info(
            f'final position: '
            f'x={result.final_x:.2f}, '
            f'y={result.final_y:.2f}'
        )

        rclpy.shutdown()

def main(args=None):
    rclpy.init(args=args)

    node1 = turactc()

    node1.send_goal(radius=2.0, turns=2)

    rclpy.spin(node1)

if __name__ == '__main__':
    main()