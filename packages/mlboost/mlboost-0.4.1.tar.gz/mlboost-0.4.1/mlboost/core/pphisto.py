#!/usr/local/bin/python

# pphisto is part of ppboost
# ppboost: PreProcessing boost library 
# ppboost should help you boost your (Machine Learning) Preprocessing steps  
# Copyright (C) 2006-2009  Francis Pieraut

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import sys
import types
from operator import itemgetter

# Compute Histogram---------------------------------
# set normalize = true and you will get a frequency distribution
def Histogram(values,normalize=False):
	hist = {}
	if len(values)==0:
		return hist
	isstring=(type("")==type(values[0]))
	for val in values:
                if isstring:
                    val=val.lower()
		hist[val] = hist.get(val,0) + 1.0
	if normalize:
		n=float(len(values))
		for k in hist:
			hist[k]/=n/100.0
	return hist

# frequency distribution (histogram normalized)
def fdist(values):
	return Histogram(values,True)

# Sort Histograms ----------------------------------
def SortHistograms(histograms,key=True,doreverse=False):

	# sort each histogram
	for k in histograms.keys():
		histograms[k]=SortHistogram(histograms[k],key,doreverse)


# Sort Histogram->return list ----------------------------------
def SortHistogram(histogram,key=True,doreverse=False):

        if type(histogram)!=type({}):
            sys.stderr.writelines("error: SortHistogram(h)...h isn't a histogram; h="+str(histogram)+"\n")
            return []
	sortedhistogram={}
	if key==False:
                items = histogram.items()
		items.sort(key=itemgetter(1), reverse=doreverse)
	else:
		titems=[]
		for k in histogram:
			titems.append([histogram[k],k])
			titems.sort(key=itemgetter(1), reverse=doreverse)
			#reverse v,k->k,v
			items=[]
			for vk in titems:
				items.append((vk[1],vk[0]))
				
	sortedhistogram=items
	return sortedhistogram

# Get Percentile dictionary-------------------------------
def PercentileDictionary(values):

	# get histogram
	hist=Histogram(values,False)
	
	keys=hist.keys()
	keys.sort()
	
	n=0.0
	percentile={}
	for v in keys:
		n+=float(hist[v])
		percentile[v]=n
		nb=float(len(values))
	for v in keys:
		percentile[v]=percentile[v]/nb*100.0#math.floor(percentile[v]/nb*100.0)
	
	return percentile



