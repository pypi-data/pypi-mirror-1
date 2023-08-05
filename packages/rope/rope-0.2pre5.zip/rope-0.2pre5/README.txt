========================
 rope, a python IDE ...
========================


Overview
========

*rope* is a Python IDE.  Its main goal is to provide features like
auto-completion, refactorings, code assists and outlines.  It is
written in python and uses the Tkinter library.


Version Overview
================

Features added in this release:

* Support for out of project modules for code completions and go to
  definitions
* Type inference of ``var = AClass()``
* Renaming function parameters inside functions
* Handling circular imports inside source files
* Completeing ``AClass(params).a_``
* Better quick outline view


If an imported module can not found inside the project, the `sys.path`
entries will be searched for it.

If it is the first time you use rope, it might be helpful to try
these:

=============  ======================
Alt-/          Show code assists
Ctrl-o         Show quick outline
F3             Go to definition
Alt-Shift-r    Rename local variable
=============  ======================

If you want to change the font or keybindings edit
`rope.editor.GraphicalEditor` class.


Keybinding
==========

The keybinding will be customizable in future.  Some of these bindings
are choosen from emacs and some from eclipse.  ('C' stands for Control
key and 'M' for Meta(Alt) key.)

=============  ==========================
key            binding
=============  ==========================
C-x C-p        open/new project
C-x C-n        new file
C-x C-f        find file
C-x b          change active editor
C-x k          close active editor
C-x C-c        exit
C-F11          run active editor
-------------  --------------------------
C-f            forward character
C-b            backward character
C-n            next line
C-p            previous line
M-f            next word
M-b            previous word
C-v            next page
M-v            previous page
C-s            start searching
C-x C-u        undo
C-x C-r        redo
C-space        set mark
C-w            cut region
M-w            copy region
C-x C-x        swap mark and insert
C-y            paste
C-x C-s        save
C-i            correct line indentation
M-/            code-assist
F3             go to definition location
C-o            show quick outline
M-R            rename refactoring
=============  ==========================


Description
===========

*rope* is a python IDE. It tries to give users lots of things that
are not available in python IDEs yet.

Refactoring
-----------

In recent years refactoring has become a basic task of everyday
programing, specially in java community. In the agile programing
methodologies, like Extreme Programing, Refactoring is one of the core
practices.

Some IDEs support some basic refactorings like 'PyDev' (which uses
bicycle repair man). These IDEs have a limited set of refactorings and
fail when doing refactorings that need to know the type of objects in
the source code (specially for relatively large projects). rope tries
to provide a rich set of refactorings. Some of the refactorings
require type inference which is described later.

Auto Completion
---------------

One of the basic features of modern IDEs is the availability of auto-
completion. Some Python IDEs have auto-completion support but in a
limited form. Since the type of many variables cannot be deduced from
simple analysis of the source code. Auto-completing modules names,
class names, static methods, class methods, function names and
variable names are easy. But auto- completing the methods and
attributes of an object is hard. Because the IDE needs to know the
type of the object that cannot be achieved easily most of the time in
dynamic languages. rope uses Type Inference algorithms to solve this
problem.

Type Inference
--------------

One disadvantage of dynamic languages like python is that you cannot
know the type of variables by a simple analysis of program source code
most of the time. Knowing the type of variables is very essential for
providing many of the refactorings and auto-completions. rope will use
type inference to overcome this problem.

Static type inference uses program source code to guess the type of
objects. But it is is very hard. There have been some attempts though
not very successful (examples: psycho: only str and int types,
StarKiller: wasn't released and ShedSkin: good but limited). They
where mostly directed at speeding up python programs by transforming
its code to other typed languages rather than building IDEs. Such
algorithms might be helpful.

There is another approach toward type inference. That is the analysis
of running programs. This dynamic approach records the types variables
are assigned to during the program execution. Although this approach
is a lot easier to implement than the alternative, it is limited. Only
the parts of the program that are executed are analyzed. If developers
write unit tests and use test driven development this approach works
very well.


Project Road Map
================

The main motive for starting this project was the lack of good
refactoring tools for python language. Refactoring programs like
"bicycle repair man" aren't reliable due to type inference problems
discussed earlier and they support a limited number of refactorings.

* Why an IDE and not a standalone library or program?

As Don Roberts one of the writers of the "Refactoring Browser" for
smalltalk writes in his doctoral thesis:

  "An early implementation of the Refactoring Browser for Smalltalk
  was a separate tool from the standard Smalltalk development
  tools. What we found was that no one used it. We did not even use it
  ourselves. Once we integrated the refactorings directly into the
  Smalltalk Browser, we used them extensively."

The main goal of rope is to concentrate on the type inference and
refactoring of python programs and not a state of art IDE (At least
not in the first phase). The type inference and refactoring parts will
not be dependent on rope and if successful, will be released as
standalone programs and libraries so that other projects may use them.


Get Involved!
=============

Rope has just started.  Right now rope's design changes rapidly and
it's not yet ready for code contributions in its central parts.  I
hope in soon future, somewhere about version 0.5, rope would be
mature enough for being extended easily in those parts.

Right now contributions are really needed in UI part and patches and
extensions in the UI part are extremely welcome.  Have a look at the
UI enhancement stories (docs/stories.txt).  Send your patches in
sourceforge.net project page, http://sf.net/projects/rope.  Patches
should use python coding style, `8`:PEP:, and should have good unit
tests.  rope uses a local repository right now, but it will be moved
to SVN repository on sourceforge.net some time before the 0.3 release.
If you're making your patches using source package distributions
specify the version of that package.


Bug Reports
===========

Send your bug reports and feature requests in rope's sourceforge.net
project page at http://sf.net/projects/rope.


License
=======

This program is under the terms of GPL(GNU General Public License).
Have a look at ``COPYING`` file for more information.

