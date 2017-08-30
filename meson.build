project('nautilus-folder-icons',
  version: '2.1',
  meson_version: '>= 0.40.0',
  default_options: [
    'prefix=/usr'
  ],
  license: 'GPL-3.0'
)

i18n = import('i18n')

file_manager = get_option('file_manager')
if file_manager == 'nautilus'
  package     = 'nautilus-folder-icons'
  destination = 'nautilus-python'
  filename    = 'nautilus-folder-icons.py'
  message('File Manager: Nautilus')
elif file_manager == 'nemo'
  package     = 'nemo-folder-icons'
  destination = 'nemo-python'
  filename    = 'nemo-folder-icons.py'
  message('File Manager: Nemo')
endif

extension_dir = join_paths(get_option('prefix'),
                           get_option('datadir'), destination, 'extensions')
pkgdata_dir   = join_paths(get_option('prefix'),
                           get_option('datadir'), package)

subdir('data')
subdir('po')

install_data(
  [
    join_paths('src', 'folder-icons', 'icons_select.py'),
    join_paths('src', 'folder-icons', 'icons_utils.py')
  ],
  install_dir: pkgdata_dir
)

# Configuration params
conf = configuration_data()
conf.set('DATA_DIR', pkgdata_dir)

configure_file(
  input: join_paths('src', file_manager, filename + '.in'),
  output: filename,
  configuration: conf,
  install_dir: extension_dir
)
