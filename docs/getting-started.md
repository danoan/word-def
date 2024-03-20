# Getting started with Word Definition

Get definition of words in any language.

The `word-def` package is an extensible library to get definition of words
in any language. It can be used as a library or as a command-line interface.

## Installation

```bash
# As a library
pip install word-def

# As a CLI
pipx install word-def
```

### Plugins available

- [Collins Dictionary English](https://github.com/danoan/word-def-plugin-english-collins/)


## Features

- `get-definition`
- `get-synonym`
- `get-pos-tag`
- `get-usage-examples`

## Examples

```bash
$ word-def get-definition joy eng
1. a deep feeling or condition of happiness or contentment
2. something causing such a feeling; a source of happiness
3. an outward show of pleasure or delight; rejoicing
4. success; satisfaction
5. to make joyful; gladden
```

You may need to specify a plugin configuration file if the plugin
requires extra parameters (e.g. credentials to access an API). You
can register such parameters in a toml file and pass it to `word-def`.

```toml
<!-- plugin-config.toml -->
["danoan.word_def.plugins.modules.english_collins"]
entrypoint = <ENTRYPOINT>
secret_key = <SECRET_KEY>
```

```bash
$ word-def --plugin-configuration-filepath plugin-config.toml get-definition joy eng
```

## Contributing

Please reference to our [contribution](http://danoan.github.io/word-def/contributing) and [code-of-conduct](http://danoan.github.io/word-def/code-of-conduct) guidelines.
