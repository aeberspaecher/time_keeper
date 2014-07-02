#!/usr/bin/env python
#-*- coding:utf-8 -*-

top = "."
out = "build"


def options(opt):
    opt.load("python")


def configure(conf):
    conf.load("python")
    conf.check_python_version((2, 4))  # TODO: which version do we need here?


def build(bld):
    bld(features="py", source=["time_keeper/_time_keeper.py", "time_keeper/__init__.py"],
        install_path="${PYTHONDIR}/time_keeper")

    bld.install_as("${PREFIX}/bin/tk", "time_keeper/tk.py",
                   chmod=0o755)

    # TODO: install tk.py
