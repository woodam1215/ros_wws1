# 기본 카운팅 하기
import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer
from interface_pkg1.action import Myaction1
import time

class MyActServ1(Node):
    def __init__(self):
        super().__init__('act_srv1_node')
        self.act_srvr1 = ActionServer(
            self,
            Myaction1,
            'action_cmd1',
            self.execute_callback
        )

        self.get_logger().info("액션 서버 시작")
        
    def execute_callback(self, goal_handle):
        # 콜백 수락 = 요청 수락 = 그 작업에 대한 서버용 콜백을 지정 
        # -> goal 받기
        target_num = goal_handle.request.target_num

        self.get_logger().info(f'목표값(Goal) 추천: {target_num}')

        # Feedback 메시지 객체 생성
        feedback_msg = Myaction1.Feedback()

        # 1부터 목표값까지 카운팅
        total = 0
        for i in range(1, target_num+1):
            # 서버의 계산값
            total += i
            # 현재 진행 상태값
            feedback_msg.current_num = i

            # feedback 전송 
            goal_handle.publish_feedback(feedback_msg)
            self.get_logger().info(f'피드백 전송: {i}')

            # 1초씩 대기
            time.sleep(1.0)

        # Goal 완료 처리
        goal_handle.succeed()

        # Result 메시지 생성
        result_msg = Myaction1.Result()
        result_msg.result_num = total

        return result_msg

def main(args=None):
    rclpy.init(args=args)

    node1 = MyActServ1()
    rclpy.spin(node1)

    node1.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()