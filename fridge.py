#!/usr/bin/env python

"""
Fridge Module
====================
The fridge module contains all things to do with food, fridges, and recipes.
Data can be parsed from CSV and JSON files. The data is then parsed and placed
into a data structure. It is then possible to determine which recipes are 
possible based on the food in the fridge.

Brief list of the classes:

FoodType: 		-- Enum type for food items, describes the units
FoodItem: 		-- Data structure for a food item. Contains amount, type, unit and expiry
FoodList: 		-- List of food items and useful functions
RecipeItem: 	-- Structure for recipes, contains a name and a FoodList
RecipeBuilder:	-- Contains current fridge and recipes, and functions to sort and search 

File structures:

The fridge file is a CSV file with food items and their expiry. The
format expected in the CSV file is: [name],[amount],[type],[date]. e.g.

			cheese,10,slices,26/12/2014

The recipe file is assumed to be a JSON string containing recipe objects 
with a name and a list of ingredients. e.g.
			[ {
			  "name": "grilled cheese on toast",
			  "ingredients": [
			   { "item":"bread", "amount":"2", "unit":"slices"},
			   { "item":"cheese", "amount":"2", "unit":"slices"}
			  ]
			} , {
			  "name": "salad sandwich",
			  "ingredients": [
			   { "item":"bread", "amount":"2", "unit":"slices"},
			   { "item":"mixed salad", "amount":"100", "unit":"grams"}
			  ]
			} ]
"""
import csv
import json
import datetime
import itertools

# enum of food types...
class FoodType:
	"""
		FoodType is an enum type for the FoodItems. This describes the 
		units for the items in the fridge or the recipe list...
	"""
	SINGLE = 'of'
	GRAMS = 'grams'
	ML = 'ml'
	SLICES = 'slices'
	@staticmethod
	def build(string):
		if string in [FoodType.SINGLE, FoodType.GRAMS, FoodType.ML, FoodType.SLICES]:
			return string
		else:
			raise Exception("Cannot parse {} as FoodType")

class FoodItem(object):
	""" 
		FoodItem contains an amount, a type, a name and an 
		expiry if required.
	"""
	def __init__(self, amt=0, food_type=FoodType.SINGLE, name='', date=None):
		self.amount = amt
		self.type = food_type
		self.name = name
		self.expiry = date
	def __str__(self):
		if self.expiry:
			return "{} {} of {}, expires {}".format(self.amount, self.type, self.name, self.expiry)
		else:
			return "{} {} of {}".format(self.amount, self.type, self.name)

class FoodList(object):
	"""
		Full food list object. Used for unpacking the strings and 
		building a structure full of ready-to-expire fridge items
	"""
	def __init__(self):
		self.items = []

	def __iter__(self):
		return iter(self.items)

	def build_fridge_item(self, name, amt, food_type, expiry=None):
		"""
			This function is used to pull in string arguments,
			then parse into the FoodItem data structure. The element
			will then be added to the internal list. If the item
			cannot be parsed, nothing is done.
		"""
		try:
			fridge_item = FoodItem()
			fridge_item.name = name.strip()
			fridge_item.type = FoodType.build(food_type.strip())
			fridge_item.amount = int(amt)
			if expiry:
				expiry = expiry.strip()
				# split date string into reversed ISO date format args...
				dates = map(int, reversed(expiry.split('/')))
				fridge_item.expiry = datetime.date(*dates)
			self.items.append(fridge_item)
		except Exception as e:
			# fail, but not catastrophic...
			print "Failed to parse fridge item: {}".format(e)

	def _compact_food_list(self, food):
		"""
			We use the groupby function to combine similar items.
			Firstly groupby needs names in contiguous positions...
		"""
		food = sorted(food, key=lambda x: x.name)
		grouped_list = itertools.groupby(food, key=lambda x: x.name)
		all_list = FoodList()
		for key, x in grouped_list:
			same_foods = list(x)
			item = same_foods[0]
			item.amount = sum(y.amount for y in same_foods)
			all_list.items.append(item)
		return all_list

	def todays_food(self):
		"""
			Here we simply need to sort on the expiry, and drop 
			anything that is past the expiry. We then combine the
			remaining food to get today's available food...
		"""
		# print out items in fridge in expiry order...
		sorted_food = sorted(self.items, key=lambda x: x.expiry)
		edible = filter(lambda x: x.expiry >= datetime.date.today(), sorted_food)
		# don't care about expiry any more, we're good. Now we can combine the items
		# for our final list...
		food = self._compact_food_list(edible)
		return food

class RecipeItem(object):
	"""
		RecipeItem is a simple data structure to store
		the name of the recipe and the FoodList required.
		The FoodList in this case will not contain relevant
		expiry data...
	"""
	def __init__(self, name='', ingredients=FoodList()):
		self.name = name
		self.ingredients = ingredients

class RecipeBuilder(object):
	"""
		The main RecipeBuilder class. This contains 2 internal data
		structures, a fridge and a list of recipes. This class performs
		parsing of input files to fill the fridge and recipes, and also
		performs the main function of sorting and selecting recipes based
		on the fridge contents...
	"""
	def __init__(self):
		# list of food items with expiry...
		self.fridge = FoodList()
		# list of RecipeItems...
		self.recipes = []
		# calculated recipe
		self.todays = RecipeItem()

	def build_all(self, fridge_file, recipe_file):
		""" 
			Load both of the files and locate the current
			recipe. This will print debug info to the terminal.

		"""
		# load fridge...
		self.build_fridge(fridge_file)
		self.build_recipes(recipe_file)
		# recalculate today's recipe...
		self.todays_recipe()

	def build_fridge(self, filename=None):
		"""
			Here we construct the fridge object 
			from a well-formed csv file. If the line
			cannot be parsed, the line is simply skipped.

			Format expected in the csv file is: [name],[amount],[type],[date]. e.g.

			cheese,10,slices,26/12/2014
		"""
		# load up the fridge...
		try:
			f = open(filename, 'rb')
			fridge_reader = csv.reader(f, delimiter=',')
			for line in fridge_reader:
				# unpack the string and add to the fridge data structure...
				self.fridge.build_fridge_item(*line)
		except Exception as e:
			print "Failed to read fridge file {}.".format(filename)
			print e
		return self.fridge

	def build_recipes(self, filename):
		""" 
			Here we expect a file with JSON containing
			recipe objects with a name and a list of 
			ingredients. e.g.

			[ {
			  "name": "grilled cheese on toast",
			  "ingredients": [
			   { "item":"bread", "amount":"2", "unit":"slices"},
			   { "item":"cheese", "amount":"2", "unit":"slices"}
			  ]
			} , {
			  "name": "salad sandwich",
			  "ingredients": [
			   { "item":"bread", "amount":"2", "unit":"slices"},
			   { "item":"mixed salad", "amount":"100", "unit":"grams"}
			  ]
			} ]
		"""
		# load up recipes from a file...
		try:
			# Here we open the file and assume we have a 
			# well formed json data structure. The data is
			# converted into a RecipeItem list...
			f = open(filename, 'rb')
			raw_data = json.load(f)
			# parse...
			for x in raw_data:
				items = FoodList()
				for y in x['ingredients']:
					# here we parse the ingredients text string
					# to construct a FoodItem in the items list... 
					items.build_fridge_item(y['item'].strip(), 
											int(y['amount']),
											y['unit'].strip())
				# now we can build a RecipeItem and add it to the list...
				rec = RecipeItem(x['name'], items)
				self.recipes.append(rec)
		except Exception as e:
			print "Failed to read recipes file {}.".format(filename)
			print e
		return self.recipes

	def _get_cooking_date(self, ingredients, food_list):
		"""
			Given a set of ingredients and a food_list, 
			returns is_possible and the youngest date, or 
			None if not possible...
		"""
		dates = []
		found = False
		# run through the ingredients...
		for y in ingredients:
			# find the item in the food list. The item must have the
			# same name, and there must be an adequate amount...
			item = None
			for z in food_list:
				if z.name == y.name and z.amount >= y.amount:
					item = z
					found = True
					break
			# if it doesn't exist, forget this whole recipe...
			if not item:
				found = False
				break
			else:
				# if it does exist, add to the expiry date...
				dates.append(item.expiry)
		if found:
			return min(dates)
		else:
			return None

	def todays_recipe(self):
		""" 
			Grab today's food and look through the recipes.
			If it is possible to build the recipe with today's 
			ingredients, then add it to a list with the nearest
			expiry date as the key. From these recipes, we can 
			then return the nearest recipe based on the expiry.
		"""
		# first we find all of the available food
		all_list = self.fridge.todays_food()
		# We can now calculate recipes...
		recipe_list = []
		# run through all the recipes and see what can be built...
		for item in self.recipes:
			# given the ingredients and the food list, find the 
			# date we need to cook by...
			date = self._get_cooking_date(item.ingredients, all_list)
			# if it is possible to cook, then add it to the 
			# list with the date as a key...
			if date:
				recipe_list.append((date, item))
		# now we have all the recipes, so we can find the nearest...
		self.todays = None
		if recipe_list:
			# find the minimum based on the date...
			recipe_obj = min(recipe_list, key=lambda x: x[0])
			# now return the full recipe...
			self.todays = recipe_obj[1]
		return self.todays
