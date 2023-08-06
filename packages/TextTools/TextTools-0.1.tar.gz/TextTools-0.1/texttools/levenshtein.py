# -*- coding: utf8 -*

# fallback when the module couldn't get compiled
def _py_edit_distance(a, b):
    """distance(a, b) -> int.

    Calculates Levenshtein's edit distance between strings "a" and "b".
    """
    if len(a) < len(b):
        return _py_edit_distance(b, a)
    if not a:
        return len(b)

    previous_row = xrange(len(b) + 1)
    for i, c1 in enumerate(a):
        current_row = [i + 1]
        for j, c2 in enumerate(b):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

try:
    from _levenshtein import edit_distance
except ImportError:
    edit_distance = _py_edit_distance

def files_distance(file1, file2):
    with open(file1) as f1:
        f1_text = f1.read()
        with open(file2) as f2:
            f2_text = f2.read()
            distance = edit_distance(f1_text, f2_text)

    f1_size = len(f1_text)
    f2_size = len(f2_text)
    if f1_size > f2_size:
        size = f1_size
    else:
        size = f2_size
    if distance > 0:
        ratio = 100. - 100. / (float(size)/float(distance))
    else:
        ratio = 100.
    return distance, ratio

