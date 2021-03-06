import pytesseract
import cv2
import sys
import math
import numpy as np
import os
from PIL import Image
from os import listdir
from os.path import isfile, join
import re
import pandas as pd


lang = 'hin+eng'
def ocr(file,lang,option,d): 
  # Define config parameters.
  # '--oem 1' for using LSTM OCR Engine
  config = ('-l '+lang+' --oem 1 --psm 3')
  if option == 1:
    # Read image from disk
    im = cv2.imread(file, cv2.IMREAD_COLOR)
  else :
    im = file
  
  if d == 1:
    temp = im
    temp = cv2.bitwise_not(temp)
    temp = cv2.resize(temp, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    thresh = 127
    temp = cv2.threshold(temp, thresh, 255, cv2.THRESH_BINARY)[1]
    temp = cv2.threshold(temp, 0, 255, cv2.THRESH_BINARY_INV)[1]
    con = pytesseract.image_to_data(temp, output_type='data.frame')
    con = con[con.conf != -1]
    con = con.groupby(['block_num'])['conf'].mean()
    text = pytesseract.image_to_string(temp, config=config)
  else:
    temp = im
    temp = cv2.fastNlMeansDenoisingColored(temp,None,20,10,7,21)
    temp = cv2.fastNlMeansDenoising(temp,None,10,7,21)
    temp = cv2.bitwise_not(temp)
    temp = cv2.resize(temp, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    thresh = 127
    temp = cv2.threshold(temp, thresh, 255, cv2.THRESH_BINARY)[1]
    #temp = cv2.threshold(temp, 0, 255, cv2.THRESH_BINARY_INV)[1]
    con = pytesseract.image_to_data(temp, output_type='data.frame')
    con = con[con.conf != -1]
    con = con.groupby(['block_num'])['conf'].mean()
    text = pytesseract.image_to_string(temp, config=config)

  temp1 =im
  #Comment for Bengali 
  temp1 = cv2.fastNlMeansDenoisingColored(temp1,None,20,10,7,21)
  temp1 = cv2.fastNlMeansDenoising(temp1,None,10,7,21)
  temp1 = cv2.bitwise_not(temp1)
  temp1 = cv2.resize(temp1, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
  thresh = 127
  temp1 = cv2.threshold(temp1, thresh, 255, cv2.THRESH_BINARY)[1]
  temp1 = cv2.threshold(temp1, 0, 255, cv2.THRESH_BINARY_INV)[1]  
  con1 = pytesseract.image_to_data(temp1, output_type='data.frame')
  con1 = con1[con1.conf != -1]
  con1 = con1.groupby(['block_num'])['conf'].mean()    
  text1 = pytesseract.image_to_string(temp1, config=config) 

  # Test conditions
  f=0
  if con.empty and text != '' and con1.empty and text1 != '':
    #print("no conf ",file,text,text1)
    return (text,con)
  if con.empty and con1.empty:
    if text1 != '':
      #print(1)
      return (text1,con1)  
    else: return text
  elif con1.empty and text !='':
    con1 =con
    return (text,con)
  elif con.empty and text1 !='':
    con =con1
    return (text1,con1)

  #if (con[1] <40) and (con1[1]< 40):
    #print(file)
    #print('low',con1[1], con[1])
    #return (text)
  if con[1] > con1[1]:
    text = text
    #print(con[1])
  elif con1[1] >con[1]:
    text = text1
    con = con1    
    #print(con1[1])
  #print(text)
  # Print recognized text
  return(text,con)

filename = ''
print("text")
er = open('outputs/output1.txt',"w+")
op = open('outputs/output1.srt',"w+")
'''file = 'img/tick-16182.84951618285.jpg'
text =(ocr(filename+file,lang,1,1))
op.write(text)
print(text)'''

def writefile(h,m,s,ms,no,f,text):
  op.write(str(no))
  op.write('\n')
  op.write(str("%02d" %(h))+':'+str("%02d" %(m))+':'+str("%02d" %(s))+','+str("%03d" %(ms))+' --> ')
  s,ms = (s+2,ms+200) if ms+200<1000 else (s+3,ms+200-1000)
  m,s = (m+1,s-60) if s>=60 else (m,s)
  op.write(str("%02d" %(h))+':'+str("%02d" %(m))+':'+str("%02d" %(s))+','+str("%02d" %(ms)))
  op.write('\n')
  '''if len(text.split(' '))>2:
    text =text.split(' ')[1:-1]
  op.write(str(' '.join(text)).replace('\n',' '))'''
  op.write(str(text).replace('\n',' '))
  op.write('\n\n')

def frameno(f):
  return re.search('[1-9]\d*(\.\d+)?',f).group(0)

def fetch_output(op):
  filename = 'img/'
  print("Writing")
  l =listdir('img/')
  for i in range(0,len(l)):
    if re.match('.*\.??g',l[i]):
      l[i] = float(frameno(l[i]))
  l = sorted(l)
  #l = list(map(lambda x:'tick-'+str(x)+'.jpg',sorted(l)))
  prev='p'
  no = 1
  for f in l[:]:
    s,ms=divmod(f,1000)
    m,s=divmod(s,60)
    h,m=divmod(m,60)
    f = 'tick-'+str(f)+'.jpg'
    try:
      text,con = ocr(filename+f,lang,1,1)
      if "".join(text.split()) == '':
        raise Exception('blank')
      text = text.split(' ')
      '''
      if (prev[len(prev)-1][0] != text[0][0]):
        op.write(prev[len(prev)-1])
        op.write(text[0]+' ')  
        print(prev[len(prev)-1][0],text[0][0])'''
      stripped = " ".join(text[0:len(text)])
      prev = text
      writefile(h,m,s,ms,no,f,stripped)      
      no+=1
    except:
      try:
        text,con =ocr('backup/'+f,lang,1,1)
        writefile(h,m,s,ms,no,f,text)
        no+=1
        op.write('\n')
        #print('try',f,text)
      except Exception as err:
        er.write(f+' '+ str(err))
        print(err)
        #op.write("ERROR "+f)
        #op.write("\n")
        er.write('\n')
          #os.remove(filename+f)'''

#op.close()
fetch_output(op)
