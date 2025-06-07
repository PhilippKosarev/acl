# Jamming
from libjam import Drawer
drawer = Drawer()

HOME = drawer.get_home()

# Stores data
class Data:
  possible_ac_dirs = [
    f"{HOME}/.local/share/Steam/steamapps/common/assettocorsa",
    f"{HOME}/.var/app/com.valvesoftware.Steam/data/Steam/steamapps/common/assettocorsa",
    f"C:/Program Files (x86)/Steam/steamapps/common/assettocorsa",
  ]
  possible_steam_locations = [
    {'path': f"/usr/lib/steam/bin_steam.sh", 'command': None},
    {'path': f"{HOME}/.var/app/com.valvesoftware.Steam", 'command': 'flatpak run com.valvesoftware.Steam'},
    {'path': f"C:/Program Files (x86)/Steam/steam.exe", 'command': None},
  ]

  def get_ac_dir(self):
    AC_DIR = None
    for directory in self.possible_ac_dirs:
      if drawer.is_folder(directory):
        AC_DIR = directory
    return AC_DIR

  def get_steam_exec(self):
    STEAM_EXEC = None
    for info in self.possible_steam_locations:
      path = info.get('path')
      command = info.get('command')
      if drawer.is_file(path) is False:
        continue
      if command is None:
        command = path
      STEAM_EXEC = command
    return STEAM_EXEC
