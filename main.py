import pygame
import time
import os
import tkinter as tk
import math

from actors import *  # Imports all classes from actors.py

screenWidth = 1000
screenHeight = 1000

root = tk.Tk()
embed = tk.Frame(root, width=screenWidth, height=screenHeight)
embed.pack()

root.resizable(False, False)
root.title("Tracker Swarm")

root.update()

os.environ['SDL_WINDOWID'] = str(embed.winfo_id())
os.environ['SDL_VIDEORIVER'] = "windib"

pygame.init()
pygame.font.init()

# Game properties
tickDelay = 0.01  # Time between updates. Lower time = faster game.
gameTitle = "Tracker Field"

screen = pygame.display.set_mode([screenWidth, screenHeight])
pygame.display.set_caption(gameTitle)

# Game class
class Game:
    def __init__(self):
        # Data
        self.data = Data()
        
        # Game States
        self.gameState = 0 # 0 = Main Menu, 1 = Help, 2 = Gameplay, 3 = Finish
        self.gameStarted = False

        # Mouse Input
        self.leftClicked = False

        # Text
        self.wimpFont = pygame.font.SysFont('Arial Black', 10)
        self.startFont = pygame.font.SysFont('Arial Black', 20)
        self.congratsFont = pygame.font.SysFont('Arial Black', 30)
        self.levelFont = pygame.font.SysFont('Agency FB', 25)
        self.timerFont = pygame.font.SysFont('Agency FB', 30)

        # Level and Timer
        self.level = 0
        self.timer = self.data.levelTimers[self.level]
        self.ticker = 100

        # Trackers
        self.ballStats = self.data.levelBalls[self.level]
        
        # Graphics
        self.backgroundColour = (255, 255, 255)
        
        self.flickerType = 0
        self.flickerState = 0
        self.flickerPositive = True

        # Infinity Spin
        self.startingLocation = [(pygame.display.list_modes()[0][0] / 2) - 500, (pygame.display.list_modes()[0][1] / 2) - 540]
        self.rotorPeriod = 0
        self.finalPhase = 0

        # Hard Mode
        self.hardMode = False

        # Text
        self.textButtons = []

        self.trackers = []
        for stat in self.ballStats:
            self.trackers.append(Ball(stat[0], stat[1], stat[2], stat[3], stat[4], stat[5]))

    def drawCentreText(self, text, colour, font, x, y):
        global screen
        
        text = font.render(text, True, colour)
        text_rect = text.get_rect(center=(x, y))
        screen.blit(text, text_rect)

        return text_rect
    
    def logic(self):
        global screenWidth
        global screenHeight
        global screen
        global gameRunning
        
        mousePos = pygame.mouse.get_pos()
        
        clicks = pygame.mouse.get_pressed()

        if self.gameState == 0:
            if clicks[0] and self.leftClicked == False:
                self.leftClicked = True
                for button in self.textButtons:
                    if button.left <= mousePos[0] <= button.right and button.top <= mousePos[1] <= button.bottom:
                        if self.textButtons.index(button) == 0:
                            self.ballStats = self.data.levelBalls[self.level]
                            self.trackers = []
                            for stat in self.ballStats:
                                self.trackers.append(Ball(stat[0], stat[1], stat[2], stat[3], stat[4], stat[5]))
                            self.timer = self.data.levelTimers[self.level]
                            self.gameState = 2
                        elif self.textButtons.index(button) == 1:
                            self.level = 0
                            self.ballStats = self.data.levelBalls[self.level]
                            self.trackers = []
                            for stat in self.ballStats:
                                self.trackers.append(Ball(stat[0], stat[1], stat[2], stat[3], stat[4], stat[5]))
                            self.timer = self.data.levelTimers[self.level]
                            self.hardMode = True
                            for tracker in self.trackers:
                                tracker.maxSpeed *= 1.2
                                tracker.maxAcceleration *= 1.2
                            self.gameState = 2
                        elif self.textButtons.index(button) == 2:
                            self.gameState = 1
                        elif self.textButtons.index(button) == 3:
                            gameRunning = False
                        elif self.textButtons.index(button) == 4 and self.level > 0:
                            self.level -= 1
                        elif self.textButtons.index(button) == 5 and self.level < 19:
                            self.level += 1
            elif not clicks[0]:
                self.leftClicked = False
                        
        elif self.gameState == 1:
            if clicks[0]:
                for button in self.textButtons:
                    if button.left <= mousePos[0] <= button.right and button.top <= mousePos[1] <= button.bottom:
                        self.gameState = 0
        
        elif self.gameState == 2:
            if not self.gameStarted:
                if clicks[0]:
                    if (mousePos[0] - 500)**2 + (mousePos[1] - 500)**2 <= 2500:
                        self.gameStarted = True
                        self.ticker = 100
                        self.rotorPeriod = 0
                        self.finalPhase = 0
            else:
                # Timer
                self.ticker -= 1
                if self.ticker <= 0:
                    self.ticker = 100
                    self.timer -= 1
                    if self.timer <= 0 and self.level < 19:
                        self.flickerType = 1
                        self.flickerState = 0
                        self.flickerPositive = True
                        self.gameStarted = False
                        self.trackers = []

                        self.level += 1
                        self.timer = self.data.levelTimers[self.level]
                        self.ballStats = self.data.levelBalls[self.level]
                        for stat in self.ballStats:
                            self.trackers.append(Ball(stat[0], stat[1], stat[2], stat[3], stat[4], stat[5]))
                        if self.hardMode:
                            for tracker in self.trackers:
                                tracker.maxSpeed *= 1.2
                                tracker.maxAcceleration *= 1.2
                    elif self.timer <= 0:
                        self.gameState = 3

                # Trackers
                for ball in self.trackers:
                    ball.updatePosition(mousePos)

                    if ball.position[0] < (ball.size * -1):
                        ball.position[0] = screenWidth + ball.size
                    elif ball.position[0] > (ball.size + screenWidth):
                        ball.position[0] = -1 * ball.size
                    
                    if ball.position[1] < (ball.size * -1):
                        ball.position[1] = screenHeight + ball.size
                    elif ball.position[1] > (ball.size + screenHeight):
                        ball.position[1] = -1 * ball.size
                    
                    if (mousePos[0] - ball.position[0])**2 + (mousePos[1] - ball.position[1])**2 <= (ball.size + 5)**2:
                        if self.hardMode:
                            self.level = 0
                            self.ballStats = self.data.levelBalls[self.level]
                        self.flickerType = -1
                        self.flickerState = 0
                        self.flickerPositive = True
                        self.gameStarted = False
                        self.trackers = []
                        for stat in self.ballStats:
                            self.trackers.append(Ball(stat[0], stat[1], stat[2], stat[3], stat[4], stat[5]))
                        self.timer = self.data.levelTimers[self.level]
                        if self.hardMode:
                            for tracker in self.trackers:
                                tracker.maxSpeed *= 1.2
                                tracker.maxAcceleration *= 1.2
                
                if not pygame.mouse.get_focused():
                    if self.hardMode:
                        self.level = 0
                        self.ballStats = self.data.levelBalls[self.level]
                    self.flickerType = -1
                    self.flickerState = 0
                    self.flickerPositive = True
                    self.gameStarted = False
                    self.trackers = []
                    for stat in self.ballStats:
                        self.trackers.append(Ball(stat[0], stat[1], stat[2], stat[3], stat[4], stat[5]))
                    self.timer = self.data.levelTimers[self.level]
                    if self.hardMode:
                        for tracker in self.trackers:
                            tracker.maxSpeed *= 1.2
                            tracker.maxAcceleration *= 1.2

                if self.level == 19:
                    root.geometry("+"+str(int(self.startingLocation[0] + (math.sin(math.radians(self.rotorPeriod)) * 300)))+"+"+str(int(self.startingLocation[1])))
                    if self.timer <= 80:
                        self.rotorPeriod += ((80 - self.timer) / 7) * 0.6
                    
                    if self.finalPhase == 0:
                        if self.timer <= 90 and len(self.trackers) == 1:
                            self.trackers.append(Ball(500, -7, (0, 255, 0), 7, 0.3, 6))
                        elif self.timer <= 80 and len(self.trackers) == 2:
                            self.trackers.append(Ball(500, -12, (0, 0, 255), 12, 0.15, 20))
                        elif self.timer <= 70 and len(self.trackers) == 3:
                            self.trackers.append(Ball(500, -6, (255, 255, 0), 6, 0.4, 2))
                        elif self.timer <= 60 and len(self.trackers) == 4:
                            self.trackers.append(Ball(500, -15, (255, 0, 255), 15, 0.35, 7))
                        elif self.timer <= 50 and len(self.trackers) == 5:
                            self.trackers.append(Ball(500, -7, (230, 230, 230), 7, 0.35, 1.5))
                        elif self.timer <= 40 and len(self.trackers) == 6:
                            self.trackers.append(Ball(500, -35, (0, 0, 0), 35, 0.1, 25))
                        elif self.timer <= 30:
                            self.finalPhase = 1
                            self.trackers = []
                    else:
                        if self.timer <= 20 and len(self.trackers) == 0:
                            self.trackers.append(Ball(500, -10, (230, 0, 0), 10, 2, 18))

    def draw(self):
        self.textButtons = []
        
        if self.flickerType != 0:
            screen.fill((255, 255 - self.flickerState, 255 - self.flickerState) if self.flickerType == -1 else (255 - self.flickerState, 255, 255 - self.flickerState))
            if self.flickerPositive:
                self.flickerState += 20
                if self.flickerState >= 200:
                    self.flickerPositive = False
            else:
                self.flickerState -= 10
                if self.flickerState <= 0:
                    self.flickerState = 0
                    self.flickerType = 0
        else:
            screen.fill(self.backgroundColour)
        if self.gameState == 0:
            self.drawCentreText("=== TRACKER SWARM ===", (0, 0, 0), self.congratsFont, 500, 50)
            self.textButtons.append(self.drawCentreText("> Play <", (0, 0, 0), self.startFont, 500, 480))
            self.textButtons.append(self.drawCentreText("> Play (Hard Mode) <", (0, 0, 0), self.startFont, 500, 520))
            self.textButtons.append(self.drawCentreText("> Help <", (0, 0, 0), self.startFont, 500, 200))

            self.textButtons.append(self.drawCentreText("Starting Level:", (0, 0, 0), self.startFont, 500, 600))
            self.drawCentreText(str(self.level + 1), (0, 0, 0), self.startFont, 500, 630)
            self.textButtons.append(self.drawCentreText("<", (0, 0, 0), self.startFont, 470, 630))
            self.textButtons.append(self.drawCentreText(">", (0, 0, 0), self.startFont, 530, 630))
            
            self.textButtons.append(self.drawCentreText("> Quit <", (0, 0, 0), self.startFont, 500, 800))
            
            pygame.display.flip() # Display drawn objects on screen
        elif self.gameState == 1:
            self.drawCentreText("=== TRACKER SWARM ===", (0, 0, 0), self.congratsFont, 500, 50)
            self.drawCentreText("Just dodge the trackers lmao", (0, 0, 0), self.startFont, 500, 500)
            self.textButtons.append(self.drawCentreText("> Back <", (0, 0, 0), self.startFont, 500, 900))

            pygame.display.flip()
        elif self.gameState == 2:
            if not self.gameStarted:
                pygame.draw.circle(screen, (0, 200, 0), (500, 500), 50)
                self.drawCentreText("START", (0, 120, 0), self.startFont, 500, 500)
            
            for ball in self.trackers:
                pygame.draw.circle(screen, ball.colour, (int(ball.position[0]), int(ball.position[1])), ball.size)

            self.drawCentreText("LEVEL " + str(self.level + 1), (0, 0, 0), self.levelFont, 500, 30)
            self.drawCentreText(str(self.timer), (0, 0, 0), self.timerFont, 500, 60)
            
            pygame.display.flip() # Display drawn objects on screen

        elif self.gameState == 3:
            if self.hardMode == False:
                self.drawCentreText("CONGRATULATIONS!", (0, 200, 0), self.congratsFont, 500, 450)
                self.drawCentreText("Now beat the game on Hard Mode for a gold star.", (0, 120, 0), self.startFont, 500, 550)
                self.drawCentreText("wimp", (0, 120, 0), self.wimpFont, 500, 570)
            else:
                self.drawCentreText("CONGRATULATIONS!", (0, 200, 0), self.congratsFont, 500, 250)
                self.drawCentreText("You beat the game on Hard Mode. Here's that star I promised you.", (0, 120, 0), self.startFont, 500, 350)
                star = pygame.image.load("Images/Star.png")
                screen.blit(star, (330, 400))
            pygame.display.flip() # Display drawn objects on screen

# Run the actual game
game = Game() # Game object

gameRunning = True
while gameRunning:
    ev = pygame.event.get()

    for event in ev:
        if event.type == pygame.QUIT:
            gameRunning = False
    
    game.logic()
    game.draw()

    root.update()

    time.sleep(tickDelay)

pygame.quit()
root.destroy()
