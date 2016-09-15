# -*- coding: utf-8 -*-
"""
Created on Sat Jun 25 16:31:15 2016

@author: arnaud
"""
import tensorflow as tf
import math
import random

from DDPG.core.networks.helper.tf_session_handler import getSession 

def variable_summaries(var, name):
  """Attach a lot of summaries to a Tensor."""
  with tf.name_scope('summaries'):
    mean = tf.reduce_mean(var)
    tf.scalar_summary('mean of ' + name, mean)
    tf.scalar_summary('max of ' + name, tf.reduce_max(var))
    tf.scalar_summary('min of ' + name, tf.reduce_min(var))
    tf.histogram_summary(name, var)

def create_weight(shape, trainable = True):
    """
    create a weight for the neural network
    question: why write trainable=trainable instead of just trainable
    question: why stddev = 0.1. Was it tuned?
    """
    with tf.name_scope('weight'):
        return tf.Variable(tf.truncated_normal(shape, stddev=0.1), trainable)

def create_bias(shape, name, trainable = True):
    """
    create a bias for the neural network
    question: why write trainable=trainable instead of just trainable
    question: why bias = 0.1. Was it tuned?
    """
    with tf.name_scope('bias'):
        bias = tf.Variable(tf.constant(0.1, shape=shape), trainable) # was 0.1
        variable_summaries(bias,'bias' + name)
        return bias

""" fully_connected_layer :
    A generic network class
        graph : the tensorflow graph in which the network should be added
        input_layers : A tensorflow tensor or list of tensorflow tensor to connect 
                        to this network as inputs
        size : the configuration of the network : list of size for each successive 
                layer, the last one is the output of the network.
                
        Optional parameters :
        
        function : a tensorflow operation or list of tensorflow operations (if list, it shoulf be of the same size as size)
                    if None somewhere, it will not add an operation.
        normalization : same as function but for normalization.
        input_layers_connections : if multiple inputs, can be used to specify to wich layer should each inputs (in the order of input_layers)
                                    should be connected (at least one value must be 0).
        trainable : specify if the weights should be updated through any optimizer
        weight_init_range : list of ranges (list of lower and upper bounds) for random initialisation of each layer's weights. 
                            If the range given for one layer is none, range will be automatically computed according to the fan_in of the layer.
"""
class fully_connected_network:
    def __init__(self, input_layers, size, function=None, normalization=None, input_layers_connections=None, trainable=True, weight_init_range=None, shared_parameters = None, cloned_parameters = None):
        self.params = []
        self.layers = []
        self.b = []
        self.w = []
        self.input_layers=input_layers
        if not isinstance(input_layers, list):
            self.graph = input_layers.graph
        else:
            self.graph = input_layers[0].graph
        with self.graph.as_default():
            
            if not isinstance(input_layers, list):
                input_layers = [input_layers]
            
            if input_layers_connections==None:
                input_layers_connections = []
                for i in range(len(input_layers)):
                    input_layers_connections.append(0)
            self.input_layers_connections = input_layers_connections
            
            if not isinstance(function, list):
                f = function
                function = []
                for i in range(len(size)):
                    function.append(f)
            self.functions = function
            
            if not isinstance(normalization, list):
                n = normalization
                normalization = []
                for i in range(len(size)):
                    normalization.append(n)
            self.normalizations = normalization
            
            if weight_init_range==None:
                weight_init_range=[]
                for i in range(len(size)):
                    weight_init_range.append(None)
            
            last_layer = []
            for i in range(len(size)):
                for l in range(len(input_layers)):
                    if input_layers_connections[l]==i:
                        last_layer.append(input_layers[l])
                if len(last_layer)==0:
                    raise Exception("Fully Connected Layer creation exception", "No connections to the last layer")
                if shared_parameters != None:
                    bias = shared_parameters[len(self.params)]
                elif cloned_parameters != None:
                    bias =  tf.Variable(cloned_parameters[len(self.params)])
                else:
                    bias = create_bias([size[i]], str(random.random()), trainable)
                self.params.append(bias)
                self.b.append(bias)
                layer = bias
                fan_in=0
                for l in last_layer:
                    fan_in+=l.get_shape()[-1].value
                self.w.append([])
                for l in last_layer:
                    if shared_parameters != None:
                        weight = shared_parameters[len(self.params)]
                    elif cloned_parameters != None:
                        weight =  tf.Variable(cloned_parameters[len(self.params)])
                    elif weight_init_range[i]==None:
                        weight = tf.Variable(tf.random_uniform([l.get_shape()[-1].value, size[i]], -1/math.sqrt(fan_in), 1/math.sqrt(fan_in)), trainable=trainable) #create_weight([l.get_shape()[-1].value, size[i]], trainable)
                    else:
                        weight = tf.Variable(tf.random_uniform([l.get_shape()[-1].value, size[i]], weight_init_range[i][0],weight_init_range[i][1]), trainable=trainable)
                    self.params.append(weight)
                    self.w[-1].append(weight)
                    layer += tf.matmul(l, weight)
                if normalization[i] != None:
                    layer = normalization[i](layer)
                if function[i] != None:
                    layer = function[i](layer)
#                print (layer)
#                print (layer.get_shape())
                self.layers.append(layer)
                last_layer = [layer]
            self.output = self.layers[-1]
            if shared_parameters == None:
                getSession(self.graph).run(tf.initialize_variables(self.params))
    def getParams(self):
        return getSession(self.graph).run(self.params)
