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
        "views/split_production_inherit_view.xml",
        "wizard/mrp_production_split.xml",
        "wizard/mrp_production_backorder.xml",
    ],
    
    'auto_install': False,
    'installable': True,
    'application': True,
}
