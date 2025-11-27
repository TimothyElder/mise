# Mise <img src='src/mise/assets/mise.png' align="right" height="138.5" /></a>

![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg) ![GitHub release](https://img.shields.io/github/v/release/TimothyElder/mise) [![macOS](https://img.shields.io/badge/macOS-000000?logo=apple&logoColor=F0F0F0)](#) [![Windows](https://custom-icon-badges.demolab.com/badge/Windows-0078D6?logo=windows11&logoColor=white)](#)

>For the professional, one's meez is an obsession, one's sword and shield, the only thing standing between you and chaos. If you have your meez right, it means you have your head together, you are "set up", stocked, organized, ready with everything you need and are likely to need for the tasks at hand.
<p align="right"/>Anthony Bourdain, <em>Le Halles Cookbook</em></p>

[Mise](https://en.wikipedia.org/wiki/Mise_en_place) is an open source qualitative data analysis tool that preserves all your data in open formats, emphasizes reproducibility of coding schemes, and is a no cost alternative to proprietary CAQDA software. It is designed to preserve the rich functionality of CAQDA software like atlas.ti or Dedoose while having no cost and a more straightforward design.

**Version:** 0.1.1 (Alpha)

**Status:** Early-stage, expect breaking changes.

**Supported OS:** macOS

[Changelog](CHANGELOG.md)

[License: GPLv3](LICENSE)

[Code of Conduct](CODE_OF_CONDUCT.md)

## Screenshots

### Welcome Widget — Create or open a project
![welcome-widget](/screenshots/welcome-widget.png)

### Project View — Import documents and manage code hierarchies
![project-view](/screenshots/project-view.png)

### Analysis View — Review coded segments and generate reports
![analysis-view](/screenshots/analysis-view.png)

## Installation

### macOS

1. Go to the [Releases page](https://github.com/TimothyElder/mise/releases).
2. Download the file named `Mise-0.1.1.dmg`.
3. Open the DMG and drag `Mise.app` into your Applications folder.
4. On first run, you may need to right-click → Open due to macOS Gatekeeper.

### Windows

1. Go to the [Releases page](https://github.com/TimothyElder/mise/releases).
2. Download the file named `Mise-0.1.1-setup.exe`.
3. Run the installer and follow the prompts.

### Install from source

On macOS you can install from source:

```sh
git clone https://github.com/TimothyElder/mise.git
cd mise
make install
make build-macos
# dist/Mise.app appears
```

## Usage

1. Create a new project or open an existing one.
2. Import documents (DOCX, TXT, Markdown).
3. Browse documents and open them in the viewer.
4. Manage and edit codes in the Code Manager.
5. Highlight and assign codes from your code system.
6. Generate segments and export reports for analysis.

## Road Map

### In progress
- Support for Windows and Linux
- PDF imports to project
- UI styling and size changes for legibility

### Planned
- Advanced reporting engine (PDF/DOCX)
- Memoing system with split document viewer
- Project versioning
- Alembic database versioning
- NLP in Analysis View + Code tree visualization
- Project API for extensibility

## Issue Reporting

Please report bugs, feature requests, or unexpected behavior through the 
[GitHub Issues](https://github.com/TimothyElder/mise/issues) page.

A good issue report includes:
- Operating system and Mise version
- Steps to reproduce the problem
- Expected behavior vs actual behavior
- Relevant screenshots or logs