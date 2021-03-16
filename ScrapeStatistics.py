'''
Created on Mar 15, 2021

@author: gregory.werner
'''

from bs4 import BeautifulSoup
import os
import requests
import time

base_url = 'https://espn.com'

example = 'Stats__TotalRow fw-bold'

def calculate_points_against(team_id, tr_directory):
    fullpath = os.path.join(tr_directory, team_id + '.txt')
    with open(fullpath, 'r', encoding='utf-8') as fs:
        lines = [l.strip() for l in fs.readlines()]
    tpa = 0
    tg = 0
    for line in lines:
        parts = line.split('\t')
        score = parts[1].replace(' 4OT', '').replace(' 3OT', '').replace(' 2OT', '').replace(' OT', '')
        pa = score.split('-')[1]
        tpa += int(pa)
        tg += 1
    return tpa / tg

def calculate_last_10(team_id, tr_directory):
    fullpath = os.path.join(tr_directory, team_id + '.txt')
    with open(fullpath, 'r', encoding='utf-8') as fs:
        lines = [l.strip() for l in fs.readlines()]
    wins = 0
    losses = 0
    for line in reversed(lines):
        parts = line.split('\t')
        score = parts[1].replace(' 4OT', '').replace(' 3OT', '').replace(' 2OT', '').replace(' OT', '')
        pf = score.split('-')[0]
        pa = score.split('-')[1]
        if pf > pa:
            wins += 1
        else:
            losses += 1
        if wins + losses == 10:
            break
    return wins / (wins + losses)

def calculate_win_pct(team_id, tr_directory):
    fullpath = os.path.join(tr_directory, team_id + '.txt')
    with open(fullpath, 'r', encoding='utf-8') as fs:
        lines = [l.strip() for l in fs.readlines()]
    wins = 0
    losses = 0
    for line in reversed(lines):
        parts = line.split('\t')
        score = parts[1].replace(' 4OT', '').replace(' 3OT', '').replace(' 2OT', '').replace(' OT', '')
        pf = score.split('-')[0]
        pa = score.split('-')[1]
        if pf > pa:
            wins += 1
        else:
            losses += 1
    return wins / (wins + losses)

# win streak, S10, PAPG, ORPG, DRPG
def calculate_derived_stats(derived_stats, stats_list, team_id, tr_directory):
    additional_stats = []
    for ds in derived_stats:
        if 'FGAPG' in ds:
            additional_stats.append(int(stats_list[ds['FGAPG'][1]]) / int(stats_list[ds['FGAPG'][0]]))
        elif 'FTAPG' in ds:
            additional_stats.append(int(stats_list[ds['FTAPG'][1]]) / int(stats_list[ds['FTAPG'][0]]))
        elif '3PAPG' in ds:
            additional_stats.append(int(stats_list[ds['3PAPG'][1]]) / int(stats_list[ds['3PAPG'][0]]))
        elif 'ORPG' in ds:
            additional_stats.append(int(stats_list[ds['ORPG'][1]]) / int(stats_list[ds['ORPG'][0]]))
        elif 'DRPG' in ds:
            additional_stats.append(int(stats_list[ds['DRPG'][1]]) / int(stats_list[ds['DRPG'][0]]))
        elif 'PAPG' in ds:
            additional_stats.append(calculate_points_against(team_id, tr_directory))
        elif 'S10' in ds:
            additional_stats.append(calculate_last_10(team_id, tr_directory))
        elif 'WPCT' in ds:
            additional_stats.append(calculate_win_pct(team_id, tr_directory))
    return additional_stats

def fetch_stats(statistics_file, output_folder, tr_directory, to_keep, derived_stats):
    with open(statistics_file, 'r', encoding='utf-8') as fs:
        stats_urls = [l.strip() for l in fs.readlines()]
    for stats_url in stats_urls:
        team_id = stats_url.split('/')[-1]
        print(team_id)
        # start with feature set version 2, we will omit the ivy league teams because they
        # did not play anyone
        if team_id in ['225', '171', '172', '159', '108', '219', '163', '43']:
            continue
        page = requests.get(base_url + stats_url)
        print(page.status_code)
        soup = BeautifulSoup(page.content, 'html.parser')
        
        all_stats = soup.findAll('span', {'class', 'Stats__TotalRow fw-bold'}, text=True)
        stats_list = []
        with open(os.path.join(output_folder, team_id + '.txt'), 'w', encoding='utf-8') as fs:
            count = 0
            for ast in all_stats:
                if ast.text != 'Total':
                    stats_list.append(ast.text)
                    if count in to_keep:
                        fs.write(ast.text + '\n')
                    count += 1
            additional_stats = calculate_derived_stats(derived_stats, stats_list, team_id, tr_directory)
            for adds in additional_stats:
                fs.write(str(adds) + '\n')

        time.sleep(1)

def main():
    statistics_file = os.path.join('data', 'statistics.txt')
    output_folder = os.path.join('data', 'team_stats_2')
    tr_directory = os.path.join('data', 'team_results')
    # all the numbers [0,23] is FS 1
    to_keep = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    # empty is correct for FS 1
    derived_stats = [{'FGAPG':[0,11]}, {'FTAPG':[0,13]}, {'3PAPG':[0,15]}, {'ORPG':[0, 17]}, {'DRPG':[0, 18]}, {'PAPG':[-1]}, {'S10':[-1]}, {'WPCT':[-1]}]
    
    fetch_stats(statistics_file, output_folder, tr_directory, to_keep, derived_stats)

if __name__ == '__main__':
    main()