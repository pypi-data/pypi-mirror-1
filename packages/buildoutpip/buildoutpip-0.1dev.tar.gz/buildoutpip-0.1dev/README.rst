This is a buildout extension that allows to buildout from a pip requirements file.

This was created very quickly to show my friend that it could be done. I don't need this right now,
but I can see this being very useful for Pinax users.

TODO:
* allow to open local requirements
* implement -e and -f requirements options
* write tests

Here is an example of a buildout file.

[buildout]
extensions = buildoutpip
requirements =
	http://github.com/pinax/pinax/raw/master/requirements/0.7/release.txt
parts = pip
eggs =

[pip]
recipe=zc.recipe.egg
eggs = ${buildout:eggs}
