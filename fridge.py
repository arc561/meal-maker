#!/usr/bin/env python

"""
Fridge Module
====================
The fridge module contains all things to do with food, fridges, and recipes.
Data can be parsed from CSV and JSON files. The data is then parsed and placed
into a data structure. It is then possible to determine which recipes are 
possible based on the food in the fridge.

Brief list of the classes:

FoodType:       -- Enum type for food items, describes the units
FoodItem:       -- Data structure for a food item. Contains amount, type, unit and expiry
FoodList:       -- List of food items and useful functions
RecipeItem:     -- Structure for recipes, contains a name and a FoodList
RecipeBuilder:  -- Contains current fridge and recipes, and functions to sort and search 

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
import os
import unittest

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
            return "{} {} {}, expires {}".format(self.amount, self.type, self.name, self.expiry)
        else:
            return "{} {} {}".format(self.amount, self.type, self.name)
    def __eq__(self, other):
        return  (self.amount == other.amount) and \
                (self.type == other.type) and \
                (self.name == other.name) and \
                (self.expiry == other.expiry) \

class FoodList(object):
    """
        Full food list object. Used for unpacking the strings and 
        building a structure full of ready-to-expire fridge items
    """
    def __init__(self):
        self.items = []

    def __iter__(self):
        return iter(self.items)

    def __getitem__(self, key):
        return self.items[key]

    def __eq__(self, other):
        if isinstance(other, FoodList):
            return self.items == other.items
        else:
            return False

    def __len__(self):
        return len(self.items)

    def build_fridge_item(self, name, amt, food_type, expiry=None):
        """
            This function is used to pull in string arguments,
            then parse into the FoodItem data structure. The element
            will then be added to the internal list. If the item
            cannot be parsed, nothing is done.
        """
        try:
            fridge_item = FoodItem()
            # grab the name, no empty strings...
            fridge_item.name = name.strip()
            if not fridge_item.name:
                raise
            # grab the item type, must be of FoodType...
            fridge_item.type = FoodType.build(food_type.strip())
            # grab numbers, must be positive
            fridge_item.amount = int(amt)
            if fridge_item.amount <= 0:
                raise
            # expiry not compulsory, but must be in format DD/MM/YYYY
            if expiry:
                expiry = expiry.strip()
                # split date string into reversed ISO date format args...
                dates = map(int, reversed(expiry.split('/')))
                fridge_item.expiry = datetime.date(*dates)
            # add the item to the fridge...
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
        # we group by name, but not by type...
        grouped_list = itertools.groupby(food, key=lambda x: x.name + x.type)
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
    def __init__(self, name='Order Takeout', ingredients=FoodList()):
        self.name = name
        self.ingredients = ingredients
    def __eq__(self, other):
        return (self.name == other.name) and (self.ingredients == other.ingredients)

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
        # calculated RecipeItem()
        self.todays = RecipeItem()

    def build_all(self, fridge_file, recipe_file):
        """ 
            Load both of the files and locate the current
            recipe. This will print debug info to the terminal.

        """
        # load fridge...
        self.build_fridge(fridge_file)
        # load recipes...
        self.build_recipes(recipe_file)
        # recalculate today's recipe...
        self.todays_recipe()

    def print_debug_info(self):
        print "===FRIDGE ITEMS==="
        for item in self.fridge: 
            print item
        print
        print "===RECIPES FOUND==="
        for recipe in self.recipes:
            print "Recipe: {}".format(recipe.name)
            for item in recipe.ingredients:
                print "\t-- ", item
        # combine the two to get the best recipe...
        print
        if self.todays:
            print "Optimal recipe is:"
            print self.todays.name

    def to_json(self):
        """
            This function will build a dictionary for use when
            passing the data over AJAX back to the web front-end.
            This will format the data to make it a little easier
            for the front end to deal with...
        """
        def item_string(item):
            return "{} {} {}".format(item.amount, item.type, item.name)
        def expiry_string(off_date):
            time = (off_date - datetime.date.today()).days
            if time == 1:
                return "1 day left"
            else:
                return "{} days left".format(time)
        try:
            output = {}
            # grab the pretty string for the fridge items...
            if not self.fridge:
                output['fridge'] = []
            else:
                output['fridge'] = [{
                                'ingredient':item_string(item), 
                                'expiry':expiry_string(item.expiry)
                                } for item in self.fridge]
            # grab the pretty string for the recipes...
            if not self.todays:
                output['recipes'] = []
            else:
                output['recipes'] = [{
                                'name':self.todays.name, 
                                'ingredients': [item_string(item) for item in self.todays.ingredients] 
                                }]
        except Exception as e:
            print e
            raise
        return output

    def build_fridge(self, filename=None, clear=True):
        """
            Here we construct the fridge object 
            from a well-formed csv file. If the line
            cannot be parsed, the line is simply skipped.

            Format expected in the csv file is: [name],[amount],[type],[date]. e.g.

            cheese,10,slices,26/12/2014
        """
        if clear:
            self.fridge = FoodList()
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

    def build_recipes(self, filename=None, clear=True):
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

            The clear argument decides whether to clear the
            existing contents of the recipe book or not...
        """
        if clear:
            self.recipes = []
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
            returns the youngest date, or None if no recipe
            is possible...
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
        self.todays = RecipeItem()
        if recipe_list:
            # find the minimum based on the date...
            recipe_obj = min(recipe_list, key=lambda x: x[0])
            # now return the full recipe...
            self.todays = recipe_obj[1]
        return self.todays

"""
===============

 UNIT TESTS for the fridge classes...

===============
"""

class TestFoodList(unittest.TestCase):
    """
        Unit tests for the food list class.
    """
    def setUp(self):
        self.t = FoodList()
    def test_build_fridge_item(self):
        # first check that items are added correctly...
        self.t.items = []
        self.t.build_fridge_item('pickles', 2, 'of', '24/12/2012')
        self.t.build_fridge_item('pickles', 20, 'grams', '24/12/2012')
        self.t.build_fridge_item('pickles', 20, 'ml', '24/12/2012')
        self.t.build_fridge_item('pickles', 2, 'slices', '24/12/2012')
        # build the comparison objects...
        food_items = [None for x in xrange(4)]
        food_items[0] = FoodItem(2, 'of', 'pickles', datetime.date(2012, 12, 24))
        food_items[1] = FoodItem(20, 'grams', 'pickles', datetime.date(2012, 12, 24))
        food_items[2] = FoodItem(20, 'ml', 'pickles', datetime.date(2012, 12, 24))
        food_items[3] = FoodItem(2, 'slices', 'pickles', datetime.date(2012, 12, 24))
        # check that they're equal...
        self.assertEqual(self.t.items[0], food_items[0])
        self.assertEqual(self.t.items[1], food_items[1])
        self.assertEqual(self.t.items[2], food_items[2])
        self.assertEqual(self.t.items[3], food_items[3])
        # next check that illegal types are not added, and no error occurs...
        self.t.items = []
        self.t.build_fridge_item('pickles', 2, 'blocks', '24/12/2012')
        self.assertEqual(self.t.items, [])
        self.t.build_fridge_item('pickles', -2, 'blocks', '24/12/2012')
        self.assertEqual(self.t.items, [])
        self.t.build_fridge_item('pickles', 2, 'blocks', 'junk')
        self.assertEqual(self.t.items, [])
        self.t.build_fridge_item('', 2, 'blocks', '24/12/2012')
        self.assertEqual(self.t.items, [])
    def test_compact_food_list(self):
        # first check make sure the list can be compacted...
        self.t.items = []
        self.t.build_fridge_item('pickles', 2, 'of', '24/12/2012')
        self.t.build_fridge_item('pickles', 20, 'grams', '24/12/2012')
        self.t.build_fridge_item('pickles', 20, 'ml', '24/12/2012')
        self.t.build_fridge_item('pickles', 2, 'slices', '24/12/2012')
        compacted = self.t._compact_food_list(self.t.items)
        self.assertEqual(len(compacted), 4)
        # next make sure different types cannot be compacted...
        self.t.items = []
        self.t.build_fridge_item('pickles', 2, 'of', '24/12/2012')
        self.t.build_fridge_item('pickles', 20, 'of', '24/12/2012')
        self.t.build_fridge_item('pickles', 20, 'of', '24/12/2012')
        self.t.build_fridge_item('pickles', 2, 'of', '24/12/2012')
        compacted = self.t._compact_food_list(self.t.items)
        self.assertEqual(len(compacted), 1)
    def test_todays_food(self):
        # remove stale food...
        self.t.items = []
        self.t.build_fridge_item('pickles', 2, 'of', '24/12/2012')
        self.t.build_fridge_item('pickles', 20, 'grams', '24/12/2012')
        self.t.build_fridge_item('pickles', 20, 'ml', '24/12/2012')
        self.t.build_fridge_item('pickles', 2, 'slices', '24/12/2012')
        today = self.t.todays_food()
        self.assertEqual(len(today), 0)

class TestRecipeBuilder(unittest.TestCase):
    """
        UnitTest class for the RecipeBuilder. These can be executed 
        from the command line with:

        python -m unittest -v -b fridge
    """
    def setUp(self):
        # constants for testing...
        self.TEST_DIR = './test/vectors/'
        self.NO_RECIPE = 'Order Takeout'
        self.EMPTY_JSON_DICT = {
                                'recipes': [{
                                                'ingredients' : [],
                                                'name' : self.NO_RECIPE
                                            }], 
                                'fridge': []
                                }
        self.rb = RecipeBuilder()
        # move to the test signals directory 
        # to simplify filename args...
        self.cwd = os.getcwd()
        os.chdir(self.TEST_DIR)

    def tearDown(self):
        # pop the current working directory...
        os.chdir(self.cwd)

    def test_init(self):
        """
            Clear the RecipeBuilder, and make sure everything is
            in empty as expected...
        """
        self.rb = RecipeBuilder()
        self.assertEqual(self.rb.recipes, [])
        self.assertEqual(self.rb.fridge, FoodList())
        self.assertEqual(self.rb.todays, RecipeItem())
        self.assertEqual(self.rb.to_json(), self.EMPTY_JSON_DICT)
        self.assertEqual(self.rb.todays.name, self.NO_RECIPE)

    def test_build_recipes(self):
        self.rb.build_recipes('recipe-default.json')
        cheese = self.rb.recipes[0]
        salad = self.rb.recipes[1]
        # check the cheese...
        self.assertEqual(cheese.name, 'grilled cheese on toast')
        self.assertEqual(len(cheese.ingredients), 2)
        ingredients = map(str, cheese.ingredients)
        self.assertEqual(ingredients,['2 slices bread', '2 slices cheese'])
        # check the salad...
        self.assertEqual(salad.name, 'salad sandwich')
        self.assertEqual(len(salad.ingredients), 2)
        ingredients = map(str, salad.ingredients)
        self.assertEqual(ingredients,['2 slices bread', '100 grams mixed salad'])

    def test_build_fridge(self):
        self.rb.build_fridge('fridge-default.csv')
        bread = self.rb.fridge[0]
        salad = self.rb.fridge[4]
        # check the elements...
        self.assertEqual(str(bread), '10 slices bread, expires 2012-12-21')
        self.assertEqual(str(salad), '10 slices cheese, expires 2014-12-26')
        self.assertEqual(len(self.rb.fridge), 8)

    def test_to_json(self):     
        self.rb.build_fridge('fridge-default.csv')
        # check the cheese...
        json_obj = self.rb.to_json()
        self.assertEqual(json_obj['recipes'], self.EMPTY_JSON_DICT['recipes'])
        self.assertEqual(len(json_obj['fridge']), 8)

    def test_build_all(self):
        # missing files
        self.rb.build_all('junk', 'junk')
        self.assertEqual(self.rb.todays.name, 'Order Takeout')
        # default example, output salad sandwich...
        self.rb.build_all('fridge-default.csv', 'recipe-default.json')
        self.assertEqual(self.rb.todays.name, 'salad sandwich')
        # swap salad and cheese expiry should get grilled cheese...
        self.rb.build_all('fridge-cheese.csv', 'recipe-default.json')
        self.assertEqual(self.rb.todays.name, 'grilled cheese on toast')
        # swap args for bad data...
        self.rb.build_all('recipe-default.json', 'fridge-cheese.csv')
        self.assertEqual(self.rb.todays.name, 'Order Takeout')
        # traditional missing data pieces...
        self.rb.build_all('fridge-missing.csv', 'recipe-missing.json')
        self.assertEqual(self.rb.todays.name, 'Order Takeout')
        # food in fridge but nothing matches...
        self.rb.build_all('fridge-no-match.csv', 'recipe-no-match.json')
        self.assertEqual(self.rb.todays.name, 'Order Takeout')
        # stale food matches nothing against any recipe...
        self.rb.build_all('fridge-stale.csv', 'recipe-stale.json')
        self.assertEqual(self.rb.todays.name, 'Order Takeout')
        # stale on the garlic recipes still fail...
        self.rb.build_all('fridge-stale.csv', 'recipe-no-match.json')
        self.assertEqual(self.rb.todays.name, 'Order Takeout')
        # ditto the initial recipes...
        self.rb.build_all('fridge-stale.csv', 'recipe-default.json')
        self.assertEqual(self.rb.todays.name, 'Order Takeout')
        # ditto the initial recipes...
        self.rb.build_all('fridge-garlic-snails.csv', 'recipe-no-match.json')
        self.assertEqual(self.rb.todays.name, 'garlic snails')

if __name__ == "__main__":
    """
        To run the unit tests enter the following at the cmd line:

        python fridge.py

        Alternatively, run:

        python -m unittest -v -b fridge
    """
    unittest.main(verbosity=2, buffer=True)
