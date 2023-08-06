Usage
=====
  >>> from google.directions import GoogleDirections
  >>> gd = GoogleDirections('your-google-directions-key')
  >>> res = gd.query('berlin','paris')
  >>> res.distance
  1055351

You also have access to the raw parser data:

  >>> res.result["Directions"]["Duration"]
  {u'seconds': 34329, u'html': u'9 hours 32 mins'}

Have fun!


Contribution
============
If you extend the gdapi, I'd love to get your extensions. Just mail
me the code and I'll make a release. See below for the mail address.

