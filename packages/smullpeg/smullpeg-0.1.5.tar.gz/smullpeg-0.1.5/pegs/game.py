"""
a version of the peg game made playable with pygame.
"""
from __future__ import absolute_import
import optparse
import os

import pygame

from .engine import Board

UPDATE_RATE=30

class Theme(object):
    def __init__(self, **kw):
        self.__dict__=dict(selected=(255,0,0),
                           occupied=(0,0,0),
                           empty=(255,255,255),
                           background=(190,190,190),
                           panel_background=(80,120,255),
                           panel_text=(255,255,255),
                           move_text=(0,0,0),
                           text=(0,170,0))
        self.__dict__.update(kw)

themes=dict(
    classic=Theme(),
    suave=Theme(background=(92, 104, 130),
                occupied=(48, 30, 0),
                selected=(219, 26, 0),
                empty=(130,92,104),
                panel_background=(214,152,172),
                text=(101,143,113)),
    wishywashy=Theme(background=(194,182,176),
                     occupied=(48, 30, 0),
                     selected=(219, 26, 0),
                     empty=(255,214,153),
                     panel_background=(50,64,84),
                     text=(101,143,113))
    )

current_theme=themes['suave']            
            

class PegHole(pygame.sprite.Sprite):
    

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
        for c in (current_theme.empty, current_theme.occupied, current_theme.selected):
            s=pygame.Surface((50, 50))
            s.fill(current_theme.background)
            pygame.draw.circle(s, c, s.get_rect().center, self.RADIUS)
            self.images.append(s.convert())
        self.update()
        self.rect=self.image.get_rect()
        x=self.point[1] * self.TILE_HEIGHT + self.TOP_OFFSET + (self.board.num_rows - self.point[0]) * self.CENTER_OFFSET
        y=self.point[0] * self.TILE_WIDTH + self.LEFT_OFFSET
        
        self.rect.topleft=(x,y)


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
        update_rate=UPDATE_RATE
        while running:
            clock.tick(update_rate)
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
        super(HelpPanel, self).__init__((210,235))

    def end_condition(self, evt):
        """
        redefine this to handle an event to dismiss the panel.
        By default, hitting escape, return, or Q will dismiss it.
        """
        return (evt.type==pygame.KEYDOWN and
                evt.key in (pygame.K_ESCAPE, pygame.K_h, pygame.K_q))
    
    def draw(self):
        bg=current_theme.panel_background
        s=self.image
        s.fill(bg)

        help=['F: toggle fullscreen',
              'H: show/hide this help',
              'M: flip board',
              'N: new game',
              'Q or Esc: quit',
              'R: rotate board',
              'T: enable hints',              
              'U: undo',]

        font = pygame.font.Font(None, 32)
        font.set_underline(True)
        text=font.render("Key bindings", 1, current_theme.panel_text, bg)
        s.blit(text, (10, 10))
        font = pygame.font.Font(None, 24)
        for line, h in enumerate(help):
            text = font.render(h, 1, current_theme.panel_text, bg)
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

    def __init__(self, open='random', show_hints=False):
        self.show_hints=show_hints        
        self._open=open
        self.board=Board(open=open)
        self.holes=pygame.sprite.RenderPlain()
        self.holemap={}
        for pt in self.board.points:
            h=PegHole(self.board, pt)
            self.holes.add(h)
            self.holemap[pt]=h
            
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
        font=pygame.font.SysFont('Verdana,Helvetica,SansSerif', 14)
        self.hinttext=font.render("Hints on", 1, current_theme.text, current_theme.background)
        self.hintbox=pygame.Surface(self.hinttext.get_size())
        self.hintbox.fill(current_theme.background)
        self.num_undos=0

    def rotate(self):
        self.board.rotate()
        h=self.selected_hole
        if h:
            newpt=self.board.rotate_point(h.point)
            h.selected=False
            self.holemap[newpt].selected=True

    def flip(self):
        self.board.flip()
        h=self.selected_hole
        if h:
            newpt=self.board.flip_point(h.point)
            h.selected=False
            self.holemap[newpt].selected=True

    @property
    def selected_hole(self):
        for h in self.holes:
            if h.selected:
                return h
        
    def draw_background(self, screen):
        self.background=pygame.Surface(screen.get_size()).convert()        
        self.background.fill(current_theme.background)
        font=pygame.font.SysFont('Verdana,Helvetica,SansSerif', 14)
        text=font.render('Press H for help.',
                         1,
                         current_theme.text,
                         current_theme.background)
        size=self.background.get_size()
        self.background.blit(text, (10, size[1] - text.get_size()[1]-5)) 
        screen.blit(self.background, (0,0))                             
        pygame.display.update()

    def draw_moves(self, screen):
        self.movebox.fill(current_theme.background)
        font = pygame.font.SysFont('Courier', 14)
        for line, move in enumerate(self.board.moves):
            text = font.render('%2d. %s %s' % (line + 1, move[0], move[1]),
                               1,
                               current_theme.move_text,
                               current_theme.background)
            self.movebox.blit(text, (10, 10+(14 * line)))
        screen.blit(self.movebox, (10, 10))
            
    def draw_hint(self, screen):
        w,h=self.hinttext.get_size()
        sw, sh=self.background.get_size()
        pos=sw-w-10, sh-h-5
        if self.show_hints:
            return screen.blit(self.hinttext, pos)
        else:
            return screen.blit(self.hintbox, pos)

        
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
        r=self.draw_hint(screen)
        self.holes.update()
        rectlist=self.holes.draw(screen)
        pygame.display.update([x.rect for x in self.holes.sprites()] + [r, self.movebox.get_rect()])
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

    def give_hint(self):
        winners=self.board.get_winning_moves()
        if winners:
            print "to win: %s" % ', '.join(["%s %s" % w for w in winners])
        else:
            self.groan()
            print "no winning moves"

    def finish(self):
        print "undos: %d" % self.num_undos
        if self.board.number==1:
            self.sounds['applause'].play()
        elif self.board.number <=4:
            self.sounds['finish'].play()
        else:
            self.sounds['mockery'].play()
        #print "DONE"

    def toggle_help(self):
        self._show_help=not self._show_help

    def undo(self):
        self.board.undo()
        self.num_undos+=1


def run():
    pygame.init()
    
    # fun little icon
    icon=pygame.Surface((32,32))
    icon.set_colorkey((0,0,0))
    center=icon.get_rect().center
    pygame.draw.circle(icon, (255,0,0), center, 15)
    pygame.draw.circle(icon, (255,255,255), center, 10)
    pygame.draw.circle(icon, (1, 1, 1), center, 5)
    pygame.display.set_icon(icon)
    
    screen=pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Smull-Peg")
    clock=pygame.time.Clock()

    # currently the parameters of this are fixed,
    # but it would be nice to be able to change the number of rows and
    # the open point.  @TBD
    game=PegGame()
    state='start'
    selected=None
    fullscreen=False
    while True:
        clock.tick(UPDATE_RATE)
        for event in pygame.event.get():
            if (event.type==pygame.QUIT or
                (event.type==pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_q))):
                pygame.quit()
                return
            elif event.type==pygame.KEYDOWN:
                
                if event.key==pygame.K_f:
                    if pygame.display.get_driver()=='x11':
                        pygame.display.toggle_fullscreen()
                    else:
                        acopy=screen.copy()                    
                        if fullscreen:
                            screen=pygame.display.set_mode((800,600))
                        else:
                            screen=pygame.display.set_mode((800,600), pygame.FULLSCREEN)
                        fullscreen= not fullscreen
                        screen.blit(acopy, (0,0))                    
                        pygame.display.update()

                elif event.key==pygame.K_h:
                    p=HelpPanel()
                    p.run(screen)

                elif event.key==pygame.K_u:
                    if game.board.moves:
                        game.undo()
                        state='start'
                        selected=None
                        for h in game.holes:
                            h.selected=False
                        if game.show_hints:
                            game.give_hint()
                    else:
                        game.beep()
                elif event.key==pygame.K_r:
                    game.rotate()

                elif event.key==pygame.K_m:
                    game.flip()
                    
                elif event.key==pygame.K_t:
                     game.show_hints=not game.show_hints
                     if game.show_hints:
                         game.give_hint()
                elif event.key==pygame.K_n:
                    state='start'
                    selected=None
                    game=PegGame(show_hints=game.show_hints)
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
                            selected=game.selected_hole
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
                                    if game.show_hints:
                                        game.give_hint()
                                    state='start'
                            
                        
        game.update(screen)

def main():
    parser=optparse.OptionParser()
    parser.add_option('-t', '--theme',   choices=list(themes), dest='theme')
    opts, args=parser.parse_args()
    if opts.theme:
        global current_theme
        current_theme=themes[opts.theme]
    run()

if __name__=='__main__':
    main()
