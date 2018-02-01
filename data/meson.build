metafile = meson.project_name() + '.metainfo.xml'
i18n.merge_file(
  input: metafile + '.in',
  output: metafile,
  po_dir: join_paths(meson.source_root(), 'po'),
  install: true,
  install_dir: join_paths(get_option('datadir'), 'metainfo')
)

# Validating the appdata file
appstreamcli = find_program(['appstreamcli', 'appstream-util'], required: false)
if appstreamcli.found()
  test (
    'Validate appdata file',
    appstreamcli,
    args: ['validate', join_paths(meson.current_build_dir (), metafile)]
  )
endif
