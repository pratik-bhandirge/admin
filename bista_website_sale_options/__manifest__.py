# See LICENSE file for full copyright and licensing details.

{
    "name": "Bista website sale options",
    "version": "11.0.1.0.0",
    "author": "Bista Solutions Pvt. Ltd.",
    "maintainer": "Bista Solutions Pvt. Ltd.",
    "website": "https://www.bistasolutions.com",
    "category": "Web",
    "license": "AGPL-3",
    'summary': 'Hide sale options module within 5 second.',
    "depends": [
        "website",
        "website_sale",
        "website_sale_options",
        "maq_prod_variant_unpublish",
        "ecommerce_category",
	"sale",
    ],
    "data": [
	'views/product_sale_view_inherit.xml',
        "views/website_sale_options.xml",
    ],
    #    "qweb": [
    #        "static/src/xml/website_sale.xml",
    #    ],
    # "images": ["static/description/groupexpand.png"],
    "installable": True,
}
