#!/bin/bash

# Session and window names for tmux
SESSION_NAME="fastapi-server"
WINDOW_NAME="fastapi"

# Path to personal tmux configuration file
TMUX_CONF_PATH="$HOME/.config/tmux/.tmux.conf"

# Path where the actual tmux.conf file is stored for copying (Assuming it's in the same directory as this script)
SCRIPT_DIR=$(dirname "$0")
TMUX_SOURCE_PATH="$SCRIPT_DIR/tmux.conf"

# Path to FastAPI project root directory
PROJECT_DIR="$HOME/fastapi-sia-test"

# Path to the preferred YAML log config file
YAML_CONF_PATH="$PROJECT_DIR/scripts/uvicorn-log.yaml"

# Path to virtual environment activation script
VENV_ACTIVATE="$HOME/.cache/pypoetry/virtualenvs/remote-device-manager-j8jdVIT5-py3.12/bin/activate"

# Uvicorn command
UVICORN_CMD="export ENV=PROD && uvicorn src.main:app --reload --host 0.0.0.0 --port 5000 --log-config $YAML_CONF_PATH"

# --------------------------

# TMUX config file check and copy
echo "Checking for tmux configuration file..."
if [ ! -f "$TMUX_CONF_PATH" ]; then
    echo "Tmux config not found at $TMUX_CONF_PATH. Attempting to copy from $TMUX_SOURCE_PATH."
    
    # Ensuring the target directory exists before copying
    mkdir -p "$(dirname "$TMUX_CONF_PATH")"
    
    if [ -f "$TMUX_SOURCE_PATH" ]; then
        cp "$TMUX_SOURCE_PATH" "$TMUX_CONF_PATH"
        echo "Successfully copied default tmux config."
    else
        echo "ERROR: Tmux default config not found at $TMUX_SOURCE_PATH. Starting tmux without it."
        # If the copy fails, we proceed, but the custom config won't load.
    fi
fi

# TMUX session management and server start
# Check if the tmux session already exists
tmux has-session -t $SESSION_NAME 2>/dev/null

if [ $? != 0 ]; then
  echo "Tmux session '$SESSION_NAME' missing. Creating new session..."

  # Creating a new detached session, loading the custom config file
  tmux new-session -d -s $SESSION_NAME -n $WINDOW_NAME -c $PROJECT_DIR -f $TMUX_CONF_PATH

  # Sending commands to the first pane (index 0)
  # a. Activating the virtual environment
  tmux send-keys -t $SESSION_NAME:1 "source $VENV_ACTIVATE" C-m

  # b. Waiting a moment for the venv to activate
  sleep 2

  # c. Running the uvicorn server
  tmux send-keys -t $SESSION_NAME:1 "$UVICORN_CMD" C-m

  echo "FastAPI server started inside tmux session: $SESSION_NAME"
else
  echo "Tmux session '$SESSION_NAME' is already running. No changes applied."
fi

exit 0