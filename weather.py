#!/usr/bin/python

import urllib2, pygame, sys

jenkins_url="http://jenkins:8080/api/python"

def get_web_page(url):
	req = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0'})
	fp = urllib2.urlopen(req)
	return fp.read()

pygame.init()

screen = pygame.display.set_mode((1920, 1080))
mirror = pygame.Surface((screen.get_width(), screen.get_height() / 4))
mirror_gradient = pygame.Surface(mirror.get_size(), flags = pygame.SRCALPHA)

for i in range(mirror_gradient.get_height()):
	val = float(i) / float(mirror_gradient.get_height() * 2)
	val += .5;
	val = min(255, max(0, int(val * 255.0)))
	pygame.draw.line(mirror_gradient, pygame.Color(0, 0, 0, val), (0, i), (mirror_gradient.get_width(), i))

screen.fill(pygame.Color(0, 0, 0, 255))

foreground = pygame.transform.smoothscale(pygame.image.load("landscape02.png"), screen.get_size())
darkness = pygame.Surface(foreground.get_size())

cloudy = pygame.image.load("cloudy02.png")
rainy = pygame.image.load("rainy02.png")
sunny = pygame.image.load("sunny.png")
sun = pygame.image.load("sun.png")

font = pygame.font.Font(pygame.font.match_font("freeserif"), 35)
bigfont = pygame.font.Font(pygame.font.match_font("freeserif"), 50)

tick = 50.0

def blit_center(src, dest):
	dest_size = dest.get_size()
	src_size = dest.get_size()
	dest.blit(src, (dest_size[0] / 2 - src_size[0] / 2, dest_size[1] / 2 - src_size[1] / 2))

def double_blit(src, dest, pos):
	myPos = pos;
	w = src.get_width()
	if(pos[0] < -w):
		myPos = (-pos[0] - (-pos[0] % w) + pos[0], pos[1])

	dest.blit(src, myPos)
	dest.blit(src, (myPos[0] + src.get_width() + 1, myPos[1]))

class Weather:
	def __init__(self, score, name):
		self.surface = pygame.Surface((300,  750))
		self.textbg = pygame.Surface((50, self.surface.get_height()))
		self.textbg.fill(pygame.Color(0, 0, 0))
		self.textbg.set_alpha(None)
		self.textbg.set_alpha(127)
		self.name = name
		self.setWeather(score)

	def setWeather(self, score):
		self.score = float(max(0, min(100, score))) / 100.0;

		red = 1.0 - self.score;
		green = self.score;

		text = font.render(self.name, True, (255, 255, 255))
		self.text = pygame.transform.rotate(text, 90)
		self.score_surface = bigfont.render("%d%%" % score, True, (int(red * 255.0), int(green * 255.0), 0))

	def redraw(self, pos):
		turbulence = 1.0 - self.score

		double_blit(rainy, self.surface, (-tick * 10.0 * turbulence - pos[0], -pos[1]))
		rainy.set_alpha(127);
		double_blit(rainy, self.surface, (-tick * 20.0 * turbulence - pos[0], -pos[1]))

		alpha = max(min(255, int((self.score - .3) * 3.0 * 255.0)), 0)
		cloudy.set_alpha(alpha)
		double_blit(cloudy, self.surface, (-tick * 15 * turbulence - pos[0], -pos[1]))
		
		alpha = max(min(255, int((self.score - .8) * 5.0 * 255.0)), 0)
		sunny.set_alpha(alpha)

		#blit_center(sunny, self.surface)
		self.surface.blit(sunny, (-490, 0))

		self.surface.blit(foreground, ((-pos[0], -pos[1])))

		darkness.set_alpha(int((0.5 - self.score * .5) * 255.0))

		self.surface.blit(darkness, (0, 0))
		self.surface.blit(self.textbg, (0, 0))
		self.surface.blit(self.text, (5, self.surface.get_height() - self.text.get_height() - 5))
		self.surface.blit(self.score_surface, (self.surface.get_width() - self.score_surface.get_width() - 5, 5))

projects = []
response = eval(get_web_page(jenkins_url))

def update_projects():
	print "updating joblist"
	append = False
	if(len(projects) != len(response['jobs'])):
		print "new job created"
		del projects[:]
		append = True

	i = 0

	for job in response['jobs']:
		if job['name'].startswith("Replace"):
			break

		score = 0
		job = eval(get_web_page('%s/api/python' % job['url']))

		if 'healthReport' in job and len(job['healthReport']) > 0:
			health = job['healthReport']
			print "%s - %s" % (job['name'], health[0]['score'])
			score = health[0]['score']

		if append:
			projects.append(Weather(score, job['name']))
			print "appending"
		else:
			projects[i].setWeather(score)
		i += 1

timer = pygame.time.get_ticks() - 10000

while 1:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()

	i = 0
	screen_size = screen.get_size()
	mirror_size = mirror.get_size()

	for project in projects:
		project_size = project.surface.get_size()
		pos = (
                                screen_size[0] / 2 - (len(projects) * (project_size[0] + 20)) / 2 + (project_size[0] + 20) * i,
                                screen_size[1] / 3.5 - project_size[1] / 3
                        )
		
		project.redraw(pos)
		screen.blit(project.surface, pos)
		i += 1

	mirror.blit(screen, (0, 0), (0, screen_size[1] - mirror_size[1] * 2, screen_size[0], mirror_size[1]))
	mirror = pygame.transform.flip(mirror, False, True)
	mirror.blit(mirror_gradient, (0, 0))
	screen.blit(mirror, (0, screen_size[1] - mirror_size[1]))

	pygame.display.update();
	pygame.time.delay(16);
	tick += .1

	if pygame.time.get_ticks() - timer > 10000:
		timer = pygame.time.get_ticks()
		update_projects()
