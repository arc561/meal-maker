#!/usr/bin/env python

"""
	RecipeBuilder
	====================
	RecipeBuilder script. This uses the Fridge module to
	construct and build a set of recipes and the current
	available food. A recipe is selected based on the food
	closest to the expiry date. If no food meets the 
	criteria, nothing is returned...

	The user has two options for the display. The application will
	launch a simple web server to display the results in a web page.
	Alternatively, the user can simply run the script from the cmd
	line.
"""

import fridge
import argparse
import json
import cgi
import BaseHTTPServer
import SimpleHTTPServer
import SocketServer

"""
	Global object for recipe builder. This allows the handler to 
	access the RecipeBuilder without multiple initializations...
"""
rb = fridge.RecipeBuilder()

class Handler(SimpleHTTPServer.SimpleHTTPRequestHandler):
	"""
		This is the basic web response handler. This object
		creates its own recipe builder, and will use the JSON
		conversion function to pretty up the food item format
		for the front page...
	"""
	def __init__(self, *arg, **kwargs):
		# constants...
		self.DATA_FILENAME = 'data.json'
		self.FRIDGE_FILE = 'data/fridge.csv'
		self.RECIPE_FILE = 'data/recipe.json'
		SimpleHTTPServer.SimpleHTTPRequestHandler.__init__(self, *arg, **kwargs)

	def do_GET(self):
		"""
			Simple Get response handler. Here we build up a new food list when
			the web ajax request asks for a new recipe/fridge list...
		"""
		if self.DATA_FILENAME in self.path:
			self.food_response()
		else:
			return SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

	def do_POST(self):
		"""
			The post handler will store the file in FRIDGE_FILE and RECIPE_FILE,
			and then recalculate the meal. The data will come in as a formData request
			and will be passed back as the standard json response...
		"""
		try:
			# first parse the headers to look for the form...
			ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
			print ctype
			if ctype == 'multipart/form-data':
				query=cgi.parse_multipart(self.rfile, pdict)
			print query
			# look for the data type and attempt to load the file...
			if query.has_key('fridge-upload'):
				# load the fridge data...
				upfilecontent = query.get('fridge-upload')
				self.prepare_content(self.FRIDGE_FILE, upfilecontent[0], rb.build_fridge)
			elif query.has_key('recipe-upload'):
				# load the recipe file...
				upfilecontent = query.get('recipe-upload')
				self.prepare_content(self.RECIPE_FILE, upfilecontent[0], rb.build_recipes)
		except Exception as e:
			print e
			self.response(500)
			print >> self.wfile, 'Post request failed:', e
			return

	def prepare_content(self, filename, filedata, fn):
		"""
			This function loads the file from the web front end and
			saves it. Response is then constructed
		"""			
		try:
			f = open(filename, 'wb')
			f.write(filedata)
			f.close()
		except:
			raise Exception('Failed to open storage file.')
		try:
			fn(filename)
			rb.todays_recipe()
		except Exception as e:
			print e
			raise Exception('Failed to rebuild recipe')
		self.food_response()

	def food_response(self, code=200):
		"""
			Here we build the http response for the server...
		"""
		try:
			foodJSON = rb.to_json()
			mime_t, reply = "application/json", json.dumps(foodJSON)
		except Exception as e:
			print e
			self.response(500)
			print >> self.wfile, 'Get request failed:', e
			return
		self.response(code, mime_t)
		print reply
		self.wfile.write(reply)

	def response(self, code, mime_t="default"):
		"""
			writes the header...
		"""
		self.send_response(code)
		if mime_t == "default":
			mime_t = "text/html"
		self.send_header('Content-Type', mime_t)
		self.end_headers()

def main():
	"""
		For the main function we have two options, we are either serving
		this as a web page, or we are simply executing from the cmd line.
		The host argument is used to determine which has been requested 
		from the user.
	"""
	# construct the initial object...
	rb.build_all(args.fridge, args.recipes)
	# now we split based on the host or simple command line app...
	if args.host:
		# This is the server option. Here the results can be viewed on the
		# host:port specified at the cmd line...
		print('Attempting to open socket at {}:{}'.format(args.host, args.port))
		# first open the HTTP to handle JSON requests and serve forever...
		s = SocketServer.ThreadingTCPServer((args.host, args.port), Handler)
		if not s:
			print "Failed to initialize server."
			return
		else:
			s.serve_forever()
	else:
		# grab today's recipe...
		rb.print_debug_info()

if __name__ == "__main__":
	"""
		The fridge csv file and the recipes JSON file should be specified on 
		the cmd line, otherwise nothing will be available...
	"""
	parser = argparse.ArgumentParser()
	parser.add_argument("--host", nargs='?', help="server location")
	parser.add_argument("--port", nargs='?', help="server port", default=8000)
	parser.add_argument("-f", "--fridge", nargs='?', help="CSV file of fridge items")
	parser.add_argument("-r", "--recipes", nargs='?', help="JSON file of recipes")
	args = parser.parse_args()
	main()