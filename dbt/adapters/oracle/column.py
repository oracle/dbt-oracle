from dataclasses import dataclass
from typing import Dict, ClassVar


from dbt.adapters.base.column import Column


@dataclass
class OracleColumn(Column):
    # https://docs.oracle.com/en/database/oracle/oracle-database/21/sqlrf/Data-Types.html#GUID-A3C0D836-BADB-44E5-A5D4-265BA5968483

    TYPE_LABELS: ClassVar[Dict[str, str]] = {
        "STRING": "VARCHAR2(4000)",
        "TIMESTAMP": "TIMESTAMP",
        "FLOAT": "FLOAT",
        "INTEGER": "INTEGER",
    }

    STRING_DATATYPES = {'char', 'nchar', 'varchar', 'varchar2', 'nvarchar2'}
    NUMBER_DATATYPES = {'number', 'float'}

    @property
    def data_type(self) -> str:
        if self.is_string():
            return self.oracle_string_type(self.dtype, self.string_size())
        elif self.is_numeric():
            return self.numeric_type(self.dtype, self.numeric_precision, self.numeric_scale)
        else:
            return self.dtype

    @classmethod
    def oracle_string_type(cls, dtype: str, size: int = None):
        """
            - CHAR(SIZE)
            - VARCHAR2(SIZE)
            - NCHAR(SIZE) or NCHAR
            - NVARCHAR2(SIZE)
        """
        if size is None:
            return dtype
        else:
            return "{}({})".format(dtype, size)

    def is_numeric(self) -> bool:
        if self.dtype.lower() in self.NUMBER_DATATYPES:
            return True
        return super().is_numeric()

    def is_string(self) -> bool:
        if self.dtype.lower() in self.STRING_DATATYPES:
            return True
        return super().is_string()
