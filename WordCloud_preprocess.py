#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 14 15:55:24 2016

@author: richanetto
"""

import numpy

#This part converts the csv data from Excel into a textfile that has increased number of words depending on the weight
#E.G.: IF THE WEIGHT OF SOME WORD (SAY, ABORTION) IS 9.28356, THE EXCEL FILE SCALES AND ROUNDS UP THIS VALUE TO GIVE 9284. 
#THE WORDCLOUD.TXT FILE AT THE END OF THIS SEGMENT OF THE CODE HAS THE WORD ABORTION IN IT 9284 TIMES
output = []

f = open( 'data5.csv', 'rU' ) #open the file in read universal mode 
#change the name of the file here to enter the new dataset that you want to process and generate the wordcloud for
for line in f:
    cells = line.split( "," )
    output.append( ( cells[ 0 ], cells[3] ) ) #since we want the first and fourth column
    
f.close()
a=[]
b=[]
for i in range(1,len(output)):
    scr = (output[i][1])
    scr = scr.strip('\n')
    a.append(output[i][0])
    b.append(scr)

b = list(map(int,b))
c=[]
for i in range(len(b)):
    for j in range(b[i]):
        c.append(a[i])
    
numpy.savetxt('wordcloud5.txt', c, delimiter=" ", fmt="%s") 



