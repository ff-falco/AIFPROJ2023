import gym
import minihack
import random
import math
import numpy as np
import matplotlib.pyplot as plt
import IPython.display as display
import sys
from io import StringIO
from minihack import LevelGenerator
from minihack.envs.room import MiniHackRoom15x15
from minihack.envs.corridor import MiniHackCorridor
from minihack.envs.mazewalk import MiniHackMazeWalk9x9


def render_des_file(des_file):

    env = gym.make('MiniHack-Skill-Custom-v0',
               character="sam-hum-neu-mal",
               observation_keys=('screen_descriptions','inv_strs','blstats','message','pixel'),
               des_file=des_file)

    obs = env.reset()
    env.render()
    plt.imshow(obs['pixel'][0:1000, 0:1000])

AVAIABLE_OBJECTS=[
'healing',
]

AVAIABLE_ITEMS=[
'healing',
]

#Avaiable weapons from the weakest to the strongest
AVAIABLE_ARROWS=[
'orcish arrow', #Level 1 
'silver arrow', #Level 2
'arrow', #Level 3
'elven arrow', #Level 4
'ya' #Level 5
]

AVAIABLE_WEAPONS=[
'spear', 
'dwarvish spear', #stout spear
'morning star',  #120
'elven broadsword', # runed broadsword
'trident'
]

AVAIABLE_ARMORS=[
'red dragon scales',
'scale mail', #250
'elven mithril-coat',
'dwarvish mithril-coat', 
'red dragon scale mail'
]

SYMBOLS=[
'!', #healing potion
')', #arrows
')', #weapons
'[', #armor
]

MOB=['newt', #Level 1 #1
     'iguana',   #Level #3
     'giant ant',   #Level 3 #4
     'lemure']  #Level 4 #5

MINIBOSS=['paper golem',  #Level 2 #4
          'dog', #Level 3 #5
          'lizard'] #Level 4 #6

BOSS=['rock mole', #Level 2  #4
      'jellyfish', #Level 3  #5
      'unicorn', #Level 4 #6
        'yeti']  #Level 5 #7


avaiableitems=['HEALING','ARROWS','WEAPON','ARMOR']


def addobject(lvl: LevelGenerator, seed:int, posx:int ,posy:int,others: [str]) ->str:
    """
    lvl is the Level Generator object, where we have to add items.
    seed is the starting number for the level generation, it has to be included in a range from 0 to 200.
    posx and posy are the coordinates for the item to spawn in the shop, it depends from the avaiable quantity.
    others is the list of the name of the others item already spawned.
    addobject returns the name of the spawned item, useful to update the others list mentioned before. 
    """
    #For the shop we use seeds that are multiple of the original seed
    levelnumber =math.floor(seed/200)
    quality=levelnumber-1
    remainingitems=avaiableitems
    #If the shop has 5 items there is an item from a highest quality, or lowest inthe level 5 case, we refresh the array with the remaining avaible items.
    for i in others:
        remainingitems.pop(remainingitems.index(i))
    if remainingitems.__len__()==0:
        remainingitems=avaiableitems
        if levelnumber==5:
            quality=quality-1
        else: quality=quality+1

    choice=seed%remainingitems.__len__()
    choosen=remainingitems[choice]
    pos=(posx,posy)

    if choosen=='HEALING':
        choosenitem=AVAIABLE_ITEMS[0]
        choosensymbol=SYMBOLS[0]
        lvl.add_object(name=choosenitem,symbol=choosensymbol,place=pos)

    elif choosen=='ARROWS':
        choosenitem=AVAIABLE_ARROWS[quality]
        choosensymbol=SYMBOLS[1]
        #In the arrow case we are spawning three of them, it's enough to kill every mob
        lvl.add_object(name=choosenitem,symbol=choosensymbol,place=(posx,posy))
        lvl.add_object(name=choosenitem,symbol=choosensymbol,place=(posx,posy+1))
        lvl.add_object(name=choosenitem,symbol=choosensymbol,place=(posx,posy+2))

    elif choosen=='WEAPON':
        choosenitem=AVAIABLE_WEAPONS[quality]
        choosensymbol=SYMBOLS[2]
        lvl.add_object(name=choosenitem,symbol=choosensymbol,place=pos)

    else:
        choosenitem=AVAIABLE_ARMORS[quality]
        choosensymbol=SYMBOLS[3]
        lvl.add_object(name=choosenitem,symbol=choosensymbol,place=pos)
        
    return choosen
    
def fillwithobj(lvl: LevelGenerator,seed: int):
    """
    fillwithobj manage the number of the items spawned depending of the number, further details are explained in the levelgenerator notebook.
    """
    random.seed(seed)
    levelnumber=math.floor(seed/200)

    if levelnumber==1:
        if seed<=360:
            numitem=3
        elif seed<=390:
            numitem=4
        else: 
            numitem=5

    elif levelnumber==2:
        if seed<=500:
            numitem=3
        elif seed<=580:
            numitem=4
        else: 
            numitem=5

    if levelnumber==3:
        if seed<=660:
            numitem=3
        elif seed<=760:
            numitem=4
        else: 
            numitem=5

    if levelnumber==4:
        if seed<=840:
            numitem=3
        elif seed<=900:
            numitem=4
        else: 
            numitem=5

    if levelnumber==5:
        if seed<=1010:
            numitem=3
        elif seed<=1040:
            numitem=4
        else: 
            numitem=5
            
    others=[]
    numitem=random.randint(3,5)  
    #In the first level a healing potion is guaranteed, the other choices are pseudo-random (depending on the seed)  
    if numitem==3:
        if levelnumber==1:
            others=['HEALING']
            lvl.add_object(name='healing',symbol='!',place=(4,3))
        else:
            others.append(addobject(lvl,seed,4,3,others))
        others.append(addobject(lvl,seed,6,3,others))
        others.append(addobject(lvl,seed,8,3,others))

    elif numitem==4:
        if levelnumber==1:
            others=['HEALING']
            lvl.add_object(name='healing',symbol='!',place=(3,3))
        else:
            others.append(addobject(lvl,seed,3,3,others))
        others.append(addobject(lvl,seed,5,3,others))
        others.append(addobject(lvl,seed,7,3,others))
        others.append(addobject(lvl,seed,9,3,others))

    elif numitem==5:
        if levelnumber==1:
            others=['HEALING']
            lvl.add_object(name='healing',symbol='!',place=(2,3))
        else:
            others.append(addobject(lvl,seed,2,3,others))
        others.append(addobject(lvl,seed,4,3,others))
        others.append(addobject(lvl,seed,6,3,others))
        others.append(addobject(lvl,seed,8,3,others))
        others.append(addobject(lvl,seed,10,3,others))


#createshop is the function that creates the shop in his complete form, with items, shopkeeper and well defined geometry.
def createshop(levelnumber: LevelGenerator,startingseed: int):
    map="""||||||||||||||||
|...............
|...........||||
|...........|    
|...........|    
|...........|   
|...........|     
|||||||||||||"""
    seed=startingseed+200*levelnumber
    lvl=LevelGenerator(map=map,lit=True,flags=['premapped','shortsighted'])
    lvl.add_line("#LEVEL: "+str(levelnumber))
    lvl.add_line("#SEED: "+str(seed))
    lvl.set_start_pos((1,6))
    #lvl.add_monster(name='shopkeeper',place=(6,1))
    lvl.add_object(name='skeleton key',symbol='(',place=(11,1)) #Skeleton Key
    lvl.add_object(name='skeleton key',symbol='(',place=(11,2))

    lvl.add_door("locked", place=(12,1))

    
    fillwithobj(lvl,seed)

    
    return lvl.get_des()

#-------------------------BATTLEFIELD DEFINITION----------------------------

#In this section we define the geometry of the battlefields that have to be merged with the shop

minibossmap="""                    ||||||||||||
                    |..........|
                    |.||||||...|
                    |.|........|
                    |.|||||....|
                    |.....|....|
                    |||||||....|
                    |..........|
                    |.|||||....|
                    |.|...|....|
                    |.|...|....|
                    ..|...|....|
                    |||.||||...|
                    |......|...|
                    |......|...|
                    |..........|
                    |......|...|
                    ||||||||||||"""




bossmap="""                          |||||      
                          |...|      
                          |...|      
                    ||||||||.||||    
                    |...|.......|    
                    |...|.......|||||
                    |...|.......|...|
                    ................|
                    |...|.......|...|
                    |...|.......|||||
                    |...|.......|    
                    |||||||||||||"""    


roommap="""                    |||||||||||||||
                    |.............|
                    |.............|
                    |.............|
                    |.............|
                    |.............|
                    |.............|
                    |.............|
                    |.............|
                    |.............|
                    |.............|
                    |.............|
                    ..............|
                    |||||||||||||||"""

mazebasemap="""                    |||||||||||||||||||||||||
                    |.                     .|
                    |.                     .|
                    |.                     .|
                    ..                     .|
                    |.                     .|
                    |.                     .|
                    |.                     .|
                    |.                     .|
                    |.                     .|
                    |.                     .|
                    |.                     .|
                    |||||||||||||||||||||||||"""

bonusroommap="""                    |||||||
                    |.....|
                    ......|
                    |.....|
                    |||||||
                    
                    
                    
                    
                    
                    """

MOB=['newt', #Level 1
     'iguana',   #Level 
     'giant ant',   #Level 3
     'lemure']  #Level 4

MINIBOSS=['paper golem',  #Level 2
          'dog', #Level 3
          'lizard'] #Level 4

BOSS=['rock mole', #Level 2 
      'jellyfish', #Level 3 
      'unicorn', #Level 4
        'yeti']  #Level 5


#Every type of the battledfield is explained better in the levelgenerator notebook, basically starting from a map, filled with gold and enemies.
#The difference between levels are in the type of enemies and the probability of a type of level.
#All these functions return the des string that identifies the battlefield level. 

def bonusroom()->str:
    lvl=LevelGenerator(lit=True,flags=['premapped'],map=bonusroommap)
    lvl.set_start_pos((21,2))
    lvl.add_stair_down(place=(24,1))
    lvl.add_line("GOLD: 5,(22,2)")
    lvl.add_line("GOLD: 5,(23,2)")
    lvl.add_line("GOLD: 5,(24,2)")
    
    return lvl.get_des()

def bossroomdes(levelnumber: int)->str:
    lvl=LevelGenerator(map=bossmap,lit=True,flags=['premapped'])
    lvl.set_start_pos((21,7))
    lvl.add_stair_down(place=(28, 1))
    lvl.add_line("GOLD: 5,(34,7)")
    lvl.add_line("GOLD: 5,(35,6)")
    lvl.add_line("GOLD: 5,(35,7)")
    lvl.add_line("GOLD: 5,(35,8)")
    lvl.add_monster(name=BOSS[levelnumber-2],place=(29,7))
    
    return lvl.get_des()

def minibossroomdes(levelnumber: int)->str:
    lvl=LevelGenerator(map=minibossmap,lit=True,flags=['premapped'])
    lvl.set_start_pos((21,11))
    lvl.add_stair_down(place=(30, 1))
    
    #MOB ZONE
    lvl.add_monster(name=MOB[levelnumber-1],place=(28,1))
    lvl.add_monster(name=MOB[levelnumber-1],place=(29,2))
    lvl.add_monster(name=MOB[levelnumber-1],place=(30,3))

    #MOB ZONE (optional)
    lvl.add_monster(name=MOB[levelnumber-1],place=(21,1))
    #MOB REWARD
    lvl.add_line("GOLD: 5,(25,5)")

    #MINIBOSS ZONE (optional)
    lvl.add_monster(name=MINIBOSS[levelnumber-2],place=(23,13))
    #MINIBOSS REWARD
    lvl.add_line("GOLD: 5,(23,10)")
    lvl.add_line("GOLD: 5,(24,10)")
    lvl.add_line("GOLD: 5,(25,10)")

    return lvl.get_des()

#For the room room we choose to spawn enemies in a pseudo-random location, based on the starting seed, to make this possible we consider the map as an matrix with coordinates i,j relative to the avaible tiles
#then we randomly pop elements from there and we spawn enemies depending on the level number.

def roomroomdes(seed: int,levelnumber : int)->str:
    lvl=LevelGenerator(map=roommap,lit=True,flags=['premapped'])
    lvl.set_start_pos((21,12))
    lvl.add_stair_down(place=(33, 1))
    random.seed(seed)

    #MUTUALLY EXCLUSIVE RANDOMNESS----
    pseudoarray=[]
    for i in range(1,13):
        pseudoarray.append(i)
    pseudomatrix=[]
    for i in range(0,10):
        pseudomatrix.append(pseudoarray)
    temporaryseed=seed
    def pseudorandompos (seed:(int))->(int,int):
        random.seed(seed)
        a=random.randint(0,9)
        b=random.choice(pseudomatrix[a])
        pseudomatrix[a].pop(pseudomatrix[a].index(b))
        return (a+22,b)
    #---------------------------------    

    for i in range(0,4):
        lvl.add_line("GOLD: 5,"+str(pseudorandompos(temporaryseed)))
        temporaryseed=temporaryseed+1

    for i in range(0,6):
        lvl.add_monster(name=MOB[levelnumber-1],place=pseudorandompos(temporaryseed))
        temporaryseed=temporaryseed+1
  
    return lvl.get_des()

#For the maze room we use the MAZEWALK functionality of minihack, it creates a random mazewalk between two point, useful to test the pathfinding capability of the agent.
def mazeroomdes(levelnumber:int )->str:
    lvl=LevelGenerator(map=mazebasemap,lit=True,flags=['premapped'])
    lvl.set_start_pos((21,4))

    lvl.add_stair_down(place=(43, 4))
    
    lvl.add_mazewalk(coord=(21,4), dir='east')

    lvl.add_monster(MOB[levelnumber-1],place=(43,3))
    lvl.add_monster(MOB[levelnumber-1],place=(43,2))
    lvl.add_monster(MOB[levelnumber-1],place=(43,8))
    lvl.add_monster(MOB[levelnumber-1],place=(43,9))

    lvl.add_line("GOLD: 5,(43,5)")
    lvl.add_line("GOLD: 5,(43,6)")
    lvl.add_line("GOLD: 5,(43,7)")
 
    return lvl.get_des()

#createbattlefield is the function that creates the battlefield in his complete form, with enemies, an entrance from the shop, a total reward of 15-20 gold, depending on the room choosen. 

def createbattlefield(levelnumber:int ,startingseed:int )->(str,str):
    if levelnumber==1:
        return roomroomdes(startingseed, levelnumber),"roomroom"
    elif levelnumber==5:
        return bossroomdes(5),"bossroom"
    else:
        random.seed(startingseed*levelnumber)
        choice=random.randint(0,200)
        if(choice<=100):
            return (roomroomdes(startingseed,levelnumber),"roomroom")
        elif(choice<=160):
            return (minibossroomdes(levelnumber),"minibossroom")
        elif(choice<=180):
            return (bossroomdes(levelnumber),"bossroom")
        elif(choice<=199):
            return (mazeroomdes(levelnumber),"mazeroom")
        else:
            return (bonusroom(),"bonusroom")

#-------------------------MAP MERGING UTILITIES----------------------------
#As we told in the presentation, shop and battlefield are two separate zones generated indipendently, then merged in a final unique des file which represents the complete level.


def takemap(desfile: str):
    dessplittato=desfile.split('\n')
    j=0
    for i in dessplittato:
        if i=="MAP":
            break
        else:
            j=j+1
    dessplittato=dessplittato[j+1:]
    l=0
    for k in dessplittato:
        if k=="ENDMAP":
            break
        else:
            l=l+1
    dessplittato=dessplittato[:l]
    return '\n'.join(dessplittato)

def mapmerger(shopmap:str,bfdmap:str):
    cleanbfd=(bfdmap)
    cleanbfdlist=cleanbfd.split('\n')
    cleanlines=[]
    for i in cleanbfdlist:
        cleanlines.append(i[18:])
    cleanshop=(shopmap)
    cleanshoplist=cleanshop.split('\n')
    cleanlen=cleanshoplist.__len__()
    finalmap=[]
    k=0
    for j in cleanlines:
        if k<cleanlen:
            finalmap.append(cleanshoplist[k]+j)
        else:
            finalmap.append("                  "+j)
        k=k+1
    cleanlines=[]
    return('\n'.join(finalmap))
#incoming extractor is needed to take the merging point between the two zones, where we will buld a simple path.
def incomingextractor(bfddes:str)->(str,(int,int)):
    bfdsplitted=bfddes.split('\n')
    for i in bfdsplitted:
        if "BRANCH" in i:
            branchsplittato=(i[7:].split(','))
            portalx=branchsplittato[2]
            portaly=branchsplittato[1]
            bfdsplitted.pop(bfdsplitted.index(i))
            return(('\n'.join(bfdsplitted)),(int(portalx)-1,int(portaly)))

def headerextractor(desfile:str): 
    dessplitted=desfile.split('\n')
    k=0
    for j in dessplitted:
        if "ENDMAP" in j:
            break
        else:
            k=k+1
    finale="\n".join(dessplitted[k+1:])
    return finale
#completemapdes returns the des file of the completed level with shop and battlefield merged in a unique level, they are connected by a simple corridor and separated by two locked door that can be unlocked by the skeleton keys in the shop.
def completemapdes(levelnumber,startingseed,custom=None):
    if custom==None:
        battlefield,custom=createbattlefield(levelnumber,startingseed)
    elif custom=="boss":
        battlefield=bossroomdes(levelnumber)
    elif custom=="miniboss":
        battlefield=minibossroomdes(levelnumber)
    elif custom=="room":
        battlefield=roomroomdes(startingseed,levelnumber)
    elif custom=="maze":
        battlefield=mazeroomdes(levelnumber)
    elif custom=="bonus":
        battlefield=bonusroom()
    else:
        print("choosen a wrong custom map")
        return None

    portal=incomingextractor(battlefield)
    battlefield=portal[0]
    incominglocation=portal[1]
    battlefieldheader=headerextractor(battlefield)
    shop=createshop(levelnumber,startingseed)
    shopheader=headerextractor(shop)
    lvl=LevelGenerator(map=mapmerger(takemap(shop),takemap(battlefield)),lit=True,flags=['premapped','shortsighted'])
    lvl.add_line(shopheader)
    lvl.add_object(name="amulet of ESP",symbol="\"",place=(1,1))
    lvl.add_line(battlefieldheader)
    lvl.add_door("locked", place=incominglocation)
    lvl.fill_terrain("rect",".",15,1,15,incominglocation[1])
    lvl.fill_terrain("rect",".",15,incominglocation[1],incominglocation[0]-1,incominglocation[1])
    return lvl.get_des(),custom





class Run:
    def __init__(self,seed=random.randint(0,200),startinglevel=1):
        self.seed=seed
        self.levelnumber=startinglevel
        self.desfile,self.roomtype=completemapdes(self.levelnumber,self.seed)

    def getdes(self):
        return self.desfile
    def gettype(self):
        return self.roomtype
    def nextlevel(self):
        if self.levelnumber==5:
            return "GG"
        else:
            self.levelnumber=self.levelnumber+1
            self.desfile,self.roomtype=completemapdes(self.levelnumber,self.seed)

    def newrun(self,seed=random.randint(0,200)):
        self.seed=seed
        self.levelnumber=1
        self.desfile,self.roomtype=completemapdes(self.levelnumber,self.seed)


