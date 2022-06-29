# Contributing to Yarrow

First of all, any contribution is welcome, thank you for taking the time to read this !

The following is a set of guidelines to let you help us. These are not rules and are not set in stone. This project is very young so feel free to suggest changes to this document.

> *This document is still a work in progress, check it later for its evolutions*

## Table of content

[How do I get started](#how-do-i-get-started)

[How to contribute](#how-to-contribute)

[Styleguides](#styleguides)

## How do I get started ?

* Look if the issue you are worried about already exists in the [issue tracker](https://github.com/michelin/YarrowFormat/issues), if not then please open one using the [bug template](.github/ISSUE_TEMPLATE/bug_report.md)
* If you are looking for a functionality read the documentation to be sure it doesn't already exist

: please fork the project and send us a Pull Request. Please read the following section for more information.

## How to contribute

* If you add a new functionality you must either add tests in the existing files or add a new test file
* Add appropriate documentation
  * More guidelines will be added later
* If you want to contribute code please fork the project and create a branch with the following template
  * `bug/<issue-name>` if you wish to correct a bug
  * `feature/<issue-name>` if you wish to implement new features or add documentation

## Styleguides

Use `black` and `isort` before pushing your modifications.
The default arguments are used which is line length = 88 (or `black -l 88`) for black
