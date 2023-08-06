Introduction
============

ReflectoImageScales adds Kupu compatible image scaling to Reflecto files. Just
add ReflectoFile as a resource type to Kupu with the same settings as the
standard Plone image types.

I'm not sure if this should be a separate project to Reflecto. There are some
very rough edges at the moment, it has to monkey patch Reflecto to satisfy
kupu's expectations and it would be nice to only make images addable.
