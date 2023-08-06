Yamlog uses a rotating file that rollovers at 128 KB, it writes messages in YAML
format since it's more easy to parse --using the international format for date
and time--, and it also logs the higher-level messages to the standard error
into single lines.

To setup the logging::

  import yamlog
  yamlog.setup(filename)

where `filename` is the file where is going to be logged; */tmp/python.log* by
default.

And to tear down it::

  yamlog.teardown()

Then, in each module where is going to be used, there is to add::

  import yamlog
  _log = yamlog.logger(__name__)

so it passes the module name where it's being run. Now, can be used the logging
methods --*debug()*, *info()*, *warning()*, *error()*, *critical()*-- to
indicate the importance of a logged message.
