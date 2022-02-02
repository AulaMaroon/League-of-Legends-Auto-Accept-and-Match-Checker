from lcu_driver import Connector
import os
import keyboard
import time
from sys import exit

connector = Connector()
# fired when LCU API is ready to be used
@connector.ready
async def connect(connection):
    second = 0
    minute = 0
    summoner = await connection.request('get', '/lol-summoner/v1/current-summoner')
    os.system('cls')
    print('Welcome ' + (await summoner.json())['displayName'])
    print()
    print('Press Space To Start Auto Accept')
    print('Press ESC To Exit Program')
    print()
    while True:
        if keyboard.is_pressed('space'):
            os.system('cls')
            while True:
                second += 1
                if second == 60:
                    minute += 1
                    second = 0
                print('Waiting For Queue')
                print()
                print('     ' + str(minute) + ' : ' + str(second))
                print()
                print('Press ESC to cancel')
                if keyboard.is_pressed('esc'):
                    exit()
                time.sleep(1)
                os.system('cls')
                gamephase = await connection.request('get', '/lol-gameflow/v1/gameflow-phase')
                currentphase = await gamephase.json()
                if currentphase == 'Lobby':
                    await connection.request('post', '/lol-lobby/v2/lobby/matchmaking/search')
                if currentphase == 'ReadyCheck':
                    await connection.request('post', '/lol-matchmaking/v1/ready-check/accept')
                if currentphase == 'ChampSelect':
                    await matchchecker(connection)
                    input()
                
            
        if keyboard.is_pressed('esc'):
            exit()

async def matchchecker(connection):
    os.system('cls')
    for i in range(5):
        try:
            champ = await connection.request('get', '/lol-champ-select/v1/summoners/'+str(i))
            summonersid = (await champ.json())['summonerId']
            sums = await connection.request('get', '/lol-summoner/v1/summoners/'+str(summonersid))
            displayname = (await sums.json())['displayName']
            puuid = (await sums.json())['puuid']
            rankstats = await connection.request('get', '/lol-ranked/v1/ranked-stats/' + puuid)
            queues = (await rankstats.json())['queues'][0]
            try:
                currentdiv = queues['division']
                currenttier = queues['tier']
                playernumber = i + 1
                print('Player ' + str(playernumber))
                if 'NA' in currentdiv:
                    print(displayname + ' (No Current Season Data)')
                else:
                    print(displayname + ' ' + '(' + currenttier + ' ' + currentdiv + ')')
            except:
                playernumber = i + 1
                print('Player ' + str(playernumber))
                print(displayname + ' (No Current Season Data)')
            try:
                previousdiv = queues['previousSeasonEndDivision']
                previoustier = queues['previousSeasonEndTier']
                if 'NA' in previousdiv:
                    print('(No Previous Season Data)')
                else:
                    print('Previous Rank (' + previoustier + ' ' + previousdiv + ')')
            except:
                print('(No Previous Rank Data)')
            try:
                currentwin = queues['wins']
                currentloss = queues['losses']
                totalmatch = (currentwin + currentloss)
                winrate = int(currentwin / totalmatch * 100)            
                print('Wins : ' + str(currentwin) + ' | ' + 'Loss : ' + str(currentloss) + ' | Win Rate : ' + str(winrate) + ' %')
                print()
            except:
                print('(No Win Rate Data)')
                print()
        except:
            pass
    await connector.stop()



# fired when League Client is closed (or disconnected from websocket)
@connector.close
async def disconnect(_):
    await connector.stop()



# starts the connector
connector.start()