from pico2d import *

import random
import math
import game_framework
import game_world
import common
from behavior_tree import BehaviorTree, Action, Sequence, Condition, Selector


# zombie Run Speed
PIXEL_PER_METER = (10.0 / 0.3)  # 10 pixel 30 cm
RUN_SPEED_KMPH = 10.0  # Km / Hour
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

# zombie Action Speed
TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 10.0

animation_names = ['Walk', 'Idle']


class Zombie:
    images = None

    def load_images(self):
        if Zombie.images == None:
            Zombie.images = {}
            for name in animation_names:
                Zombie.images[name] = [load_image("./zombie/" + name + " (%d)" % i + ".png") for i in range(1, 11)]
            Zombie.font = load_font('ENCR10B.TTF', 40)
            Zombie.marker_image = load_image('hand_arrow.png')


    def __init__(self, x=None, y=None):
        self.x = x if x else random.randint(100, 1180)
        self.y = y if y else random.randint(100, 924)
        self.load_images()
        self.dir = 0.0      # radian 값으로 방향을 표시
        self.speed = 0.0
        self.frame = random.randint(0, 9)
        self.state = 'Idle'
        self.ball_count = 0


        self.tx, self.ty = 1000, 1000
        # 여기를 채우시오.

        self.patrol_points =[(43,274),(1118,274),(1050,494),(575,804),(235,991),(575, 804),(1050,494),(1118,274)]
        self.loc_no = 0
        self.build_behavior_tree()


    def get_bb(self):
        return self.x - 50, self.y - 50, self.x + 50, self.y + 50


    def update(self):
        self.frame = (self.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % FRAMES_PER_ACTION
        # fill here
        self.bt.run()

    def draw(self):
        if math.cos(self.dir) < 0:
            Zombie.images[self.state][int(self.frame)].composite_draw(0, 'h', self.x, self.y, 100, 100)
        else:
            Zombie.images[self.state][int(self.frame)].draw(self.x, self.y, 100, 100)
        self.font.draw(self.x - 10, self.y + 60, f'{self.ball_count}', (0, 0, 255))
        Zombie.marker_image.draw(self.tx+25, self.ty-25)
        draw_rectangle(*self.get_bb())
        draw_circle(self.x, self.y, int(PIXEL_PER_METER * 7), 255, 255, 0)


        draw_rectangle(*self.get_bb())

    def handle_event(self, event):
        pass

    def handle_collision(self, group, other):
        if group == 'zombie:ball':
            self.ball_count += 1


    def set_target_location(self, x=None, y=None):
        # 여기를 채우시오.
        if x in None or y is None:
            raise ValueError('목적지 좌표가 주어지지 않았습니다.')
        self.tx, self.ty = x, y
        return BehaviorTree.SUCCESS  # 목적지 좌표 설정 임무 완료
        pass



    def distance_less_than(self, x1, y1, x2, y2, r):
        # 여기를 채우시오.
        distance2 = (x1 - x2)**2 + (y1 - y2)**2
        return distance2 < (PIXEL_PER_METER * r)**2 # r은 미터 단위, PIXEL_PER_METER 곱해줘야




    def move_little_to(self, tx, ty):
        # 여기를 채우시오.
        # 스스로 유도할 수 있어야함.
        # 삼각형 공식 tan세타 = 높이/밑변
        self.dir = math.atan2(ty - self.y, tx - self.x)
        distance = game_framework.frame_time * RUN_SPEED_PPS
        self.x += distance * math.cos(self.dir)
        self.y += distance * math.sin(self.dir)
        return BehaviorTree.SUCCESS



    def move_to(self, r=0.5):
        # 여기를 채우시오.
        self.state = 'Walk'
        self.move_little_to(self.tx, self.ty)

        # 좀비가 목적지에 도착했는지 검사
        if self.distance_less_than(self.tx,self.ty,self.x,self.y,r):
            return BehaviorTree.SUCCESS # 목적지 도착 임무 완료
        else:
            return BehaviorTree.RUNNING # 아직 목적지 도착 전

        pass



    def set_random_location(self):
        # 여기를 채우시오.
        self.tx, self.ty = random.randint(100, 1180), random.randint(100, 924)
        return BehaviorTree.SUCCESS  # 목적지 좌표 설정 임무 완료

        pass

    # 원래 코드
    def if_boy_nearby(self, r):
        if self.distance_less_than(common.boy.x, common.boy.y, self.x, self.y, r):
            return BehaviorTree.SUCCESS
        else:
            return BehaviorTree.FAIL

    # 분리 -> 공이 더 많은지 적은지
    def if_boy_nearby_more(self, distance):
        if self.distance_less_than(common.boy.x, common.boy.y, self.x, self.y, distance) and \
                self.ball_count > common.boy.ball_count:
            return BehaviorTree.SUCCESS
        return BehaviorTree.FAIL

    def if_boy_nearby_less(self, distance):
        if self.distance_less_than(common.boy.x, common.boy.y, self.x, self.y, distance) and \
                self.ball_count < common.boy.ball_count:
            return BehaviorTree.SUCCESS
        return BehaviorTree.FAIL


    def move_away_from_boy(self, r=0.5):
        # 소년으로부터 반대 방향으로 이동. 충분히 멀어지면 SUCCESS
        self.state = 'Walk'
        # 소년으로부터 반대 방향
        self.dir = math.atan2(self.y - common.boy.y, self.x - common.boy.x)
        distance = RUN_SPEED_PPS * game_framework.frame_time
        self.x += distance * math.cos(self.dir)
        self.y += distance * math.sin(self.dir)
        # 소년과 충분히 떨어지면 완료
        if not self.distance_less_than(common.boy.x, common.boy.y, self.x, self.y, r):
            return BehaviorTree.SUCCESS
        return BehaviorTree.RUNNING


    def move_to_boy(self, r=0.5):
        # 여기를 채우시오.
        self.state = 'Walk'
        # 소년 쪽으로 살짝 이동
        self.move_little_to(common.boy.x, common.boy.y)
        # 좀비가 소년에게 도착했는지 검사
        if self.distance_less_than( common.boy.x, common.boy.y,self.x, self.y, r):
            return BehaviorTree.SUCCESS
        else:
            return BehaviorTree.RUNNING # 아직 소년한테 가지 않음.

        pass


    def get_patrol_location(self):
        # 여기를 채우시오.
        self.tx, self.ty = self.patrol_points[self.loc_no]
        self.loc_no = (self.loc_no + 1) % len(self.patrol_points)
        return BehaviorTree.SUCCESS



    def build_behavior_tree(self):
        # 여기를 채우시오.
        a1 = Action("목적지 설정",self.set_target_location, 80, 800)
        a2 = Action("목적지로 이동", self.move_to)
        root = move_to_target_location = Sequence('지정된 목적지로 이동',a1, a2)

        a3 = Action('랜덤 위치 설정', self.set_random_location)
        root = wander = Sequence('랜덤 위치로 이동', a3, a2)


        #c1 = Condition('소년이 근처에 있는가', self.if_boy_nearby, 7)
        #a4 = Action('소년 추적',self.move_to_boy)
        #chase_boy_if_nearby = Sequence('소년이 근처에 있으면 추적', c1, a4)

        c1 = Condition('소년 근처이고 공이 적은가', self.if_boy_nearby_less, 7)
        a4 = Action('소년에게서 도망', self.move_away_from_boy)
        run_away_less_ball = Sequence('도망', c1, a4)

        c2 = Condition('소년 근처이고 공이 많은가', self.if_boy_nearby_more, 7)
        a5 = Action('소년 추적', self.move_to_boy)
        chase_more_ball = Sequence('추적', c2, a5)

        #root = chase_or_wander = Selector('추적 아니면 배회', chase_boy_if_nearby, wander)

        a6 = Action('다음 순찰 위치 획득', self.get_patrol_location)
        patrol = Sequence('순찰', a6, a2)


        root = Selector('도망 또는 추적 혹은 배회', run_away_less_ball, chase_more_ball, wander)
        self.bt = BehaviorTree(root)


        pass


