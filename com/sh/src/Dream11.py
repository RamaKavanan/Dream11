import unittest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import pprint
import time
import pandas as pd
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

chrome_options = Options()
chrome_options.add_argument("--window-size=1920,1080")
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--remote-debugging=9222 ")
chrome_options.add_argument("--no-sandbox")

class PythonOrgSearch:

    def setUp(self):
        self.driver = webdriver.Chrome('driver/chromedriver',
                                  chrome_options=chrome_options)

    def test_search_in_python_org(self):
        list = []
        driver = self.driver
        #urls = ['https://www.iplt20.com/match/2017/29?tab=scorecard']

        driver.get("https://www.iplt20.com/archive/2017")
        elements = driver.find_elements_by_class_name("result__button--mc")
        urls = []
        for el in elements:
            urls.append(el.get_attribute('href'))
        for url in urls:
            players = self.get_players(url)
            for player_name in players:
                list.append(players[player_name])
        #print(batsmens)
        #print(bowlers)
        #pprint.pprint(players)
        players = {}

        exist_data = pd.read_csv("/home/ubuntu/Desktop/Ideas2it/Datascience/Dream11/data/players_2017.csv")
        df = pd.DataFrame(list)
        exist_data = exist_data.append(df)
        exist_data.to_csv("/home/ubuntu/Desktop/Ideas2it/Datascience/Dream11/data/players_2017.csv", index=False)
        #print(df)
        self.tearDown()

    def get_players(self, url):
        driver = self.driver
        driver.get(url)
        timeout = 20
        try:
            element_present = EC.presence_of_element_located((By.CLASS_NAME, 'home'))
            WebDriverWait(driver, timeout).until(element_present)
        except TimeoutError :
            print("Timed out waiting for page to load")
        elem = driver.find_element_by_class_name('hpto-header__title')
        match_no, ground_name, city = elem.text.split(',')
        try:
            match_no = match_no.split('Match ')[1]
        except Exception :
            print('Match may be final/qualifiers/semi finals')
            pass
        elem = driver.find_element_by_class_name('matchSummary')
        won = elem.text.split(' won')[0]
        home = driver.find_element_by_class_name('home')
        away = driver.find_element_by_class_name('away')
        if len(home.text.split('\n')) == 4 :
            team_name1, team_score, team_run_rate, team_faced_over = home.text.split('\n')
            team_name1_lower = team_name1.lower()
            opposite_team_name1, opposite_team_score, opposite_team_run_rate, opposite_team_faced_over = away.text.split(
                '\n')
            opposite_team_name_lower = opposite_team_name1.lower()
        elif len(home.text.split('\n')) > 4:
            team_name1, team_score, team_run_rate, team_faced_over, extra_value = home.text.split('\n')
            team_name1_lower = team_name1.lower()
            opposite_team_name1, opposite_team_score, opposite_team_run_rate, opposite_team_faced_over, extra_value = away.text.split(
                '\n')
            opposite_team_name_lower = opposite_team_name1.lower()
        else:
            print('Match abandoned')

        elements = driver.find_elements_by_class_name('teamScorecard')
        players = {}
        batsmens = {}
        bowlers = {}
        # print(len(elem))
        try:
            for el in elements:
                team_name_el = el.find_element_by_class_name('teamHeader')
                team_name = team_name_el.text.lower().split(' innings')[0]
                table = el.find_element_by_class_name('batsmen')
                rows = table.find_elements_by_tag_name('tr')
                count = 0
                for row in rows:
                    player_name = ''
                    if count == len(rows):
                        break
                    else:
                        tds = row.find_elements_by_tag_name('td')
                        i = 0
                        for td in tds:
                            if row.get_attribute('class') == 'batsmanInns player-popup-link':
                                if i == 1:
                                    player_name = td.text
                                    players = self.append(players, td.text, 'name', td.text)
                                    players = self.append(players, player_name, 'match_no',
                                                          match_no.lstrip())
                                    players = self.append(players, player_name, 'ground_name',
                                                          ground_name.lstrip())
                                    players = self.append(players, player_name, 'ground_city',
                                                          city.lstrip())
                                    if team_name == team_name1_lower:
                                        players = self.append(players, player_name, 'team_name',
                                                              team_name1)
                                        players = self.append(players, player_name, 'opposite_team_name',
                                                              opposite_team_name1)
                                    else:
                                        players = self.append(players, player_name, 'team_name',
                                                              opposite_team_name1)
                                        players = self.append(players, player_name, 'opposite_team_name',
                                                              team_name1)
                                elif i == 2:
                                    if 'lbw ' in td.text:
                                        players = self.append(players, player_name, 'wicket', 'lbw')
                                        players = self.append(players, player_name, 'bowled_by', td.text.split('lbw ')[1])
                                    elif 'c ' in td.text and ' b ' in td.text:
                                        players = self.append(players, player_name, 'wicket', 'catch')
                                        players = self.append(players, player_name, 'bowled_by',
                                                              td.text.split('c ')[1].split(' b ')[1])
                                        players = self.append(players, player_name, 'catched_by',
                                                              td.text.split('c ')[1].split(' b ')[0])
                                    elif 'st ' in td.text and ' b ' in td.text:
                                        players = self.append(players, player_name, 'wicket', 'stemping')
                                        players = self.append(players, player_name, 'bowled_by',
                                                              td.text.split('st ')[1].split(' b ')[1])
                                        players = self.append(players, player_name, 'stumped_by',
                                                              td.text.split('st ')[1].split(' b ')[0])
                                    elif 'run out ' in td.text:
                                        players = self.append(players, player_name, 'wicket', 'runout')
                                        players = self.append(players, player_name, 'runout_by',
                                                              td.text.split('(')[1].split(')')[0])
                                    elif 'b ' in td.text:
                                        players = self.append(players, player_name, 'wicket', 'bold')
                                        names = td.text.split('b ')
                                        name = ''
                                        if len(names) > 2:
                                            for i in (1, (len(names) - 1)):
                                                name = name + names[i]
                                        else:
                                            name = names[1]
                                        players = self.append(players, player_name, 'bowled_by', name)
                                elif i == 3:
                                    players = self.append(players, player_name, 'run_scored', td.text)
                                elif i == 4:
                                    players = self.append(players, player_name, 'ball_faced', td.text)
                                elif i == 5:
                                    players = self.append(players, player_name, 'strike_rate', td.text)
                                elif i == 6:
                                    players = self.append(players, player_name, 'four', td.text)
                                elif i == 7:
                                    players = self.append(players, player_name, 'six', td.text)
                                i = i + 1
                        count = count + 1

                table = el.find_element_by_class_name('bowlers')
                rows = table.find_elements_by_tag_name('tr')
                count = 0
                for row in rows:
                    player_name = ''
                    if count == len(rows):
                        break
                    else:
                        tds = row.find_elements_by_tag_name('td')
                        i = 0
                        for td in tds:
                            if row.get_attribute('class') == 'player-popup-link':
                                if i == 1:
                                    player_name = td.text
                                    players = self.append(players, td.text, 'name', td.text)
                                    players = self.append(players, player_name, 'match_no',
                                                          match_no.lstrip())
                                    players = self.append(players, player_name, 'ground_name',
                                                          ground_name.lstrip())
                                    players = self.append(players, player_name, 'ground_city',
                                                          city.lstrip())

                                    if team_name == team_name1_lower:
                                        players = self.append(players, player_name, 'team_name',
                                                              opposite_team_name1)
                                        players = self.append(players, player_name, 'opposite_team_name',
                                                              team_name1)
                                    else:
                                        players = self.append(players, player_name, 'team_name',
                                                              team_name1)
                                        players = self.append(players, player_name, 'opposite_team_name',
                                                              opposite_team_name1)
                                elif i == 2:
                                    players = self.append(players, player_name, 'over', td.text)
                                elif i == 3:
                                    players = self.append(players, player_name, 'run_gave', td.text)
                                elif i == 4:
                                    players = self.append(players, player_name, 'wicket_taken', td.text)
                                elif i == 5:
                                    players = self.append(players, player_name, 'economy', td.text)
                                elif i == 6:
                                    players = self.append(players, player_name, 'dot_balls', td.text)
                                i = i + 1
                        count = count + 1
        except Exception:
            print('Exception at', url)
        return players

    def append(self, dict, player_name, key, value):
        if player_name in dict.keys():
            dict[player_name][key] = value
        else:
            #dict[player_name] = {key : value}
            player={}
            player['match_no'] = ''
            player['ground_name'] = ''
            player['ground_city'] = ''
            player['name'] = ''
            player['team_name'] = ''
            player['opposite_team_name'] = ''
            player['run_scored'] = ''
            player['ball_faced'] = ''
            player['strike_rate'] = ''
            player['four'] = ''
            player['six'] = ''
            player['wicket'] = ''
            player['bowled_by'] = ''
            player['catched_by'] = ''
            player['runout_by'] = ''
            player['over'] = ''
            player['run_gave'] = ''
            player['wicket_taken'] = ''
            player['economy'] = ''
            player['dot_balls'] = ''
            player[key] = value
            dict[player_name] = player
        return dict

    def tearDown(self):
        self.driver.close()

if __name__ == "__main__":
    #unittest.main()
    s = PythonOrgSearch()
    s.setUp()
    s.test_search_in_python_org();