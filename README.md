# nautilus-folder-icons

Nautilus extension that makes changing folders icons easy!




## Screenshots

<div align="center"><img src="screenshots/screenshot1.png" alt="Preview" /></div>

## Shortcuts

- `Escape` To close the window
- `Return` To select the new folder icon
- `<Shift><Ctrl>S` To open the folder icon selector on the current folder


## Requirements:

### Running dependencies

- `python2`

#### For Nautilus :

- `nautilus-python`:
  - Archlinux : `python2-nautilus`

### Building dependencies

- `meson` >= `0.40.0`
- `ninja`

## How to install
### Manual installation

1- Install requirements

2- Clone the repository

```bash
git clone https://github.com/bil-elmoussaoui/nautilus-folder-icons
```

3- Build it!

```bash
cd nautilus-folder-icons
meson builddir --prefix=/usr
sudo ninja -C builddir install
```


4- Restart Nautilus

```bash
nautilus -q
```

## How to uninstall

```bash
sudo ninja -C builddir uninstall
```

## Contribute :

### Translations:

In order to generate the pot file, run the following commands:

```bash
meson builddir --prefix=/usr
ninja nautilus-icons-update-po                  
```

A `.pot` will be generated on `./po`
