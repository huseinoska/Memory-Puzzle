# Memory Puzzle
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

import random, pygame, sys
from pygame.locals import *
import pygame.image #Import the necessary libraries to load the image
# Import the time module to manage the game timer.
import time


FPS = 30 # frames per second, the general speed of the program
WINDOWWIDTH = 640 # size of window's width in pixels
WINDOWHEIGHT = 480 # size of windows' height in pixels
REVEALSPEED = 8 # speed boxes' sliding reveals and covers
BOXSIZE = 40 # size of box height & width in pixels
GAPSIZE = 10 # size of gap between boxes in pixels
BOARDWIDTH = 7 # number of columns of icons
BOARDHEIGHT = 4 # number of rows of icons
assert (BOARDWIDTH * BOARDHEIGHT) % 2 == 0, 'Board needs to have an even number of boxes for pairs of matches.'
XMARGIN = int((WINDOWWIDTH - (BOARDWIDTH * (BOXSIZE + GAPSIZE))) / 2)
YMARGIN = int((WINDOWHEIGHT - (BOARDHEIGHT * (BOXSIZE + GAPSIZE))) / 2)

#            R    G    B
GRAY     = (100, 100, 100)
NAVYBLUE = ( 60,  60, 100)
WHITE    = (255, 255, 255)
RED      = (255,   0,   0)
GREEN    = (  0, 255,   0)
BLUE     = (  0,   0, 255)
YELLOW   = (255, 255,   0)
ORANGE   = (255, 128,   0)
PURPLE   = (255,   0, 255)
CYAN     = (  0, 255, 255)

BGCOLOR = NAVYBLUE
LIGHTBGCOLOR = GRAY
BOXCOLOR = WHITE
HIGHLIGHTCOLOR = BLUE

DONUT = 'donut'
SQUARE = 'square'
DIAMOND = 'diamond'
LINES = 'lines'
OVAL = 'oval'

ALLCOLORS = (RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE, CYAN)
ALLSHAPES = (DONUT, SQUARE, DIAMOND, LINES, OVAL)
assert len(ALLCOLORS) * len(ALLSHAPES) * 2 >= BOARDWIDTH * BOARDHEIGHT, "Board is too big for the number of shapes/colors defined."

# Add a constant for the total game duration in seconds.
GAME_DURATION = 120  # 60 seconds (1 minute)

def main():
    global FPSCLOCK, DISPLAYSURF, star_image, star_rect
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('Memory Game')

    STAR_IMAGE_PATH = 'star.png'  #Define the path to the image
    star_image = pygame.image.load(STAR_IMAGE_PATH)
    star_rect = star_image.get_rect()  

    mousex = 0 # used to store x coordinate of mouse event
    mousey = 0 # used to store y coordinate of mouse event
    pygame.display.set_caption('Memory Game')

    mainBoard = getRandomizedBoard()
    revealedBoxes = generateRevealedBoxesData(False)

    firstSelection = None # stores the (x, y) of the first box clicked.

    
    boxGroups = None
    startTime = None

    DISPLAYSURF.fill(BGCOLOR)
    startGameAnimation(mainBoard)

    while True: # main game loop
        mouseClicked = False

        DISPLAYSURF.fill(BGCOLOR) # drawing the window
        drawBoard(mainBoard, revealedBoxes)

        for event in pygame.event.get(): # event handling loop
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEMOTION:
                mousex, mousey = event.pos
            elif event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                mouseClicked = True
#Greshka br1: red 89 ima greshka napishano: boxx, boxy = mousex, mousey, treba da bidi:boxx, boxy = getBoxAtPixel(mousex, mousey)
        boxx, boxy = getBoxAtPixel(mousex, mousey)
        #  boxx, boxy = mousex, mousey
        if boxx != None and boxy != None:
            # The mouse is currently over a box.
            if not revealedBoxes[boxx][boxy]:
                drawHighlightBox(boxx, boxy)
            if not revealedBoxes[boxx][boxy] and mouseClicked:
                revealBoxesAnimation(mainBoard, [(boxx, boxy)])
                revealedBoxes[boxx][boxy] = True # set the box as "revealed"
                if firstSelection == None: # the current box was the first box clicked
                    firstSelection = (boxx, boxy)
                else: # the current box was the second box clicked
                    # Check if there is a match between the two icons.
                    icon1shape, icon1color = getShapeAndColor(mainBoard, firstSelection[0], firstSelection[1])
                    icon2shape, icon2color = getShapeAndColor(mainBoard, boxx, boxy)

                    if icon1shape != icon2shape or icon1color != icon2color:
                        # Icons don't match. Re-cover up both selections.
                        pygame.time.wait(1000) # 1000 milliseconds = 1 sec
                        coverBoxesAnimation(mainBoard, [(firstSelection[0], firstSelection[1]), (boxx, boxy)])
                        revealedBoxes[firstSelection[0]][firstSelection[1]] = False
                        revealedBoxes[boxx][boxy] = False
                    elif hasWon(revealedBoxes): # check if all pairs found
                        gameWonAnimation(mainBoard)
                        pygame.time.wait(2000)

                        # Reset the board
                        mainBoard = getRandomizedBoard()#greshka br2: e toa shto ne povikuva funkcija
                        revealedBoxes = generateRevealedBoxesData(False)

                        # Show the fully unrevealed board for a second.
                        drawBoard(mainBoard, revealedBoxes)
                        pygame.display.update()
                        pygame.time.wait(1000)

                        # Replay the start game animation.
                        startGameAnimation(mainBoard)
                    firstSelection = None # reset firstSelection variable
        if not boxGroups:
            boxes = []
            for x in range(BOARDWIDTH):
                for y in range(BOARDHEIGHT):
                    boxes.append((x, y))
            random.shuffle(boxes)
            boxGroups = splitIntoGroupsOf(8, boxes)

        if startTime is None:
            startTime = time.time() # Start the timer when the first box is clicked.

        # Calculate the remaining time.
        elapsedTime = time.time() - startTime
        remainingTime = max(GAME_DURATION - int(elapsedTime), 0)

        drawTime(remainingTime)

        if remainingTime <= 0:
            # Game over if the time is up.
            gameOverAnimation()
            pygame.time.wait(2000) # Wait for 2 seconds.

            # Reset the game by generating a new board.
            mainBoard = getRandomizedBoard()
            revealedBoxes = generateRevealedBoxesData(False)
            startTime = None # Reset the timer.

            # Display the fully unrevealed board for a second.
            drawBoard(mainBoard, revealedBoxes)
            pygame.display.update()
            pygame.time.wait(1000)

            # Replay the start game animation.
            startGameAnimation(mainBoard)


        # Redraw the screen and wait a clock tick.
        pygame.display.update()#Greshka br3: dodaden kod koj fali
        FPSCLOCK.tick(FPS)


def generateRevealedBoxesData(val):
    revealedBoxes = []
    for i in range(BOARDWIDTH):
        revealedBoxes.append([val] * BOARDHEIGHT)
    return revealedBoxes

#Greshka br4: dodadovme d vo imeto za da se povikuva funkcijata i da ne bidi greshka
def getRandomizedBoard():
    # Get a list of every possible shape in every possible color.
    icons = []
    for color in ALLCOLORS:
        for shape in ALLSHAPES:
            icons.append( (shape, color) )

    random.shuffle(icons) # randomize the order of the icons list
    numIconsUsed = int(BOARDWIDTH * BOARDHEIGHT / 2) # calculate how many icons are needed
    icons = icons[:numIconsUsed] * 2 # make two of each
    random.shuffle(icons)

    # Create the board data structure, with randomly placed icons.
    board = []
    for x in range(BOARDWIDTH):
        column = []
        for y in range(BOARDHEIGHT):
            column.append(icons[0])
            del icons[0] # remove the icons as we assign them
        board.append(column)
    return board


def splitIntoGroupsOf(groupSize, theList):
    # splits a list into a list of lists, where the inner lists have at
    # most groupSize number of items.
    result = []
    for i in range(0, len(theList), groupSize):
        result.append(theList[i:i + groupSize])
    return result#Greshka br5: dodaden del koj fali 


def leftTopCoordsOfBox(boxx, boxy):
    # Convert board coordinates to pixel coordinates
    # left = boxx * BOXSIZE + GAPSIZE + XMARGIN
    # top = boxy * BOXSIZE + GAPSIZE + YMARGIN
    left = boxx * (BOXSIZE + GAPSIZE) + XMARGIN #Greshka br6: promena na formula vrakame lista od listi
    top = boxy * (BOXSIZE + GAPSIZE) + YMARGIN #Greshka br7: dodadovme zagradi
    return (left, top)


def getBoxAtPixel(x, y):
    for boxx in range(BOARDWIDTH):
        for boxy in range(BOARDHEIGHT):
            left, top = leftTopCoordsOfBox(boxx, boxy)
            boxRect = pygame.Rect(left, top, BOXSIZE, BOXSIZE)
            if boxRect.collidepoint(x, y):
                return (boxx, boxy)
    return (None, None)


def drawIcon(shape, color, boxx, boxy):
    quarter = int(BOXSIZE * 0.25) # syntactic sugar
    half =    int(BOXSIZE * 0.5)  # syntactic sugar

    left, top = leftTopCoordsOfBox(boxx, boxy) # get pixel coords from board coords
    # Draw the shapes
    if shape == DONUT:
        pygame.draw.circle(DISPLAYSURF, color, (left + half, top + half), half - 5)
        pygame.draw.circle(DISPLAYSURF, BGCOLOR, (left + half, top + half), quarter - 5)
    elif shape == SQUARE:
        pygame.draw.rect(DISPLAYSURF, color, (left + quarter, top + quarter, BOXSIZE - half, BOXSIZE - half))
    elif shape == DIAMOND:
        pygame.draw.polygon(DISPLAYSURF, color, ((left + half, top), (left + BOXSIZE - 1, top + half), (left + half, top + BOXSIZE - 1), (left, top + half)))
    elif shape == LINES:
        for i in range(0, BOXSIZE, 4):
            pygame.draw.line(DISPLAYSURF, color, (left, top + i), (left + i, top))
            pygame.draw.line(DISPLAYSURF, color, (left + i, top + BOXSIZE - 1), (left + BOXSIZE - 1, top + i))
    elif shape == OVAL:
        pygame.draw.ellipse(DISPLAYSURF, color, (left, top + quarter, BOXSIZE, half))


def getShapeAndColor(board, boxx, boxy):
    # shape value for x, y spot is stored in board[x][y][0]
    # color value for x, y spot is stored in board[x][y][1]
    #  return board[boxx][boxy][1], board[boxx][boxy][0]
    #Greshka br8: promena na mesta na 0 i 1 crtanje na ikonata
    return board[boxx][boxy][0], board[boxx][boxy][1]


def drawBoxCovers(board, boxes, coverage):
    # Draws boxes being covered/revealed. "boxes" is a list
    # of two-item lists, which have the x & y spot of the box.
    for box in boxes:
        left, top = leftTopCoordsOfBox(box[0], box[1])
        pygame.draw.rect(DISPLAYSURF, BGCOLOR, (left, top, BOXSIZE, BOXSIZE))
        shape, color = getShapeAndColor(board, box[0], box[1])
        drawIcon(shape, color, box[0], box[1])
        if coverage > 0: # only draw the cover if there is an coverage
            pygame.draw.rect(DISPLAYSURF, BOXCOLOR, (left, top, coverage, BOXSIZE))
    pygame.display.update()
    FPSCLOCK.tick(FPS)


def revealBoxesAnimation(board, boxesToReveal):
    # Do the "box reveal" animation.
    for coverage in range(BOXSIZE, (-REVEALSPEED) - 1, -REVEALSPEED):
        drawBoxCovers(board, boxesToReveal, coverage)


def coverBoxesAnimation(board, boxesToCover):
    # Do the "box cover" animation.
    for coverage in range(0, BOXSIZE + REVEALSPEED, REVEALSPEED):
        drawBoxCovers(board, boxesToCover, coverage)


def drawBoard(board, revealed):
    # Draws all of the boxes in their covered or revealed state.
    for boxx in range(BOARDWIDTH):
        for boxy in range(BOARDHEIGHT):
            left, top = leftTopCoordsOfBox(boxx, boxy)
            if not revealed[boxx][boxy]:
                # Draw a covered box.
                pygame.draw.rect(DISPLAYSURF, BOXCOLOR, (left, top, BOXSIZE, BOXSIZE))
            else:
                # Draw the (revealed) icon.
                shape, color = getShapeAndColor(board, boxx, boxy)
                drawIcon(shape, color, boxx, boxy)


def drawHighlightBox(boxx, boxy):
    left, top = leftTopCoordsOfBox(boxx, boxy)
    pygame.draw.rect(DISPLAYSURF, HIGHLIGHTCOLOR, (left - 5, top - 5, BOXSIZE + 10, BOXSIZE + 10), 4)


def startGameAnimation(board):
    # Randomly reveal the boxes 8 at a time.
    coveredBoxes = generateRevealedBoxesData(False)
    boxes = []
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            boxes.append( (x, y) )
    random.shuffle(boxes)
    boxGroups = splitIntoGroupsOf(8, boxes)

    drawBoard(board, coveredBoxes)
    for boxGroup in boxGroups:
        revealBoxesAnimation(board, boxGroup)
        coverBoxesAnimation(board, boxGroup)


def gameWonAnimation(board):
    # # flash the background color when the player has won
    # coveredBoxes = generateRevealedBoxesData(True)
    # color1 = LIGHTBGCOLOR
    # color2 = BGCOLOR

    # for i in range(13):
    #     color1, color2 = color2, color1 # swap colors
    #     DISPLAYSURF.fill(color1)
    #     drawBoard(board, coveredBoxes)
    #     pygame.display.update()
    #     pygame.time.wait(300)
    # Create a clock to control the animation speed.
    clock = pygame.time.Clock()

    # Define the initial position and state of the star image.
    star_x, star_y = WINDOWWIDTH // 10, WINDOWHEIGHT // 10
    blinking = False
    coveredBoxes = generateRevealedBoxesData(True)

    # Define the blinking effect variables.
    max_blink_frames = 60  # Adjust this to control the blinking speed.
    current_blink_frame = 0
    blink_on = True

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        DISPLAYSURF.fill(LIGHTBGCOLOR)
        drawBoard(board, coveredBoxes)

        # Update the star's position.
        if star_x > -star_rect.width:
            star_x -= 10

        # Toggle the blinking effect.
        current_blink_frame += 1
        if current_blink_frame >= max_blink_frames:
            current_blink_frame = 0
            blink_on = not blink_on

        # Display the star image with the blinking effect.
        if blink_on:
            DISPLAYSURF.blit(star_image, (star_x, star_y))

        pygame.display.update()
        clock.tick(FPS)

        if star_x <= -star_rect.width:
            break


def hasWon(revealedBoxes):
    # Returns True if all the boxes have been revealed, otherwise False
    for i in revealedBoxes:
        if False in i:
            return False # return False if any boxes are covered.
    return True

# Add a new function to draw the remaining time on the screen.
def drawTime(remainingTime):
    timeFont = pygame.font.Font(None, 36)
    timeSurf = timeFont.render('Time: ' + str(remainingTime), True, WHITE)
    timeRect = timeSurf.get_rect()
    timeRect.topleft = (10, 10)  # Adjust the position as needed.
    DISPLAYSURF.blit(timeSurf, timeRect)

# Add a new function to handle the game over animation.
def gameOverAnimation():
    # Display a "Game Over" message.
    gameOverFont = pygame.font.Font(None, 72)
    gameOverSurf = gameOverFont.render('Game Over', True, RED)
    gameOverRect = gameOverSurf.get_rect()
    gameOverRect.center = (WINDOWWIDTH // 2, WINDOWHEIGHT // 2)
    DISPLAYSURF.blit(gameOverSurf, gameOverRect)
    pygame.display.update()

if __name__ == '__main__':
    main()