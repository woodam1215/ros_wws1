from setuptools import find_packages, setup

package_name = 'pkg1'

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
            'topic_pub_1 = pkg1.topic_pub_1:main',
            'topic_sub_1 = pkg1.topic_sub_1:main',
            'quizsrv1 = pkg1.quizsrv1:main',
            'quiz_cla1 = pkg1.quiz_cla1:main',
            'act_srvr1 = pkg1.act_srvr1:main',
            'act_cli1 = pkg1.act_cli1:main',
            'quiz_srvr2 = pkg1.quiz_srvr2:main',
            'quiz_cli2 = pkg1.quiz_cli2:main',
            'quiz_act_srvr1 = pkg1.quiz_act_srvr1:main',
            'quiz_act_cli1 = pkg1.quiz_act_cli1:main',
            'act_tur_srvr2 = pkg1.act_tur_srvr2:main',
            'act_tur_cli2 = pkg1.act_tur_cli2:main',
            'act_tur_srvr1 = pkg1.act_tur_srvr1:main',
            'act_tur_cli1 = pkg1.act_tur_cli1:main',
            'quiz_act_srvr3 = pkg1.quiz_act_srvr3:main',
            'quiz_act_cli3 = pkg1.quiz_act_cli3:main',
            'topic_squpub1 = pkg1.topic_squpub1:main',
            'topic_squsub1 = pkg1.topic_squsub1:main',
        ],
    },
)
