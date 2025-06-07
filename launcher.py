# Imports
import psutil, subprocess, psutil, time

# Jamming
from libjam import Drawer, Clipboard, Typewriter
drawer = Drawer()
clipboard = Clipboard()
typewriter = Typewriter()

# Shorthand vars
AC_PROCESSES = ['AssettoCorsa.ex', 'AssettoCorsa.exe', 'acs.exe', 'AC: main thread']
STEAM_PROCESSES = ['steam', 'steam.exe']

# Helper functions
def is_process_running(process_list: list):
  for process in psutil.process_iter(['name']):
    for item in process_list:
      if process.info['name'] == item:
        return True
  return False
# Batch renames a list of tuples of files
def batch_rename(directory: str, renames: list, reverse = False):
  if reverse:
    renames.reverse()
  for pair in renames:
    if reverse: old = pair[1]; new = pair[0]
    else:       old = pair[0]; new = pair[1]
    try:
      drawer.rename(directory, old, new)
    except:
      return False
  return True

# Responsible for launching AC
class Launcher:

  def __init__(self, AC_DIR: str, STEAM_EXEC: str, original_launcher=False):
    self.AC_DIR = AC_DIR
    self.STEAM_EXEC = STEAM_EXEC
    self.original_launcher = original_launcher


  def kill_ac(self):
    for process in psutil.process_iter():
      for item in AC_PROCESSES:
        if process.name() == item:
          process.kill()
          return 0
    return 1


  def launch_ac_via_steam(self,
    on_ac_started, on_ac_stopped,
    on_steam_not_running, on_renaming_error,
    on_already_running
  ):
    # Renaming files before/after execution so Steam launches the desired executable
    def do_renames(reverse=False):
      # Which files to rename
      original_launcher_renames = [
        ('AssettoCorsa.exe', 'AssettoCorsa.old'),
        ('AssettoCorsa_original.exe', 'AssettoCorsa.exe'),
      ]
      renames = [
        ('AssettoCorsa.exe', 'AssettoCorsa.old'),
        ('acs.exe', 'AssettoCorsa.exe'),
      ]
      ac_files = drawer.get_files(self.AC_DIR)
      if self.original_launcher:
        if drawer.is_file(f"{self.AC_DIR}/AssettoCorsa_original.exe"):
          return batch_rename(self.AC_DIR, original_launcher_renames, reverse)
      else:
        return batch_rename(self.AC_DIR, renames, reverse)
    # Checking if steam is running
    if is_process_running(STEAM_PROCESSES) is False:
      on_steam_not_running()
    elif is_process_running(AC_PROCESSES) is True:
      on_already_running()
      return

    if do_renames() is False:
      return on_renaming_error()

    # Starting AC
    subprocess.run([self.STEAM_EXEC, 'steam://rungameid/244210'])

    try:
      # Waiting until AC starts
      while True:
        if is_process_running(AC_PROCESSES) is True:
          break
        time.sleep(0.1)
      on_ac_started()
      time.sleep(1)
    except KeyboardInterrupt:
      if do_renames(True) is False:
        return on_renaming_error()
    # Waiting until AC stops
    try:
      while True:
        if is_process_running(AC_PROCESSES) is False:
          break
        time.sleep(0.1)
      on_ac_stopped()
    except KeyboardInterrupt:
      if is_process_running(AC_PROCESSES):
        typewriter.print('Stopping Assetto Corsa.')
        self.kill_ac()

    if do_renames(True) is False:
      return on_renaming_error()

    return 0

  # asks steam to validate ac files
  def validate_ac_files(self, on_steam_not_running):
    # Checking if steam is running
    if is_process_running(STEAM_PROCESSES) is False:
      on_steam_not_running()
      return
    # Running validation
    subprocess.run([self.STEAM_EXEC, 'steam://validate/244210'])

  def check_files(self, on_ac_dir, on_steam_exec):
    # Checking AC dir
    if self.AC_DIR is None:
      on_ac_dir()
      return
    if drawer.is_folder(self.AC_DIR) is False:
      on_ac_dir()
      return
    # Checking steam exec
    if self.STEAM_EXEC is None:
      on_steam_exec()
      return
    if self.STEAM_EXEC.startswith('/'):
      if drawer.is_file(self.STEAM_EXEC) is False:
        on_steam_exec()
        return
