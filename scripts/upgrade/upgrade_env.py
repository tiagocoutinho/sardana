""" This serves to upgrade MacroServer environment from Python 2 to Python 3:

IMPORTANT:
1. IT HAS TO BE USED WITH PYTHON 2.7!!!
2. CONDA python 2 package is missing the standard dbm package so this
   script will fail inside a conda python 2 environment
3. a new env file with an additional .db extension will be created. You
   should **NOT** change the macroserver EnvironmentDb property. The dbm
   will figure out automatically the file extension
4. a backup will of the original environment will be available with th
   extension .py2

Usage: python upgrade_env.py <ms_dev_name|ms_dev_alias>
"""
import sys
import os
import shelve
import dbm
import contextlib

import PyTango

assert sys.version_info[:2] == (2, 7), "Must run with python 2.7"

DefaultEnvBaseDir = "/tmp/tango"
DefaultEnvRelDir = "%(ds_exec_name)s/%(ds_inst_name)s/macroserver.properties"


def get_ms_properties(ms_name, ms_ds_name):
    db = PyTango.Database()
    prop = db.get_device_property(ms_name, "EnvironmentDb")
    ms_properties = prop["EnvironmentDb"]
    if not ms_properties:
        dft_ms_properties = os.path.join(
            DefaultEnvBaseDir,
            DefaultEnvRelDir)
        ds_inst_name = ms_ds_name.split("/")[1]
        ms_properties = dft_ms_properties % {
            "ds_exec_name": "MacroServer",
            "ds_inst_name": ds_inst_name}
    else:
        ms_properties = ms_properties[0]
    ms_properties = os.path.normpath(ms_properties)
    return ms_properties


def dbm_shelve(filename, flag="c"):
    # NOTE: dbm appends '.db' to the end of the filename
    return shelve.Shelf(dbm.open(filename, flag))


def migrate_file(filename):
    assert not filename.endswith('.db'), \
        "Cannot migrate '.db' (It would be overwritten)"
    with contextlib.closing(shelve.open(filename)) as src_db:
        data = dict(src_db)
    with contextlib.closing(dbm_shelve(filename)) as dst_db:
        dst_db.update(data)
    os.rename(filename, filename + '.py2')


def upgrade_env(ms_name):
    db = PyTango.Database()
    ms_info = db.get_device_info(ms_name)
    ms_ds_name = ms_info.ds_full_name

    env_filename = get_ms_properties(ms_name, ms_ds_name)
    migrate_file(env_filename)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("python upgrade_env.py <ms_dev_name|ms_dev_alias>")  # noqa
        sys.exit(1)
    ms_name = sys.argv[1]
    upgrade_env(ms_name)