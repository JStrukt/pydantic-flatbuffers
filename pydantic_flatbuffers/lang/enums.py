from matrix_enum import MatrixEnum, Member
from pydantic_flatbuffers.fbs.fbs import FBSType

class Namespaces(MatrixEnum):
    TABLES=Member(title="tables", index=FBSType.TABLE)
    STRUCTS=Member(title="structs", index=FBSType.STRUCT)
    ENUMS=Member(title="enums", index=FBSType.ENUM)
    UNIONS=Member(title="unions", index=FBSType.UNION)
