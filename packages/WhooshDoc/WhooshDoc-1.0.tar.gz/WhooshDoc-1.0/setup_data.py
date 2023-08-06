INFO = dict(
    extras_require=dict(
        ui = [
            'Traits',
            'TraitsGUI',
            'TraitsBackendWX',
            # FIXME: or TraitsBackendQt, probably.
        ],
    ),
    install_requires=[
        'argparse >= 0.8',
        'Whoosh >= 0.1.13',
        'epydoc >= 3.0.1',
    ],
    name='WhooshDoc',
    version='1.0',
)
