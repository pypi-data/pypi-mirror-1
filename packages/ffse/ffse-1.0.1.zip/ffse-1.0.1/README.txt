Firefox Session Editor 1.0.1
Kevin Vance


Description
-----------
Firefox Session Editor (FFSE) is a utility to delete entries from the Firefox
web browser's session store.  The most common reason to do this is because
you have stumbled upon a page which crashes Firefox as soon as your session
is restored.  Firefox only gives you the option of erasing your entire session
when this happens.


Supported Operating Systems
---------------------------
Linux
Mac OS X
Windows


Requirements
------------
Python 2.4 or higher
wxWidgets 2.6 (later versions may not work on OS X)


Instructions
------------
Run the script ffse.py to start the program.  If you only have a single
Firefox profile, it will be loaded automatically.  If not, you will need to
find it with one of two methods:

File -> Open Firefox Session...
   If Firefox is installed in the default location, you can select which
   profile to open in a dialog box.

File -> Open File...
   If your Firefox profile directory is in a nonstandard location, or you want
   to edit a backup file, you can open it directly.  The sessionstore file is
   normally named sessionstore.js.

When the session store is loaded, you can select all of the entries you want
to remove, and remove them with the "Delete" button.

Note: There are many more entries listed than are visible in your browser
session because recently closed tabs are included in the session store.  To
help you find a particular website, you can click on the column headings
("Title", "URL", and "ID") to sort the list by that column.

File -> Save
   If you are satisfied with your changes, save them.  If you made a mistake,
   open the session again and start over.


Technical Details
-----------------
Session store files are formatted in JavaScript Object Notation (JSON) in
such a way that every JSON python library I tried failed to read them.  FFSE
includes a modified version of demjson 1.1 that makes it flexible enough to
read in Firefox JSON files.

After the changes are made, demjson overwrites sessionstore.js in a more
strict format.  I have used this in my personal profile many times to no ill
effect.  If something does go wrong, Firefox should have made a backup called
sessionstore.bak.  You can use this to undo any damage caused by JSON
confusion.


Boilerplate
-----------
Redistribution is welcome under the terms of the GNU GPL.
FFSE (C) 2006-2007 Kevin Vance <kvance@kvance.com>.
FFSE includes a modified version of demjson 1.1 by Deron Meranda.
   <http://deron.meranda.us/python/demjson/>
The FFSE project page is located here:
   <http://kvance.com/project/ffse/>
