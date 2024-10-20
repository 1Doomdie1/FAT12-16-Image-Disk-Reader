# Instalation
After cloning the repo make sure you install the requirements
```bash
pip install -r requirements
```

# How to run

You will need to provide a FAT12/16 logical disk image created with, preferably, FTK Imager or dd.

```
python3 readfs.py path/to/file
```

This will create an interactive session which will give you access to the root directory of the disk image. From there you have access to a bunch of commands. To see a list of all the available commands please run the following command:

```
/> ?

+---------------+----------------------+-------------------------------------------------------+
|    Command    |         Args         |                      Description                      |
+---------------+----------------------+-------------------------------------------------------+
|    help|h|?   |                      |                  Shows this help menu                 |
|   ls|ll|dir   |                      |      Shows the contents of the current directory      |
|       cd      |         PATH         |                    Change directory                   |
|   clear|cls   |                      |                    Clears terminal                    |
|    cwd|pwd    |                      | Prints the full path to the current working directory |
|     chain     |   (cl|se|*) (FILE)   |       Display cluster and sector or both chains       |
|     entry     | (hex|raw) (FILE/DIR) |        Display entry (file or directory) bytes        |
| exit|quit|e|q |                      |                     Closes session                    |
+---------------+----------------------+-------------------------------------------------------+
```

Ok let's run the `ls` command and see it's output

![ls output](assets/ls_output.png)

Ok, now let's change directories (`cd`) and then use the `ls`

![cd and ls](assets/cd_ls.png)

# What's next?
- Improve session commands usability
- Code cleanup and documentation
- Adding new forensic features

# How to contribute?
Please, by all means, open issues and create PRs.<br>
I am also inclined to listen to feedback over on Discord. Here is my username: `doomdie`