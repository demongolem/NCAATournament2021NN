'''
Created on Mar 15, 2021

@author: gregory.werner
'''

from bs4 import BeautifulSoup
import os
import requests

def scrape_teams(team_url, tf, statsf, standf):
    page = requests.get(team_url)
    print(page.status_code)
    soup = BeautifulSoup(page.content, 'html.parser')

    teams = soup.findAll('h2', {'class', 'di clr-gray-01 h5'}, text=True)
    with open(tf, 'w', encoding='utf-8') as fs:
        for team in teams:
            fs.write(team.text + '\n')

    statsSchedules = soup.findAll('a', {'class', 'AnchorLink'}, text=True, href=True)
    with open(statsf, 'w', encoding='utf-8') as fs:
        for ss in statsSchedules:
            if ss.text == 'Statistics':
                fs.write(ss['href'] + '\n')
    with open(standf, 'w', encoding='utf-8') as fs:
        for ss in statsSchedules:
            if ss.text == 'Schedule':
                fs.write(ss['href'] + '\n')

def main():
    team_url = 'https://www.espn.com/mens-college-basketball/teams'
    data_dir = 'data'
    team_file = os.path.join(data_dir, 'teams.txt')
    statistics_link_file = os.path.join(data_dir, 'statistics.txt')
    standings_link_file = os.path.join(data_dir, 'schedules.txt')
    scrape_teams(team_url, team_file, statistics_link_file, standings_link_file)

if __name__ == '__main__':
    main()