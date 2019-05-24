# encoding: utf-8

{
    'name': 'Multi-Website',
    'category': 'Website',
    'sequence': 50,
    'version': '1.0',
    'depends': ['website', 'website_sale', 'website_livechat',
                'auth_signup', 'website_theme_install', 'sale_coupon'],
    'installable': True,
    'data': [
        'data/website_data.xml',
        'views/sale_order_views.xml',
        'views/templates.xml',
        'views/website_templates.xml',
        'views/website_views.xml',
        'views/res_config_settings_views.xml',
        'views/res_users.xml',
        'views/ir_module_module.xml',
        'wizard/website_urls_wizard_views.xml',
    ],
    'demo': [
        'data/website_demo.xml',
    ],
    'qweb': [
        # 'static/src/xml/website.backend.xml',
    ],
}
