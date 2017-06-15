project('nautilus-folder-icons',
  version: '1.2',
  meson_version: '>= 0.40.0'
)

i18n = import('i18n')

extension_dir = join_paths(get_option('datadir'), 'nautilus-python', 'extensions')

subdir('data')
subdir('po')

install_data(
  join_paths('src', meson.project_name() + '.py'),
  install_dir: extension_dir
)
