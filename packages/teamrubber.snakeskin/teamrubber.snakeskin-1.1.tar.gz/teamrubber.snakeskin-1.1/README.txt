Introduction
============

SnakeSkin allows skin products for Plone 3 to be created easily in a similar
way to the ZopeSkel plone3_theme template.  The primary difference is that
plone3_theme assumes either a blank theme or a customisation of the default,
whereas snakeskin allows the user to select the theme he wants to customise.

This is very useful for commercial environments where a generic skin requires 
small modifications on a client-by-client basis.

An example using an internal teamrubber skin is::

    Nimbus:teamrubber.snakeskin matthewwilkes$ paster create -t plone3_snakeskin
    Selected and implied templates:
      ZopeSkel#basic_namespace               A project with a namespace package
      teamrubber.snakeskin#plone3_snakeskin  A Theme for Plone 3.1 based on another theme egg.

    Enter project name: clienttheme.example
    Variables:
      egg:      clienttheme.example
      package:  clientthemeexample
      project:  clienttheme.example
    Enter namespace_package (Namespace package (like clienttheme)) ['clienttheme']: clienttheme
    Enter package (The package contained namespace package (like example)) ['example']: example
    Enter version (Version) ['1.0']: 1.0
    Enter theme_name (The name of this theme) ['Client Skin']: Client Skin
    Enter base_theme (The package containing the theme to base on (the name of the egg)) ['plonetheme.example']: plonetheme.example
    Enter basename (The name of the Zope skin layer the above theme provides) ['My Theme']: My Theme
    Enter description (One-line description of the package) ['A theme based on an existing arbitrary plone 3 theme.']: This is my client customisation of the defaults for plone3_theme.
    Enter long_description (Multi-line description (in reST)) ['']: I'm not feeling talkative.
    Enter author (Author name) ['']: Matthew Wilkes
    Enter author_email (Author email) ['']: matt.wilkes@teamrubber.com
    Enter keywords (Space-separated keywords/tags) ['']: 
    Enter url (URL of homepage) ['']:                           
    Enter license_name (License name) ['GPL']: 
    Enter zip_safe (True/False: if the package can be distributed as a .zip file) [False]: 
