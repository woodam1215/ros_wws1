# 터틀 직선 이동
# 거북이 이동 (execute_callback()) + Pose 
# 콜백 /turtle1/Pose 퍼블리션 동시 실행:
# -> rclpy.spin() + time.sleep() -> Pose 막힐 수도 있다
# -> 멀티 스레드가 필요함(MultiThreaded execulor callbackgroups)
import time 
import math
import rclpy 
from rclpy.node import Node
from rclpy.action import ActionServer
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup

from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from interface_pkg1.action import Myaction2

class TurActsrv1(Node):
    def __init__(self):
        super().__init__("tur_act_srvr_node1")

        # Action 실행 중에도 Pose 콜백을 위한 설정
        # execute_callback의 while 실행 중 
        # -> Pose 를 갱신해야 거의 계산이 가능함
        # -> 여러 콜백을 한 그룹으로 묶어서 멀티스레드로 명령 실행해야 함
        self.callback_group1 = ReentrantCallbackGroup()

        # 현재 turtle 의 위치 
        self.current_pose = None

        # /turtle1/pose 구독자
        self.pose_subber = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            10,
            callback_group = self.callback_group1
        )

        # /turtle1/cmd_vel 발행자
        self.cmd_pubber = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            10
        )

        # Action Server 생성
        self.action_server = ActionServer(
            self,
            Myaction2,
            'act_order1',
            self.execute_callback,
            callback_group =self.callback_group1
        )

    def pose_callback(self, msg):
        # 현재 거북이 위치 지정
        self.current_pose = msg

    def execute_callback(self, goal_handle):
        # 클라가 요청하면 -> 수락 -> 그 job 에 대한 골렛을 배정
        target_dist = goal_handle.request.target_dist 

        self.get_logger().info(
            f'Goal 수신: {target_dist:.2f} m 이동'
        )

        # Pose 수신까지 대기
        while self.current_pose is None:
            time.sleep(0.1)

        # 시작 위치 지정 
        start_x = self.current_pose.x
        start_y = self.current_pose.y

        # Feedback 객체
        feedback_msg = Myaction2.Feedback()

        # 이동 명령: x 방향으로 1 m/s 씩 전진
        cmd_msg = Twist()
        cmd_msg.linear.x = 1.0
        cmd_msg.angular.z = 0.0

        moved_dist = 0.0

        while moved_dist < target_dist:
            # 거북이 전진 
            self.cmd_pubber.publish(cmd_msg)

            # 시작 위치에서 현재 위치까지 거리 계산
            dx = self.current_pose.x - start_x
            dy = self.current_pose.y - start_y

            moved_dist = math.sqrt(
                (dx **2)+(dy **2)
            )

            # 남은 거리 계산 
            remaining_dist = target_dist - moved_dist

            # Feedback 전송
            feedback_msg.remaining_dist = remaining_dist
            goal_handle.publish_feedback(feedback_msg)

            self.get_logger().info(
                f'이동 거리: {moved_dist:.2f}m, '
                f'남은 거리: {remaining_dist:.2f}m'
            )

            time.sleep(0.1)

        # 목표 거리에 도달하면 정지
        stop_msg = Twist()
        # 디폴트 linear.x/y/z, angular.x/y/z = 0.0
        self.cmd_pubber.publish(stop_msg) # 멈츰 

        # Goal 성공 상태로 변경
        goal_handle.succeed()

        # 최종 result 작성
        result_msg = Myaction2.Result()
        result_msg.result_dist = moved_dist
        result_msg.final_x = self.current_pose.x
        result_msg.final_y = self.current_pose.y

        self.get_logger().info(
            f'Goal 완료 실제 이동 거리: {moved_dist}'
        )

        return result_msg

def main(args=None):
    rclpy.init(args=args)

    node1 = TurActsrv1()

    executor = MultiThreadedExecutor()
    executor.add_node(node1)

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node1.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()