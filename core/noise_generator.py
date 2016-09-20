# -*- coding: utf-8 -*-
"""

@author: sigaud
"""
import random

class noise_generator(object):
    """
    A noise generator from adding noise to actions
    """
    def __init__(self, logger = None):
        self.noise = 0
        self.alpha = 0.6
        self.beta = 0.4

    def sample(self):
        '''
        Ornstein-Uhlenbeck random Process
        '''
        x = self.x_prev + self.theta * (self.mu - self.x_prev) * self.dt + self.current_sigma * np.sqrt(self.dt) * np.random.normal(size=self.size)
        self.x_prev = x
        self.n_steps += 1
        return x

    def update_noise(self):
        self.noise = self.get_sample()

    def increase_noise(self):
        self.beta = self.beta*1.02

    def decrease_noise(self):
        self.beta = self.beta*0.7

    def get_sample(self):
        return self.beta*(self.noise + random.gauss(0,1))

    def add_noise(self,action_vector):
        noisy_action = []
        self.update_noise()
        for i in range(len(action_vector)):
            noisy_action.append(action_vector[i]+self.get_sample())
        return noisy_action
