from instancemanager.mainprogram import getProjects
from os import system
from Tkinter import *

commands = { 'stop':'Red',
             'start':'Green',
             'soft':'Cyan',
             'fresh':'Yellow', }

def quit_handle():
    print 'Thank you for using InstanceManager'
    import sys; sys.exit()

def command_handle(project, cmd):
    print 'INSTANCEMANAGER %s %s' % (project, cmd)
    command = 'instancemanager %s %s' % (project, cmd)
    system(command)

root = Tk()

for project in getProjects():
    box = Frame(root)
    prjlabel = Label(box, text=project)
    prjlabel.pack(side=LEFT, expand=YES, fill=BOTH)

    for cmd in commands.keys():
        bt = Button(box,
                    text=cmd,
                    command=(lambda prj=project,
                                    cmd=cmd: command_handle(prj,cmd)),
                    bg=commands[cmd])
        bt.pack(side=RIGHT, expand=YES, fill=BOTH)

    box.pack(side=TOP, expand=YES, fill=BOTH)

exitbutton = Button(root, text='Quit', command=quit_handle)
exitbutton.pack(side=TOP, expand=YES, fill=BOTH)

root.mainloop()
