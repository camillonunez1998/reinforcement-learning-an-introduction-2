#######################################################################
# Copyright (C)                                                       #
# 2016-2018 Shangtong Zhang(zhangshangtong.cpp@gmail.com)             #
# 2016 Tian Jun(tianjun.cpp@gmail.com)                                #
# 2016 Artem Oboturov(oboturov@gmail.com)                             #
# 2016 Kenta Shimada(hyperkentakun@gmail.com)                         #
# Permission given to modify the code as long as you keep this        #
# declaration at the top                                              #
#######################################################################
# Modified to include solution to programming exercises in Sutton&Barto 2018 edition.

import pdb
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from tqdm import trange

matplotlib.use('Agg')


class Bandit:
    # @k_arm: # of arms
    # @epsilon: probability for exploration in epsilon-greedy algorithm
    # @initial: initial estimation for each action
    # @step_size: constant step size for updating estimations
    # @sample_averages: if True, use sample averages to update estimations instead of constant step size
    # @UCB_param: if not None, use UCB algorithm to select action
    # @gradient: if True, use gradient based bandit algorithm
    # @gradient_baseline: if True, use average reward as baseline for gradient based bandit algorithm
    def __init__(self, k_arm=10, epsilon=0., initial=0., step_size=0.1, sample_averages=False, UCB_param=None,
                 gradient=False, gradient_baseline=False, true_reward=0., random_walk=False):
        self.k = k_arm
        self.step_size = step_size
        self.sample_averages = sample_averages
        self.indices = np.arange(self.k)
        self.time = 0
        self.UCB_param = UCB_param
        self.gradient = gradient
        self.gradient_baseline = gradient_baseline
        self.average_reward = 0
        self.true_reward = true_reward
        self.epsilon = epsilon
        self.initial = initial
        self.random_walk = random_walk

    def reset(self):
        # real reward for each action
        ###Aqui sencillamente lo que hacen es inicializar los q_i's igual que en la
        ###figura 2.1 del libro, tienen promedio 0 y varianza 1.
        self.q_true = np.random.randn(self.k) + self.true_reward

        # estimation for each action
        self.q_estimation = np.zeros(self.k) + self.initial

        # # of chosen times for each action
        self.action_count = np.zeros(self.k)

        self.best_action = np.argmax(self.q_true)

        ###Asignamos a self.best_action un vector conteniendo las mejores acciones
        self.best_action = np.where(self.q_true == np.max(self.q_true))[0]

        self.time = 0

    # get an action for this bandit
    def act(self):
        if np.random.rand() < self.epsilon:
            return np.random.choice(self.indices)

        if self.UCB_param is not None:
            UCB_estimation = self.q_estimation + \
                             self.UCB_param * np.sqrt(np.log(self.time + 1) / (self.action_count + 1e-5))
            q_best = np.max(UCB_estimation)
            return np.random.choice(np.where(UCB_estimation == q_best)[0])

        if self.gradient:
            exp_est = np.exp(self.q_estimation)
            self.action_prob = exp_est / np.sum(exp_est)
            return np.random.choice(self.indices, p=self.action_prob)
###Aqui devuelve una accion aleatoria dentro de las que tienen mejor estimacion hasta el
###momento. 
        q_best = np.max(self.q_estimation)
        return np.random.choice(np.where(self.q_estimation == q_best)[0])

    # take an action, update estimation for this action
    def step(self, action):
        # generate the reward under N(real reward, 1)
        reward = np.random.randn() + self.q_true[action]
        self.time += 1
        self.action_count[action] += 1
        self.average_reward += (reward - self.average_reward) / self.time

        if self.sample_averages:
            # update estimation using sample averages
            self.q_estimation[action] += (reward - self.q_estimation[action]) / self.action_count[action]
        elif self.gradient:
            one_hot = np.zeros(self.k)
            one_hot[action] = 1
            if self.gradient_baseline:
                baseline = self.average_reward
            else:
                baseline = 0
            self.q_estimation += self.step_size * (reward - baseline) * (one_hot - self.action_prob)
        else:
            # update estimation with constant step size
            self.q_estimation[action] += self.step_size * (reward - self.q_estimation[action])

        if self.random_walk:
            self.q_true = np.add(self.q_true, np.random.normal(0, 0.01, self.k))
            self.best_action = np.where(self.q_true == np.max(self.q_true))[0]

        return reward


def simulate(runs, time, bandits):
    rewards = np.zeros((len(bandits), runs, time))
    best_action_counts = np.zeros(rewards.shape)
    for i, bandit in enumerate(bandits):
        for r in trange(runs):
            bandit.reset()
            for t in range(time):
                action = bandit.act()
                reward = bandit.step(action)
                rewards[i, r, t] = reward
                if action in bandit.best_action:
                    best_action_counts[i, r, t] = 1
    mean_best_action_counts = best_action_counts.mean(axis=1)
    mean_rewards = rewards.mean(axis=1)
    return mean_best_action_counts, mean_rewards

def exercise_2_5_figure_e_2_5(runs=2000, time=10000):
    bandits = []
    bandits.append(Bandit(epsilon=0.1, step_size=0.1))
    bandits.append(Bandit(epsilon=0.1, sample_averages=True))
    bandits.append(Bandit(epsilon=0.1, step_size=0.1, random_walk=True))
    bandits.append(Bandit(epsilon=0.1, sample_averages=True, random_walk=True))
    best_action_counts, average_rewards = simulate(runs, time, bandits)
    # rewards = np.mean(average_rewards, axis=1)

    plt.figure(figsize=(10, 20))

    ###2 subplots, 1 columna, primer subplot
    plt.subplot(2, 1, 1)
    plt.plot(average_rewards[0], label='$\\alpha = 0.1$')
    plt.plot(average_rewards[1], label='Sample averages')
    plt.plot(average_rewards[2], label='$\\alpha = 0.1$ Random walk')
    plt.plot(average_rewards[3], label='Sample averages Random walk')
    plt.xlabel('steps')
    plt.ylabel('average reward')
    plt.legend()

    plt.subplot(2, 1, 2)
    plt.plot(best_action_counts[0], label='$\\alpha = 0.1$')
    plt.plot(best_action_counts[1], label='Sample averages')
    plt.plot(best_action_counts[2], label='$\\alpha = 0.1$ Random walk')
    plt.plot(best_action_counts[3], label='Sample averages Random walk')
    plt.xlabel('steps')
    plt.ylabel('% optimal action')
    plt.legend()

    plt.savefig('./images/figure_e_2_5.png')
    plt.close()


def exercise_2_11_figure_e_2_11(runs=2000, time=1000):
    labels = ['$\epsilon$-greedy sample avrg', '$\epsilon$-greedy $\\alpha=0.1$', '$\epsilon$-greedy $\\alpha=0.01$', 'gradient bandit',
              'UCB', 'optimistic initialization']
    generators = [lambda epsilon: Bandit(epsilon=epsilon, sample_averages=True, random_walk=True),
                  lambda epsilon: Bandit(epsilon=epsilon, step_size=0.1, random_walk=True),
                  lambda epsilon: Bandit(epsilon=epsilon, step_size=0.01, random_walk=True),
                  lambda alpha: Bandit(gradient=True, step_size=alpha, gradient_baseline=True, random_walk=True),
                  lambda coef: Bandit(epsilon=0, UCB_param=coef, sample_averages=True, random_walk=True),
                  lambda initial: Bandit(epsilon=0, initial=initial, step_size=0.1, random_walk=True)]

    parameters = [np.arange(-7, -1, dtype=float),
                  np.arange(-7, -1, dtype=float),
                  np.arange(-7, -1, dtype=float),
                  np.arange(-5, 2, dtype=float),
                  np.arange(-4, 3, dtype=float),
                  np.arange(-2, 3, dtype=float)]

    bandits = []
    for generator, parameter in zip(generators, parameters):
        for param in parameter:
            bandits.append(generator(pow(2, param)))

    _, average_rewards = simulate(runs, time, bandits)

    rewards = np.mean(average_rewards[:, :500], axis=1)

    i = 0
    for label, parameter in zip(labels, parameters):
        l = len(parameter)
        plt.plot(parameter, rewards[i:i + l], label=label)
        i += l
    plt.xlabel('Parameter($2^x$)')
    plt.ylabel('Average reward')
    plt.legend()

    plt.savefig('./images/figure_e_2_11.png')
    plt.close()


if __name__ == '__main__':

    #exercise_2_5_figure_e_2_5()
    exercise_2_11_figure_e_2_11()
