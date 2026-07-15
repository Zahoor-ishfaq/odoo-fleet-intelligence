{
    'name': 'Fleet Cost Intelligence',
    'version': '17.0.1.0.0',
    'summary': 'AI-powered fleet cost management with predictive maintenance and anomaly detection',
    'description': 'Custom fleet management module with ML-based maintenance prediction, fuel anomaly detection, and route profitability analysis.',
    'author': 'Zahoor',
    'category': 'Operations/Fleet',
    'license': 'LGPL-3',
    'depends': ['base', 'mail', 'web', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/dashboard_action.xml',
        'views/fleet_views.xml',
        'data/ml_cron.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'fleet_intelligence/static/src/components/dashboard.js',
            'fleet_intelligence/static/src/components/dashboard.xml',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}