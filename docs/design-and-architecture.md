# Design and Architecture

## System architecture

In the diagram below, the `word-def-plugin-core` is a virtual namespace. The two
classes contained within it are protocols defined in the `word-def` package.

```{mermaid}
classDiagram
    namespace word-def-plugin-core{
        class Plugin
        class PluginFactory
    }

    namespace word-def-plugin-english-collins{
        class Adapter_en["Adapter"]
        class AdapterFactory_en["AdapterFactory"]
    }

    namespace word-def-plugin-italian-pons{
        class Adapter_it["Adapter"]
        class AdapterFactory_it["AdapterFactory"]
    }

    namespace word-def{
        class get_definition
        class get_synonyme
        class get_usage_examples
    }


    Adapter_en <|.. Plugin
    AdapterFactory_en <|-- PluginFactory
    Adapter_it <|.. Plugin
    AdapterFactory_it <|-- PluginFactory

    Plugin
    <<interface>> Plugin
    Plugin: get_definition()
    Plugin: get_synonyme()
    Plugin: get_usage_examples()

    PluginFactory
    <<interface>> PluginFactory
    PluginFactory: get_language()
    PluginFactory: get_adapter()

    get_definition -- Adapter_en
    get_definition -- Adapter_it

```

## Design Notes

This document lists the design and architectural decisions taken
during the development of Word Definition. It follows
the [Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions.html) format.

### Plugin architecture

**Date: (2024-02-02)**


#### Context

The `word-def` package contains the backbone of a plugin architecture. The `word-def`
package defines the protocols to be implemented by plugins.

1. Plugin
2. PluginFactory

The entry point for plugins is the `AdapterFactory` class, which every plugin
must define. This class follows the `PluginFactory` protocol, and its goal is
to instantiate implementations of `Plugin` and provide an interface to their
metadata.

The `word-def` plugin register will attempt to load any Python modules
installed at `danoan.word_def.plugins.modules` as plugins.

```{admonition} Protocol enforcement
`word-def` uses Python protocols, which do not enforce `is-a` relationships (as
it is the case with regular inheritance and abstract classes).
```

The `word-def` package can be used as a library via the `api` module or
through a `cli`. A plugin is installed like any other python package.

#### Decision

Use plugin architecture to inject functionalities into `word-def` package.

#### Status

Done.

#### Consequences

Creation of interfaces:

1. Plugin
2. PluginFactory


### Protocols instead of Abstract Classes

**Date: (2024-02-19)**


#### Context

A plugin is a Python module that must have two classes:

1. One should implement the `Plugin` protocol.
2. The second one should implement the `PluginFactory` protocol.

The use of protocols gives us a loosely coupled object compared with
abstract classes and regular inheritance. The implementations above do
not need to inherit from any class, removing a dependency.

```{admonition} Abstract class
If we use abstract classes, we would have to create a package to hold
the abstract classes (e.g. `word-def-plugin-core`). Using protocols
allows us to reduce the number of packages to maintain, as the
protocols can be declared in the `word-def` package.
```

```{admonition} Why to declare protocols?
Since we do not have enforcement during instantiation of classes
derived from regular inheritance, why use protocols? First,
because they participate in static type checking. If we pass an
object to a function that expects protocol `P` but the object does not
implement it, an error will be raised. Second, we can take
advantage of automatic documentation generation from code to have the
protocols documented.
```

#### Decision

Implement `Plugin` and `PluginFactory` as protocols.

#### Status

Done.

#### Consequences

##### Reduced maintenance burden

We no longer need to create a `word-def-plugin-core` package. The
protocols are declared in the `word-def` package.

##### Plugins depend on `word-def` package

At first glance, it may seem odd that the `word-def` package, witch
is extended by plugins, it itself a dependency for its plugins. However,
this does not pose a problem.

Plugins are registered at running time, so the `word-def` package
is independent and can be installed without any plugins.

However, an issue arises if there are published plugins A and B:

- Plugin A uses `word-def` (v2.0)
- Plugin B uses `word-def` (v1.0)

If we try to install the latest versions of both plugins on the same machine,
it won't work because they have incompatible dependencies. The only way to have
both plugins working would be to keep v1.0 of `word-def`.

```{admonition} Incompatible dependency issue
This problem also exists in the design where we have the `word-def-core`
package.
```

This is not ideal. We would like to have both plugins with their latest versions
installed and if any issue appear, simply signalize to the user that that particular
plugin cannot be used.

To solve that issue, plugins should not specify the version of `word-def`
they depend on. Instead, the package manager (e.g. pip) will handle that.

```{admonition} Checking version compatibility
It is always possible to check the plugin version and the `word-def` version. The
PluginFactory protocol specifies the method `version`, and the api has the methods
`api_version` and `is_plugin_compatible` for that purpose.
```


### Plugin register mechanism

**Date: (2024-03-01)**


#### Context

We need a mechanism to register plugins such that `word-def`
can automatically identify and load them at runtime.

**Using a decorator**

The initial solution was to use a decorator and share the
burden with the plugin creator. In this scenario, the plugin
creator would have to add the `@register` decorator to their
implementation of the `PluginFactory` class.

```python
@model.register
class AdapterFactory:
    ...
```

However, we still needed a way to automatically load the plugin
module at runtime. The second strategy allows us to do that
without burdening the plugin creator.

```python
def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance

@singleton
class _PluginRegister:
    ...

def register(cls: T_AdapterFactory):
    plugin_register = _PluginRegister()

    def inner(*args, **kwargs):
        adapter_factory = cls(*args, **kwargs)
        plugin_register.register(adapter_factory)

    return cls
```

**Fixed plugin namespace and package introspection**

In this design, plugins must be within a fixed namespace: `danoan.word_def.modules.plugins`.
The `word-def` package can only identify and load Python modules located within this namespace.

```python
def collect_modules():
        prefix = "danoan.word_def.plugins.modules"
        plugins_module = importlib.import_module(prefix)
        for module_info in pkgutil.iter_modules(
            plugins_module.__path__, prefix=f"{prefix}."
        ):
            yield importlib.import_module(module_info.name), module_info.name

```

The strong point of this approach is automatic loading. To start using a plugin,
the user only need to install the plugin package.

The drawback is the restriction on plugin creators to create their plugins
within a fixed namespace.

#### Decision

Use package introspection and Python import system mechanisms via `importlib`
to implement the plugin mechanism in `word-def`.

#### Status

Done.

#### Consequences

Plugin packages must be created within the namespace `danoan.word_def.modules.plugins`.


### Testing the plugin register mechanism

**Date: (2024-03-02)**

#### Context

The plugin mechanism is designed to search and load modules in a given namespace. To
test this mechanism, we need to make the Python import system believe that there is
a `fake_test_plugin` python module in that namespace.

Our solution is to create a decorator that wraps the test function within a context manager.
Within the context manager, we create a temporary directory `T` and the directories
corresponding to our namespace. Finally, adding `T` to `sys.path` emulates the namespace at
runtime in the Python import system.

```python
def plugin_context(plugins_location, plugins_base_import_path):
    def decorator(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            with tempfile.TemporaryDirectory() as tempdir:
                sys.path.append(tempdir)

                # Create <tempdir>/<namespace_dir>
                # Copy fake_module to <tempdir>/<namespace_dir>

                func(*args, **kwargs)
        return inner
    return decorator


def test_plugin_register():
    plugins_location = f"{SCRIPT_FOLDER}/input"
    plugins_base_import_path = "danoan.word_def.plugins.modules"

    @plugin_context(plugins_location, plugins_base_import_path)
    def inner():
        register = api.get_register()

        language_plugins = register.get_language_plugins("eng")
        assert len(language_plugins) == 1

    inner()
```

#### Decision

Wrap test functions within a context manager to emulate the plugins namespace.

#### Status

Done.

#### Consequences

None.

### Multi-language plugins register mechanism

**Date: (2024-03-15)**

#### Context

Originally, plugins were designed to be exclusive to a certain language. An English
plugin would only respond to queries regarding the English language.

However, the `word-def-plugin-multilanguage-chatgpt` can handle several languages at
once by simple mentioning the language in the prompt. The language, in this case, is
a plugin parameter.

We did not want to change the `Plugin` or `PluginFactory` protocols, so
we decided that multi-language plugins will return an empty string for the `get_language`
method and that it is up to the `word-def` API to specify the language for the
multi-language plugin at runtime.

Every method of `word-def` API requires a language parameter. The language parameter is used
to find an available plugin to execute the task in the given language. Whenever the plugin
search begins, ensure the multi-language factory is wrapped in a wrapper class. This class
preserves the calls of every method of the multi-language factory, except
`get_language`, which is replaced with the user-specified language.


#### Decision

- Allow multi-language plugins.
- An empty string as return value of `get_method` indicates a multi-language plugin.
- The `word-def` API wraps the multi-language factory and overwrites the `get_language` method
  as needed.

#### Status

Done.

#### Consequences

None.
