# flappy-bird-NEAT-AI
Utilizes NEAT genetic algorithm to solve Flappy Bird. 

The game flappy bird was created using the Pygame library. The implementation of the NEAT network was created with the neat-python library.

The benefits of NEAT implementation are discussed [here](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.23.7372&rep=rep1&type=pdf)

The parameters of the network can be directly adjusted in the config.txt.

Run the flappy-bird.py directly to see the AI learn in real time. 

Smaller sample sizes (can be directly edited in the config.txt under ppp_size) can show the learning better as large population sizes ( > 50) often only require 1 or two generations to have perfect runs.
