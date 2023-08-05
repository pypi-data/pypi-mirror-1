#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
Search among the code samples
"""

import sys
import os

SAMPLES_PATHS = os.path.join(
	os.path.abspath(
		os.path.dirname(__file__)),"samples")

pjoin = os.path.join

# We will use here the worst posssible way of indexing the
# documentation, but it is mainly to be used as a test for the doc
# search api.

search_dict = {
	"simple plot text labels title grid" :
		( pjoin(SAMPLES_PATHS, "simple_plot.html"),
		  "basic plot (code sample)"),
	
	"bar barh chart error labels ticks title legend" :
		( pjoin(SAMPLES_PATHS, "barchart.html"),
		  "Barchart (code sample)"),
		 
	"histogram plot bin count probability labels title" :
		( pjoin(SAMPLES_PATHS, "histogram.html"),
		  "histogram (code sample)"),
	
	"log semilog semilogx scale scaling ticks grid label base10 " :
		( pjoin(SAMPLES_PATHS, "log.html"),
		  "Log and semilog plots (code sample)"),

	"pie chart percentage figure axes title" :
		( pjoin(SAMPLES_PATHS, "pie.html"),
		  "Pie chart (code sample)"),
	
	"scatter plot ticks title grid" :
		( pjoin(SAMPLES_PATHS, "scatter.html"),
		  "Scattter plot (code sample)"),
	
	"subplot plot axes figure zoom grid title label" :
		( pjoin(SAMPLES_PATHS, "subplot.html"),
		  "Subplot (code sample)"),
	}


def search(search_query):
	"""
	Search the documentation
	"""
	# split the query into its various keywords
	search_query_kw = search_query.split()
#	print search_query_kw
	result_dict = {}
	for key in search_dict.keys():
		count = 0
		for item in search_query_kw:
			if key.find(str(item))!=-1:
				count += 1
		if count != 0:
			if result_dict.has_key(count):
				result_dict[count].append(search_dict[key]) 
			else:
				result_dict[count] = [search_dict[key]]
#	print result_dict
	ranks = result_dict.keys()
	ranks.sort()
	ranks.reverse()
	results = []
	for r in ranks:
		results.extend(result_dict[r])
	print results
	return results


