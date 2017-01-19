Contributing to the Globus SDK
==============================

First off, thank you so much for taking the time to contribute! :+1:

This document is a set of guidelines for making modifications to the SDK, not a
set of strict rules.
Sometimes it's okay to go off-book if you have a good reason, so use your best
judgement.
Feel free to propose changes to this document in a pull request.

QuickStart
----------

Impatient? Want to get hacking on this right away?
A few quick rules if you don't want to read this full document:

  - All of your code *must* pass `flake8`. We won't consider merging code which
      doesn't pass `flake8`
  - Check if there's a matching
      [issue](https://github.com/globus/globus-sdk-python/issues)
      before opening a new issue or pull request
  - Any features which change the public API of the SDK must include
      documentation updates
  - `make test` must pass

Reporting Bugs
==============

We welcome any and all bugs on the
[GitHub Issue Tracker](https://github.com/globus/globus-sdk-python/issues).

However, the best bug reports are ones which follow the following rules:

  - *Check for duplicates*. You don't have to scour our issue tracker, but do a
      quick search to try to make sure you aren't reporting a known bug.
  - *Use a clear descriptive title* for the issue you are reporting. The best
      titles are short, but also uniquely describe the problem.
  - *Provide a specific example of how to reproduce*. Example code is best, but
      even a vague description is better than no description.
  - *Explain what behavior you expected* and why. Not everything unexpected is
      a bug -- what appears to you as a defect may in fact be faulty
      documentation, for example, which needs to be updated.
  - *Include a stacktrace* where applicable. If you're getting an error from
      within the SDK code itself, stacktraces often help us figure out what's
      going on much faster.

You can also help us a lot by including the following information:

  - *What version of python are you running?* The SDK supports a wide variety
      of python versions, and a wide class of bugs are results of version
      incompatibilities between those versions.
  - *What OS and OS version are you running?* `uname -a` is the easiest way to
      give us this info, but additional description like "Ubuntu Linux 15.10"
      may help.
  - *What other python packages do you have installed?* The best thing in this
      case is to show us the results of `pip freeze`


Requesting Enhancements
=======================

When requesting new features, there are a few things we ask you to do in order
to help us prioritize.

  - *Describe the end result you want*. You might have good (or great!) ideas
      about how a feature can be implemented, but we ask that you give us a bit
      more information. This lets us have a conversation about what you want
      and the best way for us to support it among our other concerns.
  - *Tell us why you want it*. If you request a feature, but we don't know what
      you want it for, it's hard for us to know how critical the request is.
      Tell us as much of the *why* as you can, not just the *what*.
  - *How important is this feature to you?* Clearly describe to us how
      important this feature is for your use case. Obviously, this is not the
      only thing we weigh when prioritizing features, but it is important for
      us to know.

Submitting Pull Requests
========================

The most important thing about a pull request is that it meets the standards
defined in this document's [Style Guide](#style-guide).

Beyond that, we have a few recommendations:

  - *Make sure it merges cleanly*. We may request that you rebase if your PR
      has merge conflicts.
  - *List any issues closed by the pull request*.
  - *Squash intermediate commits*. Help us keep our git history clean by doing
      a `git rebase --interactive` and squashing typo fixes, aborted
      implementations, and other cruft.

Additionally, make sure you follow our rules for
[Commit Messages](#commit-messages)

Commit Messages
===============

A few basic ground rules for what ideal commits should look like.

  - No lines over 72 characters
  - No GitHub emoji -- use your words
  - Reference issues and pull requests where appropriate
  - Present tense and imperative mood

Style Guide
===========

Some rules and tips for the python and documentation in this project.

  - All code must pass `flake8`. That means PEP8 compliant and passing pyflakes
  - Try to use raw strings for docstrings -- ensures that ReST won't be
      confused by characters like `\\`
  - For complex functionality, include sample usage in docstrings
  - Comment liberally
  - Use double-quotes for strings, except when quoting a string containing
      double-quotes but not containing single quotes
  - Use examples very liberally in documentation, and show where you imported
      from within the SDK. Start at least one example with
      `from globus_sdk.modulename import ClassName` on a page with docs for
      `ClassName`
  - Use absolute imports everywhere
  - Avoid circular imports whenever possible -- given the choice between adding
      a new module or adding a circular import, add the new module
  - Import non-`globus_sdk` modules and packages before importing from within
      `globus_sdk`
  - Ensure all public API methods return a `GlobusResponse` or subclass thereof,
      or explicitly document their exceptional status
  - Think very hard before adding a new dependency -- keep the dependencies of
      `globus_sdk` as lightweight as possible
