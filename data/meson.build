gnome = import('gnome')

metafile = meson.project_name() + '.metainfo.xml'
i18n.merge_file(
  input: metafile + '.in',
  output: metafile,
  po_dir: '../po',
  install: true,
  install_dir : join_paths(get_option('datadir'), 'metainfo')
)
