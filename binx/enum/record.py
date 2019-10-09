from binx.types import (SerializedStreamHeader, BinaryLibrary, 
                        ClassWithMembersAndTypes, MemberReference,
                        SystemClassWithMembersAndTypes, ObjectNull,
                        BinaryArray, ClassWithId, BinaryObjectString,
                        ClassWithMembers, SystemClassWithMembers,
                        ArraySinglePrimitive, ArraySingleString,
                        ObjectNullMultiple, ObjectNullMultiple256)

record_type_enum = [
    {
        "type": "SerializedStreamHeader",
        "class": SerializedStreamHeader,
    },
    {
        "type": "ClassWithId",
        "class": ClassWithId,
    },
    {
        "type": "SystemClassWithMembers",
        "class": SystemClassWithMembers,
    },
    {
        "type": "ClassWithMembers",
        "class": ClassWithMembers,
    },
    {
        "type": "SystemClassWithMembersAndTypes",
        "class": SystemClassWithMembersAndTypes,
    },
    {
        "type": "ClassWithMembersAndTypes",
        "class": ClassWithMembersAndTypes,
    },
    {
        "type": "BinaryObjectString",
        "class": BinaryObjectString,
    },
    {
        "type": "BinaryArray",
        "class": BinaryArray,
    },
    {
        "type": "MemberPrimitiveTyped",
    },
    {
        "type": "MemberReference",
        "class": MemberReference,
    },
    {
        "type": "ObjectNull",
        "class": ObjectNull,
    },
    {
        "type": "MessageEnd",
    },
    {
        "type": "BinaryLibrary",
        "class": BinaryLibrary,
    },
    {
        "type": "ObjectNullMultiple256",
        "class": ObjectNullMultiple256,
    },
    {
        "type": "ObjectNullMultiple",
        "class": ObjectNullMultiple,
    },
    {
        "type": "ArraySinglePrimitive",
        "class": ArraySinglePrimitive,
    },
    {
        "type": "ArraySingleObject",
    },
    {
        "type": "ArraySingleString",
        "class": ArraySingleString,
    },
    {
        "type": "MethodCall",
    },
    {
        "type": "MethodReturn",
    },
]