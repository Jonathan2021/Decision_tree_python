# Decision tree using GINI index
import enum
import operator
import random

class Classes(enum.Enum):
    RIGHT = 'R'
    LEFT = 'L'
    BALANCED = 'B'

    @staticmethod
    def get_from_str(string):
        if string == 'R':
            return Classes.RIGHT
        if string == 'L':
            return Classes.LEFT
        if string == 'B':
            return Classes.BALANCED
        return None

    @staticmethod
    def get():
        return [Classes.RIGHT, Classes.LEFT, Classes.BALANCED]

    @staticmethod
    def get_dic(init_val = 0):
        dic = dict()
        for val in Classes.get():
            dic[val] = init_val
        return dic

class Configuration:
    def __init__(self, tip, left_weight, left_distance, right_weight, right_distance):
        self._tip = tip;
        self._left_weight = left_weight
        self._left_distance = left_distance
        self._right_weight = right_weight
        self._right_distance = right_distance

    @property
    def get_class(self):
        return self._tip

    @property
    def left_weight(self):
        return self._left_weight

    @property
    def left_distance(self):
        return self._left_distance

    @property
    def right_weight(self):
        return self._right_weight

    @property
    def right_distance(self):
        return self._right_distance

    @staticmethod
    def get_attributes():
        attributes = []
        attributes.append(Configuration.left_weight.fget)
        attributes.append(Configuration.left_distance.fget)
        attributes.append(Configuration.right_weight.fget)
        attributes.append(Configuration.right_distance.fget)
        return attributes

    def __eq__(self, other):
        if not isinstance(other, Configuration):
            return False
        return self._tip == other._tip

class Node:
    def __init__(self, split, left, right, possible_class = None):
        self._split = split
        self._right = right
        self._left = left
        self._is_leaf = right is None and left is None
        self._possible_class = possible_class

    @classmethod
    def leaf(cls, possible_class):
        return cls(None, None, None, possible_class)

    @property
    def split(self):
        return self._split
    
    @property
    def is_leaf(self):
        return self._is_leaf

    @property
    def left(self):
        return self._left

    @property
    def right(self):
        return self._right

    @property 
    def possible_class(self):
        return self._possible_class
    
def gini(head_counts):
    total = sum(head_counts)
    res = 1
    for val in head_counts:
        res -= (val/total) ** 2
    return res

def get_classes_count(S):
    dic = Classes.get_dic(0)
    for s in S:
        dic[s.get_class] += 1
    return dic

def calculate_gini_split(S):
    dic = get_classes_count(S)
    return gini(dic.values())


def pick_a_random_split(S, attr):
    minimum = min(S, key= lambda x: attr(x))
    maximum = max(S, key= lambda x: attr(x))
    cut_point = random.uniform(attr(minimum), attr(maximum))
    return lambda x : attr(x) <= cut_point

def stop_split(S, non_constant_attributes, min_size = 1):
    if min_size >= len(S):
        return True
    if not non_constant_attributes:
        return True
    ref = S[0]
    if all(ref == s for s in S):
        return True
    return False


def get_splitted(S, split):
    left = []
    right = []
    for s in S:
        if split(s):
            left.append(s)
        else:
            right.append(s)
    return left, right

def calculate_gini_from_splits(left, right):
    left_count = len(left)
    right_count = len(right)
    total = left_count + right_count
    gini = (left_count / float(total))*calculate_gini_split(left) + (right_count / float(total)) * calculate_gini_split(right)
    return gini

def get_non_constant_attributes(S, attributes):
    non_constant = []
    for attr in attributes:
        comparison_value = None
        is_unique = True
        for s in S:
            if comparison_value is None:
                comparison_value = attr(s)
            elif comparison_value != attr(s):
                is_unique = False
                break
        if not is_unique:
            non_constant.append(attr)
    return non_constant

def get_best_split(S, attributes):
    min_gini = 1
    min_gini_attribute = None
    best_split = None
    best_left_split = []
    best_right_split = []
    for attribute in attributes:
        split = pick_a_random_split(S, attribute)
        left, right = get_splitted(S, split)
        gini = calculate_gini_from_splits(left, right)
        if gini < min_gini:
            min_gini = gini
            min_gini_attribute = attribute
            best_split = split
            best_left_split = left
            best_right_split = right
    return best_split, attribute, best_left_split, best_right_split

def get_majority_class(S):
    dic = get_classes_count(S)
    return max(dic.items(), key=operator.itemgetter(1))[0]

def split_a_node(S, attributes):
    attributes = get_non_constant_attributes(S, attributes)
    if stop_split(S, attributes):
        return Node.leaf(get_majority_class(S))
    split, attribute, left_split, right_split = get_best_split(S, attributes)
    #attributes.remove(attribute) # remove comment to not resue an attribute in a path
    left = split_a_node(left_split, attributes)
    right = split_a_node(right_split, attributes)
    return  Node(split, left=left, right=right)
    

def build_dt(S):
    if not S:
        return None
    attributes = Configuration.get_attributes()
    return split_a_node(S, attributes)

def get_data(path):
    data = []
    with open(path, "r") as data_file:
        for line in data_file:
            stripped_line = line.strip()
            current_config_raw = stripped_line.split(',')
            data.append(Configuration(Classes.get_from_str(current_config_raw[0]),\
                    int(current_config_raw[1]), int(current_config_raw[2]),\
                    int(current_config_raw[3]), int(current_config_raw[4])))
    return data

def estimate_class(dt, config):
    while dt and not dt.is_leaf:
        dt = dt.left if dt.split(config) else dt.right
    return dt.possible_class if dt else None

def print_results_test(totals, correct):
    print("Success rate")
    for key in totals:
        total_nb = totals[key]
        if total_nb:
            rate = float(correct[key]) * 100 / total_nb
            print(f"{key.name} : {rate} ({correct[key]} / {total_nb})")

def test(dt, configs):
    heads_count = get_classes_count(configs)
    #print(heads_count)
    correct = Classes.get_dic(0)
    for config in configs:
        #print(config.get_class.name)
        ref = config.get_class
        estimation = estimate_class(dt, config)
        if estimation == ref:
            #print("Correct")
            correct[config.get_class] += 1
        #else:
            #print("Incorrect")
            #print("Estimated ", estimation)
    print_results_test(heads_count, correct)

def calculate_tipping(LW, LD, RW, RD):
    res = LW * LD - RW * RD
    if res < 0:
        return Classes.RIGHT
    if res > 0:
        return Classes.LEFT
    return Classes.BALANCED

def generate_configs(nb):
    configs = []
    for i in range(nb):
        LW, LD, RW, RD  = random.choices(range(1,6), k=4)
        tip = calculate_tipping(LW, LD, RW, RD)
        configs.append(Configuration(tip, LW, LD, RW, RD))
    return configs

def get_path_from_user(default):
    print("Enter the path to read data from.")
    print(f"Default is '{default}', press Enter to keep")
    entry = input()
    return entry if entry else default

def main():
    path = get_path_from_user('DECISION/balance-scale.data')
    print("Reading data from file")
    configurations = get_data(path)
    print("Building decision tree")
    root = build_dt(configurations)
    print("generation test configs")
    test_configs = generate_configs(500)
    print("Testing")
    test(root, test_configs)

main()
