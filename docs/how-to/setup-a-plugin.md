# How to setup a plugin

After installing the plugin, you may need to pass some configuration values
(e.g. API entrypoint and secret key).

You can group the configuration for all your plugins in a single configurationML
file and then pass it to the `word-def` CLI.

```bash
$ word-def --plugin-configuration-filepath plugin-config.toml get-definition happiness eng
```

The `word-def` CLI will select a plugin for the specified language and gather its configuration
from the `plugin-config.toml`. The `plugin-config.toml` should look something like this:

```toml
["danoan.word_def.plugins.modules.<MY_PLUGIN_MODULE>"]
config_key=config_value

["danoan.word_def.plugins.modules.<MY_PLUGIN_MODULE_2>"]
config_key=config_value
```
