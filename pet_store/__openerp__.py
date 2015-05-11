{
    'name': 'OpenERP Pet Store',
    'version': '1.0',
    'summary': 'Sell pet toys',
    'category': 'Tools',
    'description':
    """
OpenERP Pet Store
=============================

A wonderful application to sell pet toys.
    """,
    'data': ['pet_store.xml'],
    'depends': ['sale_stock'],
    'application': True,
    'qweb': ['static/src/xml/*.xml'],
}