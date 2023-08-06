.. -*-rst-*-

===================
Plone4Artists Audio
===================

Overview
========

The p4a.ploneaudio egg is a Plone product built to expose the ``p4a.audio``
framework in a Plone setting.  In a nutshell it provides the following
features:

File support
  Uploaded File objects are scanned for audio mime 
  types and are *audio enhanced* automatically if a registered mime 
  type is found.

Audio container support
  Any folder or smart folder can be *media activated* which turns it into 
  an audio container which knows how to display an overview for all 
  contained audio.

Embedded media player support
  MP3 and Ogg audio files can be played inline within the browser.

Audio metadata support
  Audio information is read from and written to MP3 and Ogg audio files.

Podcasting support
  Audio containers (activated folders or smart folders) can have ther 
  contents broadcast using RSS with enclosures representing the individual 
  audio files.

Content Licensing support
  All audio content can automatically be licensed using the ContentLicensing_
  product.

Requirements
============

- Zope 2.10.x
- Plone 3.0.x or 3.1.x (3.0.6 and 3.1.5.1 tested)

Optional Dependencies
=====================

Licensing Support
  - ContentLicensing_ 1.0.2 or higher

Podcasting Support
  - basesyndication_ SVN trunk r3214 or higher
  - fatsyndication_ SVN trunk r32123 or higher

.. _ContentLicensing: http://plone.org/products/contentlicensing
.. _basesyndication: https://svn.plone.org/svn/collective/basesyndication/
.. _fatsyndication: https://svn.plone.org/svn/collective/fatsyndication/

Installation
============

1. Add p4a.ploneaudio to the list of eggs (for buildout: eggs=p4a.ploneaudio)

2. Add p4a.ploneaudio to zcml slugs (for buildout: zcml=p4a.ploneaudio)

For info on setting up the optional dependencies please see INSTALL.txt

Basic Usage
===========

- files with mime types ``audio/mpeg`` or ``application/ogg`` will
  automatically become *audio enhanced*

- folders and files can be toggled to be audio enhanced by selecting the
  **activate audio** menu item in their respective **actions** drop down
  menus.

Smart Folders
=============
You can use audio enhanced smart folders to display audio from across your
site. Which audio files appear in your smart folder depends on the criteria
you specify in the **criteria** drop down menu of the smart folder.

Here are step-by-step instruction for creating three commonly used audio
smart folders:

  1. A smart folder containing all audio files from the whole site:

    i) Create a smart folder, give it a Title and save it
    ii) Audio-activate the smart folder in the **actions** drop down menu
    iii) Click the **criteria** tab 
    iv) In the *Add New Search Criteria* box, set *Field name* to *MIME Types*
    v) Click *add*
    vi) In the *criterion details* column set *Value* to *audio/mpeg*
    vii) Click the *save* button just below the *MIME Types* table, i.e. not
         the save button at the bottom of the page

  2. A smart folder containing all audio by a particular artist (repeat all
     steps from #1):

    i) In the *Add New Search Criteria* box, set *Field name* to *Artist name*
    ii) Click *add*
    iii) In the *criterion details* column set *Value* for Artist name to the
         name of the artist 
    iv) Click the *save* button just below *Artist name*, i.e. not the save
        button at the bottom of the page

  3. A smart folder containing all audio of a particular genre (repeat all
     steps from #1):

    i) In the *Add New Search Criteria* box, set *Field name* to *Genre*
    ii) Click *add*
    iii) Enter the number that corresponds to the genre. For a list of genres
         and corresponding numbers, please see the file:
         ``Plone4ArtistsAudio/pythonlib/p4a/audio/genre.py``
    iv) Click the *save* button just below *Genre*, i.e. not the save button
        at the bottom of the page

*Artist name* and *genre* are set up as search criteria when Plone4Artists Audio
is installed, because they are the criteria thought most likely to be required.
If you want to add other criteria, to e.g. have a folder for all songs recorded
in 1976, you have to do a little more work. See the following page for
instructions on creating your own search criteria:
http://plone.org/documentation/how-to/using-topics
