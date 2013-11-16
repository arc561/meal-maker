'use strict';

var recipeObj = recipeObj || {}

recipeObj = {
	/**
	 *  The recipe object handles the connection to the webserver.
	 *  It expects a list of fridge elements as 
	 *
	 *		[{
	 *			'ingredient': ingredient string, 
	 *			'expiry': printable_expiry_date
	 *		}] 
	 *
	 *  the app expects recipes as 
	 *
	 *		[{
	 *			'name' : recipe_title, 
	 *			'ingredients' : list of printable ingredients... 
	 *		}]
	 *
	 *	The server is doing most of the lifting. Here the JS is only
	 *  concerned with display. 
	 **/
	init: function() {
		this.recipeDiv = $('#recipe-list');
		this.fridgeDiv = $('#fridge-list')
		this.clearRecipes();
	},
	clearRecipes: function() {		
		/**
		 *	Simply clears the recipes list on the page...
		 **/
		this.recipeDiv.text("");
	},
	addRecipes: function(recipeJSON) {		
		/**
		 *	Add recipes to the relevant list positions...
		 **/
		var content = "";
		content += "<ul>";
		if (recipeJSON.length === 0) {
			content += "Order Takeout"
		} else {
			recipeJSON.forEach(function(item){
				content += "<li>";
				content += "<h3>" + item.name + "</h3>";
				content += "<ul>";
				item.ingredients.forEach(function(ingredient) {
					content += "<li>" + ingredient + "</li>";
				});
				content += "</ul>";
				content += "</li>";
			});
		}
		content += "</ul>";
		this.recipeDiv.append(content);
	},
	clearFridge: function() {
		/**
		 *	Simply clears the fridge list on the page...
		 **/
		this.fridgeDiv.text("");
	},
	addFridgeItems: function(fridgeJSON) {		
		/**
		 *	Adds the fridge elements into the relevant list positions...
		 **/
		var content = "";
		content += "<ul>";
		fridgeJSON.forEach(function(item){
			content += "<li>";
			content += item.ingredient;
			content += "<span class='expiry'>" + item.expiry + "</span>";
			content += "</li>";
		});
		content += "</ul>";
		this.fridgeDiv.append(content);
	},
	loadData: function() {
	   /**
		*  Talks to the server to grab the JSON packets for display...
		**/
		$.ajax({
			type : 'GET',
			url: "data.json",
			contentType : 'application/json',
			timeout: 2000,
			success: function(data){
                recipeObj.displayFood(data);	
			},
			failure: function(d) {
				alert("Request to server failed...","#f66");
			},
			error: function(ts) {
				alert("Request to server failed...","#f66");		
			}
		});
	},
	displayFood: function(data) {
		// load up the recipes...
		this.clearRecipes();
		this.addRecipes(data.recipes);
		// load up the fridge...
		this.clearFridge();
		this.addFridgeItems(data.fridge);	
	}
}
window.onload = function(){
	/**
	 *  Grab the recipe information from the server on every page
	 *  load...
	 **/
	recipeObj.init();
	recipeObj.loadData();
}

var testFixtures = {
	recipes: [
		{
			"name":"Salad Sandwich", 
			"ingredients": [
				"10g of butter", 
				"200g of mixed salad", 
				"10 pieces of bread"]
		},
		{
			"name":"Grilled Cheese On Toast", 
			"ingredients": [
				"10g of butter", 
				"10 slices of cheese", 
				"10 pieces of bread"]
		},
	],
	fridge: [
		{
			"ingredient": "100g of butter",
			"expiry": "0 days left"
		},
		{
			"ingredient": "10 slices of cheese",
			"expiry": "2 days left"
		},		
		{
			"ingredient": "500g of mixed salad",
			"expiry": "3 days left"
		},		
		{
			"ingredient": "100g of beef",
			"expiry": "5 days left"
		},
	]
}

