from .pipeline.NodeFactory import NodeFactory
from .pipeline.JsonInterface import JsonInterface
from .pipeline.Pipeline import Pipeline
from blinker import signal

import traceback
import threading
import ctypes
import sys 
import trace  
import time 

class PipelineThread(threading.Thread):

    def __init__(self, file):
        threading.Thread.__init__(self)
        self.file = file
        self.killed = False

    def run(self):  
        try:
            # Extract relevant info from the JSON
            nodes, connections, globals = JsonInterface.load(self.file)

            # Build the pipeline graph
            pipeline = Pipeline(global_vars = globals)

            for node in nodes:
                pipeline.add(node[1])
                
            for conn in connections:
                pipeline.connect(parent = conn[0], child = conn[1])

            pipeline.start()
            
        # Catches any runtime errors and prints to console
        # Lets you debug the pipeline nodes if they crash
        except Exception:
            traceback.print_exc()
            signal("crash").send(self)

    def start(self): 
        self.__run_backup = self.run 
        self.run = self.__run       
        threading.Thread.start(self) 
    
    def __run(self): 
        sys.settrace(self.globaltrace) 
        self.__run_backup() 
        self.run = self.__run_backup 
    
    def globaltrace(self, frame, event, arg): 
        if event == 'call': 
          return self.localtrace 
        else: 
          return None

    def localtrace(self, frame, event, arg): 
        if self.killed: 
          if event == 'line': 
            raise SystemExit() 
        return self.localtrace 

    def kill(self): 
        self.killed = True