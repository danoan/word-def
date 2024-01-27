from danoan.word_def.core import api
from danoan.word_def.plugins import example


def main():
    api.get_adapter("sss")
    return 0
    adapter = example.Adapter(example.Configuration("entrypoint", "secret_key"))
    defs = adapter.get_definition("sadness")
    print(defs)


if __name__ == "__main__":
    main()
