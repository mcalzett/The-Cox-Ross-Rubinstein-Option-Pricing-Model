#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 14 17:44:40 2019

@author: mattiacalzetta
"""

import numpy as np

def BinomialTreeCRR(type,S0, K, r, sigma, T, N=200 ,american="false"):
    """
    Params:
        type: C (call) or P (put)
        S0: stock price at t=0
        K: strike price
        r: constant riskless short rate
        sigma: constant volatility (i.e. standard deviation of returns) of S
        T: the horizion in year fractions (i.e. 1, 2, 3.5 etc)
        american: false (european) or true (american)
    Assumptions:
        1) the original Cox, Ross & Rubinstein (CRR) method as been used (paper below)
            http://static.stevereads.com/papers_to_read/option_pricing_a_simplified_approach.pdf
        2) no dividends
    Output:
        Value of the option today
    """

    #calculate delta T    
    deltaT = float(T) / N
 
    # up and down factor calculated using the underlying volatility sigma as per the original CRR
    u = np.exp(sigma * np.sqrt(deltaT)) #up factor
    d = np.exp(-sigma * np.sqrt(deltaT)) #down factor
 
    #to work with vector we need to create the arrays using numpy. We are using N+1 because the number of outcomes is always equal to N+1
    value =  np.asarray([0 for i in range(N + 1)])
        
    #we need the stock tree for calculations of expiration values (all possible combinations of ups and downs)
    stock_price = np.asarray([(S0 * u**j * d**(N - j)) for j in range(N + 1)])
    
    #we vectorize the strikes as well to use arrays efficiently 
    strike =np.asarray( [float(K) for i in range(N + 1)])
    
    #the original paper uses "q" to indicate the probability but anyway
    p = (np.exp(r * deltaT) - d)/ (u - d)
    oneMinusP = 1 - p
    
    # Compute the leaves for every element [:] in the array
    if type =="C": #if it's a call 
        value[:] = np.maximum(stock_price-strike, 0)
        
    elif type == "P": #if it's a put
        value[:] = np.maximum(-stock_price+strike, 0)
    
    """
    Calculate backward the option prices for each node:
        1) in "value" we have the option prices
        2) in loop (one for each N), we calculate the price of the option (backwards) by pairing the outcomes 2 by 2
        3) we finally arrive to the price of the option today
    """

    for i in range(N):
        #For each (except last one) = bla bla * (except first + except last one) - this is to couple all the leaves at each node
        value[:-1]=np.exp(-r * deltaT) * (p * value[1:] + oneMinusP * value[:-1])
        #multiplying all stock prices as we are going backwards. we are using u and not p as we are walking backwards from bottom to top 
        stock_price[:]=stock_price[:]*u
        
        #only for american options as for american options we must check at each node if the option is worth more alive then dead
        if american=='true':
           #check if the option is worth more alive or dead (i.e. comparing the payoff against the value of the option)
            if type =="C":
                value[:]=np.maximum(value[:],stock_price[:]-strike[:])
            elif type == "P":
                value[:]=np.maximum(value[:],-stock_price[:]+strike[:])
                
    # print value - i.e. first element of array 
    return value[0]