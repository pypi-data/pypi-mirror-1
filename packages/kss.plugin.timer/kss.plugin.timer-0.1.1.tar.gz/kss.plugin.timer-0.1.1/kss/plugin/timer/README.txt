================================================
                kss.plugin.timer                
================================================

Explain a bit a about your project here.

Command sets
============

Describe the commandsets you provide with examples of how to use
it. The examples will be run as part of the tests.

  >>> from kss.base import KSSCommands, load_plugins

  >>> load_plugins('kss-core')

  >>> from kss.base.selectors import CSS

  >>> from {package}.commands import KssPluginTimerCommands

  >>> commands = KSSCommands()
  >>> timer = KssPluginTimerCommands(commands)

Add explanations and tests for your actions here.

  >>> timer.replaceInnerHTML(CSS('#someid'), 'example data')
  >>> print commands.render()
  yourAction(css('#someid'), parameter='example data')

