"""SQL Alchemy utilities
"""

class TableDeclarationStatement:

    no_create = False

    def __init__(self, no_create=False):
        self.no_create = no_create

    def __call__(self, *tables):
        for tbl in tables:
            if not tbl.exists():
                tbl.create()
        
declare_tables = TableDeclarationStatement()

