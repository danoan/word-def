# Design and Architecture

## System architecture

In the diagram below, the `word-def-plugin-core` is virtual. The two
classes declared within it are protocols that are actually declared
in the `word-def` package.

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

The `word-def` contains the backbones of a plugin architecture. The `word-def`
package defines the protocols to be implemented by plugins.

1. Plugin
2. PluginFactory

The entry point for plugins is the class `AdapterFactory` which every plugin
must define. This class follows the `PluginFactory` protocol and its goal is
to instantiate `Plugin` implementations and provide an interface to its
metadata.

The `word-def` plugin register will try to load as a plugin all python modules
installed at `danoan.word_def.plugins.modules`.

```{admonition} Protocol enforcement
`word-def` uses python Protocols which do not enforce `is-a` relations (as
it is the case with regular inheritance and abstract classes).
```

The `word-def` package can be used as a library, via the `api` module or via
a `cli`. A plugin is installed as any other python package.

#### Decision

Use plugin architecture to inject functionalities to `word-def` package.

#### Status

Done.

#### Consequences

Creation of interfaces:

1. Plugin
2. PluginFactory


### Protocols instead of Abstract Classes

**Date: (2024-02-19)**


#### Context

A plugin is a python module that must have two classes:

1. One should implement the `Plugin` protocol.
2. The second one should implement the `PluginFactory` protocol.

The use of protocols gives us a loosely coupled object compared with
abstract classes and regular inheritance. The implementations above do
not need to inherit from any class, and that removes a dependency.

```{admonition} Abstract class
If we use abstract classes we would have to create a package to hold
the abstract classes, e.g. `word-def-plugin-core`. Using protocols
allows us to reduce the number of packages to maintain, since the
protocols can be declared in the `word-def` package.
```

```{admonition} Why to declare protocols?
Since we do not have the enforcement during instantiation of classes
derived from regular inheritance, why would someone use protocols? First
because it participates of static type checking. If we are passing an
object to a function that expects protocol `P` but the object do not
implement it, this will raise an error. Second because we can take
advantage of automatic documentation generation from code to have the
protocols documented.
```

#### Decision

Implement `Plugin` and `PluginFactory` as protocol.

#### Status

Done.

#### Consequences

##### Reduce of maintenance burden

We don't need to create a `word-def-plugin-core` package anymore. The
protocols would be declared in the `word-def` package.

##### Plugins depends on `word-def` package

At first glance it could sound weird that the `word-def` package, that
is extended by plugins, it itself a dependence of plugins. But that
does not pose a problem.

The plugins are registered at running time, so the `word-def` package
is independent and could be installed without any plugins.

There is one issue though. Let us assume there exist published plugins
A and B. A new version of `word-def` comes out (v2.0). This version does
some changes in the interface. The maintainer of Plugin A publishes a
new version to comply with the changes. The maintainer of B does not.

- Plugin A uses word-def (v2.0)
- Plugin B uses word-def (v1.0)

If in our machine we try to install the latest versions of both plugins,
it won't work because they have incompatible dependencies. The only
scenario in which we could have both is to keep v1.0 of `word-def`.

```{admonition} Incompatible dependency issue
This problem is also present in the design in which we have the `word-def-core`
package.
```

This is not ideal. We would like to have both plugins with their latest versions
installed and if any issue appear, simply signalize to the user that that particular
plugin cannot be used.

To solve that issue, the plugins should not specify the version of `word-def`
from which they depend on and let the package install manager (e.g. pip) to
handle that.

```{admonition} Checking version compatibility
It is always possible to check the plugin version and the word-def version. The
PluginFactory protocol specifies the method `version` and the api has the methods
`api_version` and `is_plugin_compatible` for that purpose.
```


### Plugin register mechanism

**Date: (2024-03-01)**


#### Context

We need a mechanism to register plugins such that `word-def`
can automatically identify and load these plugins at runtime.

**Using a decorator**

The first solution though was to use a decorator and share the
burden with the plugin creator. In this scenario, the plugin
creator would have to add the decorator `@register` above the
`PluginFactory` class.

```python
@model.register
class AdapterFactory:
    ...
```

However, we still need a way to automatically load the plugin
module at runtime. The second strategy allows us to do that
without putting any burden at the plugin creator.

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

In this design the plugins are obliged to be within
a fixed namespace. This namespace is `danoan.word_def.modules.plugins`.
The `word-def` package can only identify and load python modules that
are located within this namespace.

```python
def collect_modules():
        prefix = "danoan.word_def.plugins.modules"
        plugins_module = importlib.import_module(prefix)
        for module_info in pkgutil.iter_modules(
            plugins_module.__path__, prefix=f"{prefix}."
        ):
            yield importlib.import_module(module_info.name), module_info.name

```

The strongest point of this approach is automatic load. The user should
only install the plugin package to have access to its functionalities.

The drawback is the restriction to plugin creators to create their plugins
in a fixed namespace.

#### Decision

Use package introspection and python import system mechanism via importlib
to implement the plugin mechanism in `word-def`.

#### Status

Done.

#### Consequences

Plugin packages must be created within the namespace `danoan.word_def.modules.plugins`.


### Testing the plugin register mechanism

**Date: (2024-03-02)**

#### Context

The plugin mechanism is designed to search and load modules in a given namespace. To
test this mechanism we need to make the python import system to believe that is
a fake_test_plugin python module in such namespace.

Our solution is to create a decorator to wrap our test function around a context manager.
Within the context manager we create a temporary directory `T` and the directories
corresponding to our namespace. Finally, it is sufficient to add `T` to `sys.path` to
emulate the namespace at runtime in the python import system.

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

Wrap test functions around context manager to emulate the plugins namespace.

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
once by simple mentioning the language in the prompt. The language in this case is
a plugin parameter.

We did not like to change the `Plugin` neither the `PluginFactory` protocols, therefore,
we decided that multilanguage plugins will return an empty string for the `get_language`
method and that it is up to the `word-def` api to inform at runtime the language to which
the multilanguage plugin should operate on.

Every method of `word-def` API needs a language parameter. The language parameter is used
to find an available plugin to execute the task in the given language. Whenever the plugin
search is started, we make sure to wrap the multilanguage factory into a wrapper class
such that the calls of every method of the multilanguage factory is preserved, except
`get_language`, which is replaced by the language specified by the user.


#### Decision

- Allow multilanguage plugins.
- The empty string as return value of `get_method` indicates a multilanguage plugin.
- `word-def` API wraps the multilanguage factory and overwrites the `get_language` method
  appropriately.

#### Status

Done.

#### Consequences

None.
