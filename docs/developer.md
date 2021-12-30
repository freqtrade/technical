# Developer documentation

This page is intended for developers of the `technical` library, people who want to contribute to the `technical` codebase or documentation, or people who want to understand the source code of the application they're running.

All contributions, bug reports, bug fixes, documentation improvements, enhancements and ideas are welcome. We [track issues](https://github.com/freqtrade/technical/issues) on [GitHub](https://github.com/freqtrade/technical).
For generic questions, please use the [discord server](https://discord.gg/p7nuUNVfP7), where you can ask questions.

## Releases

### pypi

To create a pypi release, please run the following commands:

Additional requirement: `wheel`, `twine` (for uploading), account on pypi with proper permissions.

``` bash
python setup.py sdist

# For production:
twine upload dist/*
```

Please don't push non-releases to the productive / real pypi instance.
