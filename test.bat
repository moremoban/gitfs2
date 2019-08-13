pip freeze
python setup.py develop
nosetests --with-coverage --cover-package gitfs2 --cover-package tests tests  docs/source gitfs2
