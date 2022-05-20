from dataclasses import dataclass
from enum import Enum

import asyncio
import json
import websockets

class Bbool(str, Enum):
    false = "false"
    true = "true"

@dataclass
class Piece:
    id: int # Maybe not necessary
    x_pos: float # distance of left edge to board in percent
    y_pos: float # distance of top edge to board in percent
    z_pos: int = 0 # css z of element
    height: float|Bbool = Bbool.false # Height in percent of board
    width: float|Bbool = Bbool.false # Width in percent of board
    image_url: str|Bbool = Bbool.false
    dragable: bool = False #True := Can be draged when active, False := Can be clicked when active
    owner_id: int|Bbool = Bbool.false # Piece is interactable when it is "owner"'s turn or if "owner" is true
    hover_text: str|Bbool = Bbool.false

@dataclass
class Player:
    id: int # Maybe not necessary
    colour: str # Colour in the "#rrggbb" format

class Move:
    player_id: int
    piece_id: int
    to_x: float
    to_y: float

    def __init__(self, player_id, piece_id, to_x, to_y) -> None:
        self.player_id = player_id
        self.piece_id = piece_id
        self.to_x = to_x
        self.to_y = to_y

    def to_json(self):
        return '{"type":"move","piece_id":'+str(self.piece_id)+',"to_x":'+str(self.to_x)+',"to_y":'+str(self.to_y)+'}'

class Board:
    players: list[Player]
    pieces: list[Piece]
    current_player: int|Bbool
    moves: list[Move]

    def __init__(self) -> None:
        callback[0](self)

    def to_json(self) -> str:
        # retval = '{"players":'+self.players+'"current_player":'+str(self.current_player)+'}'

        players = ''
        for player in self.players:
            players += json.dumps(player.__dict__) + ','

        pieces = ''
        for piece in self.pieces:
            pieces += json.dumps(piece.__dict__) + ','
        
        current_player = '"'+self.current_player.name+'"' if isinstance(self.current_player, Bbool) else str(self.current_player)

        retval = '{"type":"board","players":['+players.rstrip(',')+'],"pieces":['+pieces.rstrip(',')+'],"current_player":'+current_player+'}'
        return retval


clients = []
callback = [] # 0: on_create 1: on_move; 2: on_cmd


async def broadcast_move(move:Move):
    board.moves.append(move)
    for client in clients:
        await client.send(move.to_json())

async def broadcast_board():
    for client in clients:
        await client.send(board.to_json())

async def broadcast_text(text:str):
    for client in clients:
        await client.send('{"type":"text","content":"'+text+'"}')

async def handler(websocket):
    clients.append(websocket)
    try:
        await websocket.send(board.to_json())
        async for message in websocket:
            await on_message(message)
    finally:
        clients.remove(websocket)
        print(len(clients))


async def startup_server(on_create_function, on_move_function, on_cmd_function):
    global board
    callback.append(on_create_function)
    callback.append(on_move_function)
    callback.append(on_cmd_function)
    board = Board()
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()  # run forever

async def on_message(message_str: str):
    try:
        message = json.loads(message_str)
    except:
        await broadcast_text("No Json found in message")
    else:
        if "type" in message:
            if message["type"] == "set_move": #{"type":"set_move","player_id":0,"piece_id":0,"to_x":0,"to_y":12.5}
                move = move_from_json(message)
                await callback[1](move)
            if message["type"] == "set_cmd": #{"type":"set_cmd","cmd":"restart"}
                await callback[2](message["cmd"])

def move_from_json(message: dict) -> Move:
    return Move(message["player_id"],message["piece_id"],message["to_x"],message["to_y"])


##### -------------------------- DEMO Implementations

async def main():
    await startup_server(on_create, on_move, on_cmd)

def on_create(board:Board):
    board.players = [Player(0,"#FFFFFF"), Player(1,"#000000")]

    board.pieces = []
    add_piece_square(board.pieces,0,0,"board/maple.jpg",-10,8,8,False)

    add_piece_square(board.pieces,0,0,"cburnett/bR.svg")
    add_piece_square(board.pieces,1,0,"cburnett/bN.svg")
    add_piece_square(board.pieces,2,0,"cburnett/bB.svg")
    add_piece_square(board.pieces,3,0,"cburnett/bQ.svg")
    add_piece_square(board.pieces,4,0,"cburnett/bK.svg")
    add_piece_square(board.pieces,5,0,"cburnett/bB.svg")
    add_piece_square(board.pieces,6,0,"cburnett/bN.svg")
    add_piece_square(board.pieces,7,0,"cburnett/bR.svg")

    for i in range(8):
        add_piece_square(board.pieces,i,1,"cburnett/bP.svg")
    for i in range(8):
        add_piece_square(board.pieces,i,6,"cburnett/wP.svg")
    
    add_piece_square(board.pieces,0,7,"cburnett/wR.svg")
    add_piece_square(board.pieces,1,7,"cburnett/wN.svg")
    add_piece_square(board.pieces,2,7,"cburnett/wB.svg")
    add_piece_square(board.pieces,3,7,"cburnett/wQ.svg")
    add_piece_square(board.pieces,4,7,"cburnett/wK.svg")
    add_piece_square(board.pieces,5,7,"cburnett/wB.svg")
    add_piece_square(board.pieces,6,7,"cburnett/wN.svg")
    add_piece_square(board.pieces,7,7,"cburnett/wR.svg")

    board.current_player = Bbool.false
    board.moves = []

def add_piece_square(pieces:list[Piece],x:float,y:float,img:str,z:int=0,size_x:float=1,size_y:float=1,dragable:bool=True):
    n=8
    x_gap_left = 10
    x_gap_right = 10
    y_gap_top = 10
    y_gap_bot = 10
    pieces.append(Piece(len(pieces),
        x_gap_left+(100-x_gap_left-x_gap_right)*x/n,
        y_gap_top+(100-y_gap_top-y_gap_bot)*y/n,
        z,
        (100-x_gap_left-x_gap_right)*size_x/n,
        (100-y_gap_top-y_gap_bot)*size_y/n,
        img,
        dragable))

async def on_move(input_move:Move):
    move = Move(input_move.player_id, input_move.piece_id,
        round((input_move.to_x-10)/10)*10+10,
        round((input_move.to_y-10)/10)*10+10)
    board.pieces[move.piece_id].x_pos = move.to_x
    board.pieces[move.piece_id].y_pos = move.to_y
    await broadcast_move(move)

async def on_cmd(cmd:str):
    if cmd == "restart":
        global board 
        board = Board()
        await broadcast_board()
        await broadcast_text("Reset Complete<br><hr>")
    else:
        await broadcast_text("Unknown cmd")

if __name__ == "__main__":
    asyncio.run(main())



#python -m websockets ws://localhost:8001/