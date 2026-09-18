import rclpy
from rclpy.node import Node

class parameter(Node):
    def __init__(self):
        super().__init__('para_setter_node1')
        self.declare_parameter('my_para1', 'dam')
        self.timer = self.create_timer(
            1, 
            self.timer_callback
        )

    def timer_callback(self):
        my_p = self.get_parameter('my_para1').get_parameter_value().string_value

        self.get_logger().info(f'안농 {my_p}')

        my_new_p = rclpy.parameter.Parameter(
            'my_para1',
            rclpy.Parameter.Type.STRING,
            'world'
        )

        #all_new_p = (my_new_p)
        self.set_parameters([my_new_p])

def main():
    rclpy.init()

    node1 = parameter()
    rclpy.spin(node1)

if __name__ == '__main__':
    main()
