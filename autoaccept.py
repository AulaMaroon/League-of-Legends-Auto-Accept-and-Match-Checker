from lcu_driver import Connector
import os
import keyboard
import time

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
                if currentphase == 'Matchmaking':
                    await connection.request('post', '/lol-matchmaking/v1/ready-check/accept')
                if currentphase == 'ChampSelect':
                    await matchchecker(connection)
                    exit()
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
            try:
                rankstats = await connection.request('get', '/lol-ranked/v1/ranked-stats/' + puuid)
                previousdiv = (await rankstats.json())['highestRankedEntrySR']['previousSeasonEndDivision']
                previoustier = (await rankstats.json())['highestRankedEntrySR']['previousSeasonEndTier']
                currentdiv = (await rankstats.json())['highestRankedEntrySR']['division']
                currenttier = (await rankstats.json())['highestRankedEntrySR']['tier']
                currentwin = (await rankstats.json())['highestRankedEntrySR']['wins']
                currentloss = (await rankstats.json())['highestRankedEntrySR']['losses']
                totalmatch = (currentwin + currentloss)
                winrate = int(currentwin / totalmatch * 100)
                #os.system('cls')
                playernumber = i + 1
                print('Player ' + str(playernumber))
                print(displayname + ' ' + '(' + currenttier + ' ' + currentdiv + ')')
                print('Previous Rank (' + previoustier + ' ' + previousdiv + ')')
                print('Wins : ' + str(currentwin) + ' | ' + 'Loss : ' + str(currentloss) + ' | Win Rate : ' + str(winrate) + ' %')
                print()
            except:
                playernumber = i + 1
                print('Player ' + str(playernumber))
                print(displayname)
                print('(No Current/Previous Rank Data)')
                print()
        except:
            pass

# fired when League Client is closed (or disconnected from websocket)
@connector.close
async def disconnect(_):
    await connector.stop()



# starts the connector
connector.start()