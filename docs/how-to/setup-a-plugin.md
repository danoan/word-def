# How to setup a plugin

After installing the word-def plugin, it is likely the case you
should pass some values to configure it (e.g. API entrypoint and
secret key).

You can group the configuration of all your plugins in a single toml
file and then pass it to the `word-def` cli.

```bash
$ word-def --plugin-configuration-filepath plugin-config.toml get-definition happiness eng
```

The `word-def` cli will select a plugin for the specified language and then gather its configuration
from the `plugin-config.toml`. The `plugin-config.toml` should look to something similar to:

```toml
["danoan.word_def.plugins.modules.<MY_PLUGIN_MODULE>"]
config_key=config_value

["danoan.word_def.plugins.modules.<MY_PLUGIN_MODULE_2>"]
config_key=config_value
```
