Introduction
============

This patch correct an error due to this line in iw/fss/__init__.py :
context._ProductContext__app.Control_Panel.TranslationService._load_i18n_dir(i18n_dir)

It appears when i do my first bin/instance fg of a fresh buildout 
Plone-3.3 configured with iw.recipe.fss and with the egg iw.fss==2.8.0b1. 

It appears only if you never have started your instance before.

 => AttributeError: TranslationService.

May be you can remove this hook in the 2.8.0b2, the unic translation is not really necessary ;)

http://plone.org/products/filesystemstorage/issues/39


