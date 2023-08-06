
APyCoT is designed to be a higly extensible test automatisation tool. It will
fetch packages from version controlled repositories (like SVN or Hg), apply some
test on them, store the result and generate various reports from the collected
data. You just have to configure your test your tests to be informed in realtime
of broken feature or get fresh report about the health of all your projects for
your breakfast (or whatever else ;o)




.. image:: doc/images/apycot_processes.png

Cubicweb instances contains environment and test configurations, as well as test
execution information that may be used to build useful reports.

Once configured, you can explicitly queue a task (eg run tests for a
configuration) through a test configuration page. To get actual CI you'll have to
`automatize this`_.

When a task is queued through `apycotclient` or an instance, and the apycot
bot is starting it, it:

* retreives the configuration from the instance hosting it

* launch `apycotclient` to execute the task (setup environmenent, run tests),
  while parsing its output to report execution status and logs to the same
  instance

.. winclude:: apycot_links
