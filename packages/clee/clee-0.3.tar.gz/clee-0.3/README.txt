Quick Command-Line Interfaces
clee
0.3

=== Intro ===
Why? I like the command-line, I use it all day, I want it to be cool.
Unfortunately it is generally a bit of a pain to create all the objects
to do it using optparse, so this library attempts to take some of the hassle
out of it by providing a few pre-made parsers, a couple easily extensible
parsers using `sprinkles` (if you have it installed), and a bunch of pre-made
options to be easily included in your own parser objects.

Additionally, the module provides a module-level interface to some of the
standard calls making it even quicker to parse a command-line.

=== Usage ===
How? The quickest way to use this library is to use the standard set of options
that let a user specify a log file (log), a config file (config), 
verbose output (verbosity > 0) or quiet output (verbosity < 1):

import clee
options, args = clee.parse_args()

Pre-made options are provided for some common tasks, ie: opt_username and
opt_password.

To quickly extend the standard clee parser, one can call clee.add_option()
before calloiong clee.parse_args():

clee.add_option(clee.opt_username)

Or extend the class itself:

class SuperClee(clee.Clee):
    standard_option_list = [clee.opt_config, 
                            clee.opt_log, 
                            clee.opt_username]

Another method by which to extend is to set opt_* properties on the class:

class SuperClee2(clee.Clee):
    opt_enable = clee.opt_enable


Another feature is the ContextClee, which is a parser containing other
parsers wherein the parser to use is determined by the first word (aka the
context). An example of using this for a script in which writing requires
a username and password but reading does not:

class ReadParser(clee.Clee):
    pass

class WriteParser(clee.Clee):
    standard_option_list.append(clee.opt_username)
    standard_option_list.append(clee.opt_password)

c_cli = clee.ContextClee(contexts={"read":ReadParser,"write":WriteParser})   


If you want to get even fancier and have installed some of the other libraries
I've written (namely `sprinkles`) you can make use of the
plugin-capable SprinkledClee:

-- yourscript.py --
import clee
cli = SprinkledClee(package="/Users/andy/.flickr")
cli.parse_args()

-- /Users/andy/.flickr/addToSet.py --
from clee import CleeOptionSprinkleMixin, ICleeSprinkle, implements
class addToSet(CleeOptionSprinkleMixin):
    implements(ICleeSprinkle)
    option = clee.make_option(
                "--add_to_set",
                action="append",
                dest="add_to_sets", metavar="SET",
                help="add photo to an existing set")

=== Contents ===
* class Clee    --  The 'minimum' CLI, options to direct log output,
                    specify config and affect verbosity.
* class ContextClee
                --  A multi-CLI, quickly make parsers that use different
                    rulesets for different contexts
* class SprinkledClee
                --  When given the path to a directory, this CLI will attempt
                    to load plugins from files in that directory
* class SprinkledContextClee
                --  Same concept as the SprinkledClee, but using a ContextClee
* class ICleeSprinkle
                --  Base interface for clee sprinkles
* class ContextCleeSprinkleMixin
                --  A mixin to help with some of the basics of a context clee
                    sprinkle
* class CleeOptionSprinkleMixin
                --  Mixin for clee option sprinkles, a specific version
                    of the clee sprinkle class for adding options to a Clee
                    instance
* opt_*         --  Pre-made options to be easily included in your scripts

=== Todo ===
What next? 

* Default parsers for ContextClee
* Some completely different style of command-line parsing, maybe something
    regex based
* Crazy custom parsing rulesets

=== Conclusion ===
Generally, these libraries are provided as an idea about what you may be
interested in doing for yourself, my own way of massaging a few more syntax
niceties into the language I enjoy so much. If you find them useful, I'd love
to hear from you, especially if you have suggestions on additions and
improvements.

=== Author ===
Andy Smith

love.
