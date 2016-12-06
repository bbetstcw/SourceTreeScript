import re
import json
import collections
import os

CONSTANT_RULE_FILE = "rules/constant.json"
SEMI_RULE_FILE = "rules/semiconstant.json"
REGEX_RULE_FILES = "rules/regular_level"
CORRECTION_RULE_FILE = "rules/correction.json"

constant = None
regex_list = None
semi = None
correction = None
regex = None

def customize(filepath, script_path):
    getRule(script_path)
    file = open(filepath, "r", encoding="utf8")
    mdcontent = file.read()
    file.close()
    mdcontent = customize_mdcontent(mdcontent)
    file = open(filepath, "w", encoding="utf8")
    file.write(mdcontent)
    file.close()

def customize_mdcontent(mdcontent):
    mdcontent = constant_replacement(mdcontent)
    mdcontent = regex_replacement(mdcontent)
    mdcontent = semi_replacement(mdcontent)
    mdcontent = correction_replacement(mdcontent)
    return mdcontent

def constant_replacement(mdcontent):
    if len(constant) > 0:
        constRegex = re.compile("(%s)" % "|".join(map(re.escape, constant.keys())))
        mdcontent = constRegex.sub(lambda mo: constant[mo.string[mo.start():mo.end()]], mdcontent)
    return mdcontent

def regex_replacement(mdcontent):
    global regex
    for i in regex_list:
        regex = i
        if len(regex) > 0:
            regexRegex = re.compile("(%s)" % "|".join([rule["regex"] for rule in regex]))
            mdcontent = regexRegex.sub(get_replacement_for_regex, mdcontent)
    return mdcontent

def get_replacement_for_regex(mo):
    found = mo.string[mo.start():mo.end()]
    for rule in regex:
        m = re.match(rule["regex"], found)
        if m:
            match_tuple=m.groups()
            for replacement in rule["replacements"]:
                correct_replacement = True
                for condition in replacement["conditions"]:
                    if not re.match(condition["match"], match_tuple[condition["parameter"]]):
                        correct_replacement = False
                        break
                if correct_replacement == True:
                    value = re.sub(rule["regex"], replacement["replacement"], found)
                    break
            return value
    return found

def semi_replacement(mdcontent):
    if len(semi) > 0:
        semiRegex = re.compile("(%s)" % "|".join(semi.keys()))
        mdcontent = semiRegex.sub(get_replacement_for_semi, mdcontent)
    return mdcontent

def get_replacement_for_semi(mo):
    found = mo.string[mo.start():mo.end()]
    for key, value in semi.items():
        if re.match(key, found):
            return value
    return found

def correction_replacement(mdcontent):
    if len(constant) > 0:
        correctionRegex = re.compile("(%s)" % "|".join(map(re.escape, correction.keys())))
        mdcontent = correctionRegex.sub(lambda mo: correction[mo.string[mo.start():mo.end()]], mdcontent)
    return mdcontent

def getRule(script_path):
    global constant
    global semi
    global regex_list
    global correction
    if constant == None:
        file = open(script_path+"/"+CONSTANT_RULE_FILE, "r", encoding="utf8")
        constant = json.loads(file.read())
        file.close()
    if semi == None:
        file = open(script_path+"/"+SEMI_RULE_FILE, "r", encoding="utf8")
        semi = json.loads(file.read())
        file.close()
    if regex_list == None:
        i = 0
        regex_list = []
        rule_file = script_path+"/"+REGEX_RULE_FILES+str(i)+".json"
        while os.path.isfile(rule_file):
            file = open(rule_file, "r", encoding="utf8")
            regex_list.append(json.loads(file.read()))
            file.close()
            i+=1
            rule_file = script_path+"/"+REGEX_RULE_FILES+str(i)+".json"
    if correction == None:
        file = open(script_path+"/"+CORRECTION_RULE_FILE, "r", encoding="utf8")
        correction = json.loads(file.read())
        file.close()