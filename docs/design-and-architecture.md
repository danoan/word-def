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


### Context

A plugin is a python module that must have two classes:

1. One should implement the `Plugin` protocol.
2. The second one should implement the `PluginFactory` protocol.

The use of protocols gives us a loosely coupled object compared with
abstract classes and regular inheritance. The implementations above do
not need to inherit from any class, and that removes a dependency.

```{admonition} Abstract class If we use abstract classes we would have
to create a package to hold the abstract classes, e.g.
`word-def-plugin-core`. Using protocols allows us to reduce the number
of packages to maintain, since the protocols can be declared in the
`word-def` package. ```

```{admonition} Why to declare protocols? Since we do not have the
enforcement during instantiation of classes derived from regular
inheritance, why would someone use protocols? First because it
participates of static type checking. If we are passing an object to a
function that expects protocol `P` but the object do not implement it,
this will raise an error. Second because we can take advantage of
automatic documentation generation from code to have the protocols
documented. ```

### Decision

1. Implement `Plugin` and `PluginFactory` as protocol.

### Status

Done.

### Consequences

We don't need to create a `word-def-plugin-core` package anymore. The
protocols would be declared in the `word-def` package.
