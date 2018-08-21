import sys
from collections import OrderedDict

import xlrd
from django.core.management.base import BaseCommand

COLUMN_DEFAULTS = {"Contact-AcceptsEmailMarketing": True}

READERS = {
    xlrd.XL_CELL_EMPTY: lambda column, cell: COLUMN_DEFAULTS.get(column, cell.value),
    xlrd.XL_CELL_TEXT: lambda column, cell: COLUMN_DEFAULTS.get(column, cell.value),
}


def column_models(columns):
    return [column.title().replace(" ", "") for column in columns]


def convert_cell(column, cell):
    if not column:
        return
    reader = READERS.get(cell.ctype, lambda _column, _cell: _cell)
    result = reader(column, cell)
    return result


def row_values(columns, row):
    return [convert_cell(column, cell) for (column, cell) in zip(columns, row)]


def import_worksheet(worksheet, simulate):
    row_iter = worksheet.get_rows()
    next(row_iter)
    columns = column_models([column.value for column in next(row_iter)])

    for row in row_iter:
        from pprint import pprint

        row_dict = OrderedDict(
            (column, cell)
            for column, cell in zip(columns, row_values(columns, row))
            if column
        )

        pprint(row_dict)
        print("")


def import_german_orgs(xls_filename, simulate=False):
    """
    :param xls_file:
    :param simulate:
    :return:

    Import all worksheets of xls
    """
    workbook = xlrd.open_workbook(xls_filename)
    for worksheet in workbook.sheets():
        import_worksheet(worksheet, simulate)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--simulate",
            action="store_true",
            default=False,
            help="Do now actually import data",
        )

        parser.add_argument(
            "data_file", help="xls format spreadsheet containing german orgs to import."
        )

    def handle(self, data_file, *args, **options):
        simulate = options["simulate"]
        result = import_german_orgs(data_file, simulate)
        if not result:
            sys.exit(1)
