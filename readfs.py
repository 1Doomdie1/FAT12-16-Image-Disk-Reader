from os                                         import system
from sys                                        import platform, argv
from shlex                                      import split
from rich                                       import print
from magic                                      import from_file
from rich.table                                 import Table
from src.managers.file                          import Reader
from src.filesystems.FAT.main_blocks.fat        import FAT
from src.filesystems.FAT.main_blocks.dir        import Dir
from src.filesystems.FAT.main_blocks.bootsector import Bootsector
from src.filesystems.FAT.parsers.hex            import Entry_Hex_Parser
if not from_file(argv[1]).startswith("DOS/MBR"): print("File is not a disk image."); exit()


ENTRY_HEX_PARSER = Entry_Hex_Parser()
EVIDENCE_FILE    = Reader(argv[1])
BOOTSECTOR       = Bootsector(EVIDENCE_FILE.read_bytes())
FAT_STRUCTURE    = FAT(EVIDENCE_FILE.read_bytes(BOOTSECTOR.fat_offset(), BOOTSECTOR.fat_size())).parse()
ROOT_DIRECTORY   = Dir(EVIDENCE_FILE.read_bytes(BOOTSECTOR.rd_offset(), BOOTSECTOR.rd_size()))
CL2_SECTOR       = (BOOTSECTOR.rd_offset() + BOOTSECTOR.rd_size()) // BOOTSECTOR.bytes_per_sector()

GLOBAL_PATH = ""
dir_data = ROOT_DIRECTORY
while True:
    cmd = split(input(f"{GLOBAL_PATH if GLOBAL_PATH else '/'}> "))
    if not cmd:
        continue
    elif cmd[0] in ("ls", "dir", "ll"):
        columns = ("Perms", "Name", "Type", "Size", "Status", "SCL", "SSE", "Created At", "Modified At", "Accessed At")
        table = Table()

        for column in columns:
            table.add_column(column, justify = "center")

        for entry in dir_data.entries():
            table.add_row(
                entry.perms(), 
                f"[yellow]{entry.name()}[/yellow]" if entry.type() == "Directory" else f"[cyan]{entry.name()}[/cyan]", 
                f"[yellow]{entry.type()}[/yellow]" if entry.type() == "Directory" else f"[cyan]{entry.type()}[/cyan]", 
                f"[green]{entry.size()}[/green]"   if entry.size() else f"[red3]{entry.size()}[/red3]", 
                f"[green]{entry.status()}[/green]" if entry.status() == "Present" else f"[red3]{entry.status()}[/red3]",
                f"{entry.cluster_chain(FAT_STRUCTURE)[0]}", 
                f"{entry.sector_chain(FAT_STRUCTURE, CL2_SECTOR, BOOTSECTOR.sectors_per_cluster())[0]}", 
                entry.created_at(),
                entry.written_at(),
                entry.accessed_at()
            )
        print(table)
    elif cmd[0] == "cd":
        if len(cmd) < 2: print(f"[red3]Missing pagams:[/red3] cd [PATH]"); continue
        path = cmd[1].split("/")
        tmp_dir_data, tmp_path, valid_path = dir_data, "", False

        for dir_name in path:
            entry = tmp_dir_data.get_entry(dir_name, ["Directory"])
            
            if entry:
                valid_path = True
                dir_sector = entry.sector_chain(FAT_STRUCTURE, CL2_SECTOR, BOOTSECTOR.sectors_per_cluster())[0]
                tmp_dir_data = Dir(EVIDENCE_FILE.read_bytes(dir_sector * BOOTSECTOR.bytes_per_sector(), BOOTSECTOR.bytes_per_sector() * 32))

                if dir_name == "..":
                    tmp_path = "/".join(GLOBAL_PATH.split("/")[:-1])
                    GLOBAL_PATH = ""
                elif dir_name != ".":
                    tmp_path += f"/{dir_name}"
            else:
                print(f"[red3]No such directory:[/red3] {dir_name}")
                valid_path = False
                break

        if valid_path:
            GLOBAL_PATH += tmp_path
            dir_data = tmp_dir_data
    elif cmd[0] == "chain":
        if len(cmd) < 3: print(f"[red3]Missing pagams:[/red3] chain [CHAIN_TYPE (cl|se|*)] [FILE]"); continue
        entry = dir_data.get_entry(cmd[2])
        if entry:
            
            cl_chain = entry.cluster_chain(FAT_STRUCTURE)
            se_chain = entry.sector_chain(FAT_STRUCTURE, CL2_SECTOR, BOOTSECTOR.sectors_per_cluster())
            
            table = Table()
            table.add_column("File", justify="center")

            if cmd[1] == "cl":
                table.add_column("Cluster Chain", justify="center")
                
                table.add_row(
                    entry.name(),
                    " ".join(f"{cl_chain[i:i+10]}\n" for i in range(0, len(cl_chain), 10))
                )
            elif cmd[1] == "se":
                table.add_column("Sector Chain", justify="center")

                table.add_row(
                    entry.name(),
                    " ".join(f"{se_chain[i:i+10]}\n" for i in range(0, len(se_chain),10)
                    )
                )
            elif cmd[1] in ("all", "*"):
                table.add_column("Cluster Chain", justify="center")
                table.add_column("Sector Chain",  justify="center")

                table.add_row(
                    entry.name(),
                    " ".join(f"{cl_chain[i:i+10]}\n" for i in range(0, len(cl_chain), 10)),
                    " ".join(f"{se_chain[i:i+10]}\n" for i in range(0, len(se_chain), 10))
                )
            else:
                print(f"[red3]Unknown CHAIN TYPE vlaue:[/red3] {cmd[1]}")
                continue
            print(table)
        else:
            print(f"[red3]No such file or directory:[/red3] {cmd[2]}")
    elif cmd[0] == "entry":
        if len(cmd) < 3: print(f"[red3]Missing pagams:[/red3] entry (FILE|DIR) (raw|hex)"); continue
        entry = dir_data.get_entry(cmd[1])
        if entry:
            raw = b"".join(entry.raw())
            if cmd[2] == "raw":
                print(raw)
            elif cmd[2] == "hex":
                entry_hex_data = ENTRY_HEX_PARSER.hex_view(raw)
                table = Table()
                
                table.add_column("Rel. Offset", justify="center")
                table.add_column("HEX",         justify="center")
                table.add_column("Decoded",     justify="center")
                
                for relative_offset, line in enumerate(entry_hex_data):
                    table.add_row(
                        f"[black]{'0' * (8 - len(hex(relative_offset * 16)[2:].rjust(1, '0')))}[/black][cyan]{hex(relative_offset * 16)[2:]}",
                        line[0],
                        line[1]
                    )

                print(table)
            else:
                print(f"[red3]Unknow param:[/red3] {cmd[2]}")
        else:
            print(f"[red3]No such file or directory:[/red3] {cmd[1]}")

    elif cmd[0] in ("pwd", "cwd"):
        print(GLOBAL_PATH if GLOBAL_PATH else "/")
    elif cmd[0] in ("cls", "clear"):
        if platform.startswith("win"):
            system("cls")
        else:
            system("clear")
    elif cmd[0] in ("help", "h", "?"):
        help_menu_lines = (
            #  Command             Argumnets            Description          
            ("help|h|?",      "",                     "Shows this help menu"                                 ),
            ("ls|ll|dir",     "",                     "Shows the contents of the current directory"          ),
            ("cd", "PATH",                            "Change directory"                                     ),
            ("clear|cls",     "",                     "Clears terminal"                                      ),
            ("cwd|pwd",       "",                     "Prints the full path to the current working directory"),
            ("chain",         "(cl|se|*) (FILE)",     "Display cluster chain or sector chain or both"        ),
            ("entry",         "(FILE/DIR) (hex|raw)", "Display entry bytes in hex or raw"                    ),
            ("exit|quit|e|q", "",                     "Closes session"                                       )
        )
        
        table = Table()
        table.add_column("Command",     justify="left"  )
        table.add_column("Params",      justify="center")
        table.add_column("Description", justify="left"  )
        
        for line in help_menu_lines:
            table.add_row(line[0], line[1], line[2])
        
        print(table)
    elif cmd[0] in ("exit", "quit", "q", "e"):
        print("[green]Bye![/green]")
        break
    else:
        print(f"[red3]Unknown command:[/red3] {cmd[0]}")
