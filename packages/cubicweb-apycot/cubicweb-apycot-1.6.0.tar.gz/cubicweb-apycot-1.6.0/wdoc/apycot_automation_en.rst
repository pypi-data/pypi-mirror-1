Automatization
--------------

By integrating to a local repository (vcsfile)
``````````````````````````````````````````````
This is the recommanded way to get deep CI/VCS integration :

* import vcs repository data for your projects using the `vcsfile cube`_

* link a repository to relevant test configuration through the local repository
  (local_repository) relation

* set auto-test-mode to 'quick' or 'full' in instance's all-in-one.conf file.


By using apycotclient in cron jobs
``````````````````````````````````
XXX WRITE ME
see apycotclient --help until then.

.. winclude:: apycot_links
