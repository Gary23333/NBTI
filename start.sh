#!/bin/bash
# Start both backend and frontend servers

# Start backend in background
python server.py &
BACKEND_PID=$!

# Start frontend in foreground
python frontend_server.py 8080 &
FRONTEND_PID=$!

# Wait for either to exit
wait -n $BACKEND_PID $FRONTEND_PID
