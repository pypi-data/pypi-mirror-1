GitPrompt displays the current branch, the status of stash and rebase,
and optionally, non-zero exit status codes.


.. contents::


Examples
--------
To follow along, create a new repository and set your prompt::

    $ git init; touch x; git add x; git commit -m x
    $ export PS1='cwd$(../gitprompt $?) $ '

The current branch is displayed::

    cwd master $ git checkout -b new
    cwd new $ git checkout master
    cwd master $ echo y1 > y; git add y; git commit -m y1; git checkout new

The number of saved stashes is indicated::

    cwd new $ echo y2 > y; git add y; git stash save
    cwd new stash $ touch z; git add z; git stash save
    cwd new stashes! $ git stash pop ; git stash pop

Whether a rebase is in progress is indicated::

    cwd new $ git rebase master
    cwd new rebase! $ git rebase --abort
    cwd new $ git config core.editor true; git rebase --interactive master
    cwd new rebase! $ git rebase --abort

If ``gitprompt`` was passed a non-zero exit code, it will be displayed::

    cwd new $ true
    cwd new $ false
    => 1
    cwd new $
