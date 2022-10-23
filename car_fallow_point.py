import math
import pygame
BLACK =(0,0,0,255)
WHITE =(255,255,255,255)
RED = (255,0,0,255)
BLUE = (0,0,255,255)
GREEN = (0,255,0,255)
W,H =600,600
car_shift = 100,100
HW,HH =(W/2)+car_shift[0],(H/2)+car_shift[1]
AREA = W * H
class Car:
    def __init__(self,screen,map):
        self.map = map
        self.screen  = screen
        self.destination =[]
        self.source =[]
        self.front_radars =[]
        self.back_radars = []
        self.radars =[]
        self.radar = HW,HH
        self.angle_count = 0
        self.dx,self.dy = 0,0
        self.distance = 0
        self.speed = self.calculated_speed = 1
        self.surface = pygame.image.load("car.png")
        self.rotate_surface = self.surface = pygame.transform.scale(self.surface, (50, 50))
        self.rect = self.rotate_surface.get_rect()  
        self.rect.center = self.source = self.destination = self.x,self.y = HW,HH 
        self.angle_of_rotation = self.current_angle = self.new_angle = self.rot_angle = 0 
        self.rotation_speed = 1    
        self.brakes = False
        self.radar_length = self.max_radar = 100
    def rot_center(self,image, angle):
        orig_rect = image.get_rect()
        rot_image = pygame.transform.rotate(image, angle)
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        rot_image = rot_image.subsurface(rot_rect).copy()
        return rot_image
    def draw_Car(self): 
        # pygame.draw.rect(self.screen,(255,0,0),self.rect)
        self.screen.blit(self.rotate_surface, self.rect)   
        # pygame.draw.line(self.screen,(255,0,0),self.rect.center, self.destination, 1)
        pygame.draw.circle(self.screen,BLUE,self.destination,9,0)
        pygame.draw.circle(self.screen,GREEN,self.rect.center,5,0)
        # pygame.draw.circle(self.screen,BLUE,self.radar,2,0) 
        # pygame.draw.line(self.screen,(0,255,0),self.rect.center, self.radar, 1)
        self.draw_radar()
    def update_map(self,map):
        self.map = map
    def update_radars(self,front=1,back=1):
        if front == 1:
            self.front_radars.clear()
            for degree in [-45,0,45]:
                self.check_radars(degree,200,1)
            self.back_radars.clear()
        else:
            self.front_radars.clear()
        if back == 1:    
            self.back_radars.clear()
            for degree in [135,-135]:
                self.check_radars(degree,100,-1)
        else:
            self.back_radars.clear()
    def turn_radar_off(self,radar_type):
            if radar_type == 1:
                self.front_radars.clear()
            elif radar_type == -1:
                self.back_radars.clear()
    def check_radars(self,degree = 0, radar_length = 100,radar_type=0):
        self.max_radar = radar_length
        self.radar_length = 0
        radian =math.radians(self.rotation_speed - self.current_angle + degree)
        dx,dy = int(math.cos(radian) * self.radar_length),int(math.sin(radian) * self.radar_length)
        self.radar = x,y = self.rect.center[0] + dx, self.rect.center[1] + dy
        while self.map.get_at((x, y)) == BLACK and self.radar_length < self.max_radar:
            self.radar_length += 1
            radian =math.radians(self.rotation_speed - self.current_angle + degree)
            dx,dy = int(math.cos(radian) * self.radar_length),int(math.sin(radian) * self.radar_length)
            self.radar = x,y = self.rect.center[0] + dx, self.rect.center[1] + dy            
        radar_distance = int(math.hypot(x - self.rect.center[0],y - self.rect.center[1]))  
        # self.radars.append([(x,y),radar_distance])
        if radar_type == -1:
            self.back_radars.append([(x,y),radar_distance])
        elif radar_type == 1:
            self.front_radars.append([(x,y),radar_distance])

    def draw_radar(self):
        self.update_radars()
        for r in self.front_radars:
            pos = r[0]
            if r[1] < 50:color = RED
            else : color = GREEN
            pygame.draw.line(self.screen, color, self.rect.center, pos, 1)
            pygame.draw.circle(self.screen, color, pos, 5)  
        for r in self.back_radars:
            pos = r[0]
            if r[1] < 50:color = RED
            else : color = BLUE
            pygame.draw.line(self.screen, color, self.rect.center, pos, 1)
            pygame.draw.circle(self.screen, color, pos, 5)  
  
    def get_max_back_destination(self):  
        # self.update_radars()
        back_radar_distances = [i[1] for i in self.back_radars]
        back_destination = self.back_radars[back_radar_distances.index(max(back_radar_distances))][0] 
        
        return [back_destination,max(back_radar_distances)]
    def get_destination(self):
        front_radar_distances = [i[1] for i in self.front_radars]
        max_back_destination,max_back_distance = self.get_max_back_destination()
        # print(max_back_distance,max(front_radar_distances))
        if front_radar_distances[1] == max(front_radar_distances):
            destination = self.front_radars[1][0]
        elif max(front_radar_distances) < 50 :#max_back_distance:
            destination = self.rect.center#max_back_destination
            self.brake_car()
        else:
            destination = self.front_radars[front_radar_distances.index(max(front_radar_distances))][0] 

        return destination
    def calculate_directions(self): 
        if self.distance == 0 and self.angle_of_rotation == 0 :
            self.distance = int(math.hypot(self.destination[0] - self.source[0],self.destination[1] - self.source[1])/self.speed)  
            
            radians =math.atan2(self.destination[1] - self.source[1],self.destination[0] - self.source[0])
            self.dx = math.cos(radians)*self.speed
            self.dy = math.sin(radians)*self.speed
            
            # self.new_angle = self.rot_angle = int(math.degrees(math.atan2(-(self.destination[1] - self.rect.center[1]), self.destination[0] - self.rect.center[0])))
            self.new_angle = int(math.degrees(math.atan2(-(self.destination[1] - self.source[1]), self.destination[0] - self.source[0])))
            
            self.angle_of_rotation = (self.new_angle - self.current_angle) % 360             
            if abs(self.angle_of_rotation) > 180:
                self.angle_of_rotation = (self.angle_of_rotation - 180) * -int(self.angle_of_rotation/abs(self.angle_of_rotation))

            self.angle_of_rotation = (self.new_angle - self.current_angle) % 180
            if abs(self.angle_of_rotation) > abs(abs(self.angle_of_rotation) - 180):
                self.angle_of_rotation = int(abs(abs(self.angle_of_rotation) - 180) * -(abs(self.angle_of_rotation)/self.angle_of_rotation))

    def rotate_car(self):
        if not self.distance == 0 :
            self.calculate_rotation_speed()
            self.current_angle += self.rotation_speed
            self.angle_of_rotation -= self.rotation_speed
            self.rotate_surface = self.rot_center(self.surface,self.current_angle)         
    def calculate_rotation_speed(self):
        speeds = []
        if self.angle_of_rotation == 0:
            self.rotation_speed = 0
        else:
            for i in range(1,abs(int(self.angle_of_rotation))+1,1):
                if abs(self.angle_of_rotation)%i == 0:
                    speeds.append(self.angle_of_rotation/i)
            if(len(speeds)>0):
                self.rotation_speed = int(speeds.pop(int((len(speeds))/2))) 
    def calculate_speed(self):
        speeds = []
        if self.distance == 0:
            self.calculated_speed = 0
        else:
            for i in range(1,abs(self.distance)+1,1):
                if abs(self.distance)%i == 0:
                    speeds.append(self.distance/i)
            if(len(speeds)>0):
                self.calculated_speed = max(int(speeds.pop(int((len(speeds))/2))),self.speed)              
    def move_car_to_point(self):
        if not self.distance == 0 and self.angle_of_rotation == 0 :  
            self.calculate_speed()     
            self.distance -= self.calculated_speed
            self.x += self.dx * self.calculated_speed
            self.y += self.dy * self.calculated_speed
            self.rect.center = self.source = (self.x,self.y)
    def brake_car(self):
        self.destination = self.rect.center
        self.distance = self.angle_of_rotation = 0
    def movecar(self):
        self.calculate_directions()
        self.rotate_car()
        self.move_car_to_point()
        self.brake_car()
    def move_to_point(self,point = None ):
        if point == None or point == self.rect.center:
            self.brake_car()
            return
        self.destination = point 
        self.movecar()     
def events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            
pygame.init()
CLOCK = pygame.time.Clock()
DS = pygame.display.set_mode((W,H))
pygame.display.set_caption("distance and direction")
map = pygame.image.load('map2.png')
FPS = 120
car = Car(DS,map)
points =[]
point = HW,HH
click = True
while True :
    events()
    map = pygame.image.load('map2.png')
    DS.blit(map, (0, 0))
    m =pygame.mouse.get_pressed()
    
    if m[2]:
        point = car.get_destination()
    elif m[0] :
        point = pygame.mouse.get_pos()
    car.move_to_point(point)
    car.draw_Car()
    car.update_map(map)
    pygame.display.update()
    CLOCK.tick(FPS)
    DS.fill(BLACK)