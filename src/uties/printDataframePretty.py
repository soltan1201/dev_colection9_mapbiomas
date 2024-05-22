import pandas as pd
from rich.console import Console
from rich.table import Table
df = pd.DataFrame({'col_two' : [0.0001, 1e-005 , 1e-006, 1e-007],
                   'column_3' : ['ABCD', 'ABCD', 'long string', 'ABCD']})
console = Console()
table = Table('Title')
table.add_row(df.to_string(float_format=lambda _: '{:.4f}'.format(_)))
console.print(table)
