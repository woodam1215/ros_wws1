# 가상의 컨베이어 벨트 이동하기
import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer
from interface_pkg1.action import MyAction4
import time

class conveyorActSrver(Node):
    def __init__(self):
        super().__init__('quiz_act_srvr_node2')

        # 액션 서버 생성
        self.act_srvr2 = ActionServer(
            self,
            MyAction4,
            'act_cmd2',
            self.execute_callback
        )

        self.get_logger().info('컨베이어 액션 시작')

    def execute_callback(self, goal_handle):
        target_distance = goal_handle.request.target_distance
        step_distance = goal_handle.request.step_distance
        self.get_logger().info(
            f'Goal 수신: target_distance = {target_distance:.1f} cm, '
            f'이동 단위: step_distance = {step_distance:.1f} cm'
        )

        # 잘못된 Goal이면 액션 중단
        if target_distance <= 0.0 or step_distance <= 0.0:
            self.get_logger().info(
                '목표 거리는 0보다 커야 함'
            )
            goal_handle.abort()

            result = MyAction4.result()
            result.final_distance = 0.0
            result.completed = False
            return result

        current_distance = 0.0
        feedback_msg = MyAction4.Feedback()

        while current_distance + target_distance:
            current_distance += step_distance

            if current_distance > target_distance:
                current_distance = target_distance

            remaining_distance = target_distance - current_distance

            feedback_msg.current_distance = current_distance
            feedback_msg.remaining_distance = remaining_distance

            goal_handle.publish_feedback(feedback_msg)

            self.get_logger().info(
                f'현재 거리: {current_distance:.1f}cm '
                f'남은 거리: {remaining_distance:.1f}cm'
            )
            time.sleep(0.5)

        goal_handle.succeed()

        result = MyAction4.Result()
        result.final_distance = current_distance 
        result.completed = True

        self.get_logger().info('컨베이어 이동 완료')
        return result

def main(args=None):
    rclpy.init(args=args)

    node1 = conveyorActSrver()
    rclpy.spin(node1)
    node1.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()