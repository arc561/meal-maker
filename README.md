Meal Maker
==========

This is a Python program that calculates which meals to make based
on a set of recipes and a list of current available food. A recipe 
is chosen to be optimal if the food is available and the recipe uses
the food closest to the expiry date. If no food meets the criteria,
nothing is returned...

Running
-------
To run the application, simply specify the csv and json file at the command line:

> python run.py --fridge test/default/fridge.csv --recipes test/default/recipe.json

fridge.py
---------

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
