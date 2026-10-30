# Thiago's simple desktop launcher
![image](https://github.com/thiagolopes/dialog_xsessions/assets/5994972/e95da4a2-ee9d-4351-86e9-1360cb2344b3)

## About
Start any desktop environment installed in the system. X11 and Wayland.

This script is not a complete display manager like GDM. Use logind to manage login (PAM).

## Run
You can use in `.bashrc`|`.zshrc` to run when logging to TTY1
```sh
if [[ -z "$DISPLAY" ]] && [[ $(tty) = /dev/tty1 ]]; then
    DP_PATH="$(python ~/.display_manager.py)"
    echo "Executing: $DP_PATH"
    eval "$DP_PATH"
fi
```

- python 3.10>=
- dialog (optional)

References:

[What is a Display Manager?](https://freedesktop.org/wiki/Software/LightDM/Design/)

[tbsm](https://loh-tar.github.io/tbsm/)
