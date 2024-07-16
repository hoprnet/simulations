from pandas import DataFrame, Series, read_excel


class Entry:
    @classmethod
    def fromXLSX(cls, filename: str):
        data = read_excel(filename, sheet_name="Sheet1")
        return cls.fromDataFrame(data)

    @classmethod
    def fromDataFrame(cls, entries: DataFrame):
        entries = sum(
            [cls.fromPandaSerie(entry) for _, entry in entries.iterrows()], []
        )
        return [entry for entry in entries if entry is not None]

    @classmethod
    def fromPandaSerie(cls, entry: Series):
        raise NotImplementedError
