"""
a model for the "I.Q. Tester" triangular peg board game.

"""
import anydbm
from copy import deepcopy
import gzip
from operator import itemgetter
import os
import random
from string import center

try:
    import psyco
except ImportError:
    pass
else:
    psyco.full()


class Point(tuple):
    """
    a named tuple Point class which can
    represents itself in a notation similar
    to algebraic notation in chess
    """

    def __new__(cls, *args):
        if len(args)==1:
            args=args[0]
        if isinstance(args, basestring):
            if len(args)!=2:
                raise ValueError("not a valid point: %s" % args)
            args=(int(args[1])-1, ord(args[0])-97)
        result=tuple.__new__(cls, args)
        if len(result)!=2:
            raise ValueError("not a valid point: %s" % result)
        return result


    def __str__(self):
        return '%s%d' % (chr(97+self[1]), 1+self[0])

    x=property(itemgetter(0))
    y=property(itemgetter(1))

# anydbm book (deprecated, but used for building)    
DB_PATH=os.path.join(os.path.abspath(os.path.dirname(__file__)), 'book.db')

# gzipped file (what we use at runtime now that the book is built)
GZ_PATH=os.path.join(os.path.abspath(os.path.dirname(__file__)), 'book.txt.gz')

def _init_book():
    """
    load book into memory.
    """
    d={}
    fp=gzip.GzipFile(GZ_PATH, 'rb')
    for line in fp:
        k, moves=line.split(' ')
        moves=moves.strip()
        d[k]=[(Point(m[:2]), Point(m[2:])) for m in moves.split(',')] if moves else []
    return d

try:
    _book_data=_init_book()
except IOError:
    _book_data={}

class Board(object):
    """
    
    a representation of an I.Q. Tester triangular peg board game.  The
    holes of the board are represented by ordered pairs of the form
    (row, column) where both row and column start at zero at the top
    left.  The board stores the moves that have been played on it as
    well as the current position.

    Some important attributes and properties:

      start_open: the initial open point (by default randomly chosen).
      moves: the list of moves played.
      possible_moves: a list of legal moves from the given position.
      open_points: the points open on the board.
      closed_points: the points occupied by pegs.      
      number: the number of closed points.
      is_finished: if the game is finished or not (i.e., there are no possible moves).


    Example usage:

     >>> b=Board(open=(3,2))
     >>> b
         X          
        X X         
       X X X        
      X X O X       
     X X X X X     
     >>> b.move((1,0), (3,2))
         X          
        O X         
       X O X        
      X X X X       
     X X X X X     

    A board can be cloned (with clone()) if you want experiment with a
    position without disturbing your primary setup; the method clone_move()
    does that and also makes a move.

    To generate all solutions of a board that meet some criterion, use walk().

    """
    def __init__(self, num_rows=5, open='random'):
        self.num_rows=num_rows
        self.points=dict.fromkeys((Point(i,j) for i in range(num_rows) for j in range(i+1)), 1)
        if open=='random':
            open=random.choice(list(self.points))
        if open:
            self.start_open=open            
            self.open(open)
        self.moves=[]
        self._possible_moves=None

    def rotate_point(self, p):
        x, y=p
        n=self.num_rows-1
        return Point((n-x+y, n-x))

    def transpose(self, tr):
        b=self.clone()
        for letter in tr:
            if letter=='r':
                b=b.rotate()
            elif letter=='f':
                b=b.flip()
            elif letter=='s':
                pass
            else:
                raise ValueError("invalid tranposition: %s" % letter)
        return b
    

    def transpose_point(self, p, tr):

        for letter in tr:
            if letter=='s':
                pass
            elif letter=='f':
                p=self.flip_point(p)
            elif letter=='r':
                p=self.rotate_point(p)
            else:
                raise ValueError("invalid transposition: %s" % letter)
        return p

    def untranspose_point(self, p, tr):
        return self.transpose_point(p, tr.replace('r', 'rr'))

    def _get_transpositions(self):
        trs=('r', 'rr', 'f', 'fr', 'frr', 's')
        return dict((t, self.transpose(t)) for t in trs)

    def get_canonical_transposition(self):
        t=self._get_transpositions()
        d=dict((tuple(sorted(b.open_points)), (k, b)) for k, b in t.items())
        return d[min(d)]

    def flip_point(self, p):
        x, y=p
        return Point((x, x-y))

    def flip(self):
        f=self.flip_point
        self.points=dict((f(p), v) for p,v in self.points.items())
        self.start_open=f(self.start_open)
        self.moves=[map(f, m) for m in self.moves]
        self._possible_moves=None
        return self

    def rotate(self, backwards=False):
        rp=self.rotate_point
        self.points=dict((rp(p), v) for p,v in self.points.items())
        self.start_open=rp(self.start_open)
        self.moves=[map(rp, m) for m in self.moves]
        self._possible_moves=None
        if backwards:
            # one mo time
            self.rotate(False)
        return self

    def clone(self):
        """
        returns a copy of the board.
        """
        return deepcopy(self)

    def clone_move(self, p1, p2):
        """
        returns a copy of the board with the given move played.
        """
        return self.clone().move(p1, p2)

    def open(self, pt):
        pt=Point(pt)
        if not pt in self.points:
            raise ValueError("not a valid point for this board: %s" % pt)
        if self.start_open is None:
            self.start_open=pt
        self.points[pt]=0

    @property
    def open_points(self):
        return set(k for k, v in self.points.iteritems() if v==0)

    @property
    def closed_points(self):
        return set(k for k, v in self.points.iteritems() if v==1)

    @property
    def is_finished(self):
        return len(self.possible_moves)==0

    @property
    def number(self):
        return len(self.closed_points)

    def move(self, p1, p2):
        """
        move the peg at point p1 to point p2, removing the
        intervening peg.  Only legal moves allowed.  The move
        is recorded in the board's moves list, and the board itself
        is returned.
        """
        p3=self.removal_point(p1, p2)
        if not p3:
            raise ValueError("illegal move: %s => %s" % (p1, p2))
        self._possible_moves=None
        self.moves.append((Point(p1), Point(p2)))
        self.points[p1]=0
        self.points[p2]=1
        self.points[p3]=0
        return self

    def undo(self):
        if self.moves:
            u1,u2=m=self.moves.pop()
            self._possible_moves=None
            self.points[u1]=1
            self.points[u2]=0
            self.points[self.removal_point(u1, u2)]=1
            return m

    def ran_move(self):
        """
        make a random move.
        """
        if self.possible_moves:
            self.move(*random.choice(self.possible_moves))
        return self

    def ran_play(self):
        """
        continues playing from the current position, making
        random choices.
        """
        while True:
            moves=self.possible_moves
            if moves:
                m=random.choice(moves)
                self.move(*m)
            else:
                break
        return self

    def walk(self, save_criterion=lambda b: True):
        """
        an iterator returning all possible games from the current position
        that meet the save_criterion (defaulting to all of them).
        """
        if not self.possible_moves:
            if save_criterion(self):
                yield self
        else:
            for m in self.possible_moves:
                b=self.clone()
                b.move(*m)
                for r in b.walk(save_criterion):
                    yield r


    def __repr__(self):
        buff=['']
        width=self.num_rows*4
        for i in range(self.num_rows):
            line=[]
            for j in range(i+1):
                line.append('X' if self.points[(i,j)] else 'O')
            buff.append(center(' '.join(line), width))
        return '\n'.join(buff)

    @property
    def position_hash(self):
        return '%d%s' % (self.num_rows, ''.join(map(str, self.open_points)))


    def removal_point(self, p1, p2):
        """
        p2 must be open, p1 closed
        p1 and p2 must be on a line, separated by one closed point.
        returns the closed point.
        
        """
        if self.points[p2]:
            # p2 is occupied
            return None
        if not self.points[p1]:
            # p1 is empty
            return None
        if ((p1[0]==p2[0] and abs(p1[1]-p2[1])==2) or
            (p1[1]==p2[1] and abs(p1[0]-p2[0])==2) or
            (abs(p1[0]-p2[0])==2 and abs(p1[1]-p2[1])==2)):
            return Point(int((p1[0]+p2[0])/2), int((p1[1]+p2[1])/2))


    def lookup_winning_moves(self):
        t, b=self.get_canonical_transposition()
        moves=_book_data.get(b.position_hash, None)
        if moves:
            moves=[(self.untranspose_point(m[0], t), self.untranspose_point(m[1], t)) for m in moves]
        return moves

    def get_winning_moves(self, use_book=True):
        """
        returns the moves that lead to a solution with exactly one closed peg.
        N.B.: this can be expensive.
        """
        if use_book:
            ret = self.lookup_winning_moves()
            if ret is not None:
                return ret
        ret=[]
        for m in self.possible_moves:
            b=self.clone_move(*m)
            for r in b.walk(lambda x: x.number==1):
                ret.append(m)
                break
        return ret
    
    @property
    def possible_moves(self):
        if self._possible_moves is not None:
            return self._possible_moves
        moves=[]
        for p in self.open_points:
            # find pairs of closed points adjacent
            # to this point.  
            x, y=p
            for p1, p2 in (((x-1, y-1), (x-2, y-2)),  # NW
                           ((x-1, y),   (x-2, y)),    # NE
                           ((x,   y-1), (x,   y-2)),  # E
                           ((x,   y+1), (x,   y+2)),  # W
                           ((x+1, y),   (x+2, y)),    # SW
                           ((x+1, y+1), (x+2, y+2))): # SE

                if self.points.get(p1) and self.points.get(p2):
                    # both are closed, it is a move
                    moves.append((Point(p2), Point(p)))
        self._possible_moves=moves
        return moves
        
    
def play_random_game(num_rows=5, open=None):
    """
    plays a totally random game.
    """
    b=Board(num_rows=num_rows)
    if open is None:
        open=random.choice(list(b.points))
    b.open(open)
    print "open:", open
    print b
    print
    while True:
        possible=b.possible_moves
        if not possible:
            break
        m=random.choice(possible)
        b.move(*m)
        print "%s -> %s" % m
        print b
        print

    print "number of closed points: %d" % len(b.closed_points)
    
        

#### routines for building book database ####

def _process_db(db, board, level, fail=False):
    print "in _process: level: %s, fail: %s" % (level, fail), board
    board=board.get_canonical_transposition()[1]
    hash=board.position_hash
    if fail:
        moves=[]
        db[hash]=''
        db.sync()
    elif not hash in db:
        moves=board.get_winning_moves(False)
        db[hash]=','.join(['%s%s' % m for m in moves])
        db.sync()
    else:
        moves=db[hash]
        moves=[(Point(m[:2]), Point(m[2:])) for m in moves.split(',')] if moves else []
    
    if level > 0:
        for m in board.possible_moves:
            _process_db(db, board.clone_move(*m), level-1, not m in moves)

            

def build_db(levels=6, path=DB_PATH, num_rows=5):
    """
    this builds the book database.  Takes a long time.
    """
    db=anydbm.open(path, 'c')
    for p in list(Board(num_rows=num_rows).points):
        b=Board(open=p, num_rows=num_rows)
        _process_db(db, b, levels)
    db.close()

def convert_db(dbfile, gzpath):
    db=anydbm.open(dbfile)
    fp=gzip.GzipFile(gzpath, 'wb')
    for k,v in db.iteritems():
        fp.write('%s %s\n' % (k, v))
    fp.close()
    


        
