#!/usr/bin/env python3

import socket
import time
import string
import hashlib
import random
import os
import binascii
import base64
#import matplotlib as plt
from PIL import Image
import io
import numpy as np
from threading import Thread

HOST = "challs.xmas.htsp.ro"
PORT = 14001
CHUNK = 10000000

THRESHOLD = 200

chatLog = ''

def sendData(msg):
  global chatLog
  #print("Sending " + msg)
  chatLog += msg
  sent = s.send(msg)
  if sent != len(msg):
    raise RuntimeError("socket connection broken")
  time.sleep(0.5)

def recvData(retries=4):
  global chatLog
  data = s.recv(CHUNK)
  chatLog += data
  print(data)
  if data == '':
    if retries > 0:
      time.sleep(2)
      recvData(retries-1)
    else:
      raise RuntimeError("I can't hear you")
  time.sleep(0.5)
  return data


searching = True
found = None

def shaChallenge(suffix):
    return os.popen("./shapow " + suffix).read().strip()

def stringToRGB(base64_string):
  imgdata = base64.b64decode(str(base64_string))
  with open('last.png', 'wb') as f:
    f.write(imgdata)
    f.close()
  image = Image.open('last.png')
  return image

def getNeighbors(p):
  return [(p[0]+1, p[1]), (p[0]-1, p[1]), (p[0], p[1]+1), (p[0], p[1]-1)]

def getMinIndex(img):
  m = 9999999
  i = (0, 0)
  for y in range(0, img.shape[1]):
    for x in range(0, img.shape[0]):
      v = img[x, y]
      if v < m:
        m = v
        i = (x, y)
  return (i, m)

def countHolesInSymbolContainingPixel(img, startPixel):
  start = time.time()

  boxMin = startPixel
  boxMax = startPixel
  visited = set()
  toVisit = {startPixel}
  adjacentWhite = set()
  while len(toVisit) > 0:
    pixel = toVisit.pop()
    boxMin = (min(pixel[0], boxMin[0]), min(pixel[1], boxMin[1]))
    boxMax = (max(pixel[0], boxMax[0]), max(pixel[1], boxMax[1]))
    visited.add(pixel)
    for neighbor in getNeighbors(pixel):
      if img[neighbor] > THRESHOLD:
        adjacentWhite.add(neighbor)
      else:
        if not neighbor in visited:
          toVisit.add(neighbor)

  if len(visited) < 100:
    for pixel in visited:
      img[pixel] = 255
    return -1

#  print(adjacentWhite)
  boxMin = (boxMin[0] - 1, boxMin[1] - 1)
  boxMax = (boxMax[0] + 1, boxMax[1] + 1)
  print(boxMin)
  print(boxMax)

  halfway = time.time()
  print("Done traversing black, took %f" % (halfway - start))

  holeCount = 0
  labels = {}
  i = 0
  sameLabels = set()
  toVisit.clear()
  sameLabelAs = [0] * len(adjacentWhite)
  for whitePixel in adjacentWhite:
    labels[whitePixel] = i
    toVisit.add(whitePixel)
    sameLabelAs[i] = i
    i += 1

  while len(toVisit) > 0:
    whitePixel = toVisit.pop()
    #print(whitePixel)
    if whitePixel[0] < boxMin[0] or whitePixel[1] < boxMin[1] or whitePixel[0] > boxMax[0] or whitePixel[1] > boxMax[1]:
      continue
    # current pixel is already labeled!
    for other in getNeighbors(whitePixel):
      if img[other] <= THRESHOLD:
        #print('not white')
        continue
      if other in labels:
        sameLabels.add((labels[whitePixel], labels[other]))
        #print('Already labeled')
      else:
        labels[other] = labels[whitePixel]
        toVisit.add(other)
        #print('Adding ' + str(whitePixel))

  oneMore = time.time()
  print("Done traversing white, took %f" % (oneMore - halfway))

  #print(sameLabels)
  for i in range(0, 60):
    for (a, b) in sameLabels:
      mi = min(a, b)
      ma = max(a, b)
      mima = sameLabelAs[ma] # <= ma
      mimi = sameLabelAs[mi] # <= mi
      l = min(mima, mimi)
      sameLabelAs[a] = l
      sameLabelAs[b] = l

  uniqued = time.time()
  print("Done propagating labels, took %f" % (uniqued - oneMore))

  print(sameLabelAs)

  uniqueLabels = set()
  for l in sameLabelAs:
    uniqueLabels.add(l)

  print(uniqueLabels)

  # remove the symbol
  for pixel in visited:
    img[pixel] = 255

  counts = {}
  for pixel in labels:
    l = sameLabelAs[labels[pixel]]
    counts[l] = counts.get(l, 0) + 1
    # debug: overwrite all white pixels with their labels
    #img[pixel] = l

  # filter out lone pixels
  for l in counts:
    if counts[l] < 15:
      uniqueLabels.remove(l)

  end = time.time()
  print("Done with postprocessing, took %f" % (end - uniqued))
  print("Overall time: %f" % (end - start))

  return len(uniqueLabels) - 1





online = True
rounds = 0

if online:
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect((HOST, PORT))
  suffix = recvData()[-7:-1]
  print('Attacking suffix ' + suffix)
  sendData(str(shaChallenge(suffix) + '\n'))




try:
  while True:

    if online:
      response = recvData()
      response = response.split("b'")[1]
      while response.find("(e.g. 0,1,2,3,4,5)") == -1:
        response = response + recvData()
      b64img = response.split("'")[0]
      #print(b64img)
      image = stringToRGB(b64img)
    else:
      #response = open("last.jpg", "r").read()
      image = Image.open('last.png')
    #image.show()

    print("Counting symbols")

    img = np.array(image)[:, :, 0]
    #image = Image.fromarray(img)
    #print(img.shape)
    #print(np.max(img))

    threshold = np.max(img)/2

    counts = [0, 0, 0, 0, 0, 0]

    while True:
      t1 = time.time()
      #(index, maxValue) = getMinIndex(img)
      i = np.argmin(img)
      #print(i)
      index = np.unravel_index(i, img.shape)
      t2 = time.time()
      print("Finding next pixel took %f" % (t2 - t1))
      if img[index] > THRESHOLD:
        break
      count = countHolesInSymbolContainingPixel(img, index)
      #Image.fromarray(img).show()
      if (count < 0):
        continue
      counts[count] = counts[count] + 1

    print(counts)
    rounds = rounds + 1

    if not online:
      time.sleep(5)
      exit(0)

    #plt.figure()
    #plt.imshow(decoded_image)
    #plt.show()

    reply = ','.join([str(c) for c in counts])
    sendData(reply + '\n')

finally:
  print(chatLog)
  print('Died on round %i' % rounds)
