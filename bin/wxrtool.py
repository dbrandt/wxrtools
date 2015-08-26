#!/usr/bin/env python
import importlib
from wxrtools.app import app


def resolve_handler(handler_name):
    mod, cls = handler_name.rsplit(".", 1)
    return getattr(importlib.import_module(mod), cls)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--handler", help="import path for handler class",
                        default="wxrtools.app.PrintHandler")
    parser.add_argument("wxr_file", nargs=1, help="WordPress export file")

    args = parser.parse_args()

    app(args.wxr_file.pop(), resolve_handler(args.handler))
