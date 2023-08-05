Termie's Standard Library:  Extensibility
sprinkles
0.3

=== Intro ===
Why? Every time I want to release a project I end up thinking, "Gee, wouldn't
it be cool if I had some kind of plugin system so that people could easily
extend the functionality of whatever script I was writing. Well, honestly
more so that I can extend the functionality of the script.

This library isn't particularly security-minded, it basically scans a
directory you specify and loads up the python files in it to look for 
classes that can be imported.

=== Usage ===
How? This is the most complex of all the libraries I've written for the tsl,
but let's see if I can explain it. What is *does* is fairly simple, what you
need to do to write a sprinkle is a little more complex.

What it does is search a directory, file, module, or module directory for 
importable python files, attempts to import them for classes that exend 
sprinkles.Sprinkle (that way random libraries aren't imported) and then if a 
specific filterer has been provided it will make sure the item passes that 
filter as well (this way you can make sure only certain types of items are 
imported at certain times). If that all goes off without a hitch, it returns 
a list of classes.

To get a list of sprinkles in a directory:

    foo_sprinkles = sprinkles.from_path(somedir)

... from a file
    
    bar_sprinkles = sprinkles.from_file(somepath, somefilename)

... from a module

    baz_sprinkles = sprinkles.from_mod("some.mod")

... or if you happen to have a module already loaded
    
    baz_sprinkles = sprinkles.from_mod(some.mod)

... from a module directory

    quux_sprinkles = sprinkles.from_mod_dir(some)


Now, the more complex part is how to use a sprinkle in some sort of plugin
system. It's not really that complex, in fact it can be superbly simple, but 
the actual architecture of a plugin system is something people seem to have 
issues with.

A Simple Sprinkle:

class FooSprinkle(sprinkles.Sprinkle):
    foo = "bar"

That's all you need for a sprinkle, but this sprinkle probably won't be all
that useful for you.

A slightly more useful sprinkle:

#### bar.py #####
class BarSprinkle(sprinkles.Sprinkle):
    def __init__(self):
        self.somevar = "foo"

    def __call__(self, other):
        other.somevar = self.somevar
#### yourscript.py #####
mainvar = SomeObject()
foo_sprinkles = sprinkles.from_file("my_sprinkle_dir","bar.py")
for spr in foo_sprinkles:
    o = spr()   # Initialize the sprinkle
    o(mainvar)  # Call the sprinkle on an object

Basically, for every sprinkle you initialize the sprinkle and then call it on
whatever item is is supposed to extend, giving it free reign to modify that
object at will. Obviously you'll need to know what objects you are modifying
and should make use of good filters to prevent loading random sprinkles
for a specific task.

Of course these could be used differently, you could simply be importing a
list of objects, items you want to include in some other list, or whatever. 
All in all it is pretty free form, but the most common use case I have run
into is the one described above.

=== Contents ===
* class Sprinkle
                --  The base class for a plugin, doesn't do much except act
                    as a way to filter out non-plugins

* def from_path -- Search a directory and call from_file on all the items
                    in it. ** from_dir is deprecated **                    

* def from_file --  Attempt to load sprinkles from a file

* def from_mod  --  Attempt to load sprinkles from a module

* def from_mod_dir
                --  Attempt to load sprinkles from a module directory

* def issprinkle
                --  Checks if something is a sprinkle by calling issubclass

=== Todo ===
What next? 

* Some other formats to describe plugins
* Some security stuff, I guess. Probably won't extend much beyond checking
    permissions on the file and making sure it isn't world-writable though.

=== Conclusion ===
Generally, these libraries are provided as an idea about what you may be
interested in doing for yourself, my own way of massaging a few more syntax
niceties into the language I enjoy so much. If you find them useful, I'd love
to hear from you, especially if you have suggestions on additions and
improvements.

=== Author ===
Andy Smith <tsl@an9.org>

love.

