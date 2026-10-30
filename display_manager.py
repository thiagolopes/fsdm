#!/usr/bin/python3
"""
This script generate a output to execute a Desktop Environment (DE) - with Xorg and Wayland Support.

author: Thiago Lopes (TLP)
e-mail: thiagolopes at protonmail dot com

---

Copyright (C) 2023 - Thiago Lopes

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
import argparse
import configparser
import os
import shutil
import subprocess
import sys
import tempfile
from collections import OrderedDict

X11_PATH = "/usr/share/xsessions"
XORG_CMD_FMT = "XDG_SESSION_TYPE=x11 startx {cmd} -- -nolisten tcp"

WAYLAND_PATH = "/usr/share/wayland-sessions"
WAYLAND_CMD_FMT = "XDG_SESSION_TYPE=wayland {cmd}"


class DialogMenu:
    """
    A class for creating and displaying a dialog menu using the 'dialog' command-line tool.
    """
    DIALOG_CMD = "dialog"

    def __init__(self, title, header, width, height, lines=0):
        if not shutil.which(self.DIALOG_CMD):
            raise FileNotFoundError(f"{self.DIALOG_CMD=} not found")
        self.cmd = f"{self.DIALOG_CMD};--title;{title};--menu;{header};{height};{width};{lines}".split(";")

    def enumarate_options(self, options):
        return [str(item) for n, i in enumerate(options) for item in (n, i)]

    def ask(self, options):
        temp_output = tempfile.TemporaryFile()
        enumarated_options = self.enumarate_options(options)

        subprocess.run(
            self.cmd + enumarated_options,
            stderr=temp_output, stdout=sys.stderr, check=True,
        )

        temp_output.seek(0)
        resp = int(temp_output.read())
        temp_output.close()
        return resp


BOLDIT = "\033[1m{}\033[0m"


class TextMenu:
    def __init__(self, title, header):
        self.title = title
        self.header = header

    def print(self, msg, new_line=True):
        sys.stderr.write(msg)
        if new_line:
            sys.stderr.write("\n")
        sys.stderr.flush()

    def input(self, msg):
        self.print(msg, False)
        return input()

    def ask(self, options):
        s = 36
        self.print("-" * s)
        self.print(self.title)
        self.print("-" * s)
        for i, option in enumerate(options):
            self.print(BOLDIT.format(i) + "\t" + option)
        self.print("-" * s)
        while True:
            choice = self.input(BOLDIT.format("Choice: "))
            try:
                # validate if choice is int, if not will raise ValueError
                choice = int(choice)
                # validate if choice has entry, if not will raise IndexError
                options[choice]
                break
            except ValueError:
                self.print("Only numbers")
            except IndexError:
                self.print(f"{choice} is not valid option, only 0 - {len(options) - 1}")
        return choice


class DesktopParser:
    cp = configparser.ConfigParser()

    def read(self, file_path):
        self.cp.read(file_path)
        humable_name = self.cp["Desktop Entry"]["Name"]
        executable_name = self.cp["Desktop Entry"]["Exec"]
        return humable_name, shutil.which(executable_name) or executable_name


if __name__ == "__main__":
    x11_sessions_files = [f"{X11_PATH}/{f}" for f in os.listdir(X11_PATH)]
    wayland_files = [f"{WAYLAND_PATH}/{f}" for f in os.listdir(WAYLAND_PATH)]
    # TODO exit is no desktop found

    all_sessions = {}
    dp = DesktopParser()
    for x11_file in x11_sessions_files:
        x11_humable_name, x11_executable = dp.read(x11_file)
        all_sessions[x11_humable_name] = XORG_CMD_FMT.format(cmd=x11_executable)
    for way_file in wayland_files:
        way_humable_name, way_executable = dp.read(way_file)
        all_sessions[way_humable_name] = WAYLAND_CMD_FMT.format(cmd=way_executable)

    sessions_entries = OrderedDict(sorted(all_sessions.items(), key=lambda k: str.casefold(k[0])))
    sessions_names = list(sessions_entries.keys())

    arg_parse = argparse.ArgumentParser()
    arg_parse.add_argument("--dialog", action="store_true")
    args = arg_parse.parse_args()

    program_prompt = ("FSDM", "Select the desktop:")

    fallback = False
    if args.dialog:
        try:
            dialog_menu = DialogMenu(*program_prompt, 60, 10)
            index_result = dialog_menu.ask(sessions_names)
        except FileNotFoundError:
            print("[{}] dialog not found.".format(BOLDIT.format("error")))
            fallback = True
    if fallback or not args.dialog:
        text_menu = TextMenu(*program_prompt)
        index_result = text_menu.ask(sessions_names)

    cmd_result = sessions_entries[sessions_names[index_result]]
    print(cmd_result, flush=True)  # stdout
