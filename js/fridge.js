"use strict";

var RecipeObj = (function () {
        /**
         *  The recipe object handles the connection to the webserver.
         *  It expects a list of fridge elements as 
         *
         *                [{
         *                        'ingredient': ingredient string, 
         *                        'expiry': printable_expiry_date
         *                }] 
         *
         *  the app expects recipes as 
         *
         *                [{
         *                        'name' : recipe_title, 
         *                        'ingredients' : list of printable ingredients... 
         *                }]
         *
         *        The server is doing most of the lifting. Here the JS is only
         *  concerned with display. 
         **/
        var obj = {};

        /**        
         *  Initialize the fridge and recipe lists and talk to the server 
         **/
        obj.init = function () {
                this.recipeDiv = $('#recipe-list');
                this.fridgeDiv = $('#fridge-list');

                this.initFridgeUpload();
                this.initRecipeUpload();
                this.clearRecipes();
        };

        /**        
         *  Initialize the fridge upload... 
         **/
        obj.initFridgeUpload = function () {
                // sub out the fridge upload button...
                $('#fridge-button').click(function (e) {
                        e.preventDefault();
                        $('#fridge-upload').click();
                });
                $('#fridge-upload').change(function () {
                        // build a form data object to send to the server...
                        var data = new FormData();
                        data.append('fridge-upload', $('#fridge-upload')[0].files[0]);
                        obj.refreshFromPost(data);
                        // reset the surrounding form...
                        $(':input', '#fridge-form').val('');
                });
        };

        /**        
         *  Initialize the recipe upload...
         **/
        obj.initRecipeUpload = function () {
                // sub out the recipe upload button...
                $('#recipe-button').click(function (e) {
                        e.preventDefault();
                        $('#recipe-upload').click();
                });
                $('#recipe-upload').change(function () {
                        // build a form data object to send to the server...
                        var data = new FormData();
                        data.append('recipe-upload', $('#recipe-upload')[0].files[0]);
                        obj.refreshFromPost(data);
                        // reset the surrounding form...
                        $(':input', '#recipe-form').val('');
                });
        };

        /**        
         *  refresh the post  
         **/
        obj.refreshFromPost = function (data) {
                $.ajax({
                        data: data,
                        cache: false,
                        contentType: false,
                        processData: false,
                        type: 'POST',
                        success: function (data) {
                                obj.displayFood(data);
                        },
                        failure: function (d) {
                                console.log('FAILURE');
                                console.log(d);
                                alert("Request to server failed…", "#f66");
                        },
                        error: function (ts) {
                                console.log('ERROR');
                                console.log(ts);
                                alert("Request to server failed…", "#f66");
                        }
                });
        };

        /**        
         *  Simply clears the recipes list on the page...
         **/
        obj.clearRecipes = function () {
                this.recipeDiv.text("");
        };

        /**        
         *  Add recipes to the relevant list positions...
         **/
        obj.addRecipes = function (recipeJSON) {
                var content = "";
                content += "<ul>";
                if (recipeJSON.length === 0) {
                        content += "Order Takeout";
                } else {
                        recipeJSON.forEach(function (item) {
                                content += "<li>";
                                content += "<h3>" + item.name + "</h3>";
                                content += "<ul>";
                                item.ingredients.forEach(function (ingredient) {
                                        content += "<li>" + ingredient + "</li>";
                                });
                                content += "</ul>";
                                content += "</li>";
                        });
                }
                content += "</ul>";
                this.recipeDiv.append(content);
        };

        /**        
         *  Simply clears the fridge list on the page... 
         **/
        obj.clearFridge = function () {
                this.fridgeDiv.text("");
        };

        /**        
         *  Adds the fridge elements into the relevant list positions...
         **/
        obj.addFridgeItems = function (fridgeJSON) {
                var content = "";
                content += "<ul>";
                if (fridgeJSON.length === 0) {
                        content += "No Food";
                } else {
                        fridgeJSON.forEach(function (item) {
                                content += "<li>";
                                content += item.ingredient;
                                content += "<span class='expiry'>" + item.expiry + "</span>";
                                content += "</li>";
                        });
                }
                content += "</ul>";
                this.fridgeDiv.append(content);
        };

        /**        
         *  Talks to the server to grab the JSON packets for display...
         **/
        obj.loadData = function () {
                $.ajax({
                        type : 'GET',
                        url: "data.json",
                        contentType : 'application/json',
                        timeout: 2000,
                        success: function (data) {
                                obj.displayFood(data);
                        },
                        failure: function () {
                                alert("Request to server failed…", "#f66");
                        },
                        error: function () {
                                alert("Request to server failed…", "#f66");
                        }
                });
        };

        /**        
         *  Redraws the display...
         **/
        obj.displayFood = function (data) {
                // load up the recipes...
                this.clearRecipes();
                this.addRecipes(data.recipes);
                // load up the fridge...
                this.clearFridge();
                this.addFridgeItems(data.fridge);
        };

        return obj;

}());

window.onload = function () {
        /**
         *  Grab the recipe information from the server on every page
         *  load...
         **/
        RecipeObj.init();
        RecipeObj.loadData();
};

var testFixtures = {
        recipes: [
                {
                        "name": "Salad Sandwich",
                        "ingredients": [
                                "10g of butter",
                                "200g of mixed salad",
                                "10 pieces of bread"]
                },
                {
                        "name": "Grilled Cheese On Toast",
                        "ingredients": [
                                "10g of butter",
                                "10 slices of cheese",
                                "10 pieces of bread"]
                }
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
                }
        ]
};