'''
Created on Mar 15, 2021

@author: gregory.werner
'''

from Features import features_2
import joblib
import os
import pandas as pd
import torch
import torch.nn as nn

def lookup_features_for_team(team_id, sd):
    formed_path = os.path.join(sd, team_id + '.txt')
    return_list = []
    with open(formed_path, 'r', encoding='utf-8') as fs:
        lines = [l.strip() for l in fs.readlines()]
    for line in lines:
        return_list.append(float(line))
    return return_list

def infer(t1, t2, sd, net, sf):
    us_features = lookup_features_for_team(t1, sd)
    them_features = lookup_features_for_team(t2, sd)
    master_list = [us_features + them_features]
    headers = features_2
    
    X_test = pd.DataFrame(master_list, columns=headers)
    
    scalar = joblib.load(sf)

    for col in X_test:
        X_test[col] = scalar.transform(X_test[col].values.reshape(-1, 1))

    y_hat = net(torch.FloatTensor(X_test.values))

    return y_hat

def perform_inference(mdlf, mf, pf, sd, sf):
    #model = torch.load(mdlf)

    # adjust as feature set changes 
    n_input_dim = 36
    # adjust as feature set changes 
    n_hidden = 41 
    n_output = 1
    
    model = nn.Sequential(
        nn.Linear(n_input_dim, n_hidden),
        nn.ELU(),
        nn.Linear(n_hidden, n_output),
        nn.Sigmoid())
    
    model.load_state_dict(torch.load(mdlf))
    
    with open(mf, 'r', encoding='utf-8') as fs:
        matches = [l.strip() for l in fs.readlines()]
    with open(pf, 'w', encoding='utf-8') as fs:
        for match in matches:
            parts = match.split('\t')
            team1 = parts[0]
            team2 = parts[1]
            p1 = infer(team1, team2, sd, model, sf)
            p2 = infer(team2, team1, sd, model, sf)
            fs.write('Team ' + str(team1) + ' vs ' + str(team2) + ' has ' + str(p1) + ' and ' + str(p2) + '\n')
            
def main():
    model_filename = os.path.join('model', 'model2.mdl')
    scaler_file = os.path.join('model', 'scaler2.save')
    matchup_file = os.path.join('data', 'rounds', 'national_championship.txt')
    prediction_file = os.path.join('predictions', 'national_championship.txt')
    stats_directory = os.path.join('data', 'team_stats_2')
    perform_inference(model_filename, matchup_file, prediction_file, stats_directory, scaler_file)

if __name__ == '__main__':
    main()