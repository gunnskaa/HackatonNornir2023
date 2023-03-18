import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import threading
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
import requests
import json
import datetime
import time


mic1_x = 192
mic1_y = 462

mic2_x = 390
mic2_y = 930

smile_emoji = mpimg.imread('smile.png')
mad_emoji = mpimg.imread('mad.png')
bg_image = mpimg.imread('gruva_small.png')

def plotEmojis(ax,x1, y1, x2, y2, mic1_emoji, mic2_emoji, size1, size2):
    
    # Display the background image
    ax.imshow(bg_image)

    # Create offset images for the emojis with the desired size
    oi1 = OffsetImage(mic1_emoji, zoom=size1)
    oi2 = OffsetImage(mic2_emoji, zoom=size2)

    # Create annotation boxes for the emojis at the specified positions
    ab1 = AnnotationBbox(oi1, (x1, y1), frameon=False)
    ab2 = AnnotationBbox(oi2, (x2, y2), frameon=False)

    # Add the annotation boxes to the axis
    ax.add_artist(ab1)
    ax.add_artist(ab2)

    # Set the axis limits to match the background image size
    ax.set_xlim(0, bg_image.shape[1])
    ax.set_ylim(bg_image.shape[0], 0)

    # Remove axis ticks and labels
    ax.set_xticks([])
    ax.set_yticks([])


fig, ax = plt.subplots(2,1)
fig2, ax2 = plt.subplots()


# def animate(i):
#    threadLock.acquire()
#    ax[0].clear()
#    ax[1].clear()
#    for sender, data in database_loudness.items():
#       if "TIMESTAMP" in data and len(data["TIMESTAMP"]) > 3:
         
#          ax[0].stairs(data["LOUDNESS"][1:], data["TIMESTAMP"],
#                baseline=None, label=sender)
         
#       # plot the last 5 data points
#    for sender, data in database_hc.items():
#       nPeopl = data["HEADCOUNT"][-1]
#       ax[1].text(5,10,f"Number of people: {nPeopl}", fontsize=20)
#       # if "TIMESTAMP" in data and len( data["TIMESTAMP"])>3:
#       #    ax[1].stairs(data["HEADCOUNT"][1:], data["TIMESTAMP"],
#                   # baseline=None, label=sender)
#    ax[1].set_xlim([0,20])
#    ax[1].set_ylim([0,20])
#    ax[1].set_xticks([])
#    ax[1].set_yticks([])
#    ax[0].set_title("Sound level")
#    ax[0].set_ylabel("Normalized sound level")
#    # ax[1].set_ylabel("Number of people")
#    ax[0].set_xlabel("Time")
#    ax[0].legend()
#    ax[1].legend()
#    threadLock.release()

         
def animate(i):
   threadLock.acquire()
   ax[0].clear()
   ax[1].clear()
   for sender, data in database_loudness.items():
      if "TIMESTAMP" in data and len(data["TIMESTAMP"]) > 3:
         
         ax[0].stairs(data["LOUDNESS"][1:], data["TIMESTAMP"],
               baseline=None, label=sender)
      # plot the last 5 data points
   for sender, data in database_hc.items():
      nPeopl = data["HEADCOUNT"][-1]
      ax[1].text(5,10,f"Number of people: {nPeopl}", fontsize=20)
      # if "TIMESTAMP" in data and len( data["TIMESTAMP"])>3:
      #    ax[1].stairs(data["HEADCOUNT"][1:], data["TIMESTAMP"],
                  # baseline=None, label=sender)
   ax[1].set_xlim([0,20])
   ax[1].set_ylim([0,20])
   ax[1].set_xticks([])
   ax[1].set_yticks([])
   ax[0].set_title("Sound level")
   ax[0].set_ylabel("Normalized sound level")
   # ax[1].set_ylabel("Number of people")
   ax[0].set_xlabel("Time")
   ax[0].legend()
   ax[1].legend()
   threadLock.release()

def animate2(i):
   threadLock.acquire()
   ax2.clear()
   noise_mic1 = 0
   noise_mic2 = 0
   i = 0
   for sender, data in database_loudness.items():
      if "TIMESTAMP" in data and len(data["TIMESTAMP"]) > 3:
         if i == 0:
            noise_mic1 = data["LOUDNESS"][-1]
            i += 1
         elif i == 1:
            noise_mic2 = data["LOUDNESS"][-1]
    
   if noise_mic1 > 0.1:
      noise_mic1 = 0.1
      mic1_emoji = mad_emoji
   else:
      mic1_emoji = smile_emoji
   if noise_mic2 > 0.1:
      noise_mic2 = 0.1
      mic2_emoji = mad_emoji 
   else:
      mic2_emoji = smile_emoji

   plotEmojis(ax2,mic1_x, mic1_y, mic2_x, mic2_y, mic1_emoji, mic2_emoji,0.05 + noise_mic1, 0.05 + noise_mic2)
   threadLock.release()


def streaming():
  s = requests.Session()
  payload = {
     "token": "aToken_36d8715e3531fd8e8c01fcbfd26bf5af1908e14f15014d2d14817b568bc0bb0e",
     "objectID": "1",
     "format": "json"
  }

  headers = {
    'Synx-Cat': '4',
    'Content-Type': "application/x-www-form-urlencoded"
  }
  req = requests.Request("POST", 'https://8group.cioty.com/example1',
                         headers=headers, params=payload).prepare()
  resp = s.send(req, stream=True)

  for line in resp.iter_lines():
    if line:
      yield line


class myThread (threading.Thread):
   def __init__(self, threadID, name, counter):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.counter = counter

   def run(self):
      for line in streaming():
         data = json.loads(line.decode())
         
         try:
            sender = data["RTW"]["SENDER"]
            time = data["RTW"]["TIMESTAMP"]
            time = datetime.datetime.strptime(time, "%Y/%m/%d, %H:%M:%S")
         except:
            continue
         threadLock.acquire()

         if "LOUDNESS" in data["RTW"]:
            if not sender in database_loudness:
               database_loudness[sender] = {}
            if "TIMESTAMP" in database_loudness[sender] and time < database_loudness[sender]["TIMESTAMP"][-1]:
               threadLock.release()
               continue
            if "LOUDNESS" in database_loudness[sender]:
               database_loudness[sender]["LOUDNESS"].append(float(data["RTW"]["LOUDNESS"]))
               database_loudness[sender]["TIMESTAMP"].append(time)
            else:
               database_loudness[sender]["LOUDNESS"] = [float(data["RTW"]["LOUDNESS"])]
               database_loudness[sender]["TIMESTAMP"] = [time]
         if "HEADCOUNT" in data["RTW"]:
            if not sender in database_hc:
               database_hc[sender] = {}
            if "TIMESTAMP" in database_hc[sender] and time < database_hc[sender]["TIMESTAMP"][-1]:
               threadLock.release()
               continue
            if "HEADCOUNT" in database_hc[sender]:
               database_hc[sender]["HEADCOUNT"].append(int(data["RTW"]["HEADCOUNT"]))
               database_hc[sender]["TIMESTAMP"].append(time)
            else:
               database_hc[sender]["HEADCOUNT"] = [int(data["RTW"]["HEADCOUNT"])]
               database_hc[sender]["TIMESTAMP"] = [time]
         print(data)
         threadLock.release()
         for sender in database_loudness:
            if (datetime.datetime.now() - database_loudness[sender]["TIMESTAMP"][0]).total_seconds() > 60:
               database_loudness[sender]["TIMESTAMP"].pop(0)
               database_loudness[sender]["LOUDNESS"].pop(0)
         for sender in database_hc:
            if (datetime.datetime.now() - database_hc[sender]["TIMESTAMP"][0]).total_seconds() > 60:
               database_hc[sender]["TIMESTAMP"].pop(0)
               database_hc[sender]["HEADCOUNT"].pop(0)
         
         
    

temps = []
times = []

database_loudness = {}
database_hc = {}

thread1 = myThread(1, "Thread-1", 1)


thread1.start()
# call the animation
threadLock = threading.Lock()
ani = FuncAnimation(fig, animate, interval=500)
ani2 = FuncAnimation(fig2, animate2, interval=500)
plt.show()

# Example usage
# plotEmojis(mic1_x, mic1_y, mic2_x, mic2_y, 0.05, 0.05)