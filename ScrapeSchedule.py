'''
Created on Mar 15, 2021

@author: gregory.werner
'''

from bs4 import BeautifulSoup
import os
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import time

base_url = 'https://espn.com'

example='<tr class="filled Table__TR Table__TR--sm Table__even" data-idx="3"><td class="Table__TD"><span>Fri, Dec 4</span></td><td class="Table__TD"><div class="flex items-center opponent-logo"><span class="pr2">@</span><span class="tc pr2" style="width:20px;height:20px"><a class="AnchorLink" tabindex="0" href="/mens-college-basketball/team/_/id/150/duke-blue-devils"><img alt="Duke" title="Duke" src="https://a.espncdn.com/combiner/i?img=/i/teamlogos/ncaa/500/150.png&amp;w=50&amp;h=50"> </a></span><span>6 <a class="AnchorLink" tabindex="0" href="/mens-college-basketball/team/_/id/150/duke-blue-devils">Duke<!-- --> </a></span></div></td><td class="Table__TD"><span class="fw-bold clr-negative">L</span><span class="ml4"><a class="AnchorLink" tabindex="0" href="http://www.espn.com/mens-college-basketball/game?gameId=401254014">76-54 <!-- --> </a></span></td><td class="Table__TD"><span>0-1 (0-0)</span></td><td class="Table__TD"><span><a class="AnchorLink" tabindex="0" href="https://www.espn.com/mens-college-basketball/player/_/id/4700830/nick-thelen">Thelen<!-- --> </a> <!-- -->14</span></td><td class="Table__TD"><span><a class="AnchorLink" tabindex="0" href="https://www.espn.com/mens-college-basketball/player/_/id/4279924/pedro-bradshaw">Bradshaw<!-- --> </a> <!-- -->7</span></td><td class="Table__TD"><span><a class="AnchorLink" tabindex="0" href="https://www.espn.com/mens-college-basketball/player/_/id/4700826/dylan-penn">Penn<!-- --> </a> <!-- -->4</span></td></tr>'

def fetch_results(sf, od):
    # for quick restarts
    active = False
    start_id = '154'
    
    with open(sf, 'r', encoding='utf-8') as fs:
        schedules_urls = [l.strip() for l in fs.readlines()]
    for schedule_url in schedules_urls:
        team_id = schedule_url.split('/')[-1]
        print(team_id)
        if team_id == start_id:
            active = True
        if not active:
            continue

        time.sleep(1)
        browser = webdriver.Chrome(executable_path='./chromedriver')
        browser.get(base_url + schedule_url)
    
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        
        all_results = soup.findAll('tr')       
        valid_results = 0
        with open(os.path.join(od, team_id + '.txt'), 'w', encoding='utf-8') as fs:
            for ar in all_results:
                if not 'Table__TR' in ar['class'] or not 'Table__TR--sm' in ar['class'] or not 'Table__even' in ar['class']:
                    continue

                irows = ar.findAll('td')
                if len(irows) < 3:
                    continue
                
                opponent = irows[1]
                result = irows[2]
                                
                if 'Canceled' == result.text or 'Postponed' == result.text:
                    continue
                                
                atags = opponent.find_all('a', {'class':'AnchorLink'})
                if len(atags) < 2:
                    # this includes the case when there is no icon for the school
                    continue
                print(atags)
                opponent_link = atags[1]['href']
                opponent_id = opponent_link.split('/')[-2]
                
                atags = result.find_all('a', {'class':'AnchorLink'})
                if len(atags) == 0:
                    continue
                if ':' in atags[0].text:
                    # this is likely a tourney game to be played
                    continue
                sptags = result.find_all('span')
                updown = sptags[0].text
                if updown == 'W':
                    reported_score = atags[0].text.strip()
                else:
                    print(atags[0].text)
                    parts = atags[0].text.split('-')
                    if len(parts) != 2:
                        # perhaps a forfeited or non-contested game (because of COVID)
                        continue
                    reported_score = parts[1].strip() + '-' + parts[0]
                
                valid_results += 1                
                
                fs.write(opponent_id + '\t' + reported_score + '\n')

        browser.close()

        print(valid_results)
        
        if team_id == '154':
            return

def main():
    schedule_file = os.path.join('data', 'schedules.txt')
    output_dir = os.path.join('data', 'team_results')
    fetch_results(schedule_file, output_dir)

if __name__ == '__main__':
    main()