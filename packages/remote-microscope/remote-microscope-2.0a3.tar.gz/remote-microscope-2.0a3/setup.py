#! /usr/bin/env python
from distutils.core import setup, Extension

setup(name="remote-microscope",
      version="2.0a3",
      description="Remotely-controllable microscope.",
      author="The MEMS Exchange",
      author_email="microscope-feedback@mems-exchange.org",
      url="http://www.mems-exchange.org/software/microscope/",

      packages = ["mems.instrument",
                  "mems.instrument.hardware", "mems.instrument.server",
                  ],
      package_dir = {"mems.instrument": "."},

      scripts=['scripts/microscoped', 'scripts/start-microscope']
     )

