# flappy-bird-NEAT-AI
Utilizes NEAT genetic algorithm to have AI solve the game Flappy Bird. 

The game flappy bird was created using the Pygame library and the NEAT neural network was implemented with the [neat-python library](https://neat-python.readthedocs.io/en/latest/neat_overview.html).

The benefits of NEAT neural networks implementation are discussed [here](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.23.7372&rep=rep1&type=pdf)

The parameters of the network can be directly adjusted in the config.txt.

Simply run the flappy-bird.py file directly to run the game and see the AI learn in real time. 

Note: Smaller sample sizes (can be directly edited in the config.txt under ppp_size) can show the learning better as large population sizes ( > 50) often only require one or two generations to begin having perfect runs.
