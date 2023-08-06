Setupdocs is a setuptools extension that help doc building automation. It adds two commands to the 
setup.py command.

build_docs
----------
Finds Sphinx source in docs/ and buils html. Can also build latex and pdf with --formats= directive if
latex is installed.

dist_docs
---------
Builds html docs and creates an html.zip in the dist/ folder. With -c, replaces the html.zip in the docs 
folder and checks it in. With -u, it doesn't create the html.zip but instead updates the docs on the 
website. It does this by 1) getting a fresh svn checkout of the docs, 2) building the docs with Sphinx 
and overwriting the old ones, 3) svn adding and checking in the new and changed docs, 4) ssh login to www,
5) cd to the doc dir, 6) svn up and chmod g+w. It's not perfect, but it pretty much works.

Some options can be configured in setup.py, and are in Mayavi and Chaco.

Command-line help is available via -h.
