import sys, pygame, random, time,math
from turtle import width
from pygame.locals import *

pygame.init()
pygame.mouse.set_visible(0)

#----------
# CONSTANTS
#----------

infoobject = pygame.display.Info()
WIDTH = infoobject.current_w
HEIGHT = infoobject.current_h
#WIDTH = 800
#HEIGHT = 500
BLACK = (0,0,0)
WHITE = (255,255,255)
screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
#screen = pygame.display.set_mode((WIDTH,HEIGHT))

pygame.display.set_caption('My Pong')

#-----------------------

#---------
# CLASSES
#---------
class Ball:
	def __init__(self, screen, color, posX, posY, radius):
		self.screen = screen
		self.color = color
		self.posX = posX
		self.posY = posY
		self.radius = radius
		self.dx = 0
		self.dy = 0
		self.show()
	
	def show(self):
		pygame.draw.circle(self.screen, self.color, (int(self.posX), int(self.posY)), int(self.radius))

	def start_moving(self):
		number = round(random.uniform(0, 1))
		if number == 0:
			number = -1

		randomdx = random.randint(300,450)
		randomdy = random.randint(100, 250)
		self.dx = randomdx * number
		self.dy =  randomdy * number
	
	def move(self, dt):
		self.posX += self.dx * dt
		self.posY += self.dy * dt


	def paddle_collision(self):
		self.dx = self.dx * -1
		if self.dx < 0:
			self.dx = self.dx - 25
		elif self.dx > 0:
			self.dx = self.dx + 25

	def wall_collision(self):
		self.dy = self.dy * -1
		if self.dy < 0:
			self.dy = self.dy - 25 
		elif self.dy > 0:
			self.dy = self.dy + 25

	def restart_pos(self):
		self.posX = WIDTH//2
		self.posY = HEIGHT//2
		self.dx = 0
		self.dy = 0
		self.show()

class Paddle:
	def __init__(self, screen, color, posX, posY, width, height):
		self.screen = screen
		self.color = color
		self.posX = posX
		self.posY = posY
		self.width = width
		self.heigh = height
		self.state = 'stopped'
		self.show()

	def show(self):
		pygame.draw.rect( self.screen, self.color,(self.posX, self.posY, self.width, self.heigh))
	
	def move(self, dt):
		if self.state == 'up':
			self.posY -= 500 * dt
		elif self.state == 'down':
			self.posY += 500 * dt

	def clamp(self):
		if self.posY <= 0:
			self.posY = 0
		
		if self.posY + self.heigh >= HEIGHT:
			self.posY = HEIGHT - self.heigh

	def restart_pos(self):
		self.posY = HEIGHT//2 - self.heigh//2
		self.state = 'stopped'
		self.show()

class Score:
	def __init__(self, screen, points, posX, posY):
		self.screen = screen
		self.points = points
		self.posX = posX
		self.posY = posY
		self.font = pygame.font.SysFont("monospace", 80, bold=True)
		self.label = self.font.render(self.points, 0, WHITE)
		self.show()
	
	def show(self):
		self.screen.blit(self.label, (self.posX - self.label.get_rect().width//2, self.posY))

	def increase(self):
		points = int(self.points) + 1
		self.points = str(points)
		self.label = self.font.render(self.points, 0, WHITE)

	def restart(self):
		self.points = "0"
		self.label = self.font.render(self.points, 0, WHITE)
	
class CollisionManager:
	def between_ball_and_paddleLeft(self, ball, paddleLeft):
		if ball.posY + ball.radius > paddleLeft.posY and ball.posY - ball.radius < paddleLeft.posY + paddleLeft.heigh:
			if ball.posX - ball.radius <= paddleLeft.posX + paddleLeft.width:
				return True
		
		return False


	def between_ball_and_paddleRight(self, ball, paddleRight):
		if ball.posY + ball.radius > paddleRight.posY and ball.posY - ball.radius < paddleRight.posY + paddleRight.heigh:
			if ball.posX + ball.radius >= paddleRight.posX:
				return True
		
		return False

	def between_ball_and_wall(self, ball):
		# top collision
		if ball.posY - ball.radius <= 0:
			return True

		#bottom collision
		if ball.posY + ball.radius >= HEIGHT:
			return True

		return False

	def check_goal_left(self, ball):
		return ball.posX - ball.radius >= WIDTH

	def check_goal_right(self, ball):
		return ball.posX + ball.radius <= 0
#---------------------

#----------
# FUNCTIONS
#----------

def paint_black():
	screen.fill(BLACK)
	pygame.draw.line( screen, WHITE, (WIDTH//2, 0), (WIDTH//2, HEIGHT), 5 )

paint_black()

def restart():
	paint_black()
	scoreLeft.restart()
	scoreRight.restart()
	paddleLeft.restart_pos()
	paddleRight.restart_pos()
	ball.restart_pos()

#objects
ball = Ball(screen, WHITE, WIDTH//2, HEIGHT//2, 15)
paddleLeft = Paddle(screen, WHITE, 15, HEIGHT//2-60, 20, 120)
paddleRight = Paddle(screen, WHITE, WIDTH - 20 - 15, HEIGHT//2 -60, 20, 120)
collision = CollisionManager()
scoreLeft = Score(screen, "0", WIDTH//4, 15)
scoreRight = Score(screen, "0", WIDTH - WIDTH//4, 15)

# VARIABLES
playing = False
dt = 0
prev_time = time.time()

while 1:
	#compute delta time.
	now = time.time()
	dt = now - prev_time
	prev_time = now

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()
		
		if event.type == pygame.KEYDOWN:
			#the start button.
			if event.key == pygame.K_p:
				ball.start_moving()
				playing = True
			
			if event.key == pygame.K_SPACE:
				sys.exit()

			#the restart button
			if event.key == pygame.K_r:
				restart()
				playing = False

			#if the key is pressed move the paddles.
			if event.key == pygame.K_w:
				paddleLeft.state = 'up'
			if event.key == pygame.K_s:
				paddleLeft.state = 'down'
				
			if event.key == pygame.K_UP:
				paddleRight.state = 'up'
			if event.key == pygame.K_DOWN:
				paddleRight.state = 'down'
		
		#check if the player lifted the key so we can stop the paddle.
		if event.type == pygame.KEYUP:
			if event.key == pygame.K_w or event.key == pygame.K_s:
				paddleLeft.state = 'stopped'
			if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
				paddleRight.state = 'stopped'

	if playing:
		paint_black()

		#ball movement
		ball.move(dt)
		ball.show()

		paddleLeft.move(dt)
		paddleLeft.clamp()
		paddleLeft.show()

		paddleRight.move(dt)
		paddleRight.clamp()
		paddleRight.show()

		#check for collisions
		if collision.between_ball_and_paddleLeft(ball, paddleLeft):
			ball.paddle_collision()
		if collision.between_ball_and_paddleRight(ball, paddleRight):
			ball.paddle_collision()
		if collision.between_ball_and_wall(ball):
			ball.wall_collision()
		
		if collision.check_goal_left(ball):
			paint_black()
			scoreLeft.increase()
			ball.restart_pos()
			paddleLeft.restart_pos()
			paddleRight.restart_pos()
			playing = False
		if collision.check_goal_right(ball):
			paint_black()
			scoreRight.increase()
			ball.restart_pos()
			paddleLeft.restart_pos()
			paddleRight.restart_pos()
			playing = False

	scoreLeft.show()
	scoreRight.show()
	
	pygame.display.update()