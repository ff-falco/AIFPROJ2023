import numpy as np
import math

from typing import Tuple, List


NUM_TO_DIR_MAP = {
    0 : 'north',
    1 : 'east',
    2 : 'south',
    3 : 'west',
    4 : 'northeast',
    5 : 'southeast',
    6 : 'southwest',
    7 : 'northwest'
}

DIR_TO_NUM_MAP = {
    'north': 0,
    'east' : 1,
    'south': 2,
    'west' : 3,
    'northeast' : 4,
    'southeast' : 5,
    'southwest' : 6,
    'northwest' : 7,
}


def get_player_location(game_map: np.ndarray, symbol : str = "@") -> Tuple[int, int]:
    x, y = np.where(game_map == ord(symbol))
    return (x[0], y[0])

def get_target_location(game_map: np.ndarray, symbol : str = ">") -> Tuple[int, int]:
    x, y = np.where(game_map == ord(symbol))
    return (x[0], y[0])

def is_wall(position_element: int) -> bool:
    obstacles = "|- "
    return chr(position_element) in obstacles

def get_valid_moves(game_map: np.ndarray, current_position: Tuple[int, int]) -> List[Tuple[int, int]]:
    x_limit, y_limit = game_map.shape
    valid = []
    x, y = current_position    
    # North
    if y - 1 > 0 and not is_wall(game_map[x, y-1]):
        valid.append((x, y-1)) 
    # East
    if x + 1 < x_limit and not is_wall(game_map[x+1, y]):
        valid.append((x+1, y)) 
    # South
    if y + 1 < y_limit and not is_wall(game_map[x, y+1]):
        valid.append((x, y+1)) 
    # West
    if x - 1 > 0 and not is_wall(game_map[x-1, y]):
        valid.append((x-1, y))
     #NorthEast
    if x + 1 < x_limit and y - 1 > 0 and not is_wall(game_map[x+1, y-1]):
        valid.append((x+1,y-1))
    #SudEast
    if x + 1 < x_limit and y + 1 < y_limit and not is_wall(game_map[x+1, y+1]):
        valid.append((x+1,y+1))
    #SudWest
    if x - 1 > 0 and y + 1 < y_limit and not is_wall(game_map[x-1, y+1]):
        valid.append((x-1,y+1))
    # NorthWest
    if x - 1 > 0 and y - 1 > 0 and not is_wall(game_map[x-1, y-1]):
        valid.append((x-1,y-1))

    return valid


def actions_from_path(start: Tuple[int, int], path: List[Tuple[int, int]]) -> List[int]:
    action_map = {
        "N": 0,
        "E": 1,
        "S": 2,
        "W": 3,
        "NE": 4,
        "SE": 5,
        "SW": 6,
        "NW": 7,

    }
    actions = []
    x_s, y_s = start
    for (x, y) in path:
        if x_s == x:
            if y < y_s:
                actions.append(action_map["W"])
            else: actions.append(action_map["E"])
        elif y_s == y:
            if x < x_s:
                actions.append(action_map["N"])
            else: actions.append(action_map["S"])
        elif x < x_s : #northSomething
            if y < y_s : 
                actions.append(action_map["NW"])
            else : actions.append(action_map["NE"])
        elif x > x_s :
            if y < y_s :
                actions.append(action_map["SW"])
            else : actions.append(action_map["SE"])
            
        x_s = x
        y_s = y
    
    return actions

def chebyshev_distance(point1: Tuple[int, int], point2: Tuple[int, int]) -> int:
    x1, y1 = point1
    x2, y2 = point2
    return max(abs(x1 - x2),abs(y1 - y2))

def get_money_location(des_file) :
    locations = list()
    for line in des_file.splitlines() :
        if 'GOLD' in line :
            amount, pos = line.split(',',1)
            amount = int(amount.split()[1])
            (x,y) = eval(pos)
            locations.append((amount,(y,x)))
    return locations

def get_closest_gold(gold_pos_list,start_pos) :
    #computes chebyshev distance to find closest gold
    #since we are using an Heuristic, it is not necessarily the best
    min_dist = float('infinity')
    min_dest = None
    for gold_pos in gold_pos_list :
        curr_dist = chebyshev_distance(start_pos,gold_pos)
        if curr_dist < min_dist :
            min_dist = curr_dist
            min_dest = gold_pos

    return min_dest

def get_stair_location(des_file) :
     for line in des_file.splitlines() :
        if 'STAIR' in line and 'down' in line :
            pos= line.split(':',1)[1].split(')')[0] +')'
            (x,y) = eval(pos)
            return (y,x)
        
def get_reference_des(des_file) :
    for line in des_file.splitlines() :
        if 'amulet of ESP' in line :
            #OBJECT:('"',"amulet of ESP"),(1, 1)
            pos = '(' + line.split('(')[2]
            (x,y) = eval(pos)
            return (y,x)
        