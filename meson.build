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


# Run tests
python = find_program(['python3', 'python'], required: false)
if python.found()
  test_files = ['test_code_format.py', 'test_utils.py']

  foreach test_file : test_files
    test (
      'Running unittests' + test_file,
      python,
      args: [join_paths(meson.source_root(), 'tests', test_file)]
    )
  endforeach

endif



install_data(
  [
    'src/widgets.py',
    'src/utils.py'
  ],
  install_dir: pkgdata_dir
)

# Configuration params
conf = configuration_data()
conf.set('DATA_DIR', pkgdata_dir)
conf.set('GETTEXT', meson.project_name())
conf.set('FILE_MANAGER', file_manager)

configure_file(
  input: 'src/folder-icons.py.in',
  output: 'folder-icons.py',
  configuration: conf,
  install_dir: extension_dir
)
