from dataactcore.models.validationModels import FieldType, FileColumn
from dataactvalidator.validation_handlers.validator import Validator
from tests.integration.baseTestValidator import BaseTestValidator
from dataactcore.models.lookups import FIELD_TYPE_DICT


class ValidatorTests(BaseTestValidator):

    @classmethod
    def setUpClass(cls):
        """Set up class-wide resources (test data)"""
        super(ValidatorTests, cls).setUpClass()
        # TODO: refactor into a pytest fixture

        # create test schema
        stringType = FieldType()
        stringType.field_type_id = 1
        stringType.name = "STRING"

        intType = FieldType()
        intType.field_type_id = 2
        intType.name = "INT"

        floatType = FieldType()
        floatType.field_type_id = 3
        floatType.name = "DECIMAL"

        booleanType = FieldType()
        booleanType.field_type_id = 4
        booleanType.name = "BOOLEAN"

        longType = FieldType()
        longType.field_type_id = 5
        longType.name = "LONG"

        column1 = FileColumn()
        column1.file_column_id = 1
        column1.name = "test1"
        column1.required = True
        column1.field_type = stringType
        column1.field_types_id = FIELD_TYPE_DICT[stringType.name]
        column1.file_id = 1

        column2 = FileColumn()
        column2.file_column_id = 2
        column2.name = "test2"
        column2.required = True
        column2.field_type = floatType
        column2.field_types_id = FIELD_TYPE_DICT[floatType.name]
        column2.file_id = 1

        column3 = FileColumn()
        column3.file_column_id = 3
        column3.name = "test3"
        column3.required = True
        column3.field_type = booleanType
        column3.field_types_id = FIELD_TYPE_DICT[booleanType.name]
        column3.file_id = 1

        column4 = FileColumn()
        column4.file_column_id = 3
        column4.name = "test4"
        column4.required = True
        column4.field_type = intType
        column4.field_types_id = FIELD_TYPE_DICT[intType.name]
        column4.file_id = 1

        column5 = FileColumn()
        column5.file_column_id = 3
        column5.name = "test5"
        column5.required = False
        column5.field_type = intType
        column5.field_types_id = FIELD_TYPE_DICT[intType.name]
        column5.file_id = 1

        column6 = FileColumn()
        column6.file_column_id = 6
        column6.name = "test6"
        column6.required = False
        column6.field_type = stringType
        column6.field_types_id = FIELD_TYPE_DICT[stringType.name]
        column6.file_id = 1

        column7 = FileColumn()
        column7.file_column_id = 7
        column7.name = "test7"
        column7.required = False
        column7.field_type = longType
        column7.field_types_id = FIELD_TYPE_DICT[longType.name]
        column7.file_id = 1

        cls.schema = {
            "test1": column1,
            "test2": column2,
            "test3": column3,
            "test4": column4,
            "test5": column5,
            "test6": column6,
            "test7": column7
        }

    def test_types(self):
        """Test data type checks."""
        self.assertTrue(Validator.check_type("1234Test", "STRING"))
        self.assertFalse(Validator.check_type("1234Test", "INT"))
        self.assertFalse(Validator.check_type("1234Test", "DECIMAL"))
        self.assertFalse(Validator.check_type("1234Test", "BOOLEAN"))
        self.assertFalse(Validator.check_type("1234Test", "LONG"))

        self.assertTrue(Validator.check_type("", "STRING"))
        self.assertTrue(Validator.check_type("", "INT"))
        self.assertTrue(Validator.check_type("", "DECIMAL"))
        self.assertTrue(Validator.check_type("", "BOOLEAN"))
        self.assertTrue(Validator.check_type("", "LONG"))

        self.assertTrue(Validator.check_type("01234", "STRING"))
        self.assertTrue(Validator.check_type("01234", "INT"))
        self.assertTrue(Validator.check_type("01234", "DECIMAL"))
        self.assertTrue(Validator.check_type("01234", "LONG"))
        self.assertFalse(Validator.check_type("01234", "BOOLEAN"))

        self.assertTrue(Validator.check_type("1234.0", "STRING"))
        self.assertFalse(Validator.check_type("1234.0", "INT"))
        self.assertTrue(Validator.check_type("1234.00", "DECIMAL"))
        self.assertFalse(Validator.check_type("1234.0", "LONG"))
        self.assertFalse(Validator.check_type("1234.0", "BOOLEAN"))

    def test_schema_optional_field(self):
        """Test optional fields."""
        schema = self.schema
        record = {
            "test1": "hello",
            "test2": "1.0",
            "test3": "YES",
            "test4": "1",
            "test5": "1",
        }
        self.assertTrue(Validator.validate(record, schema))
        record["test5"] = ""
        self.assertTrue(Validator.validate(record, schema))
        record["test5"] = "s"
        self.assertTrue(Validator.validate(record, schema))
        record["test5"] = ""
        record["test3"] = ""
        self.assertTrue(Validator.validate(record, schema))
