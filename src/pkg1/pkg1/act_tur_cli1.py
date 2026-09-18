# 터틀 직선 이동
# 주의: 거북이가 벽에 부딪히면 거리가 줄지 않아 무한 루프에 빠짐
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from action_msgs.msg import GoalStatus
from interface_pkg1.action import Myaction2

class TurActCli1(Node):
    def __init__(self):
        super().__init__('tur_act_cli1_node')

        # 액션 클라 생성
        self.act_cli1 = ActionClient(
            self,
            Myaction2,
            'act_order1'
        )

    def send_goal(self, target_dist):
        # Action server 준비될 때까지 대기
        self.act_cli1.wait_for_server()

        # Goal 메시지 생성
        goal_msg = Myaction2.Goal()
        goal_msg.target_dist = target_dist

        self.get_logger().info(
            f'Goal 전송: {target_dist:.2f}m 이동'
        )

        # [future1: send_goal_async()로 생성]
        # goal 전송 후 수락/거절 응답 기다림
        self.goal_future = self.act_cli1.send_goal_async(
            goal_msg,
            feedback_callback= self.feedback_callback
        )

        self.goal_future.add_done_callback(
            self.goal_response_callback
        )

    def goal_response_callback(self, future):
        # Goal 응답에서 clientgoalhandle 받기
        cli_goal_handle = future.result()

        # goal 수락 여부 판별 확인
        if not cli_goal_handle.accepted:
            self.get_logger().info('골 거절됨')
            rclpy.shutdown()
            return

        self.get_logger().info('골 수락됨')

        # future2: get_result_async() 생성
        # ClientGoalHandle을 통해 최종 결과물 실행함
        self.result_future = cli_goal_handle.get_result_async()

        self.result_future.add_done_callback(
            self.result_callback
        )


    def feedback_callback(self, feedback_msg):
        # 실제 피드백 메시지를 꺼내기
        fb1 = feedback_msg.feedback

        self.get_logger().info(
            f'남은 거리: {fb1.remaining_dist:.2f}m'
        )

    # 두 번째 future 가 정해준 콜백
    def result_callback(self, future):
        # 최종 액션 응답
        result_resp = future.result()

        # 실제 result 메시지 꺼내기
        ## final_x, final_y, result_dist
        result_final = result_resp.result
        ## 0: UNKNOWN, 1: ACCEPTED 2: EXECUTING 3: CANCELING
        ## 4: SUCCEEDED 5: CANCELED 6: ABORTED 
        status_final = result_resp.status

        self.get_logger().info(
            f'실제 이동 거리: {result_final.result_dist:.2f}m'
        )

        self.get_logger().info(
            f'최종 위치: '
            f'x= {result_final.final_x:.2f}, '
            f'y= {result_final.final_y:.2f}'
        )

        self.get_logger().info(
            f'결과 생태: {status_final}'
        )

        # 일회성 클라이언트는 result_final을 받은 뒤 종료
        rclpy.shutdown()

def main(args=None):
    rclpy.init(args=args)

    node1 = TurActCli1()

    # 3m 이동 goal 전송
    node1.send_goal(3.0)

    rclpy.spin(node1)

    node1.destroy_node()

if __name__ =='__main__':
    main()