PyPI Browser
============

:Author: David Boddie <david@boddie.org.uk>
:Date: 2006-07-30

*Note: This text is marked up using reStructuredText formatting. It should be
readable in a text editor but can be processed to produce versions of this
document in other formats.*

.. contents::


Introduction
------------

PyPI Browser is a graphical user interface (GUI) browser for the `Python Package Index`_ (PyPI)
that aims to make it easier for users to find and download useful Python software from a central
repository. It provides facilities for searching the package index, can display information
about individual packages, allows packages to be marked so that they can be downloaded together,
and records information about existing packages so that new ones can be highlighted.

.. _`Python Package Index`: http://www.python.org/pypi

Installating and Running the Browser
------------------------------------

Currently, PyPI Browser is designed to be run from within the directory that is created when its
archive is unpacked. Later versions will use a standard `setup.py` script to install the
Python sources in the correct places on your system.

To run the browser, enter the unpacked directory and type the following at a command prompt::

  python pypibrowser.py

Alternatively, this file can be run from within a suitable file manager.

Configuring the Browser
-----------------------

The first thing you should do once the browser is running is to open the **Configure Browser**
dialog by opening the **Settings** menu and selecting the **Configure Browser...** menu item.
In this dialog, you should specify the download directory you want to use for software you
request from the package index.

You can also specify some preferences for the package formats you want software to be
supplied in. By default, the package index URL is the one used for the Python Package Index
at *python.org* - you only need to customize this if you have a private package index.

Using the Browser
-----------------

The browser is arranged in the same way as most applications:

* The menu bar provides access to application-wide actions, such as opening a connection
  and exiting.
* The region in the centre of the window is a view onto the contents of a package index
  and is disabled until you open a connection.
* The controls at the bottom of the window are used to search the package index.

Searches restrict the packages shown in the main view to include only those that are
relevant.

Opening a Connection
~~~~~~~~~~~~~~~~~~~~

To open a connection to the package index, open the **File** menu and select the **Open...**
item, or press **Ctrl+O** on the keyboard. The **Open Index** dialog should automatically
contain a suitable URL for a package index, and you can accepted this by clicking the **OK**
button. The browser will fetch information about all available packages and update the main
window - this may take a moment.

Examining and Downloading Packages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each item in the main window represents a package in the index. Since these may have more than
one release associated with them, they are shown as parent items in a tree view. Clicking on
the node next to a package name will cause the list of releases for that package to be
displayed. You can double-click on a package or a release to see more information about it.

Releases that have associated download information are shown as checkable items in the tree
view. You can check as many of these as you like to indicate that you want to download them
later. The list of marked releases can be shown by applying the marked package filter: open
the **Packages** menu and check the **Filter Marked** item. Uncheck this menu item to switch
this filter off.

If you have run PyPI Browser before, you can check to see if any new packages have been added
to the package index by applying the new package filter: open the **Packages** menu and check
the **Filter New** item. Uncheck this menu item to switch this filter off.

Searching the Package Index
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each release of a package in the package index has several fields associated with it that can
be searched for a series of search terms. The combobox at the bottom of the main window allows
you to select which field should be searched in the index. The line edit next to the combobox
is used to enter a space-separated set of words that must appear in the field of any matching
releases.

The current search is executed when you click the **Search** button, press the **Return** key
in the line edit, or change the current search field in the combobox. The contents of the main
view will be updated to show any packages that match your search terms.

Downloading Packages
~~~~~~~~~~~~~~~~~~~~

Once you have selected all the packages you want to download, open the **Packages** menu and
select the **Download...** item, or press **Ctrl+Return** (**Command+Return** on Mac OS X).
The **Download Packages** dialog will open and the releases marked earlier will start being
downloaded from the package index. The progress of each download operation is shown alongside
its name and the name of the file that will be saved in the configured download directory.

Click the **Stop** button at any time to stop the download operations.

If a package cannot be downloaded, either **Failed** or the URL of its home page will be shown
in its progress indicator. You can launch a web browser by clicking on any home page URLs shown,
or return to the main window and get more information about the packages that could not be
downloaded. Any partially downloaded packages will be deleted.

Click **Open Directory** to open the download directory using your system's web or file browser.

Exiting the Browser
-------------------

Exit the browser by opening the **File** menu and selecting the **Exit** item or by pressing
**Ctrl+Q** (**Command+Q** on Mac OS X). Alternatively, you can simply close the main window to
exit.

Currently, the browser will notify you if you try to exit while there are marked packages.
Future releases of the browser may prompt you to save this information or automatically save
it along with other package information in its configuration file.

Architecture
------------

PyPI Browser uses the PyQt4_ bindings to the `Qt 4`_ framework for its graphical user
interface. Behind the scenes, it uses *xmlrpclib* to access the Python Package Index's XML-RPC
interface to obtain information about available packages.

.. _PyQt4:  http://www.riverbankcomputing.co.uk/pyqt/
.. _`Qt 4`: http://www.trolltech.com/products/qt/