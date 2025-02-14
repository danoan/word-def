# How to test a plugin

A `word-def` plugin depends on the `word-def` package itself, which makes
it very convenient to locally test your plugin in a interactive pythonn
session or by creating unit tests.

## Recommended unit tests

We recommend creating the following unit tests for your plugin:

### Plugin language test

Make sure that your plugin is returning a valid IETF 639-3 language code
or an empty string if your plugin is multi-language.

```python
def test_language():
    language_code = my_plugin.AdapterFactory().get_language()
    assert pycountry.languages.get(alpha_3=language_code) is not None
    assert language_code == "eng"
```

### Protocol compatibility

Ensure that your plugin is compatible with the version of `word-def`
it depends on.

```python
def test_plugin_compatibility():
    assert api.is_plugin_compatible(my_plugin.AdapterFactory())
```

???+ Hint
     A plugin package is considered compatible with `word-def` if both
     have the same major version number. For example: 1.0.12 is
     compatible with 1.7.3

### API response handlers

It is common for plugins to call third-party packages or make
API calls to base theirs responses on. It is a good idea to separate the
method that does the API call from the one that prepares the response.

We suggest creating regular unit tests for the response handler and
integration tests (run in a regular basis, e.g. every two weeks) for the
API calls.
