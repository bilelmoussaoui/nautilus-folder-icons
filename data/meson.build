metafile = meson.project_name() + '.metainfo.xml'
i18n.merge_file(
  'appdata',
  input: metafile + '.in',
  output: metafile,
  po_dir: join_paths(meson.source_root(), 'po'),
  install: true,
  install_dir: join_paths(get_option('datadir'), 'metainfo')
)

# Validating the appdata file
appstream_util = find_program('appstream-util', required: false)
if appstream_util.found()
  test (
    'Validate appdata file',
    appstream_util,
    args: ['validate', '--nonet', join_paths(meson.current_build_dir (), metafile)]
  )
endif
