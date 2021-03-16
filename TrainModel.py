'''
Created on Mar 15, 2021

@author: gregory.werner
'''

import joblib
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
from sklearn import preprocessing
import torch
import torch.nn as nn

def train_model(tf, model_name, scaler_name):
    df = pd.read_csv(tf)
    print(df.head(5))
    
    n_input_dim = len(df.columns) - 1
    n_output = 1
    alpha = 5
    n_hidden = int(df.shape[0] / ((n_input_dim + n_output) * alpha))
    net = nn.Sequential(
        nn.Linear(n_input_dim, n_hidden),
        nn.ELU(),
        nn.Linear(n_hidden, n_output),
        nn.Sigmoid())
    
    loss_func = nn.BCELoss()
    learning_rate = 0.0001
    optimizer = torch.optim.Adam(net.parameters(), lr=learning_rate)   
    
    print(n_input_dim)
    print(n_output)
    print(n_hidden)

    Y_train = df['result']
    X_train = df.drop('result', axis = 1)

    min_max_scaler = preprocessing.MinMaxScaler()
    for col in X_train:
        X_train[col] = min_max_scaler.fit_transform(X_train[col].values.reshape(-1, 1))

    print(X_train.head(5))

    train_loss = []
    train_accuracy = []
    iters = 1000
    Y_train_t = torch.FloatTensor(Y_train).reshape(-1, 1)
    for i in range(iters):
        X_train_t = torch.FloatTensor(X_train.values)
        y_hat = net(X_train_t)
        loss = loss_func(y_hat, Y_train_t)
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()
        y_hat_class = np.where(y_hat.detach().numpy() < 0.5, 0, 1)
        accuracy = np.sum(Y_train.values.reshape(-1,1) == y_hat_class) / len(Y_train)
        train_accuracy.append(accuracy)
        train_loss.append(loss.item())
        
    torch.save(net.state_dict(), model_name)
    joblib.dump(min_max_scaler, scaler_name)         
        
    fig, ax = plt.subplots(2, 1, figsize=(12,8))
    ax[0].plot(train_loss)
    ax[0].set_ylabel('Loss')
    ax[0].set_title('Training Loss')
    
    ax[1].plot(train_accuracy)
    ax[1].set_ylabel('Classification Accuracy')
    ax[1].set_title('Training Accuracy')
    
    plt.tight_layout()
    plt.show()

def main():
    training_filename = os.path.join('data', 'training_set_2.csv')
    model_name = os.path.join('model', 'model2.mdl')
    scaler_name = os.path.join('model', 'scaler2.save')
    train_model(training_filename, model_name, scaler_name)

if __name__ == '__main__':
    main()