import re, Levenshtein


def similar(s1, s2):
    s1 = re.sub("[^A-Za-z]", "", s1).lower()
    s2 = re.sub("[^A-Za-z]", "", s2).lower()
    if s1 == s2 or Levenshtein.ratio(s1, s2) > 0.7:
        return True
    return False
