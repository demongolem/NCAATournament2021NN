'''
Created on Mar 15, 2021

@author: gregory.werner
'''

import os

def human_it(legend_file, rounds_dir):
    legend_dict = dict()
    with open(legend_file, 'r', encoding='utf-8') as fs:
        lines = [l.strip() for l in fs.readlines()]
    for line in lines:
        parts = line.split('\t')
        legend_dict[parts[0]] = parts[1]

    for single_round in os.listdir(rounds_dir):
        if single_round == 'first_four.txt' or 'human' in single_round:
            continue
        fullpath = os.path.join(rounds_dir, single_round)
        with open(fullpath, 'r', encoding='utf-8') as fs:
            matches = [l.strip() for l in fs.readlines()]
        with open(os.path.join(rounds_dir, single_round[0:-4] + '_human.txt'), 'w', encoding='utf-8') as fs:
            for match in matches:
                parts = match.split('\t')
                fs.write(legend_dict[parts[0]] + '\t' + legend_dict[parts[1]] + '\n')
    
def main():
    rounds_dir = os.path.join('data', 'rounds')
    legend_file = os.path.join('data', 'legend.txt')
    human_it(legend_file, rounds_dir)

if __name__ == '__main__':
    main()