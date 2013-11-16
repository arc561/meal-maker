#!/usr/bin/env python

"""
	RecipeBuilder
	====================
	RecipeBuilder script. This uses the Fridge module to
	construct and build a set of recipes and the current
	available food. A recipe is selected based on the food
	closest to the expiry date. If no food meets the 
	criteria, nothing is returned...

"""

import fridge
import argparse

def main():
	# This is just the standard cmd line 
	rb = fridge.RecipeBuilder()
	# construct the initial object...
	rb.build_all(args.fridge, args.recipes)
	# grab today's recipe...
	recipe = rb.todays
	if recipe:
		print "Optimal recipe is: {}".format(recipe.name)
	else:
		print "No recipe available. Buy more food."

if __name__ == "__main__":
	"""
		The fridge csv file and the recipes JSON file should be specified on 
		the cmd line, otherwise nothing will be available...
	"""
	parser = argparse.ArgumentParser()
	parser.add_argument("-f", "--fridge", nargs='?', help="CSV file of fridge items")
	parser.add_argument("-r", "--recipes", nargs='?', help="JSON file of recipes")
	args = parser.parse_args()
	main()