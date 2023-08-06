"""
a version of the peg game made playable with pygame.
"""
from __future__ import absolute_import
import os

import pygame

from .engine import Board

UPDATE_RATE=30

class PegHole(pygame.sprite.Sprite):
    
    SELECTED_COLOR=(255,0,0)
    OCCUPIED_COLOR=(0,0,0)
    EMPTY_COLOR=(255,255,255)
    TILE_HEIGHT=100
    TILE_WIDTH=100
    LEFT_OFFSET=60
    TOP_OFFSET=100
    CENTER_OFFSET=50
    RADIUS=15
    
    def __init__(self, board, point, selected=False):
        super(PegHole, self).__init__()
        self.board=board
        self.point=point
        self.selected=selected

        self.images=[]
        for c in (self.EMPTY_COLOR, self.OCCUPIED_COLOR, self.SELECTED_COLOR):
            s=pygame.Surface((50, 50))
            s.fill(PegGame.BACKGROUND_COLOR)
            pygame.draw.circle(s, c, s.get_rect().center, self.RADIUS)
            self.images.append(s.convert())
        self.update()
        self.rect=self.image.get_rect()
        x=self.point[1] * self.TILE_HEIGHT + self.TOP_OFFSET + (self.board.num_rows - self.point[0]) * self.CENTER_OFFSET
        y=self.point[0] * self.TILE_WIDTH + self.LEFT_OFFSET
        
        self.rect.topleft=(x,y)
        #print self.rect.topleft, self.point, 'occupied' if self.board.points[point] else 'empty'
        
    def update(self):
        if self.selected:
            self.image=self.images[2]
        elif self.board.points[self.point]:
            self.image=self.images[1]
        else:
            self.image=self.images[0]
    
    def has_position(self, pos):
        """
        returns whether or not the position is in the drawn circle.
        """
        cx, cy=self.rect.center
        x,y=pos
        # one grace pixel
        r=self.RADIUS + 1
        return (cx-r <= x <= cx+r) and (cy-r <= y <= cy+r)

class Panel(pygame.sprite.DirtySprite):
    """
    a blocking dialog that processes its own events.
    """
    def __init__(self, size):
        self.size=size
        self.image=pygame.Surface(size)
        self.draw()
        super(Panel, self).__init__()

    def draw(self):
        """
        put whatever you want on the background
        """
        pass

    def end_condition(self, evt):
        """
        redefine this to handle an event to dismiss the panel.
        By default, hitting escape, return, or Q will dismiss it.
        """
        return (evt.type==pygame.KEYDOWN and
                evt.key in (pygame.K_ESCAPE, pygame.K_q))

    def handle_event(self, evt):
        """
        override to provide any additional event handling
        """
        pass

    def run(self, screen, pos='center'):
        if pos == 'center':
            sr=screen.get_rect()
            ir=self.image.get_rect()
            pos=sr.centerx-ir.centerx, sr.centery-ir.centery
            del sr, ir
        original=screen.copy()
        r=screen.blit(self.image, pos)
        pygame.display.update()
        clock=pygame.time.Clock()
        running=True
        while running:
            clock.tick(UPDATE_RATE)
            for evt in pygame.event.get():
                if evt.type==pygame.QUIT:
                    pygame.quit()
                    return
                if self.end_condition(evt):
                    running=False
                    break
                else:
                    self.handle_event(evt)
        screen.blit(original, (0,0))
        pygame.display.update()


class HelpPanel(Panel):
    def __init__(self):
        super(HelpPanel, self).__init__((210,200))

    def end_condition(self, evt):
        """
        redefine this to handle an event to dismiss the panel.
        By default, hitting escape, return, or Q will dismiss it.
        """
        return (evt.type==pygame.KEYDOWN and
                evt.key in (pygame.K_ESCAPE, pygame.K_h, pygame.K_q))
    
    def draw(self):
        bg=(80,120,255)
        s=self.image
        s.fill(bg)

        help=['H: show/hide this help',
              'U: undo',
              'N: new game',
              'F: toggle fullscreen',
              'T: enable hints',
              'Q or Esc: quit']

        font = pygame.font.Font(None, 32)
        font.set_underline(True)
        text=font.render("Key bindings", 1, (255, 255, 255), bg)
        s.blit(text, (10, 10))
        font = pygame.font.Font(None, 24)
        for line, h in enumerate(help):
            text = font.render(h, 1, (255,255,255), bg)
            s.blit(text, (10, 42+(24 * line)))
        


class NonSound(object):
    def  play(self):
        pass
    
def load_sound(name):
    if pygame.mixer:
        return pygame.mixer.Sound(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                               'sounds',
                                               name))
    return NonSound()

        
class PegGame(object):
    BACKGROUND_COLOR=(190,190,190)

    def __init__(self, open='random'):
        self._open=open
        self.board=Board(open=open)
        self.holes=pygame.sprite.RenderPlain()
        for pt in self.board.points:
            self.holes.add(PegHole(self.board, pt))
        self.background=None
        self.sounds={}
        self.sounds['click']=load_sound('click.ogg')
        self.sounds['beep']=load_sound('beep.ogg')
        self.sounds['finish']=load_sound('finish.ogg')
        self.sounds['applause']=load_sound('applause.ogg')
        self.sounds['mockery']=load_sound('mockery.ogg')
        self.sounds['groan']=load_sound('groan.ogg')
        self._show_help=False
        self._showing_help=False
        self._help_screen=None
        self.show_moves=False
        self.movebox=pygame.Surface((100, 14 * 15))

        
    def draw_background(self, screen):
        self.background=pygame.Surface(screen.get_size()).convert()        
        self.background.fill(self.BACKGROUND_COLOR)
        font=pygame.font.SysFont('Verdana,Helvetica,SansSerif', 14)
        text=font.render('Press H for help.', 1, (0,170,0), self.BACKGROUND_COLOR)
        size=self.background.get_size()
        self.background.blit(text, (10, size[1]-24))
        screen.blit(self.background, (0,0))                             
        pygame.display.update()

    def draw_moves(self, screen):
        self.movebox.fill(self.BACKGROUND_COLOR)
        font = pygame.font.SysFont('Courier', 14)
        for line, move in enumerate(self.board.moves):
            text = font.render('%2d. %s %s' % (line + 1, move[0], move[1]), 1, (0,0,0), self.BACKGROUND_COLOR)
            self.movebox.blit(text, (10, 10+(14 * line)))
        screen.blit(self.movebox, (10, 10))
            

    def find_hole(self, pos):
        for h in self.holes:
            if h.has_position(pos):
                return h
        

    def update(self, screen):
        """
        this updates the display.
        """
        if self.background is None:
            self.draw_background(screen)
        self.draw_moves(screen)
        self.holes.update()
        rectlist=self.holes.draw(screen)
        pygame.display.update([x.rect for x in self.holes.sprites()] + [self.movebox.get_rect()])
        if self._show_help:
            if not self._showing_help:
                self.draw_help(screen)
                self._showing_help=True
        elif self._showing_help:
            self._help_screen.get_rect()
            

    def beep(self):
        self.sounds['beep'].play()
        #print 'BEEP'

    def click(self):
        # this sounds delayed, so commenting out ...
        #self.sounds['click'].play()
        #print "CLICK"
        pass

    def groan(self):
        self.sounds['groan'].play()


    def finish(self):
        if self.board.number==1:
            self.sounds['applause'].play()
        elif self.board.number <=4:
            self.sounds['finish'].play()
        else:
            self.sounds['mockery'].play()
        #print "DONE"

    def toggle_help(self):
        self._show_help=not self._show_help


def main():
    pygame.init()
    screen=pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Smull-Peg")
    clock=pygame.time.Clock()

    # currently the parameters of this are fixed,
    # but it would be nice to be able to change the number of rows and
    # the open point.  @TBD
    game=PegGame()
    state='start'
    selected=None
    show_hints=False
    while True:
        clock.tick(UPDATE_RATE)
        for event in pygame.event.get():
            if (event.type==pygame.QUIT or
                (event.type==pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_q))):
                pygame.quit()
                return
            elif event.type==pygame.KEYDOWN:
                
                if event.key==pygame.K_f:
                    pygame.display.toggle_fullscreen()
                elif event.key==pygame.K_h:
                    p=HelpPanel()
                    p.run(screen)
                    #game.toggle_help()
                elif event.key==pygame.K_u:
                    if game.board.moves:
                        game.board.undo()
                        state='start'
                        selected=None
                        for h in game.holes:
                            h.selected=False
                    else:
                        game.beep()
                elif event.key==pygame.K_t:
                     show_hints=not show_hints
                elif event.key==pygame.K_n:
                    state='start'
                    selected=None
                    game=PegGame()
            elif event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                pos=event.pos
                hole=game.find_hole(pos)
                if hole:
                    if state=='start':
                        # is this a legal move?
                        pt=hole.point
                        if pt in [x[0] for x in game.board.possible_moves]:
                            game.click()
                            hole.selected=True
                            selected=hole
                            state='selected'
                        else:
                            game.beep()
                    elif state=='selected':
                        if hole.selected:
                            game.click()
                            hole.selected=False
                            state='start'
                            selected=None
                        else:
                            pt=hole.point
                            assert selected
                            start_pt=selected.point
                            if not (start_pt, pt) in game.board.possible_moves:
                                game.beep()
                            else:
                                game.board.move(start_pt, pt)
                                game.click()

                                selected.selected=False
                                selected=None
                                if game.board.is_finished:
                                    game.finish()
                                    state='end'
                                else:
                                    if show_hints:
                                        winners=game.board.get_winning_moves()
                                        if winners:
                                            print "to win: %s" % ', '.join(["%s %s" % w for w in winners])
                                        else:
                                            game.groan()
                                            print "no winning moves"
                                    state='start'
                            
                        
        game.update(screen)


if __name__=='__main__':
    main()
