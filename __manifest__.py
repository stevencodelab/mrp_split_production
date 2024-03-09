{
    "name": "MRP Production Split",
    "summary": "Split Manufacturing Orders into smaller ones",
    "version": "14.0.1.0.0",
    "author": "Steven Morison (stevenmorizon123@gmail.com)",
    "website": "",
    "license": "AGPL-3",
    "category": "Manufacturing",
    "depends": ["mrp","product","stock"],
    "data": [
        "security/ir.model.access.csv",
        "views/split_production_view.xml",
        "wizard/mrp_production_split.xml",
    ],

    'auto_install': False,
    'installable': True,
    'application': True,

    'pre_init_hook': '_pre_init_mrp',
    'post_init_hook': '_create_warehouse_data',
    'uninstall_hook': 'uninstall_hook',
}
