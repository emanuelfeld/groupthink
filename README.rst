=============
groupthink
=============

.. image:: https://travis-ci.org/emanuelfeld/groupthink.svg?branch=master
    :target: https://travis-ci.org/emanuelfeld/groupthink

.. image:: https://img.shields.io/pypi/v/groupthink.svg
    :target: https://pypi.python.org/pypi/groupthink

The groupthink package helps you install, update, and manage GitHub organization-specific command line scripts. Let's say your organization is called :code:`foo`.

Running :code:`groupthink install foo` looks for a repository at :code:`https://github.com/foo/foo-cli`. If it finds one, it installs to the :code:`foo-cli` directory within :code:`~/.groupthink`. Like this:

::

    .groupthink
    └── foo-cli
        ├── CONTRIBUTING.md
        ├── LICENSE.md
        ├── README.md
        └── bin
            ├── help
            ├── init
            ├── scan
            ├── setup
            └── validate

It also install as :code:`foo` script to :code:`/usr/local/bin`, which allows you to invoke any of the scripts found within the :code:`foo-cli/bin` directory. So :code:`foo init` would run the :code:`init` script within :code:`foo-cli/bin`, :code:`foo help` would run the :code:`help` script in the same directory, and so on.

You can check for updates made to the remote :code:`foo-cli` repository with :code:`groupthink update foo`. :code:`groupthink upgrade foo` would install all updates. And :code:`groupthink uninstall foo` removes both the :code:`foo` script in :code:`/usr/local/bin` and the :code:`foo-cli` directory in :code:`~/.groupthink`.

Finally, you can list all the organization commands you have installed to :code:`~/.groupthink` with :code:`groupthink list`.

To sum up the options:

* :code:`groupthink install <org>` installs the scripts for :code:`<org>`
* :code:`groupthink uninstall <org>` removes the scripts for :code:`<org>`
* :code:`groupthink update <org>` checks for updates made to :code:`<org>`'s scripts
* :code:`groupthink upgrade <org>` installs all updates made to :code:`<org>`'s scripts
* :code:`groupthink list` lists all groupthink scripts you have installed for any :code:`<org>`
* :code:`groupthink install <org> --alias <alias>` install the scripts for :code:`<org>` under :code:`<altname>` (if you use this, replace :code:`<org>` with :code:`<altname>` in the options above)

Requirements
==============

* Python (v. 2.7 or 3.3+)
* git
* If you're running Windows, use `Git Bash <https://git-for-windows.github.io/>`_

Installation
==============

Install groupthink with :code:`pip install groupthink`
