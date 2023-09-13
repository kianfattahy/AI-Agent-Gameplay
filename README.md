# Colosseum Survival! with AI Agent

"Colosseum Survival!" is a strategic, turn-based game set on a chessboard. In this repository, I've showcased my custom AI agent, designed using the Monte Carlo Tree Search (MCTS) algorithm, to compete and excel in the game.

![Colosseum Image](https://cdn.britannica.com/36/162636-050-932C5D49/Colosseum-Rome-Italy.jpg?w=690&h=388&c=crop)

## Game Mechanics

Players move on an MxM chess board, taking turns. During each turn, a player can move in either a horizontal or vertical direction and then place a barrier around themselves. The objective is to control the largest territory on the board.

## AI Agent - StudentAgent

The `StudentAgent` uses the MCTS algorithm to predict the best moves. Dive into the `student_agent.py` file to see how the agent uses simulations to determine the next action.

## How to Play

1. **Setup**: Clone this repository and install any necessary dependencies.

    ```bash
    pip install -r requirements.txt
    ```

2. **Playing against the AI**: To challenge my AI agent:

    ```bash
    python simulator.py --player_1 human_agent --player_2 student_agent --display
    ```

3. **Simulate AI vs. Random Agent**: To see how the AI performs against a random agent:

    ```bash
    python simulator.py --player_1 random_agent --player_2 student_agent --display
    ```

4. **Autoplay multiple games**:

    ```bash
    python simulator.py --player_1 random_agent --player_2 student_agent --autoplay
    ```
