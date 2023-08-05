Termie's Standard Library:  Logging
scribe
0.2

=== Intro ===
Why? This is somewhere between the reason for `clee` and the reason for 
`courriel`. This exists because I always found it annoying to have to create
a logger and set formats all the time before I use a logger. So, I made a
couple default loggers that are easy to get to. The interface is generally
compatible with `logging` but I hope to add bells and whistles as things
proceed.

=== Usage ===
How?

Log a random message at the warning level to stdout:
import scribe
scribe.warning("Some warning message, j00 know")

or

Log that stuff to a file with a name based on the name of the current script
with a more 'loggingish' format:

logger = scribe.FormalScribe()

=== Contents ===
* class Scribe  --  Base class wrapping `logging`

* class CasualScribe
                --  The default scribe, uses scribe.casual_format and outputs
                    to sys.stdout

* class FormalScribe
                --  A scribe more like a standard logger, outputting to a file
                    in scribe.formal_format

* def setScribe,
  def setLevel  --  Functions to affect the default scribe (the one used by
                    the following functions)

* def log,
  def critical,
  def error,
  def warning,
  def info,
  def debug     --  Functions calling their namesakes on whichever is the
                    default scribe

=== Todo ===
What next? 

* BufferedScribe
* MysqlScribe
* SQLiteScribe
* Some magic to supply a bunch of env variables to the logging functions to
    be replaced in the %(somevar)s fields

=== Conclusion ===
Generally, these libraries are provided as an idea about what you may be
interested in doing for yourself, my own way of massaging a few more syntax
niceties into the language I enjoy so much. If you find them useful, I'd love
to hear from you, especially if you have suggestions on additions and
improvements.

=== Author ===
Andy Smith <tsl@an9.org>

love.

