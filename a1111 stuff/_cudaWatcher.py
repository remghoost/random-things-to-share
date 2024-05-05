import subprocess
import os
import time
import sys

ascii_art = '''
                _       _    _       _       _               
               | |     | |  | |     | |     | |              
  ___ _   _  __| | __ _| |  | | __ _| |_ ___| |__   ___ _ __ 
 / __| | | |/ _` |/ _` | |/\| |/ _` | __/ __| '_ \ / _ | '__|
| (__| |_| | (_| | (_| \  /\  | (_| | || (__| | | |  __| |   
 \___|\__,_|\__,_|\__,_|\/  \/ \__,_|\__\___|_| |_|\___|_|   
                                                                                                                  
'''

script_directory = os.path.dirname(os.path.abspath(__file__))
batch_file_path = os.path.join(script_directory, "_cudaWatcherRun.bat")
print(ascii_art)
print("sorry, it messes with the output of A1111")
print("everything still works fine on the A1111 side")
print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-")


def terminate_process(process):
    try:
        subprocess.run(["taskkill", "/F", "/T", "/PID",
                       str(process.pid)], check=True)
    except subprocess.CalledProcessError:
        pass  # Ignore if taskkill fails


def monitor_output(process):
    print("MONITOR ACTIVE")
    print("")
    while True:
        lineOutput = process.stdout.readline().decode().strip()
        lineReadout = process.stdout.readline().decode()
        print(lineReadout, end='')
        sys.stdout.flush()  # Flush the output to ensure immediate display
        if lineOutput:
            if "CUDA out of memory" in lineOutput:
                print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-")
                print("HE'S DEAD JIM")
                print("RESTARTING BACKEND SERVER")
                print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-")

                terminate_process(process)
                process = subprocess.Popen(
                    "webui-user.bat", stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True
                )
                print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-")
                print("BACKEND SERVER REBOOT SUCCESSFUL")
                # sys.exit()


process = subprocess.Popen(
    "webui-user.bat", stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True
)

monitor_output(process)
