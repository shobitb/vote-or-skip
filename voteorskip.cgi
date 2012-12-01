#!/usr/bin/python

import cgi
import cgitb
import commands
import os
import re
import random
import string

cgitb.enable()
form = cgi.FieldStorage()

""" Starting the Http Response """
print 'Content-Type: text/html'
print

""" This is used on multiple pages """
footer = """
<hr>
<ul>
	<li> See <a href="voteorskip.cgi?results=true&c=%s">all results</a> </li>
	<li> Back to <a href="voteorskip.cgi">categories</a> </li>
</ul>
"""

""" This handles the front page -- displays the categories """
def index():
	categories = os.listdir("/home/ssb402/.head2head/items/")
	output = """
		<html>
			<body>
				<form action="voteorskip.cgi" method="get">
					<input type="radio" name="category" value="%s"> %s </input><br />
					<input type="radio" name="category" value="%s"> %s </input><br />
					<input type="submit" value="Submit" />
				</form>	
			</body>
		</html>
	""" % (categories[0],categories[0],categories[1],categories[1])
	print output

""" This handles the page immediately after choosing a category """
def category(cat):
	fd = open("/home/ssb402/.head2head/items/%s" % cat)
	lines = fd.readlines()
	len_lines = len(lines)
	# generate random numbers for random items
	one = lines[random.randint(0, len_lines-1)].rstrip('\n')
	two = one
	# to make sure same items are not selected by keeping two != one
	while two == one:
		two = lines[random.randint(0, len_lines-1)].rstrip('\n')
	output = """
		<html>
			<body>
				<b>Category:</b> %s
				<form action="voteorskip.cgi" method="get">
					<input type="radio" name="item" value="%s"> %s </input><br />
					<input type="radio" name="item" value="%s"> %s </input><br />
					<input type="submit" value="Vote!" name="vote"/>
					<input type="submit" value="Skip" name="skip"/>
					<input type="hidden" name="first" value="%s"></input>
					<input type="hidden" name="second" value="%s"></input>
					<input type="hidden" name="cat" value="%s"></input>
				</form>	
			</body>
		</html>
	""" % (cat,one,one,two,two,one,two,cat)
	print output

""" This handles the submission of vote """
def vote(cat):
	winner = form.getvalue("item")
	if winner == form.getvalue("first"):
		loser = form.getvalue("second")
	else:
		loser = form.getvalue("first")
	commands.getoutput('echo "%s/%s" >> "/home/ssb402/.head2head/ssb402/%s"' % (winner,loser,cat) )
	output = """
		<html>
			<body>
				<em>You voted for \"%s\" over \"%s\"</em><br>
	""" % (winner,loser)
	output += "<br><b>Current Totals:</b><br><table border='1'>"
	# The sed script builds the rows and columns for the table
	output += commands.getoutput('HEAD2HEAD_DATA=ssb402 /home/ssb402/ost-shell-assg/head2head.sh results ssb402/"%s" 2> /dev/null | egrep "%s|%s" | cut -d"," -f1,2 | sed "s/^\\(.*\\)$/\<tr\>\<td\>\\1\<\/td\>\<\/tr\>/" | sed "s/,/\<\/td\>\<td\>/"' % (cat,winner,loser))
	output += "</table><hr></body></html>"
	print output
	category(cat)

""" This handles the all results link """
def result(cat):
	output = "<table border='1'>"
	# The sed script builds the rows and columns for the table
	output += commands.getoutput('HEAD2HEAD_DATA=ssb402 /home/ssb402/ost-shell-assg/head2head.sh results ssb402/"%s" 2> /dev/null | sed "s/^\\(.*\\)$/\<tr\>\<td\>\\1\<\/td\>\<\/tr\>/" | sed "s/,/\<\/td\>\<td\>/g"' % cat)
	output += "</table>"
	print output

""" Choosing what to display based on the get arguments """
if form.has_key("category"):
	cat = form.getvalue("category")
	category(cat)
elif form.has_key("skip"):
	cat = form.getvalue("cat")
	category(cat)
	print footer % cat
elif form.has_key("item"):
	if form.has_key("vote"):
		cat = form.getvalue("cat")
		vote(cat)
		print footer % cat
elif os.environ['QUERY_STRING'].find('results') == 0:
	cat = form.getvalue('c')
	result(cat)
else:
	index()