Introduction
============

The scope of this library is to help developers to simply display text inside a `pygame.Rect`__ instance.
After obtainer a KTextSurfaceWriter instance, you can use its ''draw'' method to display
the text over a `pygame.Surface`__.

__ http://www.pygame.org/docs/ref/rect.html
__ http://www.pygame.org/docs/ref/surface.html

Visit the `home page of the project`__ for more.

__ http://keul.it/develop/python/ktextsurfacewriter/

Examples
========

Here a fully example of use of this library. Even if I use the Python doctest format, this isn't a
politically correct test because I wait for user input and no real tests are done on the results.

Maybe someday I'll fix this!

However the code in this page is a working example. If you know nothing about doctests, only know that you can
run this code simple launching python interpreter and typing:

   import ktextsurfacewriter

   ktextsurfacewriter.runTests()

...or, if you have the source of the library with the "tests.py" file inside, just type:

   python tests.py

Init all the pygame stuff
-------------------------

Lets begin loading the KTextSurfaceWrite class

   >>> from ktextsurfacewriter import KTextSurfaceWriter

Now init the minimum pygame environment we need.

   >>> import pygame
   >>> from pygame.locals import *
   >>> import pygame.font
   >>> pygame.font.init()
   >>> screen = pygame.display.set_mode((640,480), 0, 32)

To make things more complicated, I'll not draw directly on the screen but I get a Surface where I can draw.

   >>> surface = pygame.Surface( (400,400), flags=SRCALPHA, depth=32 )
   >>> surface.fill( (255,255,255,255) )
   <rect(0, 0, 400, 400)>

Now we can blit the surface on the screen. We will repeat this procedure several times so its better create out first
dummy function (those functions aren't useful outside this test environment):

   >>> def blitSurface():
   ...     screen.blit(surface, (50,50) )
   ...     pygame.display.update()

So we can call it for the first time.

   >>> blitSurface()

This is a graphical test, so we need to delay the drawing and make possible that user can look at results and then go over.
We wait for user input before going on. To do this we create a second  silly function that we'll call often later.

   >>> def waitForUserAction():
   ...     while True:
   ...
   ...         for event in pygame.event.get():
   ...             if event.type == QUIT:
   ...                 import sys
   ...                 sys.exit(0)
   ...             if event.type==KEYDOWN:
   ...                 return

Ok, lets call it for the first time.

   >>> waitForUserAction()

Simple text drawing
-------------------

We are ready to create our instance of the class. The __init__ method want a pygame.Rect.
This Rect will be our bound, inside which the text will be keep.

   >>> text_rect = pygame.Rect( (10,10),(350,350) )
   >>> text_rect
   <rect(10, 10, 350, 350)>
   
This mean that the text will be displayed on a surface starting from x,y coordinates (10,10)
from the top left corner.
The text will also not be larger than 350 pixels in height and width.

Now we will load the text inside the KTextSurfaceWriter, but before this we (obviously) need the instance.

   >>> ktext = KTextSurfaceWriter(text_rect)

Now the text.

   >>> import example_texts
   >>> ktext.text = example_texts.EXAMPLE_TEXT_1

Now some color for a better display experience

   >>> ktext.color = (0,0,0,255)
   >>> ktext.fillcolor = (155,155,155,255)

We changed the fillcolor to grey because this way is simpler to see that we drawn a white surface onto a
black screen, and on this surface we blit the text inside a rectangle shorter that the surface itself.

Ok, stop talking, lets display it!

   >>> ktext.draw(surface)
   >>> blitSurface()
   >>> waitForUserAction()

Simple (but longer) text drawing
--------------------------------

The text above is very short so we didn't tested all the KTextSurfaceWriter features right now.
Lets try with a longer ones...

   >>> ktext.text = example_texts.EXAMPLE_TEXT_2
   
Now we can immediatly test this new text.

   >>> ktext.draw(surface)
   >>> blitSurface()
   >>> waitForUserAction()

What is changed? Even if the EXAMPLE_TEXT_2 string is not splitted on several lines, the displayed text never exit from
the constrain pygame.Rect instance we used!

And what is the text will be already splitted on several lines?

   >>> ktext.text = example_texts.EXAMPLE_TEXT_3
   >>> ktext.draw(surface)
   >>> blitSurface()
   >>> waitForUserAction()

Obviously the carriage return in the text are kept.
We can also think about do a little indentation, to make different render for new lines that are wanted (because are
inserted into the text) and other that are generated automatically for a too long text.

   >>> ktext.justify_chars = 3

If we draw again now, we get no difference.
For performance needs the KTextSurfaceWriter.draw method don't evaluate every time the text and the font
graphical stuff, but memoize the result.
When you change the text you also automatically invalidate this cache, but if you didn't change it, you can
always do it manually.

   >>> ktext.invalidate()

Ok, now you'll see the difference.

   >>> ktext.draw(surface)
   >>> blitSurface()
   >>> waitForUserAction()
   
Text too loong for a single line
--------------------------------

We want to draw text always inside a rectangle, but this isn't always possible, even if we use a pygame.Rect
big as the entire surface, is always possible that the text we pass is too long.

What happen in this case?

   >>> ktext.text = example_texts.EXAMPLE_TEXT_4
   >>> ktext.draw(surface)
   >>> blitSurface()
   >>> waitForUserAction()

The default behaviour is to cut the word at the maximum lenght possible. This because without saying anything the
KTextSurfaceWriter instance use a criteria called "cut".
You can change this to another value

   >>> ktext.line_length_criteria = "split"

Then if we repeat the test we get a new behaviour.

   >>> ktext.invalidate()
   >>> ktext.draw(surface)
   >>> blitSurface()
   >>> waitForUserAction()

The text now is splitted on many lines and no one characters gets lost. Of course, the too long single word is splitted
by an ugly barbarian at some random character (depending on the rect size, font, and so on).

Another possible value for the 'line_length_criteria' attribute is "overflow" (dangerous! See below).

   >>> ktext.line_length_criteria = "overflow"
   >>> ktext.invalidate()
   >>> ktext.draw(surface)
   >>> blitSurface()
   >>> waitForUserAction()

As you can see, the too long word now is alone on a text line (like before) but the word itself isn't modified:
simply the text is draw outside the Rect defined (and also the Surface...).

Text too long for the Rect height
---------------------------------

To test the vertical limit, I change the font used by the example, so I can use less text.

   >>> ktext.font = pygame.font.Font(None, 42)
   >>> ktext.invalidate()
   >>> ktext.draw(surface)
   >>> blitSurface()
   >>> waitForUserAction()

First of all note that the previous test has not cleaned correctly the window. This because using the "overflow"
criteria for the 'line_length_criteria' attribute can lead to text drawn outside the area that the
KTextSurfaceWriter normally refresh.
You are on your own!

Lets go back to the new example.
As you can also note there's not limit to the text height rigth now. So if you display too much text in the Rect, this simply
will pass over the bottom constraint.

This is the default behaviour that you can change modifying the 'page_length_criteria' attribute. The default value is
"overflow", as you see above (again: can be dangerous).
We can change this to "cut" and we will se a different result.

   >>> ktext.page_length_criteria = "cut"
   >>> ktext.invalidate()
   >>> ktext.draw(surface)
   >>> blitSurface()
   >>> waitForUserAction()

You haven't seen difference? This is not true... The problem is always related to our bad test above: we blit outside the
controlled area of the KTextSurfaceWriter instance! And the invalidate method seems doing nothing because it can't clean
our dirty work.

Lets clean the surface a little, before going on!

   >>> surface.fill( (255,255,255,255) )
   <rect(0, 0, 400, 400)>

Now we can try again.

   >>> ktext.invalidate()
   >>> ktext.draw(surface)
   >>> blitSurface()
   >>> waitForUserAction()

Conlusion
---------

As you can see, the library does a single thing, but try to do it well!

Comments, issues found and feedbacks are welcome, `contact me`__!

__ mailto:lucafbb@gmail.com

   >>> pygame.quit()

TODO
====

 * A way to scroll a too (vertically) long text.
 * Split PyGame logic fron pure text algorithms.

Subversion and other
====================

The SVN repository is hosted at the `Keul's Python Libraries`__

__ https://sourceforge.net/projects/kpython-utils/

