import copy
import math
import random


class Defect:
    def __init__(self, type=0, cords=(0, 0, 0)):
        self.type = type
        self.cords = cords

    def __str__(self):
        return f"[{self.type},{self.cords}]"

    def __repr__(self):
        return f"[{self.type},{self.cords}]"

    def __copy__(self):
        my_copy = type(self)()
        my_copy.type = self.type
        my_copy.cords = self.cords
        return my_copy

    def copy(self):
        return self.__copy__()

    def __eq__(self, other):
        return ((self.type, self.cords) ==
                (other.type, other.cords))

    def __hash__(self):
        return hash((self.type, self.cords))


class DefectSet:

    def add_defect(self, defect: Defect):
        if defect in self:
            raise ValueError(f"Defect {defect} is already in set {self}")
        self.positions_set.add(defect.cords)
        self.defect_set.add(defect)
        return

    def add_defect_to_nearest(self, defect: Defect, get_possible_moves):
        possible_defects = [defect]
        id = 0
        while defect in self:
            id += 1
            if id >= len(possible_defects):
                possible_defects.extend(get_possible_moves(possible_defects))
            defect = possible_defects[id]
        self.positions_set.add(defect.cords)
        self.defect_set.add(defect)
        return defect

    def remove_defect(self, defect: Defect):
        if defect not in self:
            raise ValueError(f"Trying to delete defect {defect}, that isn't in the set: {self}")
        self.positions_set.remove(defect.cords)
        self.defect_set.remove(defect)
        return

    def is_occupied(self, defect: Defect):
        return defect.cords in self.positions_set

    def __contains__(self, defect: Defect):
        return defect in self.defect_set or self.is_occupied(defect)

    def __init__(self, eval_function):
        self.defect_set = set()
        self.positions_set = set()
        self.eval_function = eval_function

    def __str__(self):
        return f"{self.defect_set}"

    def __repr__(self):
        return f"{self.defect_set}"

    def get_energy(self, debug=False):
        return self.eval_function(self.defect_set, debug)/len(self)

    def __copy__(self):
        my_copy = type(self)(self.eval_function)
        my_copy.defect_set = self.defect_set.copy()
        my_copy.positions_set = self.positions_set.copy()
        return my_copy

    def copy(self):
        return self.__copy__()

    def __iter__(self):
        return iter(self.defect_set)

    def __len__(self):
        return len(self.defect_set)


class EvalFunction:
    def __init__(self, eval_function, structure, matrices, function_set):
        self.eval_function = eval_function
        self.structure = structure
        self.matrices = matrices
        self.function_set = function_set

    def __call__(self, defect_set, debug=False):
        return self.eval_function(self.structure, self.matrices, defect_set, self.function_set, debug)


class Batch:
    def __init__(self, max_members, preferred_percent=0.2):
        self.members = []
        self.max_members = max_members
        self.preferred_percent = preferred_percent
        self.batch_type = -1
        return

    def process_members(self, potential_members: list):
        new_len = min(self.max_members, math.ceil(len(potential_members) * self.preferred_percent))
        self.members = potential_members[:new_len].copy()
        return

    def __iter__(self):
        return iter(self.members)

    def mutate(self, mutate_function):
        for idx, member in enumerate(self.members):
            self.members[idx] = mutate_function(member)

    def __copy__(self):
        my_copy = type(self)(self.max_members)
        my_copy.members = self.members.copy()
        my_copy.preferred_percent = self.preferred_percent
        my_copy.batch_type = self.batch_type
        return my_copy

class TopBatch(Batch):
    def __init__(self, max_members, preferred_percent=0.2):
        super().__init__(max_members, preferred_percent)
        self.batch_type = 0
        return


class RandomBatch(Batch):
    def __init__(self, max_members, preferred_percent=0.2):
        super().__init__(max_members, preferred_percent)
        self.batch_type = 1
        return

    def process_members(self, potential_members: list):
        new_len = min(self.max_members, math.ceil(len(potential_members) * self.preferred_percent))
        self.members = random.choices(potential_members, k=new_len)
        return


class BatchOper:
    batches = []

    def __init__(self, batches, target_energy=0):
        self.batches = batches
        self.target_energy = target_energy
        for batch in batches:
            if batch.batch_type == -1:
                raise ValueError("One or more of the batches are blank.")

    def _return_all(self):
        for batch in self.batches:
            for member in batch:
                yield member

    def __iter__(self):
        return self._return_all()

    def sort(self, potential_members):
        return sorted(potential_members, key=lambda x: (x.get_energy() - self.target_energy)**2)

    def process_members(self, potential_members: list):
        potential_members = self.sort(potential_members)
        for batch in self.batches:
            batch.process_members(potential_members)

    def __getitem__(self, i):
        return self.batches[i]
