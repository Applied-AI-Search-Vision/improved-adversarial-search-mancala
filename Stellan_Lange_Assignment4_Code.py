#!/usr/bin/python          

import socket  
import numpy as np
import time
from multiprocessing.pool import ThreadPool
import os
import math

CHAMPION_ONE = 1
CHAMPION_TWO = 2
MAX_SIDE = list(range(0, 6))
MIN_SIDE = list(range(7, 13))
INFINITY = math.inf
OPPOSITE_HOLES_FOR_CAPTURE = {0: 12, 1: 11, 2: 10, 3: 9, 4: 8, 5: 7, 7: 5, 8: 4, 9: 3, 10: 2, 11: 1, 12: 0}

    

def utility(board, player):
    if player == CHAMPION_ONE:
        return board[6] + sum(board[remaining_rocks] for remaining_rocks in MAX_SIDE) - (board[13] + sum(board[remaining_rocks] for remaining_rocks in MIN_SIDE))
    elif player == CHAMPION_TWO:
        return board[13] + sum(board[remaining_rocks] for remaining_rocks in MIN_SIDE) - (board[6] + sum(board[remaining_rocks] for remaining_rocks in MAX_SIDE))


def max_value(board, depth):
    if depth == 0 or terminal_state(board):
        return utility(board, CHAMPION_ONE)

    v = -INFINITY 
    for hole in MAX_SIDE:
        if board[hole] != 0:
            new_board, extra_turn = make_champion_picked_hole(board, hole, CHAMPION_ONE)
            next_player = CHAMPION_ONE if extra_turn else CHAMPION_TWO
            if next_player == CHAMPION_ONE:
                v = max(v, max_value(new_board, depth - 1 if not extra_turn else depth))
            else:
                v = max(v, min_value(new_board, depth - 1 if not extra_turn else depth))
    return v

def min_value(board, depth):
    if depth == 0 or terminal_state(board):
        return utility(board, CHAMPION_TWO)

    v = INFINITY
    for hole in MIN_SIDE:
        if board[hole] != 0:
            new_board, extra_turn = make_champion_picked_hole(board, hole, CHAMPION_TWO)
            next_player = CHAMPION_TWO if extra_turn else CHAMPION_ONE
            if next_player == CHAMPION_TWO:
                v = min(v, min_value(new_board, depth - 1 if not extra_turn else depth))
            else:
                v = min(v, max_value(new_board, depth - 1 if not extra_turn else depth))
    return v



def minimax_decision_CHAMPION_ONE(current_board, depth):
    best_eval = -INFINITY
    best_move = None
    for hole in MAX_SIDE:
        if current_board[hole] != 0:
            new_board, extra_turn = make_champion_picked_hole(current_board, hole, CHAMPION_ONE)
            current_eval = max_value(new_board, depth - 1 if not extra_turn else depth) if extra_turn else min_value(new_board, depth - 1 if not extra_turn else depth)
            if current_eval > best_eval:
                best_eval = current_eval
                best_move = hole
    if best_move is not None:
        best_move += 1
    return str(best_move)

def minimax_decision_CHAMPION_TWO(current_board, depth):
    best_eval = INFINITY
    best_move = None
    for hole in MIN_SIDE:
        if current_board[hole] != 0:
            new_board, extra_turn = make_champion_picked_hole(current_board, hole, CHAMPION_TWO)
            current_eval = min_value(new_board, depth - 1 if not extra_turn else depth) if extra_turn else max_value(new_board, depth - 1 if not extra_turn else depth)
            if current_eval < best_eval:
                best_eval = current_eval
                best_move = hole
    if best_move is not None:
        best_move -= 6
    return str(best_move)


def terminal_state(board):
    no_more_stones = True
    for hole in range(0, 6):
        if board[hole] != 0:
            no_more_stones = False
            break
    if no_more_stones:
        return True
    
    no_more_stones = True
    for hole in range(7, 13):
        if board[hole] != 0:
            no_more_stones = False
            break
    if no_more_stones:
        return True



def make_champion_picked_hole(board, champion_picked_hole, player):
    new_board = board.copy()
    rocks = new_board[champion_picked_hole]
    new_board[champion_picked_hole] = 0
    hole_rock_is_thrown_into = champion_picked_hole 
    store = 6 if player == CHAMPION_ONE else 13

    while rocks > 0: 
        hole_rock_is_thrown_into += 1 
        if hole_rock_is_thrown_into == len(new_board): 
            hole_rock_is_thrown_into = 0

        if (player == CHAMPION_ONE and hole_rock_is_thrown_into == 13) or (player == CHAMPION_TWO and hole_rock_is_thrown_into == 6):
            continue

        new_board[hole_rock_is_thrown_into] += 1 
        rocks -= 1 

    last_hole = hole_rock_is_thrown_into
    player_side = last_hole in (MAX_SIDE if player == CHAMPION_ONE else MIN_SIDE)

    if player_side and new_board[last_hole] == 1:
        opposite_hole = OPPOSITE_HOLES_FOR_CAPTURE[last_hole]
        new_board[store] += new_board[opposite_hole] + 1 
        new_board[last_hole] = 0 
        new_board[opposite_hole] = 0

    if last_hole == store:
        extra_turn = True
    else:
        extra_turn = False


    return new_board, extra_turn



def receive(socket):
    msg = ''.encode()  

    try:
        data = socket.recv(1024)  
        msg += data
    except:
        pass
    return msg.decode()


def send(socket, msg):
    socket.sendall(msg.encode())


# VARIABLES
playerName = 'Stellan'
host = '127.0.0.1'
port = 30000  
s = socket.socket()  
pool = ThreadPool(processes=1)
gameEnd = False
MAX_RESPONSE_TIME = 20

print('The player: ' + playerName + ' starts!')
s.connect((host, port))
print('The player: ' + playerName + ' connected!')

while not gameEnd:

    asyncResult = pool.apply_async(receive, (s,))
    startTime = time.time()
    currentTime = 0
    received = 0
    data = []
    while received == 0 and currentTime < MAX_RESPONSE_TIME:
        if asyncResult.ready():
            data = asyncResult.get()
            received = 1
        currentTime = time.time() - startTime

    if received == 0:
        print('No response in ' + str(MAX_RESPONSE_TIME) + ' sec')
        gameEnd = 1

    if data == 'N':
        send(s, playerName)

    if data == 'E':
        gameEnd = 1

 
    if len(data) > 1:

        
        board = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        playerTurn = int(data[0])
        i = 0
        j = 1
        while i <= 13:
            board[i] = int(data[j]) * 10 + int(data[j + 1])
            i += 1
            j += 2

        # Using your intelligent bot, assign a champion_picked_hole to "champion_picked_hole"
        #
        # example: champion_picked_hole = '1';  Possible champion_picked_holes from '1' to '6' if the game's rules allows those champion_picked_holes.
        # TODO: Change this
        ################
        if playerTurn == CHAMPION_ONE:
            move = minimax_decision_CHAMPION_ONE(board, 2)
        else:  
            move = minimax_decision_CHAMPION_TWO(board, 2)
        send(s, move)

