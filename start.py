import sys, pygame, random, time
from pygame.locals import *

pygame.init()

#----------
# CONSTANTS
#----------
BLACK = (0,0,0)
WHITE = (255,255,255)
infoobject = pygame.display.Info()

#Release Mode
WIDTH = infoobject.current_w
HEIGHT = infoobject.current_h
screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)

#Debug Mode
#WIDTH = 800
#HEIGHT = 500
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
		#pick a random direction
		number = round(random.uniform(0, 1))
		if number == 0:
			number = -1

		#pick an random speed to start the ball off width
		randomdx = random.randint(300,450)
		randomdy = random.randint(100, 250)

		#set the direction with the speed.
		self.dx = randomdx * number
		self.dy =  randomdy * number
	
	def move(self, dt):
		self.posX += self.dx * dt
		self.posY += self.dy * dt


	def paddle_collision(self):
		#reverse the direction when it hits a paddle
		self.dx = self.dx * -1

		#increase its speed over time by a small amount to make the game harder and harder.
		if self.dx < 0:
			self.dx = self.dx - 25
		elif self.dx > 0:
			self.dx = self.dx + 25

	def wall_collision(self):
		#reverse the direction when it hits a wall.
		self.dy = self.dy * -1

		#increase its speed over time by a small amount to make the game harder and harder.
		if self.dy < 0:
			self.dy = self.dy - 25 
		elif self.dy > 0:
			self.dy = self.dy + 25

	def restart_pos(self):
		self.posX = WIDTH//2
		self.posY = HEIGHT//2
		self.start_moving()
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
	
	#player control.
	def move(self, dt):
		if self.state == 'up':
			self.posY -= 500 * dt
		elif self.state == 'down':
			self.posY += 500 * dt

	#simple AI that moves up and down to align itself with the balls posY
	def self_move(self, dt, ball):
		if self.posY + self.heigh//2 > ball.posY:
			self.state = 'up'
			self.posY -= AISPEED * dt			
		elif self.posY + self.heigh//2 < ball.posY:
			self.state = 'down'
			self.posY += AISPEED * dt
		
		self.state = 'stopped'
		self.posY = self.posY


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

# VARIABLES
PLAYERS = 1
AISPEED = 400 #normal
playing = False
dt = 0
prev_time = time.time()

def get_AI_Mode():
	AIMODE = "Normal"
	if AISPEED == 100:
		AIMODE = "Super Baby"
	elif AISPEED == 200:
		AIMODE = "Baby"
	elif AISPEED == 300:
		AIMODE = "Easy"
	elif AISPEED == 400:
		AIMODE = "Normal"
	elif AISPEED == 500:
		AIMODE = "Human"
	elif AISPEED == 600:
		AIMODE = "A Challange"
	elif AISPEED == 700:
		AIMODE = "Super Human"
	elif AISPEED == 800:
		AIMODE = "Pong Genius"
	elif AISPEED == 900:
		AIMODE = "Are you sure?"
	elif AISPEED == 1000:
		AIMODE = "God Mode!"
	
	return AIMODE

# a function to draw the line and background. and if needed the controls.
def paint_black():
	screen.fill(BLACK)

	#show the controls when we are not playing.
	if playing == False:
		AI_Mode_Text = get_AI_Mode()

		#i could figure out how to do this in a for or foreach loop. but from a few google searches this seemed quite hard in pygame.
		font = pygame.font.SysFont("monospace", int(40*WIDTH / WIDTH), bold=True)
		label = font.render("CONTROLS", 0, WHITE)
		font2 = pygame.font.SysFont("monospace", int(20*WIDTH / WIDTH), bold=False)
		label2 = font2.render("1 = 1 player game.", 0, WHITE)
		label3 = font2.render("2 = 2 player game.", 0, WHITE)
		label4 = font2.render("3 = decrease AI difficulty.", 0, WHITE)
		label5 = font2.render("4 = increase AI difficulty.", 0, WHITE)
		label6 = font2.render("p = start game.", 0, WHITE)
		label7 = font2.render("r = reset game.", 0, WHITE)
		label8 = font2.render("Space = Close Game.", 0, WHITE)

		label9 = font2.render(("AI Difficulty: {}").format(AI_Mode_Text), 0, WHITE)

		widthOffSet = WIDTH//2 - label.get_rect().width
		screen.blit(label, (widthOffSet, HEIGHT//5))
		increasedHeight = label.get_rect().height
		screen.blit(label2, (widthOffSet, (HEIGHT//5 + increasedHeight)))
		increasedHeight += label2.get_rect().height
		screen.blit(label3, (widthOffSet, (HEIGHT//5 + increasedHeight)))
		increasedHeight += label3.get_rect().height
		screen.blit(label4, (widthOffSet, (HEIGHT//5 + increasedHeight)))
		increasedHeight += label4.get_rect().height		
		screen.blit(label5, (widthOffSet, (HEIGHT//5 + increasedHeight)))
		increasedHeight += label5.get_rect().height	
		screen.blit(label6, (widthOffSet, (HEIGHT//5 + increasedHeight)))
		increasedHeight += label6.get_rect().height
		screen.blit(label7, (widthOffSet, (HEIGHT//5 + increasedHeight)))
		increasedHeight += label7.get_rect().height
		screen.blit(label8, (widthOffSet, (HEIGHT//5 + increasedHeight)))
		increasedHeight += label8.get_rect().height*2
		
		if PLAYERS == 1:
			screen.blit(label9, (widthOffSet, (HEIGHT//5 + increasedHeight)))
	elif playing == True:
		pygame.draw.line( screen, WHITE, (WIDTH//2, 0), (WIDTH//2, HEIGHT), 5 )

#to restart the game.
def restart():
	paint_black()
	scoreLeft.restart()
	scoreRight.restart()
	paddleLeft.restart_pos()
	paddleRight.restart_pos()
	ball.restart_pos()
	pygame.mouse.set_visible(1)


#Create Objects for the game.
ball = Ball(screen, WHITE, WIDTH//2, HEIGHT//2, 15)
paddleLeft = Paddle(screen, WHITE, 15, HEIGHT//2-60, 20, 120)
paddleRight = Paddle(screen, WHITE, WIDTH - 20 - 15, HEIGHT//2 -60, 20, 120)
collision = CollisionManager()
scoreLeft = Score(screen, "0", WIDTH//4, 15)
scoreRight = Score(screen, "0", WIDTH - WIDTH//4, 15)

while 1:
	#compute delta time. so the ball doesnt go BRRRRRRR.
	now = time.time()
	dt = now - prev_time
	prev_time = now

	#check for user input.
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()
		
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_p:
				ball.start_moving()
				playing = True
			
			if event.key == pygame.K_SPACE:
				sys.exit()

			if event.key == pygame.K_1 or event.key == pygame.K_KP1:
				if playing == False:
					PLAYERS = 1

			if event.key == pygame.K_2 or event.key == pygame.K_KP2:
				if playing == False:
					PLAYERS = 2

			if event.key == pygame.K_4 or event.key == pygame.K_KP4:
				if playing == False:
					AISPEED += 100
					if AISPEED > 1000:
						AISPEED = 1000

			if event.key == pygame.K_3 or event.key == pygame.K_KP3:
				if playing == False:
					AISPEED -= 100
					if AISPEED < 100:
						AISPEED = 100

			#the restart button
			if event.key == pygame.K_r:
				restart()
				playing = False
				

			#if the key is pressed move the paddles.
			if event.key == pygame.K_w:
				paddleLeft.state = 'up'
			if event.key == pygame.K_s:
				paddleLeft.state = 'down'

			if PLAYERS == 2:	
				if event.key == pygame.K_UP:
					paddleRight.state = 'up'
				if event.key == pygame.K_DOWN:
					paddleRight.state = 'down'
		
		#check if the player lifted the key so we can stop the paddle.
		if event.type == pygame.KEYUP:
			if event.key == pygame.K_w or event.key == pygame.K_s:
				paddleLeft.state = 'stopped'
			if PLAYERS == 2:
				if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
					paddleRight.state = 'stopped'
	
	paint_black()
	
	if playing:
		pygame.mouse.set_visible(0)
        #the scores
		scoreLeft.show()
		scoreRight.show()

		#ball movement
		ball.move(dt)
		ball.show()

		#move player 1
		paddleLeft.move(dt)
		paddleLeft.clamp()
		paddleLeft.show()

		#move player 2 or AI
		if PLAYERS == 2:
			paddleRight.move(dt)
		elif PLAYERS != 2:
			paddleRight.self_move(dt, ball)

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
			paddleLeft.restart_pos()
			paddleRight.restart_pos()
			ball.restart_pos()

		if collision.check_goal_right(ball):
			paint_black()
			scoreRight.increase()
			paddleLeft.restart_pos()
			paddleRight.restart_pos()
			ball.restart_pos()

	
	pygame.display.update()