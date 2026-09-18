from setuptools import find_packages, setup

package_name = 'param_pkg1'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='dam',
    maintainer_email='dam@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'param_setor1 = param_pkg1.param_setor1:main',
            'paran_pub1 = param_pkg1.paran_pub1:main',
            'paran_sub1 = param_pkg1.paran_sub1:main',
            'param_actsr1 = param_pkg1.param_actsr1:main',
        ],
    },
)
