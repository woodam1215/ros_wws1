# act_thread_srvr4.py
# Action + MultiThread + Dynamic Parameter + Turtlesim

import math
import time

import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup

from geometry_msgs.msg import Twist
from turtlesim.msg import Pose

from rcl_interfaces.msg import (
    SetParametersResult,
    ParameterDescriptor,
    FloatingPointRange
)

from interface_pkg1.action import ParaAction1


class DistSrvr4(Node):

    def __init__(self):
        super().__init__('act_srvr_node4')

        # ----------------------------------------
        # 1. 멀티스레드 Callback Group
        # ----------------------------------------
        self.callback_group = ReentrantCallbackGroup()

        # ----------------------------------------
        # 2. 거북이 위치 관련 변수
        # ----------------------------------------
        self.current_pose = None

        self.previous_x = 0.0
        self.previous_y = 0.0
        self.is_first_time = True

        self.total_dist = 0.0

        # ========================================
        # 3. Dynamic Parameter
        # ========================================

        # quantile_time
        # 제어 루프 실행 간격
        quantile_desc = ParameterDescriptor(
            description='Action control loop period',
            floating_point_range=[
                FloatingPointRange(
                    from_value=0.01,
                    to_value=1.0,
                    step=0.01
                )
            ]
        )

        # near_goal_dist
        # 실제로는 목표까지 남은 거리의 기준값
        near_goal_desc = ParameterDescriptor(
            description='Stop distance before goal',
            floating_point_range=[
                FloatingPointRange(
                    from_value=0.05,
                    to_value=2.0,
                    step=0.05
                )
            ]
        )

        self.declare_parameter(
            'quantile_time',
            0.1,
            quantile_desc
        )

        self.declare_parameter(
            'near_goal_dist',
            0.2,
            near_goal_desc
        )

        # 최초 Parameter 값 읽기
        self.quantile_time = (
            self.get_parameter(
                'quantile_time'
            ).value
        )

        self.near_goal_dist = (
            self.get_parameter(
                'near_goal_dist'
            ).value
        )

        # Parameter 변경 Callback 등록
        self.add_on_set_parameters_callback(
            self.param_callback
        )

        # ========================================
        # 4. Pose Subscriber
        # ========================================

        self.pose_sub = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            10,
            callback_group=self.callback_group
        )

        # ========================================
        # 5. cmd_vel Publisher
        # ========================================

        self.cmd_pub = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            10
        )

        # ========================================
        # 6. Action Server
        # ========================================

        self.action_server = ActionServer(
            self,
            ParaAction1,
            'dist_action4',
            self.execute_callback,
            callback_group=self.callback_group
        )

        self.get_logger().info(
            'Action Server + Dynamic Parameter 시작'
        )

        self.get_logger().info(
            f'quantile_time = {self.quantile_time}'
        )

        self.get_logger().info(
            f'near_goal_dist = {self.near_goal_dist}'
        )

    # ============================================
    # Parameter 변경 Callback
    # ============================================

    def param_callback(self, params):

        for param in params:

            if param.name == 'quantile_time':

                if param.value <= 0.0:
                    return SetParametersResult(
                        successful=False,
                        reason='quantile_time은 0보다 커야 합니다.'
                    )

                self.quantile_time = param.value

                self.get_logger().info(
                    f'quantile_time 변경: '
                    f'{self.quantile_time:.2f}'
                )

            elif param.name == 'near_goal_dist':

                if param.value <= 0.0:
                    return SetParametersResult(
                        successful=False,
                        reason='near_goal_dist은 0보다 커야 합니다.'
                    )

                self.near_goal_dist = param.value

                self.get_logger().info(
                    f'near_goal_dist 변경: '
                    f'{self.near_goal_dist:.2f}'
                )

        return SetParametersResult(
            successful=True
        )

    # ============================================
    # Pose Subscriber Callback
    # ============================================

    def pose_callback(self, msg):

        self.current_pose = msg

    # ============================================
    # 이동 거리 계산
    # ============================================

    def calc_diff_pose(self):

        if self.current_pose is None:
            return 0.0

        # 최초 한 번
        if self.is_first_time:

            self.previous_x = self.current_pose.x
            self.previous_y = self.current_pose.y

            self.is_first_time = False

            return 0.0

        dx = (
            self.current_pose.x
            - self.previous_x
        )

        dy = (
            self.current_pose.y
            - self.previous_y
        )

        diff_dist = math.sqrt(
            dx ** 2 + dy ** 2
        )

        # 현재 위치를 다음 계산의 이전 위치로 저장
        self.previous_x = self.current_pose.x
        self.previous_y = self.current_pose.y

        return diff_dist

    # ============================================
    # 거북이 정지
    # ============================================

    def stop(self):

        msg = Twist()

        msg.linear.x = 0.0
        msg.angular.z = 0.0

        self.cmd_pub.publish(msg)

        self.get_logger().info(
            '거북이 정지'
        )

    # ============================================
    # Action Execute Callback
    # ============================================

    def execute_callback(self, goal_handle):

        self.get_logger().info(
            'Action Goal 수신'
        )

        # Pose를 아직 받지 못했다면 잠깐 기다림
        while (
            self.current_pose is None
            and rclpy.ok()
        ):
            time.sleep(0.05)

        # 새로운 Action을 위한 초기화
        self.total_dist = 0.0
        self.is_first_time = True

        feedback_msg = ParaAction1.Feedback()

        # Goal 값으로 이동속도 생성
        move_msg = Twist()

        move_msg.linear.x = (
            goal_handle.request.linear_x
        )

        move_msg.angular.z = (
            goal_handle.request.angular_z
        )

        target_dist = (
            goal_handle.request.dist
        )

        self.get_logger().info(
            f'목표 거리: {target_dist:.2f}'
        )

        # ========================================
        # 이동 시작
        # ========================================

        while rclpy.ok():

            # 취소 요청 확인
            if goal_handle.is_cancel_requested:

                self.stop()

                goal_handle.canceled()

                result = ParaAction1.Result()

                result.pose_x = self.current_pose.x
                result.pose_y = self.current_pose.y
                result.pose_theta = self.current_pose.theta
                result.result_dist = self.total_dist

                return result

            # ------------------------------------
            # 거북이 움직이기
            # ------------------------------------

            self.cmd_pub.publish(
                move_msg
            )

            # ★ Dynamic Parameter 사용
            time.sleep(
                self.quantile_time
            )

            # ------------------------------------
            # 실제 이동 거리 계산
            # ------------------------------------

            self.total_dist += (
                self.calc_diff_pose()
            )

            remaining_dist = (
                target_dist
                - self.total_dist
            )

            # Feedback 작성
            feedback_msg.remaining_dist = (
                max(
                    0.0,
                    remaining_dist
                )
            )

            goal_handle.publish_feedback(
                feedback_msg
            )

            self.get_logger().info(
                f'이동 거리: '
                f'{self.total_dist:.2f}, '
                f'남은 거리: '
                f'{remaining_dist:.2f}'
            )

            # ====================================
            # ★ Dynamic Parameter 실제 사용
            # ====================================

            if (
                remaining_dist
                <= self.near_goal_dist
            ):

                self.get_logger().info(
                    '목표 지점 근접 → 정지'
                )

                break

        # ========================================
        # 반드시 정지
        # ========================================

        self.stop()

        # Action 성공
        goal_handle.succeed()

        # Result
        result = ParaAction1.Result()

        result.pose_x = self.current_pose.x
        result.pose_y = self.current_pose.y
        result.pose_theta = self.current_pose.theta
        result.result_dist = self.total_dist

        self.get_logger().info(
            f'최종 이동 거리: '
            f'{self.total_dist:.2f}'
        )

        return result


# ================================================
# main
# ================================================

def main(args=None):

    rclpy.init(args=args)

    node = DistSrvr4()

    # Action 실행 중에도 Pose Callback,
    # Parameter Callback 실행 가능
    executor = MultiThreadedExecutor(
        num_threads=4
    )

    executor.add_node(node)

    try:

        executor.spin()

    except KeyboardInterrupt:

        pass

    finally:

        # 종료 시 거북이 정지
        node.stop()

        executor.shutdown()

        node.destroy_node()

        rclpy.shutdown()


if __name__ == '__main__':
    main()