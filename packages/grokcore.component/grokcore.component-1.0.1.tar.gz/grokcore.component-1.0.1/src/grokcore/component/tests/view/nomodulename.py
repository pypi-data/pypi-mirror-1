"""
You can't call grok.name on a module:

  >>> import grokcore.component.tests.view.nomodulename_fixture
  Traceback (most recent call last):
    ...
  GrokImportError: grok.name can only be used on class level.

"""
