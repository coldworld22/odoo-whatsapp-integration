{
    'name': 'SkillBridge Login Page',
    'version': '1.1',
    'author': 'SkillBridge',
    'category': 'Theme',
    'website': 'https://eduskillbridge.net',
    'summary': 'Custom corporate login page for SkillBridge',
    'description': 'Professional customized login page with SkillBridge branding.',
    'depends': ['web', 'auth_oauth'],
    'data': [
        'views/login_template.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            '/skillbridge_login/static/src/css/login_style.css',
        ],
    },
    'installable': True,
    'application': False,
}
