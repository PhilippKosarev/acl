# Imports
import psutil, subprocess, psutil, time
from libjam import Drawer, Clipboard, Typewriter

# Jam objects
drawer = Drawer()
clipboard = Clipboard()
typewriter = Typewriter()

AC_PROCESSES = ['AssettoCorsa.ex', 'AssettoCorsa.exe', 'acs.exe', 'AC: main thread']
STEAM_PROCESSES = ['steam']

# Helper functions
def is_process_running(process_list: list):
  for process in psutil.process_iter(['name']):
    for item in process_list:
      if process.info['name'] == item:
        return True
  return False

# Responsible for launching AC
class ACLauncher:
  def __init__(self, config: dict, options=None):
    self.AC_DIR = config.get('paths').get('AC_DIR')
    self.STEAM_EXEC = config.get('paths').get('STEAM_EXEC')
    self.options = options
  
  def kill_ac(self):
    for process in psutil.process_iter():
      for item in AC_PROCESSES:
        if process.name() == item:
          process.kill()
          return 0
    return 1

  def launch_ac_via_steam(
    self,
    on_ac_started, on_ac_stopped,
    on_steam_not_running, on_renaming_error,
    on_already_running,
  ):
    # Renaming files before execution so Steam launches the desired executable
    def prepare_files_for_execution(ac_files):
      try:
        if self.options.get('original').get('enabled'):
          original_launcher = clipboard.match_suffix(ac_files, 'AssettoCorsa_original.exe')
          if len(original_launcher) == 1:
            drawer.rename(self.AC_DIR, 'AssettoCorsa.exe', 'AssettoCorsa.old')
            drawer.rename(self.AC_DIR, 'AssettoCorsa_original.exe', 'AssettoCorsa.exe')
        else:
          drawer.rename(self.AC_DIR, 'AssettoCorsa.exe', 'AssettoCorsa.old')
          drawer.rename(self.AC_DIR, 'acs.exe', 'AssettoCorsa.exe')
        return True
      except:
        return False
    # Renaming files back to their original filenames
    def reset_filenames(ac_files):
      try:
        if self.options.get('original').get('enabled'):
          original_launcher = clipboard.match_suffix(ac_files, 'AssettoCorsa_original.exe')
          if len(original_launcher) == 1:
            drawer.rename(self.AC_DIR, 'AssettoCorsa.exe', 'AssettoCorsa_original.exe')
            drawer.rename(self.AC_DIR, 'AssettoCorsa.old', 'AssettoCorsa.exe')
        else:
          drawer.rename(self.AC_DIR, 'AssettoCorsa.exe', 'acs.exe')
          drawer.rename(self.AC_DIR, 'AssettoCorsa.old', 'AssettoCorsa.exe')
        return True
      except:
        return False

    # Checking if steam is running
    if is_process_running(STEAM_PROCESSES) is False:
      on_steam_not_running()
    elif is_process_running(AC_PROCESSES) is True:
      on_already_running()
      return

    ac_files = drawer.get_files(self.AC_DIR)
    successful = prepare_files_for_execution(ac_files)
    if successful is False:
      on_renaming_error()
      return

    # Starting AC
    subprocess.run([self.STEAM_EXEC, 'steam://rungameid/244210'])
    time.sleep(2)

    # Waiting until AC starts
    while True:
      if is_process_running(AC_PROCESSES) is True:
        break
      time.sleep(0.1)
    on_ac_started()
    time.sleep(1)
    # Waiting until AC stops
    try:
      while True:
        if is_process_running(AC_PROCESSES) is False:
          break
        time.sleep(0.1)

      if on_ac_stopped is not None:
        on_ac_stopped()

    except KeyboardInterrupt:
      if is_process_running(AC_PROCESSES):
        typewriter.print('Stopping Assetto Corsa.')
        self.kill_ac()

    successful = reset_filenames(ac_files)
    if successful is False:
      on_renaming_error()
      return

    return 0

  def validate_ac_files(self, on_steam_not_running):
    # Checking if steam is running
    if is_process_running(STEAM_PROCESSES) is False:
      on_steam_not_running()
      return
    # Running validation
    subprocess.run([self.STEAM_EXEC, 'steam://validate/244210'])
