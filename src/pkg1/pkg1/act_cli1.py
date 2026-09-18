#  기본 카운팅하기
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from interface_pkg1.action import Myaction1

class Myactcli1(Node):
    def __init__(self):
        super().__init__('act_cli1_node')

        # 액션 클라이언트 생성
        self.act_cli1 = ActionClient(
            self,
            Myaction1,
            'action_cmd1'
        )

    def send_goal(self, target_num):
        # 액션 서버가 준비 될 때까지 대기 
        self.act_cli1.wait_for_server()

        # 목표값 (goal) 생성
        goal_msg = Myaction1.Goal()
        goal_msg.target_num = target_num

        # [1단계 future] 목표 값 (Goal)을 전송하고 수락/거절 응답용 future에 발동
        self.get_logger().info(f'목표값 전송: {target_num}')
        self.future1 = self.act_cli1.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback1
        )

        # Goal 응답이 오면 실행할 콜백 함수 지정
        self.future1.add_done_callback(self.resp_callback)

    def resp_callback(self, future):
        # 클라용 Goal Handle 객체 생성
        ## cli_goal_handle.accepted
        ## cli_goal_handle.get_result_async()
        ## cli_goal_handle.cancel_goal_async()

        cli_goal_handle = future.result()

        if not cli_goal_handle.accepted:
            self.get_logger().info('Goal 거절됨')
            return
        self.get_logger().info(f'goal 승인됨')

        # [2단계 future] 이제 이번 goal의 최종 결과를 요청함
        self.result_future2 = cli_goal_handle.get_result_async()
        # future2는 cli_goal_handle.get_result_async로 간다 

        self.result_future2.add_done_callback(
            self.result_callback # 이것은 어떻게 만들어지냐하면 future2로 간다
        )

    def feedback_callback1(self, feedback_msg):
        # feedbackMessage 안에서 실제 feedback 데이터 꺼내기
        feedback = feedback_msg.feedback

        self.get_logger().info(
            f'현재 카운트: {feedback.current_num}'
        )


    def result_callback(self, future):
        # [3단계] 2단계 result_future2로 응답이 들어오면
        # future를 인자로 전달받아서 future.result()로
        # 최종 액션 결과 응답 수령

        result_resp = future.result()

        # result_response 객체 안에 있는 데이터 꺼내기 
        result = result_resp.result 
        success = result_resp.status

        self.get_logger().info(
            f'합계: {result.result_num}, 결과판정: {success}'
        )

        rclpy.shutdown()

        # 클라는 결과를 받으면 종료하도록 여기서 바로 shutdown 한다
        # 반면, 서버는 다른 goal도 받아야 하므로 종료하지 않고 on 유지
 
def main(args=None):
    rclpy.init(args=args)

    node1 = Myactcli1()
    node1.send_goal(7)
    rclpy.spin(node1)

    node1.destroy_node()

if __name__ == '__main__':
    main()