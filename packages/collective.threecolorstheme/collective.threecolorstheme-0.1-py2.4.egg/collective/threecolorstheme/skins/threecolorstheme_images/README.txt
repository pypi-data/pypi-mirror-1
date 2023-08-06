We use classic skins layers here for images because we want
to be able to overload easily images, without rewriting css :

An example :
if http://mysite.org/my_phantasy_skin/myimage.gif exists,
it will overload http://mysite.org/myimage.gif
Otherwise it will returns http://mysite.org/myimage.gif

The Zope2 acquisition is magic and we still love it.