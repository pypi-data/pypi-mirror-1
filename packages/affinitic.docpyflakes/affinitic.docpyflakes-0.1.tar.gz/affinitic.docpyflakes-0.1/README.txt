Introduction
============

Check your doctest for various errors. Depends on pyflakes (http://pypi.python.org/pypi/pyflakes).

Usage example::

    docpyflakes yourdoctext.txt

This package has an entry point for buildout to create a script via::

    [buildout]
    parts = ...
            scripts

    [scripts]
    recipe = zc.recipe.egg:scripts
    eggs = affinitic.docpyflakes

VIM
===

My vim configuration integration to run docpyflakes while I am working on my doctest and handle errors quickly::

    fun! PyflakesForDocTest()
        let tmpfile = tempname()
        execute "w" tmpfile
        execute "set makeprg=(docpyflakes\\ " . tmpfile . "\\\\\\|sed\\ s@" . tmpfile ."@%@)"
        make
        cw
        redraw!
    endfun

    autocmd BufWrite *.{txt} :call PyflakesForDocTest()

EMACS
=====

Learn VIM
