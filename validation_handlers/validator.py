import re
from validation_handlers.validationError import ValidationError

class Validator(object):
    """
    Checks individual records against specified validation tests
    """
    IS_INTERGER  = re.compile(r"^[-]?[1-9]\d*$")
    IS_DECIMAL  = re.compile(r"^[-]?((\d+(\.\d*)?)|(\.\d+))$")

    @staticmethod
    def validate(record,rules,csvSchema):
        """
        Args:
        record -- dict represenation of a single record of data
        rules -- list of rule Objects
        csvSchema -- dict of schema for the current file.
        Returns:
        True if validation passed, False if failed, and list of failed rules, each with field, description of failure, and value that failed
        """
        recordFailed = False
        failedRules = []
        for fieldName in csvSchema :
            if(csvSchema[fieldName].required and  not fieldName in record ):
                return False, [[fieldName, ValidationError.requiredError, ""]]

        for fieldName in record :

            currentSchema =  csvSchema[fieldName]
            ruleSubset = Validator.getRules(fieldName,rules)
            currentData = record[fieldName].strip()


            if(len(currentData) == 0):
                if(currentSchema.required ):
                    # If empty and required return field name and error
                    return False, [[fieldName, ValidationError.requiredError, ""]]
                else:
                    #if field is empty and not required its valid
                    continue
            # Always check the type in the schema
            if(not Validator.checkType(currentData,currentSchema.field_type.name) ) :
                recordFailed = True
                failedRules.append([fieldName, ValidationError.typeError, currentData])
                # Don't check value rules if type failed
                continue

            # Check for a type rule in the rule table, don't want to do value checks if type is not correct
            typeFailed = False
            for currentRule in ruleSubset:
                if(currentRule.rule_type.name == "TYPE"):
                    if(not Validator.checkType(currentData,currentRule.rule_text_1) ) :
                        recordFailed = True
                        typeFailed = True
                        failedRules.append([fieldName, ValidationError.typeError, currentData])
            if(typeFailed):
                # If type failed, don't do value checks
                continue
            #Field must pass all rules
            for currentRule in ruleSubset :
                if(not Validator.evaluateRule(currentData,currentRule,currentSchema.field_type.name)):
                    recordFailed = True
                    failedRules.append([fieldName, "Failed rule: " + str(currentRule.description), currentData])
        return (not recordFailed), failedRules

    @staticmethod
    def getRules(fieldName,rules) :
        returnList =[]
        for rule in rules :
            if( rule.file_column.name == fieldName) :
                returnList.append(rule)
        return returnList

    @staticmethod
    def checkType(data,datatype) :
        if(datatype == "STRING") :
            return(len(data) > 0)
        if(datatype == "BOOLEAN") :
            if(data.upper() in ["TRUE","FALSE","YES","NO","1","0"]) :
                return True
            return False 
        if(datatype == "INT") :
            return Validator.IS_INTERGER.match(data) is not None
        if(datatype == "DECIMAL") :
            if (Validator.IS_DECIMAL.match(data) is None ) :
                return Validator.IS_INTERGER.match(data) is not None
            return True
        raise ValueError("Data Type Error, Type: " + datatype + ", Value: " + data)

    @staticmethod
    def getIntFromString(data) :
        return int(float(data))

    @staticmethod
    def getType(data,datatype) :
        if(datatype =="INT") :
            return int(float(data))
        if(datatype =="DECIMAL") :
            return float(data)
        if(datatype == "STRING" or datatype =="BOOLEAN") :
            return data
        raise ValueError("Data Type Invalid")

    @staticmethod
    def evaluateRule(data,rule,datatype):
        value1 = rule.rule_text_1
        currentRuleType = rule.rule_type.name
        if(currentRuleType =="LENGTH") :
            return len(data.strip()) <= Validator.getIntFromString(value1)
        elif(currentRuleType =="LESS") :
            return Validator.getType(data,datatype) < Validator.getType(value1,datatype)
        elif(currentRuleType =="GREATER") :
            return Validator.getType(data,datatype) > Validator.getType(value1,datatype)
        elif(currentRuleType =="EQUAL") :
            return Validator.getType(data,datatype) == Validator.getType(value1,datatype)
        elif(currentRuleType =="NOT EQUAL") :
            return not (Validator.getType(data,datatype) == Validator.getType(value1,datatype))
        elif(currentRuleType == "TYPE"):
            # Type checks happen earlier, but type rule is still included in rule set, so skip it
            return True
        raise ValueError("Rule Type Invalid")
