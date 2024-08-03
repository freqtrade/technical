# Developer documentation

This page is intended for developers of the `technical` library, people who want to contribute to the `technical` codebase or documentation, or people who want to understand the source code of the application they're running.

All contributions, bug reports, bug fixes, documentation improvements, enhancements and ideas are welcome. We [track issues](https://github.com/freqtrade/technical/issues) on [GitHub](https://github.com/freqtrade/technical).
For generic questions, please use the [discord server](https://discord.gg/p7nuUNVfP7), where you can ask questions.

## Releases

Bump the `__version__`  naming in `technical/__init__.py` and create a new release on github with a matching tag.

!!! Note
    Version numbers must follow allowed versions from PEP0440 to avoid failures pushing to pypi.

### Pypi

Pypi releases happen automatically on a new release through github actions.
