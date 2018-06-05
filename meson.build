project('com.github.bilelmoussaoui.nautilus-folder-icons',
  version: '2.2',
  meson_version: '>= 0.40.0',
  default_options: [
    'prefix=/usr'
  ],
  license: 'GPL-3.0'
)

i18n = import('i18n')

file_manager = get_option('file_manager')
if file_manager == 'nautilus'
  destination = 'nautilus-python'
  message('File Manager: Nautilus')
elif file_manager == 'nemo'
  destination = 'nemo-python'
  message('File Manager: Nemo')
endif

extension_dir = join_paths(get_option('prefix'),
                           get_option('datadir'), destination, 'extensions')
pkgdata_dir   = join_paths(get_option('prefix'),
                           get_option('datadir'), meson.project_name())

subdir('data')
subdir('po')

install_data(
  [
    'src/icons_select.py',
    'src/icons_utils.py'
  ],
  install_dir: pkgdata_dir
)

# Configuration params
conf = configuration_data()
conf.set('DATA_DIR', pkgdata_dir)
conf.set('GETTEXT', meson.project_name())
conf.set('FILE_MANAGER', file_manager)

configure_file(
  input: join_paths('src/folder-icons.py.in'),
  output: 'folder-icons.py',
  configuration: conf,
  install_dir: extension_dir
)
