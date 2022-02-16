from lcu_driver import Connector
import os
import keyboard
import time
from sys import exit
import datetime

connector = Connector()
# fired when LCU API is ready to be used
@connector.ready
async def connect(connection):
    queuetimer = 0 
    summoner = await connection.request('get', '/lol-summoner/v1/current-summoner')
    os.system('cls')
    print('Welcome ' + (await summoner.json())['displayName'])
    print()
    gamephase = await connection.request('get', '/lol-gameflow/v1/gameflow-phase')
    currentphase = await gamephase.json()
    if currentphase == 'None':
        await lobbycreator(connection)
    os.system('cls')
    while True:
        gamephase = await connection.request('get', '/lol-gameflow/v1/gameflow-phase')
        currentphase = await gamephase.json()
        if currentphase == 'Lobby' or currentphase == 'Matchmaking':
            await connection.request('post', '/lol-lobby/v2/lobby/matchmaking/search')
            while True:
                print('Waiting For Queue')
                print()
                print(str(datetime.timedelta(seconds=queuetimer)))
                queuetimer += 1
                print()
                print('Press ESC to cancel')
                time.sleep(1)
                if keyboard.is_pressed('esc'):
                    exit()
                os.system('cls')
                gamephase = await connection.request('get', '/lol-gameflow/v1/gameflow-phase')
                currentphase = await gamephase.json()
                if currentphase == 'ReadyCheck':
                    await connection.request('post', '/lol-matchmaking/v1/ready-check/accept')
                    queuetimer == 0
                if currentphase == 'ChampSelect':
                    await matchchecker(connection)
                    input()

async def matchchecker(connection):
    os.system('cls')
    for i in range(5):
        try:
            champ = await connection.request('get', '/lol-champ-select/v1/summoners/'+str(i))
            summonersid = (await champ.json())['summonerId']
            sums = await connection.request('get', '/lol-summoner/v1/summoners/'+str(summonersid))
            displayname = (await sums.json())['displayName']
            puuid = (await sums.json())['puuid']
            sumslevel = (await sums.json())['summonerLevel']
            reroll = (await sums.json())['rerollPoints']['numberOfRolls']
            rankstats = await connection.request('get', '/lol-ranked/v1/ranked-stats/' + puuid)
            queues = (await rankstats.json())['queues'][0]
            try:
                currentdiv = queues['division']
                currenttier = queues['tier']
                playernumber = i + 1
                print('Player ' + str(playernumber) + ' - Level ' + str(sumslevel) + ' - Reroll ' + str(reroll))
                if 'NA' in currentdiv:
                    print(displayname + ' (No Current Season Data)')
                else:
                    print(displayname + ' ' + '(' + currenttier + ' ' + currentdiv + ')')
            except:
                playernumber = i + 1
                print('Player ' + str(playernumber) + ' - Level ' + str(sumslevel) + ' - Reroll ' + str(reroll))
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

async def lobbycreator(connection):
    print("1.Summoner's Rift")
    print('2.Howling Abyss(ARAM)')
    print('3.Teamfight Tactics(TFT)')
    gamemodeoption = input('Select the map/gamemode you want to play : ')
    os.system('cls')
    if int(gamemodeoption) == 1:
        print('1.Blind Pick')
        print('2.Draft Pick')
        print('3.Ranked Solo/Duo')
        print('4.Ranked Flex')
        sroptions = input('Select the gametype : ')
        if int(sroptions) == 1:
            await connection.request('post', '/lol-lobby/v2/lobby', data = {'queueId':430})
        if int(sroptions) == 2:
            await connection.request('post', '/lol-lobby/v2/lobby', data = {'queueId':400})
        if int(sroptions) == 3:
            await connection.request('post', '/lol-lobby/v2/lobby', data = {'queueId':420})
        if int(sroptions) == 4:
            await connection.request('post', '/lol-lobby/v2/lobby', data = {'queueId':440})
    if int(gamemodeoption) == 2:
        await connection.request('post', '/lol-lobby/v2/lobby', data = {'queueId':450})
    if int(gamemodeoption) == 3:
        print('1.Normal')
        print('2.Ranked')
        print('3.Hyper Roll')
        print('4.Double Up')
        tftoptions = input('Select the gametype : ')
        if int(tftoptions) == 1:
            await connection.request('post', '/lol-lobby/v2/lobby', data = {'queueId':1090})
        if int(tftoptions) == 2:
            await connection.request('post', '/lol-lobby/v2/lobby', data = {'queueId':1100})
        if int(tftoptions) == 3:
            await connection.request('post', '/lol-lobby/v2/lobby', data = {'queueId':1130})
        if int(tftoptions) == 4:
            await connection.request('post', '/lol-lobby/v2/lobby', data = {'queueId':1150})

# fired when League Client is closed (or disconnected from websocket)
@connector.close
async def disconnect(_):
    await connector.stop()



# starts the connector
connector.start()