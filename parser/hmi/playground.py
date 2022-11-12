"""
Demonstrates a dynamic Layout
"""

from datetime import datetime

from time import sleep

from rich.align import Align
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich.table import Table
import csv



console = Console()
layout = Layout()




table = Table(title="Space Vehicles",show_header=False, show_lines=True)
table2 = Table()
table2.add_column("Date&Time")
table2.add_column("Category")
table2.add_column("Message")


text = Text("  SV1  ")
text.stylize(style="bold white on red")
text2 = Text("  SV2  ")
text2.stylize(style="bold white on green")

text3 = Text("  SV3 [SV2]  ")
text3.stylize(style="bold white on green")


table.add_row(text                           ,text2,text3,"SV4","SV5","SV6","SV7","SV8","SV9",)
table.add_row("SV10","SV11","SV12","SV13","SV14","SV15","SV16","SV17","SV18",)
table.add_row("SV19","SV20","SV21","SV22","SV23","SV24","SV25","SV26","SV27",)
table.add_row("SV28","SV29","SV30","SV31","SV32","SV33","SV34","SV35","SV36",)


layout.split(
    Layout(name="header", size=1),
    Layout(ratio=1, name="main"),
    Layout(size=8, name="footer"),
)

layout["main"].split_row(Layout(name="body"), Layout(name="side", ratio=2))
layout["side"].update(
Align.left(
    table
)
)

layout["body"].update(
    Align.center(
        Text(
            "DSM Type: DSM-KROOT"+"\n"+"DSM Blocks: 9/9 Blocks"+"\n"+"OSNMA Status: DSM-KROOT"+"\n"+"KROOT: 0xFFFFFFFFFFFF",
            justify="left",
        ),
        vertical="middle",
        
    ),
    
)


class Clock:
    """Renders the time in the center of the screen."""
    def __rich__(self) -> Text:
        return Text("OSNMA live Demonstrator v0  "+datetime.now().ctime(), style="bold magenta", justify="center")
    
class updatedTable:
    """ Example of an update of table"""
    def __rich__(self) -> Table:
        table3 = Table()
        table3.add_column("Date and Time")
        table3.add_column("Category")
        table3.add_column("Message")
        with open('logname.log', 'r') as csvfile:
            csvreader = list(csv.reader(csvfile))
            for row in csvreader[-4:]:
                try:
                    if row[1] == "WARNING":
                        text66 = Text("WARNING")
                        text66.stylize(style="bold black on yellow")
                        table3.add_row(row[0], text66, row[2])
                    if row[1] == "ERROR":
                        text66 = Text("ERROR")
                        text66.stylize(style="bold white on red")
                        table3.add_row(row[0], text66, row[2])
                    if row[1] == "INFO":
                        text66 = Text("INFO")
                        text66.stylize(style="bold white on red")
                        table3.add_row(row[0], row[1], row[2])
                except: pass
        return table3

layout["header"].update(Clock())

layout["footer"].update(Align.center(updatedTable()))

with Live(layout, screen=True, redirect_stderr=False) as live:
    i = 1
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        pass