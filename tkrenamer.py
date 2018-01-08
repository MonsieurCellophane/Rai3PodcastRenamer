#! /usr/bin/env python
#https://stackoverflow.com/questions/13318742/python-logging-to-tkinter-text-widget
import time
import threading
import logging
try:
    import tkinter as tk # Python 3.x
    import tkinter.scrolledtext as ScrolledText
except ImportError:
    import Tkinter as tk # Python 2.x
    import ScrolledText

class TextHandler(logging.Handler):
    # This class allows you to log to a Tkinter Text or ScrolledText widget
    # Adapted from Moshe Kaplan: https://gist.github.com/moshekaplan/c425f861de7bbf28ef06
    
    def __init__(self, text):
        # run the regular Handler __init__
        logging.Handler.__init__(self)
        # Store a reference to the Text it will log to
        self.text = text
        self.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    def emit(self, record):
        msg = self.format(record)
        def append():
            self.text.configure(state='normal')
            self.text.insert(tk.END, msg + '\n')
            self.text.configure(state='disabled')
            # Autoscroll to the bottom
            self.text.yview(tk.END)
        # This is necessary because we can't modify the Text from other threads
        self.text.after(0, append)

class myGUI(tk.Frame):

    # This class defines the graphical user interface 
    
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.root = parent
        self.build_gui()
        
    def build_gui(self):                    
        # Build GUI
        self.root.title('RAI Radio3 podcast renamer')
        self.root.option_add('*tearOff', 'FALSE')
        # self.grid(column=0, row=0, sticky='news')
        # self.grid_columnconfigure(0, weight=1, uniform='a')
        # self.grid_columnconfigure(1, weight=1, uniform='a')
        # self.grid_columnconfigure(2, weight=1, uniform='a')
        # self.grid_columnconfigure(3, weight=1, uniform='a')
        
        # # Add text widget to display logging info
        # st = ScrolledText.ScrolledText(self, state='disabled')
        # st.configure(font='TkFixedFont')
        # st.grid(column=0, row=1, sticky='news', columnspan=4)
        #https://stackoverflow.com/questions/42006805/python-scrolledtext-module
        self.root.minsize(width=666, height=666)
        textContainer = tk.Frame(self.root, borderwidth=1, relief="sunken")
        text = tk.Text(textContainer, width=24, height=13, wrap="none", borderwidth=0)
        textVsb = tk.Scrollbar(textContainer, orient="vertical", command=text.yview)
        textHsb = tk.Scrollbar(textContainer, orient="horizontal", command=text.xview)
        text.configure(yscrollcommand=textVsb.set, xscrollcommand=textHsb.set)

        text.grid(row=0, column=0, sticky="nsew")
        textVsb.grid(row=0, column=1, sticky="ns")
        textHsb.grid(row=1, column=0, sticky="ew")

        textContainer.grid_rowconfigure(0, weight=1)
        textContainer.grid_columnconfigure(0, weight=1)

        textContainer.pack(side="top", fill="both", expand=True)

        text.configure(font='TkFixedFont')
        # Create textLogger
        text_handler = TextHandler(text)
        
        # Logging configuration
        logging.basicConfig(                     #filename='test.log',
            level=logging.INFO ,         #, level=logging.INFO, 
            format='%(asctime)s - %(levelname)s - %(message)s')        
        
        # Add the handler to logger
        logger = logging.getLogger()        
        logger.addHandler(text_handler)
              
########################################################
# http://effbot.org/zone/tkinter-directory-chooser.htm
# tkDirectoryChooser.py
# $Id: tkinter-directory-chooser.txt 3403 2008-03-25 22:53:59Z fredrik $
#
# tk common directory dialogue
#
# this module provides interfaces to the native directory dialogue
# available in Tk 8.3 and newer.
#
# written by Fredrik Lundh, November 2000.
#

#
# options (all have default values):
#
# - initialdir: initial directory.  preserved by dialog instance.
#
# - mustexist: if true, user must pick an existing directory
#
# - parent: which window to place the dialog on top of
#
# - title: dialog title
#

from tkCommonDialog import Dialog

class Chooser(Dialog):

    command = "tk_chooseDirectory"

    def _fixresult(self, widget, result):
        if result:
            # keep directory until next time
            self.options["initialdir"] = result
        self.directory = result # compatibility
        return result

#
# convenience stuff

def askdirectory(**options):
    "Ask for a directory name"

    return apply(Chooser, (), options).show()

########################################################
import re
#for os.listdir
import os
#for os.path.split,join,splitext
import os.path
import sys

def add_dir(folder):
    stuff=[]
    for line in os.listdir(folder):
        if line == '.' : continue
        if line == '..' : continue
        line=os.path.join(folder,line)
        if not os.path.isdir(line):
            stuff.append(line)
        else:
            stuff.extend(add_dir(line))
            
    return stuff
    
def worker(item):
    print("Using item: %s"%item)
    #rc=re.compile(r'(?P<channel>[\w_]+)_del_(?P<day>\d\d)_(?P<month>\d\d)_(?P<year>\d\d\d\d)_+(?P<title>.*)$')
    rc=re.compile(r'^(?P<channel>.+)_del_(?P<day>\d\d)_(?P<month>\d\d)_(?P<year>\d\d\d\d)(_+)?(?P<title>.*)?$')
    #m=rc.match(name)
    #m.group('title')
    if not os.path.isdir(item):
        logging.fatal("Not a directory:'%s'"%item)
        sys.exit(1)
    files=add_dir(item)

    for p in files:
        (top,suffix)=os.path.splitext(p)
        #import ipdb; ipdb.set_trace()
        if suffix.lower() != '.mp3' :
            logging.warning("Skipping non mp3 (%s) :%s"%(suffix,p))
            #import ipdb; ipdb.set_trace()
            continue
        
        (dirname,basename)=os.path.split(top)
        mt=rc.match(basename)
        if not mt:
            logging.warning("Problems in matching %s"%p)
            #import ipdb; ipdb.set_trace()
            continue
        
        (channel,day,month,year,title,)=(mt.group('channel'),mt.group('day'),mt.group('month'),mt.group('year'),mt.group('title'),)
        if channel and day and month and year:
            target=os.path.join(dirname,"%s_%s_%s_%s_%s%s"%(year,month,day,title,channel,suffix))
            logging.info("Renaming %s to %s"%(p,target))
            os.rename(p,target)
        else:
            logging.warn("Skipping non conformant name %s"%basename)
    logging.info("*******************************************")
    logging.info("**       DONE                            **")
    logging.info("**  You can close this window now        **")
    logging.info("*******************************************")
                
########################################################
def main():
    
    root = tk.Tk()
    myGUI(root)
    
    t1 = threading.Thread(target=worker, args=[str(askdirectory())])
    t1.start()
        
    root.mainloop()
    t1.join()
    
main()
