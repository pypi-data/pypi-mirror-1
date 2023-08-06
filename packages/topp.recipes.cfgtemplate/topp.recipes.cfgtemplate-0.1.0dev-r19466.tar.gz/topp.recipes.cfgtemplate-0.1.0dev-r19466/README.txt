========================
topp.recipes.cfgtemplate
========================

This is a zc.buildout recipe that provides support for template
substitution within the buildout.cfg file.  When this recipe is loaded
in a buildout.cfg file, it will search the buildout configuration for
any instances of the the template syntax, i.e. any text enclosed by
{{double-curly-braces}}.  If substitutions are found, the
configuration will be altered directly in memory, and any subsequent
recipes will be run with the substituted values.

The template substitution values come from a separate config file,
specified in the topp.recipes.cfgtemplate configuration, defaulting to
"cfgsubs.cfg".  If the substitution file does not exist, or if it is
missing any values required by the buildout.cfg file, then the user
will be interactively prompted to enter the requested information, and
the substitution file will be created or amended with the provided
values.

The idea is that you'll create a templatized buildout.cfg file and
store it in a revision control system (RCS).  The templatized values
would represent information that is not suitable for storage in the
RCS, such as port numbers, passwords, database connection strings, or
anything else that is either sensitive or likely to vary from
deployment to deployment.  The first time this buildout.cfg file is
used in a new location, the user will interactively provide these
values, which would then be stored in the substitution file, which is
left out of the RCS, or (if desired) is stored in a more secure
repository elsewhere.
