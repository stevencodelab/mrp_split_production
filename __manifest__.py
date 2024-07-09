{
    "name": "MRP Production Split",
    "summary": "Split Manufacturing Orders Into Smaller",
    "version": "14.0.1.0.0",
    "author": "Steven Morison (stevenmorizon123@gmail.com)",
    "website": "",
    "license": "AGPL-3",
    "category": "Manufacturing",
    "depends": ["mrp","product","stock"],
    "data": [
        "security/ir.model.access.csv",
        "views/inherit_mrp_production_view.xml",
        "views/inherit_mrp_workorder_view.xml",
        "wizard/mrp_production_split.xml",
    ],
    
    'auto_install': False,
    'installable': True,
    'application': True,
}
