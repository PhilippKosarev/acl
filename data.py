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

  def get_ac_dir(self):
    AC_DIR = None
    for directory in self.possible_ac_dirs:
      if drawer.is_folder(directory):
        AC_DIR = directory
    return AC_DIR
