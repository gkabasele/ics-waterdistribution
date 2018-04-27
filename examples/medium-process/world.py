import pygame

#Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

pygame.init()

size = (700, 500)
screen = pygame.display.set_mode(size)

pygame.display.set_caption("Test")

done = False

clock = pygame.time.Clock()

def draw_approvisionning(screen, color, pos, width, app1 = True ):
    pygame.draw.rect(screen, color, pos, width)
    if app1:
        xs = pos[0] + pos[2]
        ys = pos[1] + pos[3] - 30
        rect_width = 25
        rect_length = 10

    else:
        rect_width = 25
        rect_length = 10
        xs = pos[0] - rect_width
        ys = pos[1] + pos[3] - 30

    pygame.draw.rect(screen, color, [xs, ys, rect_width, rect_length], width)

def draw_valve(screen, color, pos, width):
    pygame.draw.ellipse(screen, color, pos,width)


while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
    # Game logic

    # Screen clearing code goes here

    screen.fill(WHITE)

    # Drawing code 

    #a1
    draw_approvisionning(screen, BLUE, [10,5,40,80], 2)
    #a2
    draw_approvisionning(screen, BLUE, [110,5,40,80], 2, False)
    #t1
    draw_approvisionning(screen, BLUE, [60,90,40,80], 2)
    #s1
    draw_approvisionning(screen, BLUE, [110, 180, 40, 80],2)
    #s2
    draw_approvisionning(screen, BLUE, [160, 250, 40, 80],2)
    #s3
    draw_approvisionning(screen, BLUE, [210, 340, 40, 80],2)



    # Update screen
    pygame.display.flip()
    # Limit to 60 frames per second
    clock.tick(60)

pygame.quit()
