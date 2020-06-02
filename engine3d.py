import pygame
import math
import colorsys

##################################################################
##   3D WORLD ENGINE USING QUATERNIONS MADE BY SIMON LABUNSKY   ##
##################################################################

# screen settings
win_width = 800
win_height = 500
win = pygame.display.set_mode((win_width,win_height))

zoom = 1000
pos_x = win_width/2
pos_y = win_height/2
world_rot = (0,0,0,1)

light_vec = (1,1,1)
camera_vec = (0,0,100)

dot_radius = 2

################################################################################ Quaternion math
def quaternion_mul(q1, q2):
	x =  q1[0] * q2[3] + q1[1] * q2[2] - q1[2] * q2[1] + q1[3] * q2[0]
	y = -q1[0] * q2[2] + q1[1] * q2[3] + q1[2] * q2[0] + q1[3] * q2[1]
	z =  q1[0] * q2[1] - q1[1] * q2[0] + q1[2] * q2[3] + q1[3] * q2[2]
	w = -q1[0] * q2[0] - q1[1] * q2[1] - q1[2] * q2[2] + q1[3] * q2[3]
	return (x,y,z,w)
	
def quaternion_mul_unit(q1, q2):
	prod = quaternion_mul(q1, q2)
	size = math.sqrt(prod[0]**2 + prod[1]**2 + prod[2]**2 + prod[3]**2)
	x = prod[0]/size
	y = prod[1]/size
	z = prod[2]/size
	w = prod[3]/size
	return (x,y,z,w)
	
def quaternion_con_mul(vec, q1):
	q2 = (-q1[0], -q1[1], -q1[2], q1[3])
	vec_q = (vec[0], vec[1], vec[2], 0)
	a1 = quaternion_mul(q1, vec_q)
	a2 = quaternion_mul(a1, q2)
	return (a2[0], a2[1], a2[2])
	
def normalize_quaternion(q):
	size = math.sqrt(q[0]**2 + q[1]**2 + q[2]**2 + q[3]**2)
	if size == 0:
		return (0,0,0,0)
	x = q[0]/size
	y = q[1]/size
	z = q[2]/size
	w = q[3]/size
	return (x,y,z,w)
	
def normalize_vec(q):
	size = math.sqrt(q[0]**2 + q[1]**2 + q[2]**2)
	if size == 0:
		return (0,0,0)
	x = q[0]/size
	y = q[1]/size
	z = q[2]/size
	return (x,y,z)
	
def axis_from_quaternion(q):
	axis = normalize_vec((q[0], q[1], q[2]))
	return axis

def quaternion_from_axis_angle(axis, angle):
	qx = axis[0] * math.sin(angle/2)
	qy = axis[1] * math.sin(angle/2)
	qz = axis[2] * math.sin(angle/2)
	qw = math.cos(angle/2)
	return (qx, qy, qz, qw)
	
################################################################################ Transformation

def param(x,y,z):
	vec = quaternion_con_mul((x,y,z), world_rot)
	return ((zoom * vec[0])/(70-vec[2]) + pos_x,-( (zoom * vec[1])/(70-vec[2]) ) + pos_y)

################################################################################ Misc

def smap(value,a,b,c,d,clamped = False):
	ans = (value - a)/(b - a) * (d - c) + c
	if clamped:
		if ans > d:
			return d
		if ans < c:
			return c
	return (value - a)/(b - a) * (d - c) + c
	
def hsv2rgb(h,s,v):
	h/=100
	s/=100
	v/=100
	return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h,s,v))
	
def dist2view(point):
	return math.sqrt((point[0] - cam_vec[0])**2 + (point[1] - cam_vec[1])**2 + (point[2] - cam_vec[2])**2)
	
################################################################################ Drawing


def draw_point(pos, color, depth=False):
	pos_param = (int(param(pos[0], pos[1], pos[2])[0]), int(param(pos[0], pos[1], pos[2])[1]))
	if not depth:
		pygame.draw.circle(win, color, pos_param , dot_radius)
	else:
		dist = dist2view(pos)
		pygame.draw.circle(win, color, pos_param , int(max(1, smap(dist, 0,100,20,1))))

def draw_poly(p1, p2, p3, p4, color):
	vec1 = (p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2])
	vec2 = (p4[0] - p1[0], p4[1] - p1[1], p4[2] - p1[2])
	normal = (vec1[1]*vec2[2] - vec1[2]*vec2[1], -(vec1[0]*vec2[2] - vec1[2]*vec2[0]), vec1[0]*vec2[1] - vec1[1]*vec2[0])
	product = normal[0]*light_vec[0] + normal[1]*light_vec[1] + normal[2]*light_vec[2]
	
	color = hsv2rgb(color,smap(product,3,0,0,100,True),smap(product,0,3,50,100,True))
	pygame.draw.polygon(win, color, [param(p1[0],p1[1],p1[2]),param(p2[0],p2[1],p2[2]),param(p3[0],p3[1],p3[2]),param(p4[0],p4[1],p4[2])])

def draw_path(list, color):
	if len(list) == 1:
		list.append(list[0])
	if len(list) == 0:
		return
	lines_list = []
	for pos in list:
		pos_param = (int(param(pos[0], pos[1], pos[2])[0]), int(param(pos[0], pos[1], pos[2])[1]))
		lines_list.append(pos_param)
	pygame.draw.lines(win, color, False, lines_list)
	
def draw_axis():
	draw_path([(0,0,0), (5,0,0)], (255,0,0))
	draw_path([(0,0,0), (0,5,0)], (0,255,0))
	draw_path([(0,0,0), (0,0,5)], (0,0,255))

################################################################################ Setup

mouse_hold = False
angle_offset = 0.1
mouse_speed = (0,0)
mouse_current = (0,0)
mouse_last = (0,0)

#initial rotation:
world_rot = quaternion_mul_unit(quaternion_from_axis_angle((1,0,0), -2*math.pi/6), world_rot)

################################################################################ Keys check and Main Loop

def mouse_event_check(event):# in events check
	global mouse_hold, mouse_speed, zoom
	#if event.type == pygame.MOUSEMOTION:
	#	mouse_speed = event.rel
	if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
		mouse_hold = True
	if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
		mouse_hold = False
	if event.type == pygame.MOUSEBUTTONDOWN and event.button == 4:
		zoom += 100
	if event.type == pygame.MOUSEBUTTONDOWN and event.button == 5:
		if zoom > 0:
			zoom -= 100
			
def mouse_hold_check():#in main loop
	global mouse_hold, world_rot, mouse_speed, mouse_last, mouse_current
	mouse_last = mouse_current
	mouse_current = pygame.mouse.get_pos()
	mouse_speed = (mouse_current[0] - mouse_last[0], mouse_current[1] - mouse_last[1])
	if mouse_hold:
		offset_x = mouse_speed[0]
		offset_y = mouse_speed[1]
		
		world_rot = quaternion_mul(quaternion_from_axis_angle(axis_z, offset_x*0.01), world_rot)
		world_rot = quaternion_mul(quaternion_from_axis_angle((1,0,0), offset_y*0.005), world_rot)
	#else:
	#	mouse_speed = (0,0)
			
def world_position_keys_check():
	global pos_x, pos_y
	if keys[pygame.K_a]:
		pos_x -= 1
	if keys[pygame.K_d]:
		pos_x += 1
	if keys[pygame.K_w]:
		pos_y -= 1
	if keys[pygame.K_s]:
		pos_y += 1
		
def world_position_start(x,y):
	global pos_x, pos_y
	pos_x += x
	pos_y += y

def world_rotation_keys_check():
	global world_rot
	if keys[pygame.K_KP9]:
		world_rot = quaternion_mul(quaternion_from_axis_angle((1,0,0), angle_offset), world_rot)
	if keys[pygame.K_KP7]:
		world_rot = quaternion_mul(quaternion_from_axis_angle((1,0,0), -angle_offset), world_rot)
	if keys[pygame.K_KP6]:
		world_rot = quaternion_mul(quaternion_from_axis_angle((0,1,0), angle_offset), world_rot)
	if keys[pygame.K_KP4]:
		world_rot = quaternion_mul(quaternion_from_axis_angle((0,1,0), -angle_offset), world_rot)
	if keys[pygame.K_KP3]:
		world_rot = quaternion_mul(quaternion_from_axis_angle((0,0,1), angle_offset), world_rot)
	if keys[pygame.K_KP1]:
		world_rot = quaternion_mul(quaternion_from_axis_angle((0,0,1), -angle_offset), world_rot)
	if keys[pygame.K_KP_PERIOD]:
		world_rot = (0,0,0,1)
		
def update_vecs():#in main loop
	global cam_vec, axis_z
	cam_vec = quaternion_con_mul(camera_vec, (-world_rot[0], -world_rot[1], -world_rot[2], world_rot[3]))
	axis_z = quaternion_con_mul((0,0,1), world_rot)

################################################################################ copy this main loop

def main_loop_to_copy():
	run = True
	while run:
		#pygame.time.delay(1)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
			engine3d.mouse_event_check(event)
		keys = pygame.key.get_pressed()
		if keys[pygame.K_ESCAPE]:
			run = False
		
		#background:
		win.fill((0,0,0))
		engine3d.mouse_hold_check()
		engine3d.update_vecs()
		
		#step:
		engine3d.draw_axis()
		
		
		pygame.display.update()
	pygame.quit()
