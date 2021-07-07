import time
import psutil
import subprocess
#from fnctime import time_check

def kill(proc_pid):
    process = psutil.Process(proc_pid)
    for proc in process.children(recursive=True):
        proc.kill()
    process.kill()

#ttime = time_check()

#begin process
p0 = subprocess.Popen('cd /Users/amygooch/GIT/ViSOARAgExplorer_SCI" && python VisoarAgExplorer.py', stderr=subprocess.PIPE,  shell=True)
#define variable for checking if p0 is alive
status = p0.poll()

try:
    while True:
        if status != None:          #if process is dead  start it again
            print('\nStart it again')
            p0 = subprocess.Popen('cd /Users/amygooch/GIT/ViSOARAgExplorer_SCI" && python VisoarAgExplorer.py', stderr=subprocess.PIPE,   shell=True)
            status = p0.poll()      #and renew status
            
        while status == None:                        #while it is alive
            print(p0.stdout if p0.stdout else '', end='')     #print what it has printed
            time.sleep(1)                    #wait
            status = p0.poll()              #check again
            
        a, b = p0.communicate()
        
        if b == 'Segmentation fault\n':        #if Segmentation fault occured: 
            print('--Segmentation fault--')
            continue                           #go again
        # if 'UnicodeDecodeError' in b:
        #     print('Unicode Decode Error')
        #     continue
        print(f'--b: {b} --')
        print('--all done--')
        break                        #break whole loop
except KeyboardInterrupt:          #if ctrl^C was clicked
    try:
        kill(p0.pid)           #kill the process
    except:
        print('already dead')      #unless it's dead already

#ttime.check()
