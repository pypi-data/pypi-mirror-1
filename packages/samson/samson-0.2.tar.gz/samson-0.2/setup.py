# samson - curl helpers.
#
#       http://github.com/davidreynolds/samson
#
# Copyright 2009 David Reynolds
#
# Use and distribution licensed under the MIT license. See
# the LICENSE file for full text.

import distutils.core

distutils.core.setup(
    name="samson",
    version="0.2",
    packages=["samson", "samson.tests"],
    author="David Reynolds",
    author_email="david@alwaysmovefast.com",
    url="http://github.com/davidreynolds/samson",
    license="MIT License",
    description="Samson is just a wrapper for simple curl operations."
)
