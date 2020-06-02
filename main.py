import pygame
import math
import engine3d

win_width = 800
win_height = 500
win = pygame.display.set_mode((win_width,win_height))

################################################################################ Setup

#get points and joint
file = open("cell120vertex.txt",'r')
points = []
for line in file:
	index, x, y, z, w = line.split()
	points.append((float(x),float(y),float(z),float(w)))
file.close()

file = open("cell120joint.txt", 'r')
joints = []
for line in file:
	pack = line.split()
	for p in pack:
		vertex, numbers = p.split("(")
		numbers = numbers[:-1]
		n1s, n2s, n3s, n4s = numbers.split(",")
		n1, n2, n3, n4 = int(n1s), int(n2s), int(n3s), int(n4s)
		joints.append((int(vertex), n1, n2, n3, n4))
file.close()

# 4d transforms:
a_zw = 0

def rot_zw(vec):
	x = vec[0]
	y = vec[1]
	z = vec[2]*math.sin(a_zw) - vec[3]*math.cos(a_zw)
	w = vec[2]*math.cos(a_zw) + vec[3]*math.sin(a_zw)
	return (x,y,z,w)

d = 2
def param4d(vec):
	vec = rot_zw(vec)
	x = vec[0]
	y = vec[1]
	z = vec[2]
	w = vec[3]
	return (12*x/(d+w), 12*y/(d+w), 12*z/(d+w))
	
def draw_joint(joint):
	index = joint[0]
	n1, n2, n3, n4 = joint[1], joint[2], joint[3], joint[4]
	engine3d.draw_path([param4d(points[index-1]), param4d(points[n1-1])], (0,106,200))
	engine3d.draw_path([param4d(points[index-1]), param4d(points[n2-1])], (0,106,200))
	engine3d.draw_path([param4d(points[index-1]), param4d(points[n3-1])], (0,106,200))
	engine3d.draw_path([param4d(points[index-1]), param4d(points[n4-1])], (0,106,200))

################################################################################ Main Loop:

run = True
while run:
	#pygame.time.delay(1)
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False
		engine3d.mouse_event_check(event)
		if event.type == pygame.KEYDOWN:
			#key pressed once:
			if event.key == pygame.K_p:
				d += 0.1
			if event.key == pygame.K_o:
				d -= 0.1
	keys = pygame.key.get_pressed()
	if keys[pygame.K_ESCAPE]:
		run = False
	if keys[pygame.K_KP7]:
		a_zw += 0.05
	if keys[pygame.K_KP9]:
		a_zw -= 0.05
	#background:
	win.fill((0,0,0))
	engine3d.mouse_hold_check()
	engine3d.update_vecs()
	
	#step:
	engine3d.draw_axis()
	for j in joints:
		draw_joint(j)
	for p in points:
		engine3d.draw_point(param4d(p), (106,200,0))
	
	
	# engine3d.draw_point(param4d(points[1]),(255,255,0))
	# engine3d.draw_path([param4d(points[polygon[0]]), param4d(points[polygon[1]]), param4d(points[polygon[2]]), param4d(points[polygon[3]]), param4d(points[polygon[4]])], (255,0,0))
	
	pygame.display.update()
pygame.quit()
