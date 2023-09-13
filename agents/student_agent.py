# Student agent: Add your own agent here
from agents.agent import Agent
from store import register_agent
from copy import deepcopy
import numpy as np
import time
import sys
from collections import defaultdict


@register_agent("student_agent")
class StudentAgent(Agent):
    def __init__(self):
        super(StudentAgent, self).__init__()
        self.name = "StudentAgent"
        self.dir_map = {
            "u": 0,
            "r": 1,
            "d": 2,
            "l": 3,
        }

        self.autoplay = True
        self.root = None

    def step(self, chess_board, my_pos, adv_pos, max_step):
        start_time = time.time()
        state = MCTSState(chess_board,my_pos,adv_pos,max_step, True)
        turn_time = 2

        if not self.root:
            self.root = MCTSNode(state,None,None)
            turn_time = 29.97
        else:
            self.root = self.root.find_opponent_node(state)
        
        self.root = self.root.best_action(turn_time)
        self.root.parent = None

        if self.root.state.gg:
            move = self.root.parent_move
            self.root = None
            return move

        # print("NEW MOVE")
        print("this turn took ", time.time() - start_time, "seconds")
        return self.root.parent_move
    
class MCTSState():
    def __init__(self,chess_board,my_pos, adv_pos,max_step,my_move):
        self.chess_board = chess_board
        self.my_pos = my_pos
        self.adv_pos = adv_pos
        self.max_step = max_step
        self.gg = True
        self.my_move = my_move

        self.my_moves = self.find_possible_moves(my_pos)
        self.adv_moves = self.find_possible_moves(adv_pos)

        # print("my moves: ", self.my_moves)
        # print("adv moves: ", self.adv_moves)

        my_visited = {my_pos: True}
        adv_visited = {adv_pos: True}
        if my_move:
            self.bfs_me([my_pos],[0],[adv_pos],[0],my_visited,adv_visited,1)
        else:
            self.bfs_adv([my_pos],[0],[adv_pos],[0],my_visited,adv_visited,1)

        self.my_squares = my_visited.keys()
        self.adv_squares = adv_visited.keys()
        
        # print("\n",self.gg)
        # print("mys: ",len(self.my_squares))
        # print("advs: ",len(self.adv_squares))
        # print("tot: ",len(self.my_squares) + len(self.adv_squares))


        # self.eval = len(self.my_squares) / (len(self.adv_squares) + len(self.my_squares))
        self.eval = 0
        if len(self.my_squares) > len(self.adv_squares):
            self.eval = 1
        elif len(self.my_squares) < len(self.adv_squares):
            self.eval = -1

    def is_valid(self, point):
        return not (point[0] < 0 or 
                    point[1] < 0 or
                    point[0] >= len(self.chess_board) or 
                    point[1] >= len(self.chess_board[0]))

    def bfs_me(self, a_q, a_d, b_q, b_d, a_visited, b_visited, step_count):
        dirs = [(-1,0),(0,1),(1,0),(0,-1)]
        b = self.chess_board
        while len(a_q) > 0 and a_d and a_d[0] <= step_count:
            cell = a_q[0]
            del a_q[0]
            distance = a_d[0]
            del a_d[0]

            x = cell[0]
            y = cell[1]
            
            for i,(dx,dy) in enumerate(dirs):
                new_x = x + dx
                new_y = y + dy
                if (self.is_valid((new_x,new_y)) and 
                   (not b[x][y][i])):

                    if (new_x,new_y) in b_visited:
                        self.gg = False
                    elif not (new_x,new_y) in a_visited:
                        a_d.append(distance+1)
                        a_q.append((new_x,new_y))
                        a_visited[(new_x,new_y)] = True
        
        if not self.my_move:
            step_count += 1

        if len(b_q) > 0:
            self.bfs_adv(a_q,a_d,b_q,b_d,a_visited,b_visited, step_count)

    def bfs_adv(self, a_q, a_d, b_q, b_d, a_visited, b_visited, step_count):
        dirs = [(-1,0),(0,1),(1,0),(0,-1)]
        b = self.chess_board
        while len(b_q) > 0 and b_d and b_d[0] <= step_count:
            cell = b_q[0]
            del b_q[0]
            distance = b_d[0]
            del b_d[0]

            x = cell[0]
            y = cell[1]
            
            for i,(dx,dy) in enumerate(dirs):
                new_x = x + dx
                new_y = y + dy
       
                if (self.is_valid((new_x,new_y)) and 
                   (not b[x][y][i])):

                    if (new_x,new_y) in a_visited:
                        self.gg = False
                    elif not (new_x,new_y) in b_visited:
                        b_d.append(distance+1)
                        b_q.append((new_x,new_y))
                        b_visited[(new_x,new_y)] = True
        
        if self.my_move:
            step_count += 1

        if len(a_q) > 0:
            self.bfs_me(a_q,a_d,b_q,b_d,a_visited,b_visited, step_count)

    def find_possible_moves(self, p):
        b = self.chess_board
        q = [p]
        distances = [0]
        visited = {p:True}
        dirs = [(-1,0),(0,1),(1,0),(0,-1)]
        while len(q) > 0:
            cell = q[0]
            del q[0]
            distance = distances[0]
            del distances[0]

            x = cell[0]
            y = cell[1]

            if distance + 1 > self.max_step:
                continue

            for i,(dx,dy) in enumerate(dirs):
                new_x = x + dx
                new_y = y + dy

                if (not (new_x,new_y) in visited and 
                    self.is_valid((new_x,new_y)) and 
                    (not b[x][y][i]) and 
                    ((self.my_move and not (new_x,new_y) == self.adv_pos) or
                    not self.my_move and not (new_x,new_y) == self.my_pos)):

                    distances.append(distance+1)
                    q.append((new_x,new_y))
                    visited[(new_x,new_y)] = True
        
        m = []
        for cell in list(visited.keys()):
            m += self.all_moves_for_cell(cell) 

        return m
        
    def all_moves_for_cell(self, cell):
        moves = []
        for d,direction in enumerate(self.chess_board[cell[0]][cell[1]]):
            if not direction:
                moves.append((cell,d))
        return moves

    def game_result(self): 
        return self.eval
 
    def get_next_state(self,move):
        dirs = [(-1,0),(0,1),(1,0),(0,-1)]
        temp = deepcopy(self.chess_board)
        point = move[0]
        d = move[1]
        temp[point[0]][point[1]][d] = True
        temp[point[0] + dirs[d][0]][point[1] + dirs[d][1]][(d+2)%4] = True

        if self.my_move:
            return MCTSState(temp,point,self.adv_pos,self.max_step,False)
        return MCTSState(temp,self.my_pos,point,self.max_step, True)

    def get_possible_moves(self):
        if self.my_move:
            return self.my_moves
        else: 
            return self.adv_moves

class MCTSNode():
    def __init__(self, state, parent, parent_move):
        self.state = state
        self.parent = parent
        self.parent_move = parent_move
        self.children = []
        self.n_visits = 0
        self.results = defaultdict(int)
        self.results[1] = 0
        self.results[-1] = 0
        self.unvisited_moves = deepcopy(state.get_possible_moves())

    def add_node(self):
        move = self.unvisited_moves.pop()
        child_node = MCTSNode(self.state.get_next_state(move), self, move)
        self.children.append(child_node)
        return child_node 

    def rollout(self):
        r_state = self.state
        while not r_state.gg:
            possible_moves = r_state.get_possible_moves()
            move = possible_moves[np.random.randint(len(possible_moves))]
            r_state = r_state.get_next_state(move)
        return r_state.game_result()

        # eval = r_state.game_result()
        # if eval > 0.5:
        #     return 1
        # elif eval < 0.5:
        #     return -1
        # return 0

    def bp(self, result):
        self.n_visits += 1.
        self.results[result] += 1.
        if self.parent:
            self.parent.bp(result)
 
    def get_value(self):
        return (self.results[1] - self.results[-1]) / self.n_visits

    def best_child(self, c=0.2):
        w = [child.get_value() + c * np.sqrt((np.log(self.n_visits) / child.n_visits)) for child in self.children]
        if not self.state.my_move:
            return self.children[np.argmin(w)]
        else: 
            return self.children[np.argmax(w)]

    def tp(self):
        node = self
        while not node.state.gg:
            if not len(node.unvisited_moves) == 0:
                return node.add_node()
            else:
                node = node.best_child()
        return node

    def best_action(self, time_delta):
        end_time = time.time() + time_delta - 0.03

        while time.time() < end_time:
            node = self.tp()
            node.bp(node.rollout())

        return self.best_child(c=0.)

    def find_opponent_node(self,state):
        for c in self.children:
            if (np.array_equal(c.state.chess_board,state.chess_board) and
                c.state.my_pos == state.my_pos and
                c.state.adv_pos == state.adv_pos):
                # print("FOUND CHILD")
                return c

        return MCTSNode(state,None,None)