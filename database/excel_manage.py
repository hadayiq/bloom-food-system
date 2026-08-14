import os
from openpyxl import load_workbook


class ExcelManager:

    def __init__(self):

        self.file_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "inventory.xlsx"
        )

    def workbook(self):

        return load_workbook(self.file_path)

    def save(self, workbook):

        workbook.save(self.file_path)