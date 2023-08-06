============================
Using the flufl.i18n library
============================

This is how to use the flufl.i18n library from your application.  The first
thing you should do is import the global registry.

    >>> from flufl.i18n import registry

Next, decide on a strategy for finding your application's catalogs when given
a language code.  flufl.i18n comes with a fairly simple one that looks up
catalogs from the file system using GNU gettext's convention.  The base
directory for the catalogs is rooted in a submodule.

    >>> from flufl.i18n import PackageStrategy
    >>> import flufl.i18n.testing.messages

The first argument is the application name, which must be unique among all
registered strategies.

    >>> strategy = PackageStrategy('flufl', flufl.i18n.testing.messages)

Once you have the desired strategy, register this with the global registry.
The registration process returns an application object which can be used to
look up language codes.

    >>> application = registry.register(strategy)

The application object keeps track of a current translation catalog, and
exports method which you can bind to the 'underscore' function in your module
globals for convenient gettext usage.  By doing so, at run time, _() will
always translate the string argument to the current catalog's language.

    >>> _ = application._

By default the application just translates the source string back into the
source string.  I.e. it is a null translator.

    >>> print _('A test message')
    A test message

If your application uses more than one language, you can temporarily push a
new language context to the top of the stack, which automatically rebinds the
underscore function to the language's catalog.  If your application only uses
one language, just do this once in your initialization code.

    >>> _.push('xx')

    # The testing 'xx' language rot13's the source string.
    >>> print _('A test message')
    N grfg zrffntr

Pop the current language to return to the default.  Once you're at the bottom
of the stack, more pops will just give you the null translation.

    >>> _.pop()
    >>> print _('A test message')
    A test message

The underscore method has a context manager called `using` which can be used
to temporarily set a new language inside a `with` statement.

    >>> with _.using('xx'):
    ...     print _('A test message')
    N grfg zrffntr

    >>> print _('A test message')
    A test message

These with statements are nestable.

    >>> with _.using('xx'):
    ...     print _('A test message')
    ...     with _.using('yy'):
    ...         print _('A test message')
    ...     print _('A test message')
    N grfg zrffntr
    egassem tset A
    N grfg zrffntr

    >>> print _('A test message')
    A test message

You can set the bottom language context, which replaces the default null
translation.

    >>> _.default = 'xx'
    >>> print _('A test message')
    N grfg zrffntr

    >>> _.pop()
    >>> print _('A test message')
    N grfg zrffntr

    >>> with _.using('yy'):
    ...     print _('A test message')
    egassem tset A

    >>> print _('A test message')
    N grfg zrffntr
