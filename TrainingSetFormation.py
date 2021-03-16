'''
Created on Mar 15, 2021

@author: gregory.werner
'''

import os
import pandas as pd
from Features import features_pred_2

def lookup_features_for_team(team_id, sd):
    formed_path = os.path.join(sd, team_id + '.txt')
    return_list = []
    with open(formed_path, 'r', encoding='utf-8') as fs:
        lines = [l.strip() for l in fs.readlines()]
    for line in lines:
        return_list.append(float(line))
    return return_list

def create_training_set(rd, sd, of):
    team_results_files = os.listdir(rd)
    master_list = []
    for trf in team_results_files:
        our_team = trf.split('.')[0]
        # start with feature set version 2, we will omit the ivy league teams because they
        # did not play anyone
        if our_team in ['225', '171', '172', '159', '108', '219', '163', '43']:
            continue        
        us_features = lookup_features_for_team(our_team, sd)
        
        fullpath = os.path.join(rd, trf)
        with open(fullpath, 'r', encoding='utf-8') as fs:
            lines = fs.readlines()
        for line in [l.strip() for l in lines]:
            parts = line.split('\t')
            opponent = parts[0]
            result = parts[1].replace('4OT', '')
            result = result.replace('3OT', '')
            result = result.replace('2OT', '')
            result = result.replace('OT', '')
            score_parts = result.split('-')
            score_us = score_parts[0].strip()
            score_them = score_parts[1].strip()
            if int(score_us) > int(score_them):
                win = 1
            else:
                win = 0

            them_features = lookup_features_for_team(opponent, sd)
            
            master_list.append(us_features + them_features + [win])
                        
    headers = features_pred_2
    
    df = pd.DataFrame(master_list, columns=headers)
    df.to_csv(of, index=False)
    print(df.shape)

def main():
    results_dir = os.path.join('data', 'team_results')
    stats_dir = os.path.join('data', 'team_stats_2')
    output_file = os.path.join('data', 'training_set_2.csv')
    create_training_set(results_dir, stats_dir, output_file)

if __name__ == '__main__':
    main()