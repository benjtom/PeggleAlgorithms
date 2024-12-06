
# Team Members:
Ben Tomlinson

# Dependencies
    gymnasium==0.29.1
    numpy==1.23.5
    pygame==2.6.1
    stable_baselines3==2.3.2

# Features
This project contains 3 main parts:
1. A custom Peggle gymnasium environment (gym_peggle/envs/peggle.py) and a Python notebook file (peggle.ipynb) that is used to train and test the RL models
2. A script that enables alternate algorithms (such as optimal stopping) to play games in the Peggle environment (peggle_optimal_stop.py)
3. A version of the Peggle environment that is playable by humans (peggle_human.py)

# Running Instructions - Reinforcement Learning
Navigate to 'peggle.ipynb'.

Run the following code cell to import the necessary packages:
```
import gymnasium as gym
import gym_peggle
import stable_baselines3
from stable_baselines3 import PPO
```

Run the following code cell if you want to load the existing model:
NOTE: Due to github's file size constraints, I was unable to push the model that was validated for the final project report.
```
env = gym.make('Peggle')

model = PPO.load("./models/PPO_BounceShots.zip", env=env)
```

Alternatively, run the following code cell if you want to train a new model similar to the one used in the report:
```
env = gym.make('Peggle')

model = PPO("MlpPolicy", env, verbose=1, device='cuda')
model.learn(total_timesteps=100000)
```

Run this line of code to save a model that you trained:
```
model.save("./models/PPO_BounceShots.zip")
```

Finally, run the last code cell to have your model play 30 episodes of Peggle. You can change the number of episodes.
If you want to watch the model play, change the env's render mode to "human". (see commented-out code)

Output: Average reward, average number of pegs hit, and number of total misses for the given number of episodes.


# Running Instructions - Other Algorithms
Run 'peggle_optimal_stop.py'. If running from the command line, you can provide up to three arguments:

    python3 peggle_optimal_stop.py <mode> <num_simulations> <render>

"mode" is the type of algorithm that you would like to play the game. There are 4 options:
1. "optimal-stop" : The modified optimal stop algorithm that is described in the final report.
2. "default" : The algorithm which was approximated from the behavior of the opponents in the original Peggle game.
3. "perfect" : Every shot taken will be the best shot possible.
4. "random" : Every shot will be random.

"num_simulations" is how many games or episodes you would like the algorithm to play.

"render" specifies whether or not you would like the PyGame window to appear and render the games.
Leave this argument blank if you don't want it to render, or type "true" or "render" if you would like it to render.

These are the default arguments if no arguments are provided:
    mode = "optimal-stop'
    num_simulations = 1
    render = False

Output: The average number of pegs hit over the given number of game simulations. Any time a “total miss” happens (rarely), it is reported as well.

# Running Instructions - Human Playable Game
Simply run 'peggle_human.py'.

Controls:
Left/Right arrow keys = adjust aim
Enter = Fire





