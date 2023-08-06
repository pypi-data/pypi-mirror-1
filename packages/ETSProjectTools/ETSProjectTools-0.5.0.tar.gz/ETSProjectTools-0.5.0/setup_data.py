# A dictionary of the setup data information.
INFO = {
    'extras_require' : {
        # All non-ets dependencies should be in this extra to ensure users can
        # decide whether to require them or not.
        'nonets': [
            'setuptools >=0.6c6',
            ],
        },
    'install_requires' : [
        # NOTE: This package should never depend on other ETS projects!!
        ],
    'name': 'ETSProjectTools',
    'version': '0.5.0',
    }

