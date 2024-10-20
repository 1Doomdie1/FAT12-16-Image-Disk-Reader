from os                                     import system
from sys                                    import platform, argv
from shlex                                  import split
from magic                                  import from_file
from colorama                               import init, Style, Fore
from prettytable                            import PrettyTable
from src.managers                           import FileReader
from src.filesystems.FAT.parsers.fat        import FAT
from src.filesystems.FAT.parsers.dirparser  import DirParser
from src.filesystems.FAT.parsers.bootsector import Bootsector
init()
if not from_file(argv[1]).startswith("DOS/MBR"): print("File is not a disk image."); exit()


EVIDENCE_FILE = FileReader(argv[1])
BOOTSECTOR = Bootsector(EVIDENCE_FILE.read_bytes())
FAT_STRUCTURE = FAT(EVIDENCE_FILE.read_bytes(BOOTSECTOR.fat_offset(), BOOTSECTOR.fat_size())).parse()
ROOT_DIRECTORY = DirParser(EVIDENCE_FILE.read_bytes(BOOTSECTOR.rd_offset(), BOOTSECTOR.rd_size()))
CL2_SECTOR = (BOOTSECTOR.rd_offset() + BOOTSECTOR.rd_size()) // BOOTSECTOR.bytes_per_sector()

GLOBAL_PATH = ""
dir_data = ROOT_DIRECTORY
while True:
    cmd = split(input(f"{GLOBAL_PATH if GLOBAL_PATH else '/'}> "))
    if not cmd:
        continue
    elif cmd[0] in ("ls", "dir", "ll"):
        table = PrettyTable(["Perms", "Name", "Type", "Size", "Deleted", "SCL", "SSE", "Created At", "Modified At", "Accessed At"])
        for entry in dir_data.entries():
            table.add_row((
                entry.perms(), 
                f"{Fore.YELLOW}{entry.name()}{Style.RESET_ALL}" if entry.type() == "Directory" else f"{Fore.CYAN}{entry.name()}{Style.RESET_ALL}", 
                f"{Fore.YELLOW}{entry.type()}{Style.RESET_ALL}" if entry.type() == "Directory" else f"{Fore.CYAN}{entry.type()}{Style.RESET_ALL}", 
                f"{Fore.GREEN}{entry.size()}{Style.RESET_ALL}" if entry.size() else f"{Fore.RED}{entry.size()}{Style.RESET_ALL}", 
                f"{Fore.GREEN}{entry.status()}{Style.RESET_ALL}" if entry.status() == "Present" else f"{Fore.RED}{entry.status()}{Style.RESET_ALL}",
                entry.cluster_chain(FAT_STRUCTURE)[0], 
                entry.sector_chain(FAT_STRUCTURE, CL2_SECTOR, BOOTSECTOR.sectors_per_cluster())[0], 
                entry.created_at(),
                entry.written_at(),
                entry.accessed_at()
            ))
        print(table)
    elif cmd[0] == "cd":
        if len(cmd) < 2: print(f"{Fore.RED}Missing pagams:{Style.RESET_ALL} cd [PATH]"); continue
        path = cmd[1].split("/")
        tmp_dir_data, tmp_path, valid_path = dir_data, "", False

        for dir_name in path:
            entry = tmp_dir_data.get_entry(dir_name, ["Directory"])
            
            if entry:
                valid_path = True
                dir_sector = entry.sector_chain(FAT_STRUCTURE, CL2_SECTOR, BOOTSECTOR.sectors_per_cluster())[0]
                tmp_dir_data = DirParser(EVIDENCE_FILE.read_bytes(dir_sector * BOOTSECTOR.bytes_per_sector(), BOOTSECTOR.bytes_per_sector() * 32))

                if dir_name == "..":
                    tmp_path = "/".join(GLOBAL_PATH.split("/")[:-1])
                    GLOBAL_PATH = ""
                elif dir_name != ".":
                    tmp_path += f"/{dir_name}"
            else:
                print(f"No such directory: {dir_name}")
                valid_path = False
                break

        if valid_path:
            GLOBAL_PATH += tmp_path
            dir_data = tmp_dir_data
    elif cmd[0] in ("exit", "quit", "q", "e"):
        print("Bye!")
        break
    elif cmd[0] == "chain":
        if len(cmd) < 3: print(f"{Fore.RED}Missing pagams:{Style.RESET_ALL} chain [CHAIN_TYPE (cl|se|*)] [FILE]"); continue
        entry = dir_data.get_entry(cmd[2])
        if entry:
            cl_chain = entry.cluster_chain(FAT_STRUCTURE)
            se_chain = entry.sector_chain(FAT_STRUCTURE, CL2_SECTOR, BOOTSECTOR.sectors_per_cluster())
            if cmd[1] == "cl":
                table = PrettyTable(("File", "Cluster Chain"))
                table.add_row((entry.name(), " ".join(f"{cl_chain[i:i+10]}\n" for i in range(0, len(cl_chain), 10))))
            elif cmd[1] == "se":
                table = PrettyTable(("File", "Sector Chain"))
                table.add_row((entry.name(), " ".join(f"{se_chain[i:i+10]}\n" for i in range(0, len(se_chain), 10))))
            elif cmd[1] in ("all", "*"):
                table = PrettyTable(("File", "Cluster Chain", "Sector Chain"))
                table.add_row((
                    entry.name(), 
                    " ".join(f"{cl_chain[i:i+10]}\n" for i in range(0, len(cl_chain), 10)),
                    " ".join(f"{se_chain[i:i+10]}\n" for i in range(0, len(se_chain), 10))
                ))
            else:
                print(f"{Fore.RED}Unknown CHAIN TYPE vlaue:{Style.RESET_ALL} {cmd[1]}")
                continue
            print(table)
        else:
            print(f"{Fore.RED}No such file or directory:{Style.RESET_ALL} {cmd[2]}")
    elif cmd[0] == "entry":
        if len(cmd) < 3: print(f"{Fore.RED}Missing pagams:{Style.RESET_ALL} entry (raw|hex) (FILE|DIR)"); continue
        entry = dir_data.get_entry(cmd[2])
        if entry:
            raw = b"".join(entry.raw())
            if cmd[1] == "raw":
                print(raw)
            elif cmd[1] == "hex":
                for i in range(0, len(raw), 16):
                    relative_offset = f"{Fore.CYAN}{hex(i)[2:].upper().rjust(8, '0')}{Style.RESET_ALL}"
                    hex_line = raw[i:i+16].hex(" ").upper()
                    decoded_hex = " ".join([ f"{Fore.MAGENTA}{chr(j)}{Style.RESET_ALL}" if 33 <= j <= 126 else "." for j in raw[i:i+16]])
                    print(f'| {relative_offset} | {hex_line} | {decoded_hex} |')
            else:
                print(f"{Fore.RED}Unknow param:{Style.RESET_ALL} {cmd[1]}")
        else:
            print(f"{Fore.RED}No such file or directory:{Style.RESET_ALL} {cmd[2]}")

    elif cmd[0] in ("pwd", "cwd"):
        print(GLOBAL_PATH if GLOBAL_PATH else "/")
    elif cmd[0] in ("cls", "clear"):
        if platform.startswith("win"):
            system("cls")
        else:
            system("clear")
    elif cmd[0] in ("help", "h", "?"):
        table = PrettyTable(("Command", "Args", "Description"))
        table.add_rows((
            ("help|h|?", "", "Shows this help menu"),
            ("ls|ll|dir", "", "Shows the contents of the current directory"),
            ("cd", "PATH", "Change directory"),
            ("clear|cls", "", "Clears terminal"),
            ("cwd|pwd", "", "Prints the full path to the current working directory"),
            ("chain", "(cl|se|*) (FILE)", "Display cluster and sector or both chains"),
            ("entry", "(hex|raw) (FILE/DIR)", "Display entry (file or directory) bytes"),
            ("exit|quit|e|q", "", "Closes session")
        ))
        print(table)
    else:
        print(f"{Fore.RED}Unknown command:{Style.RESET_ALL} {cmd[0]}")
