#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'caraciol@gmail.com'

"""
	Post a photo to TweetPhoto
"""

import os, sys
from pyTweetPhoto import *


if __name__ == '__main__':
	
	"""
	Usage: tweetphotoUp.py -u USER_NAME -p PASSWORD -k API_KEY [options] IMG_PATH

	Options:
	  -h, --help            show this help message and exit
	  -u USER, --user=USER  TweetPhoto user name
	  -p PASSWD, --passwd=PASSWD
	                        TweetPhoto password
	  -k KEY, --key=KEY     TweetPhoto API key
	  -b, --both            post to twitter together
	  -m MSG, --msg=MSG     message, if multiple words put inside quotes
	  -t TAGS, --tags=TAGS  tags must be separated by comma like: cats,animals
	  -l GEO, --geo=GEO     GeoLocation (Must be separated by commas like:
	                        -14.00,-15.00)
	
	Docummentation:
	
	If the --user or --passwd command line arguments are present they will be used to authenticate to TweetPhoto.
	"""
	
	from optparse import OptionParser
	optPsr = OptionParser('usage: %prog -u USER_NAME -p PASSWORD -k API_KEY [options] IMG_PATH')
	optPsr.add_option('-u', '--user', type='string', help='TweetPhoto user name')
	optPsr.add_option('-p', '--passwd', type='string', help='TweetPhoto password')
	optPsr.add_option('-k', '--key' , type='string', help= 'TweetPhoto API key')
	optPsr.add_option('-b', '--both' , action='store_true', default=False, 
					help = 'post to twitter together')
	optPsr.add_option('-m', '--msg', type='string' , help = 'message, if multiple words put inside quotes')
	optPsr.add_option('-t', '--tags', type='string' , help = 'tags must be separated by comma like: cats,animals')
	optPsr.add_option('-l', '--geo' , type='string', help = 'GeoLocation (Must be separated by commas like: -14.00,-15.00)')

	(opts,args) = optPsr.parse_args()

	if not opts.user:
		optPsr.error('no USER_NAME')

	if not opts.passwd:
		optPsr.error('no PASSWORD')

	if not opts.key:
		optPsr.error('no API_KEY')

	if not args:
		optPsr.error('no IMG_PATH to upload')

	if opts.geo:
		geoPosition = opts.geo.split(',')
		if len(geoPosition) == 2:
			try:
				geoPosition = (float(geoPosition[0]),float(geoPosition[1]))
			except:
				optPsr.error('Invalid format of GeoLocation. It must be: lat,long')
		else:
			optPsr.error('Invalid format of GeoLocation. It must be: lat,long')


	if len(args) > 1:
		optPsr.error('multiple img upload not allowed')


	api = TweetPhotoApi(opts.user, opts.passwd, opts.key)

	posted_url = api.Upload(args[0], message=opts.msg, tags=opts.tags, 
					geoLocation = opts.geo, post_to_twitter = opts.both)

	print posted_url['MediaUrl'] #The URL Of tweetphoto!
