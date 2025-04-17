from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Collect all submodules of scipy
hiddenimports = collect_submodules('scipy')

# Collect data files of scipy.special
datas = collect_data_files('scipy.special')