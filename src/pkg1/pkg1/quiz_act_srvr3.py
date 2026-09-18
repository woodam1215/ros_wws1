# turtlesim 원 그리기 action 서버
import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from interface_pkg1.action import QuizAction1
import math, time

class CiActSrv1(Node):
    def __init__(self):
        super().__init__('circle_act_srvr_node1')

        # action 실행 중에도 pose_callback을 실행할 수 있도록 설정
        self.callback_group1 = ReentrantCallbackGroup()

        # 현재 터틀심의 포즈
        self.current_pose = None

        # 이전 theta 
        self.prev_theta = None

        # /turtle1/pose 구독 
        self.subber1 = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            10,
            callback_group=self.callback_group1
        )

        # /turtle1/cmd_vel 발행
        self.pubber1 = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            10,
            callback_group= self.callback_group1
        )

        # Action Server 생성
        self.act_srvr = ActionServer(
            self,
            QuizAction1,
            'draw_circle_cmd1',
            self.execute_callback,
            callback_group = self.callback_group1
        )

        self.get_logger().info(
            '원 그리기 액션 서비 시작'
        )

    def pose_callback(self, msg):
        # 터틀십의 현재 위치/속도 저장
        self.current_pose = msg

    def execute_callback(self, goal_handle):
        # client가 보낸 goal의 값
        radius = goal_handle.request_radius
        turns = goal_handle.request_turns

        self.get_logger().info(
            f'골 수신: 반지름={radius:.2f}m, '
            f'{turns:.2f}바퀴')

        # Pose가 아직 한번도 수신되지 않았다면 대기
        while self.current_pose is None:
            time.sleep(0.05)

        # 원 운동 속도 설정: v = r * w
        angular_speed = 0.5
        linear_speed = (radius * angular_speed)

        cmd_msg = Twist()
        cmd_msg.linear.x = linear_speed
        cmd_msg.angular.z = angular_speed

        # 총 목표 회전량
        target_angle = 2.0 * math.pi * turns
        # 누적 회전량
        total_angle = 0.0

        # 현재 theta 를  이전 theta로 저장
        self.prev_theta = self.current_pose.theta

        # Feedback 객체
        feedback_msg = QuizAction1.Feedback()

        # 목표 회전량 도달까지 계속 실행
        while total_angle < target_angle:
            # 거북이 이동 명령
            self.cmd_pubber1.publish(cmd_msg)

            # 현재 각도
            current_theta = self.current_pose.theta

            # 어떤 각도와 현재 각도의 차이
            delta_theta = (current_theta - self.prev_theta)

            # turtlesim thete가 -pi <=> +pi 경계를 넘을 때 보정
            if delta_theta > math.pi:
                delta_theta <= 2.0 * math.pi
            elif delta_theta < math.pi:
                delta_theta += 2.0 * math.pi

            # 실제 회전한 양을 누적
            total_angle += abs(delta_theta)

            # 현재 theta 저장
            self.prev_theta = current_theta

            # 진행률 계산
            progress = (total_angle / target_angle) *100.0

            # Feedback 데이터
            feedback_msg.progress = progress
            feedback_msg.current_angle = total_angle

            # Client Feedback 전송
            goal_handle.publish_feedback(
                feedback_msg
            )

            self.get_logger().info(
                f'진행률: {progress:.2f}%'
            )

            time.sleep(0.1)

        # 목표 완료 -> 거북이 정지
        stop_msg = Twist()
        # 디폴트가 0 이므로 값을 따로 설정하지 않고 보냄
        self.pubber1.publish(stop_msg) 

        # Goal 상태를 SUCCEEDED 로 설정
        goal_handle.succeed()

        # Result 작성
        result_msg = QuizAction1.Result()

        result_msg.completed_turns = turns
        result_msg.final_x = self.current_pose.x
        result_msg.final_y = self.current_pose.y

        self.get_logger().info(f'원 그리기 완료: {turns}바퀴')
        return

def main(args=None):
    rclpy.init(args=args)

    node1 = CiActSrv1()

    # execute_callback과 pose_callback을 
    # 동시에 처리할 수 있도록 MultiThreadedExecutor 사용
    executor = MultiThreadedExecutor()

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node1.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()