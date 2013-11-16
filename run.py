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
import BaseHTTPServer
import SimpleHTTPServer
import SocketServer

class Handler(SimpleHTTPServer.SimpleHTTPRequestHandler):
	"""
		This is the basic web response handler. This object
		creates its own recipe builder, and will use the JSON
		conversion function to pretty up the food item format
		for the front page...
	"""
	def __init__(self, *arg, **kwargs):
		self.rb = fridge.RecipeBuilder()
		self.rb.build_all(args.fridge, args.recipes)
		self.DATA_FILENAME = 'data.json'
		SimpleHTTPServer.SimpleHTTPRequestHandler.__init__(self, *arg, **kwargs)

	def do_GET(self):
		if self.DATA_FILENAME in self.path:
			try:
				foodJSON = self.rb.to_json()
				mime_t, reply = "application/json", json.dumps(foodJSON)
			except Exception as e:
				print e
				self.response(500)
				print >> self.wfile, 'Function process_query failed:', e
				return
			self.response(200, mime_t)
			print reply
			self.wfile.write(reply)
		else:
			return SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

	def response(self, code, mime_t="default"):
		self.send_response(code)
		if mime_t == "default":
			mime_t = "text/html"
		self.send_header('Content-Type', mime_t)
		self.end_headers()

def start_server(host, port, threaded=True):
	"""
		This function will start the server. In this
		case it will server forever and block...

	"""	
	# first open the HTTP to handle JSON requests...
	s = SocketServer.ThreadingTCPServer((host, port), Handler)
	if not s:
		return (True, None)
	s.serve_forever()
	return (False, t)

def main():
	"""
		For the main function we have two options, we are either serving
		this as a web page, or we are simply executing from the cmd line.
		The host argument is used to determine which has been requested 
		from the user.
	"""
	if args.host:
		# This is the server option. Here the results can be viewed on the
		# host:port specified at the cmd line...
		print('Attempting to open socket at {}:{}'.format(args.host, args.port))
		(err,server_thread) = start_server(args.host, args.port)
		if err:
			print "Failed to initialize server."
			return
	else:
		# This is just the standard cmd line 
		rb = fridge.RecipeBuilder()
		# construct the initial object...
		rb.build_all(args.fridge, args.recipes)
		# grab today's recipe...
		recipe = rb.todays
		if recipe:
			print "Optimal recipe is:"
			print recipe.name
		else:
			print "Order Takeout"

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