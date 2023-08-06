=Python TweetPhoto=

_A python wrapper around the TweetPhoto API_

Author: `Marcel Caraciolo <caraciol@gmail.com>`

==Introduction==

This library provides a pure python interface for the TweetPhoto API.

TweetPhoto (http://tweetphoto.com) provides a service that allows people to
upload photos to the web. The TweetPhoto exposes a web services API
and this library is intended to make the process easier for python
programmers to use.

  
==Building==

*From source:*

Install the dependencies:

  http://cheeseshop.python.org/pypi/simplejson

Download the latest python-twitter library from:

  http://code.google.com/p/python-tweetphoto/


Untar the source distribution and run:

{{{
  $ python setup.py build
  $ python setup.py install
}}}


==Getting the code==

View the trunk at:

  http://python-tweetphoto.googlecode.com/svn/trunk/

Check out the latest development version anonymously with:

{{{
  $ svn checkout http://python-tweetphoto.googlecode.com/svn/trunk/ python-tweetphoto
}}}

==Documentation==

View the last release API documentation at:

It will be soon released.


==Using==

The library provides a python wrapper around the TweetPhoto API.

*API:*

The API is exposed via the pyTweetPhoto.TweetPhotoApi class.


To create an instance of the pyTweetPhoto.TweetPhotoApi with login credentials (many API
calls required the client to be authenticated):

  >>> api = pyTweetPhoto.TweetPhotoApi(username='username', password='password', apiKey='apiKey') 
'

To fetch the photo Details:

{{{
  >>> details = api.GetPhotoDetails(photo_id=929293)
  >>> print details
}}}

To Favorite a Photo (requires authentication): 

{{{
  >>> status = api.FavoritePhoto(photo_id=929292,post_to_twitter=True)
  >>> print status
}}}

To Add a comment to a Photo (requires authentication):

{{{
  >>> status = api.AddComment(photo_id=939393, comment_id=382828)
  >>> print status
}}}

To upload a photo to tweetPhoto (requires authentication):

{{{ 
	>>> status = api.Upload(api.Upload(fileName='FILE_PATH',
	               message='This is a new photo! max: 200 characters', tags='tag1,tag2,tag3',
	               geoLocation='lat,long',post_to_twitter=True))

}}}

There are many more API methods, to read the full API documentation:

{{{
  $ pydoc pyTweetPhoto.TweetPhotoApi
}}}

==Todo==

New patches or bug comments are welcome as also model classes
to hold the objetcs provided from the api method responses.

Develop a coverage test for the API.

Not all methods are covered in this release, so new methods could be added
too in accordance to the original source code.

==More Information==

Please visit http://python-tweetphoto.googlecode.com/  for more information.

==Contributors==

Special thanks to the TweetPhoto Team for all support gave to me during
the project.

==License==

{{{
 Copyright (c) 2010/2009, Marcel Caraciolo
 caraciol@gmail.com
 twitter: marcelcaraciolo

 Redistribution and use in source and binary forms, with or without
 modification, are permitted provided that the following conditions are met:
     * Redistributions of source code must retain the above copyright
       notice, this list of conditions and the following disclaimer.
     * Redistributions in binary form must reproduce the above copyright
       notice, this list of conditions and the following disclaimer in the
       documentation and/or other materials provided with the distribution.
     * Neither the name of the author nor the names of its contributors may
       be used to endorse or promote products derived from this software
       without specific prior written permission.

 THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS``AS IS'' AND ANY
 EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 DISCLAIMED. IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE FOR ANY#
 DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
}}}