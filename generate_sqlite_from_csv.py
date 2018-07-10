#!/usr/bin/env python3
"""Based on csvs_to_sqlite but with clean handling of duplicate columns"""

import os
import re
import sqlite3
import sys

from csvs_to_sqlite.utils import (
    LoadCsvError,
    csvs_from_paths,
    load_csv,
    refactor_dataframes,
    table_exists,
    to_sql_with_foreign_keys,
)


def convert_csv_to_sqlite(csv_filename):
    sqlite_filename = "%s.sqlite" % os.path.splitext(csv_filename)[0]
    conn = sqlite3.connect(sqlite_filename)

    dataframes = []
    csvs = csvs_from_paths(csv_filename)

    for name, path in csvs.items():
        try:
            df = load_csv(path, separator=",", skip_errors=False, quoting=0, shape=None)
            df.table_name = "Items"
            dataframes.append(df)
        except LoadCsvError as e:
            print("Could not load {}: {}".format(path, e), file=sys.stderr)

    print("Loaded {} dataframes".format(len(dataframes)))

    # Use extract_columns to build a column:(table,label) dictionary
    foreign_keys = {}

    column_map = [
        (re.compile(r"Other Title(?:|_\d+)"), "Title"),
        (re.compile(r"Creator/Publisher(?:|_\d+)"), "Creator"),
        (re.compile(r"Subject(?:|_\d+)"), "Subject"),
        (re.compile(r"Collection(?:|_\d+)"), "Collection"),
        (re.compile(r"Era(?:|_\d+)"), "Era"),
        (re.compile(r"Location(?:|_\d+)"), "Location"),
        (re.compile(r"Geography(?:|_\d+)"), "Geography"),
    ]

    assert len(dataframes) == 1

    for column_name in dataframes[0].columns:
        for regex, mapped in column_map:
            if regex.search(column_name):
                foreign_keys[column_name] = (mapped, "value")

    # Now we have loaded the dataframes, we can refactor them
    created_tables = {}
    refactored = refactor_dataframes(conn, dataframes, foreign_keys)

    for df in refactored:
        # This is a bit trickier because we need to
        # create the table with extra SQL for foreign keys
        if table_exists(conn, df.table_name):
            df.to_sql(df.table_name, conn, if_exists="append", index=False)
        else:
            to_sql_with_foreign_keys(conn, df, df.table_name, foreign_keys)
            created_tables[df.table_name] = df

    conn.close()

    print("Updated", sqlite_filename)


if __name__ == "__main__":
    convert_csv_to_sqlite(sys.argv[1])
