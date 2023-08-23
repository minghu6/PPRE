from py2exe import freeze

options = {
      'bundle_files': 3,
      "verbose": 4,
      'includes': ['PyQt6.sip']
}

freeze(
      windows=['ppre.py'],
      data_files=[('', ['PPRE.ico'])],
      options=options
)