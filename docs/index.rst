======================
Hydra Slayer |version|
======================

.. raw:: html

    <a class="github-button" href="https://github.com/catalyst-team/hydra-slayer" data-icon="octicon-star" data-size="large" data-show-count="true" aria-label="Star leverxgroup/esrgan on GitHub">Star</a> |
    <a class="github-button" href="https://github.com/catalyst-team/hydra-slayer/fork" data-icon="octicon-repo-forked" data-size="large" data-show-count="true" aria-label="Fork leverxgroup/esrgan on GitHub">Fork</a> |
    <a class="github-button" href="https://github.com/catalyst-team/hydra-slayer/issues" data-icon="octicon-issue-opened" data-size="large" data-show-count="true" aria-label="Issue leverxgroup/esrgan on GitHub">Issue</a>

|Build-Status| |PyPI-Version| |Py-Versions| |License| |Slack|

----

**Hydra Slayer** is a 4th level spell in the School of Fire Magic.
Depending of the level of expertise in fire magic, slayer spell increases attack of target troop by 8.

.. table::
   :widths: auto

   +---------------------------------+------------------------+
   | .. centered:: Hydra Slayer                               |
   +=================================+========================+
   | .. image:: ./_static/slayer.png | :School: Fire Magic 🔥 |
   +   :width: 192                   +------------------------+
   |                                 | :Level: 4th 📜         |
   +                                 +------------------------+
   |                                 | :Cost: 16/12 🔮        |
   +---------------------------------+------------------------+
   | **Basic effect**                                         |
   +---------------------------------+------------------------+
   | Target allied troop's attack rating is increased by      |
   | 8 against                                                |
   |                                                          |
   | behemoths 👹, dragons 🐉, hydras |hydra|, phoenixes 🦜.  |
   |                                                          |
   | .. |hydra| image:: https://hydra.cc/img/Hydra-head.svg   |
   |   :width: 14.4px                                         |
   +---------------------------------+------------------------+
   | **Advanced effect**                                      |
   +---------------------------------+------------------------+
   | Same as basic effect, except that attack bonus also      |
   |                                                          |
   | affects devils 👿 and angels 👼.                         |
   +---------------------------------+------------------------+
   | **Expert effect**                                        |
   +---------------------------------+------------------------+
   | Same as advanced effect, except attack bonus also        |
   |                                                          |
   | affects giants/titans.                                   |
   +---------------------------------+------------------------+

What is more, it also allows configuring of complex applications just by config and few lines of code.


Communication
=============

* GitHub Issues: Bug reports, feature requests, install issues, RFCs, thoughts, etc.

* Slack: The `Catalyst Slack <catalyst_slack_>`_ hosts a primary audience of moderate to experienced Hydra-Slayer
  (and Catalyst) users and developers for general chat, online discussions, collaboration, etc.

* Email: Feel free to use feedback@catalyst-team.com as an additional channel for feedback.


GitHub
======

The project's GitHub repository can be found `here <slayer_>`_.
Bugfixes and contributions are very much appreciated!


License
=======

``hydra-slayer`` is released under a Apache-2.0 license. See `LICENSE <license_>`_ for additional details about it.


Citation
========

Please use this bibtex if you want to cite this repository in your publications:

.. code-block:: text

   @misc{catalyst,
      author = {Sergey Kolesnikov and Yauheni Kachan},
      title = {Hydra-Slayer},
      year = {2021},
      publisher = {GitHub},
      journal = {GitHub repository},
      howpublished = {\url{https://github.com/catalyst-team/hydra-slayer}},
   }

.. toctree::
   :maxdepth: 3
   :caption: General

   pages/install
   pages/examples

.. toctree::
   :maxdepth: 2
   :caption: API

   pages/api/registry
   pages/api/factory
   pages/api/functional

Indices and tables
==================

:ref:`genindex`

.. _slayer: https://github.com/catalyst-team/hydra-slayer
.. _slayer_pypi: https://pypi.org/project/hydra-slayer/
.. _license: ../LICENSE
.. _catalyst_slack: https://join.slack.com/t/catalyst-team-core/shared_invite/zt-d9miirnn-z86oKDzFMKlMG4fgFdZafw
.. _catalyst_email: mailto:feedback@catalyst-team.com
.. |Build-Status| image:: https://github.com/catalyst-team/hydra-slayer/actions/workflows/build.yml/badge.svg
   :target: https://github.com/catalyst-team/hydra-slayer/actions/workflows/build.yml
.. |PyPI-Version| image:: https://img.shields.io/pypi/v/hydra-slayer
   :target: `slayer_pypi`_
.. |Py-Versions| image:: https://img.shields.io/pypi/pyversions/hydra-slayer
   :target: `slayer_pypi`_
.. |License| image:: https://img.shields.io/github/license/catalyst-team/hydra-slayer
   :target: `license`_
.. |Slack| image:: https://img.shields.io/badge/slack-join_chat-brightgreen.svg
   :target: `catalyst_slack`_
