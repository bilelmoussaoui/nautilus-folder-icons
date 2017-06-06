project('nautilus-icons',
  version: '1.0',
  meson_version: '>= 0.40.0'
)


i18n = import('i18n')
pkgdata_dir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
extension_dir = join_paths(get_option('datadir'), 'nautilus-python', 'extensions')

subdir('data')
subdir('po')

install_subdir('src', install_dir: pkgdata_dir)

# Configuration params
conf = configuration_data()
conf.set('DATADIR', pkgdata_dir)
conf.set('PROJECT', meson.project_name())


install_data(
    'src/nautilus-icons.py',
    install_dir: extension_dir
)
