# GameBoard

A simple python/JS GameBoard.

## Simple Setup
First, point the line 69 of html/index.html to the server runing server.py.
Then, serve the html folder on the network, and start server.py.

## Make it yours
To start the server with custom functionality, call ```startup_server(on_create, on_move, on_cmd)``` with three callbacks as arguments.

1) ```on_create```:
This function gets called whenever a new Board is created (at server startup and on game reset)
2) ```on_move```:
This function gets called whenever an online player makes a move
3) ```on_cmd```:
This function gets callled when an online player writes a message in the textbox

- In order to send a move to all connected clients, call the ```broadcast_move()``` function
- In order to send the current board to all connected clients, call the ```broadcast_board()``` function
- In order to send a message to all connected clients, call the ```broadcast_text()``` function

Enjoy!


Chess graphics taken from lichess-org/lila
