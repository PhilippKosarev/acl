# Imports
from libjam import drawer, clipboard, typewriter
import psutil, subprocess, time

# Internal imports
from .data import data

# Helper functions
def is_process_running(requested_process: str) -> bool:
  if requested_process not in data.get('process_names'):
    raise NotImplementedError(f"Process names for '{requested_process}' not defined.")
  requested_process_names = data.get('process_names').get(requested_process)
  for process in psutil.process_iter(['name']):
    for item in requested_process_names:
      if process.info['name'] == item:
        return True
  return False

def kill_process(requested_process: str):
  if requested_process not in data.get('process_names'):
    raise NotImplementedError(f"Process names for '{requested_process}' not defined.")
  requested_process_names = data.get('process_names').get(requested_process)
  for process in psutil.process_iter(['name']):
    for item in requested_process_names:
      if process.info['name'] == item:
        process.kill()
        return True
  return False

# Batch renames a list of tuples of files
def batch_rename(directory: str, renames: list, reverse: bool = False):
  if reverse:
    renames.reverse()
  for pair in renames:
    if reverse:
      old = pair[1]; new = pair[0]
    else:
      old = pair[0]; new = pair[1]
    drawer.rename(directory, old, new)

# Custom exceptions
class SteamNotRunningError(Exception):
  pass
class RenamingError(Exception):
  pass
class AlreadyRunningError(Exception):
  pass

# Assetto Corsa launcher.
class Launcher:

  def kill_ac(self):
    return kill_process('ac')

  # A very hacky method, but better than nothing.
  def launch_ac_via_steam(self,
    AC_DIR: str,
    on_ac_started: callable = None,
    on_ac_stopped: callable = None,
  ):
    # Checking running processes
    if not is_process_running('steam'):
      raise SteamNotRunningError()
    if is_process_running('ac'):
      raise AlreadyRunningError()
    # Checking AC_DIR
    if not drawer.exists(AC_DIR):
      raise FileNotFoundError(f"Specified directory to AC ('{AC_DIR}') does not exist.")
    # Checking and renaming ac executables
    renames = data.get('steam-launch-renames')
    def do_renames(reverse: bool = False):
      local_renames = renames
      if reverse:
        local_renames = tuple(reversed(local_renames))
      for pair in local_renames:
        # Getting filenames
        original_file = pair[int(reverse)]
        renamed_file = pair[int(not reverse)]
        # Getting full paths
        original_path = f"{AC_DIR}/{original_file}"
        renamed_path = f"{AC_DIR}/{renamed_file}"
        # print(renamed_path)
        # Checking files
        if drawer.is_file(original_path) and drawer.is_file(renamed_path):
          print(f"Attempted to rename '{original_file}' to '{renamed_file}', but both already exist in '{AC_DIR}'")
          raise RenamingError(
            f"Attempted to rename '{original_file}' to '{renamed_file}', but both already exist in '{AC_DIR}'"
          )
        if drawer.is_file(renamed_path):
          drawer.rename(AC_DIR, renamed_file, original_file)
        if not drawer.is_file(original_path):
          raise RenamingError(
            f"The Assetto Corsa's executable file at '{original_path}' does not exist."
          )
        # Renaming after passing all checks
        drawer.rename(AC_DIR, original_file, renamed_file)
    # Doing the stuff
    do_renames()
    try:
      # Starting AC
      drawer.open('steam://rungameid/244210', is_path=False)
      # Waiting until AC starts
      while True:
        if is_process_running('ac'):
          break
        time.sleep(0.1)
      # After AC starts
      on_ac_started()
      # Waiting until AC stops
      while True:
        if not is_process_running('ac'):
          break
        time.sleep(0.1)
      # After AC stops
      on_ac_stopped()
    finally:
      do_renames(reverse=True)

  # Asks steam to validate Assetto Corsa's files.
  def validate_ac_files(self, AC_DIR: str):
    # Cleaning up the trash leftover by the program
    renames = data.get('steam-launch-renames')
    for old_filename, new_filename in renames:
      old_file = f"{AC_DIR}/{old_filename}"
      new_file = f"{AC_DIR}/{new_filename}"
      old_exists = drawer.is_file(old_file)
      new_exists = drawer.is_file(new_file)
      if old_exists and new_exists:
        drawer.delete_file(new_file)
      elif new_exists:
        drawer.rename(AC_DIR, new_filename, old_filename)
    # Asking steam to validate AC
    if is_process_running('steam'):
      return drawer.open('steam://validate/244210', is_path=False)
    else:
      raise SteamNotRunningError()
