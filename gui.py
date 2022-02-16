from tkinter import *
from tkinter import font
from tracemalloc import start
from turtle import left
from lcu_driver import Connector

'''root = tk.Tk()
text = tk.StringVar()
text.set("test")
label = tk.Label(root, textvariable=text)
def changetext():
    text.set("text changed")
button = tk.Button(root, text="click to change", command=changetext)
button.pack()
label.pack()
root.mainloop()'''
connector = Connector()
# fired when LCU API is ready to be used
@connector.ready
async def connect(connection):
    window = Tk()
    window.geometry("350x200")

    #Username Welcome
    summoner = await connection.request('get', '/lol-summoner/v1/current-summoner')
    summonername = ((await summoner.json())['displayName'])
    var = StringVar()
    label = Label(window, textvariable=var, font=(None, 20))
    var.set('Welcome ' + summonername)

    #Start Button
    startbutton = Button(window, text="Start", font=(None, 15), width=8)
    cancelbutton = Button(window, text="Stop", font=(None, 15), width=8)
    startbutton.place(x=50, y=80)
    cancelbutton.place(x=200, y=80)

    label.pack()
    mainloop()

# fired when League Client is closed (or disconnected from websocket)
@connector.close
async def disconnect(_):
    await connector.stop()
    

# starts the connector
connector.start()


