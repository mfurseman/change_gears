#!/usr/bin/env python3.10

import bisect
import itertools
import math


INCH_TO_MM = 25.4


TARGET_ERROR = 1.0 / 1000.0
PRINT_FORMAT = "0.3f"


class GearSet:
    def __init__(self, driving, driven):
        assert len(driving) == len(driven)
        self.driving = sorted(driving)
        self.driven = sorted(driven)
        self.ratio = math.prod(self.driven) / math.prod(self.driving)

    def __eq__(self, other: object) -> bool:
        return self.ratio == other.ratio

    def __lt__(self, other: object) -> bool:
        return self.ratio < other.ratio

    def __hash__(self) -> int:
        return hash(tuple((tuple(self.driving), tuple(self.driven))))

    def __repr__(self) -> str:
        return f"{self.ratio:^{PRINT_FORMAT}} -> [{list(self.driving)} : {list(self.driven)}]"


def filter_best(gear_set):
    shortest_train_length = min([len(gs.driving) for gs in gear_set])
    shortest_trains = {
        gs for gs in gear_set if len(gs.driving) == shortest_train_length
    }
    return list(shortest_trains)


def filter_ratio(gear_sets, ratio):
    left = bisect.bisect_left(
        gear_sets,
        ratio * (1 - TARGET_ERROR),
        hi=len(gear_sets) - 1,
        key=lambda gs: gs.ratio,
    )
    right = bisect.bisect_right(
            gear_sets,
            ratio * (1 + TARGET_ERROR),
            hi=len(gear_sets) - 1,
            key=lambda gs: gs.ratio,
        ) + 1
    return gear_sets[left:right]


def generete_gear_set(length):
    if length % 2 != 0:
        raise ValueError("Length must be even")
    gear_sets = []
    combinations = list(set([c for c in itertools.combinations(gears, length)]))
    for combination in combinations:
        unpaired = list(itertools.combinations(combination, length // 2))
        paired = zip(unpaired, unpaired[::-1])
        for pair in paired:
            gear_sets.append(GearSet(pair[0], pair[1]))
    return gear_sets


gears = sorted([20, 20, 22, 28, 30, 32, 38, 38, 40, 50, 50, 55, 73])


metric_pitches = [  # mm
    0.15,
    0.20,
    0.25,
    0.30,
    0.35,
    0.40,
    0.45,
    0.50,
    0.60,
    0.70,
    0.75,
    0.80,
    1.00,
    1.25,
    1.50,
    1.75,
    2.00,
    2.50,
    3.00,
    3.50,
    4.00,
    4.50,
    5.00,
    5.50,
    6.00,
]

imperial_pitches = [  # tpi
    180,
    160,
    140,
    120,
    100,
    80,
    72,
    64,
    56,
    48,
    44,
    40,
    36,
    32,
    28,
    26,
    24,
    20,
    19,
    18,
    16,
    14,
    13,
    12,
    11,
    10,
    9,
    8,
    7,
    6,
    5,
    4.5,
    4,
    3.5,
    3,
    2.875,
    2.75,
    2.625,
    2.5,
]


gear_sets = sorted(generete_gear_set(2) + generete_gear_set(4) + generete_gear_set(6))
starting_pitch = 1 / 8  # 8 tpi leadscrew in inches per thread

print()
print("Metric Pitches")
print("-" * 120)
print("  mm \t ratio \t\t Gearsets")
for pitch in metric_pitches:
    ratio = INCH_TO_MM * starting_pitch / pitch
    gear_set = filter_best(filter_ratio(gear_sets, ratio))
    print(f"{pitch:^{PRINT_FORMAT}}\t({ratio:^{PRINT_FORMAT}}) \t->\t{gear_set}")

print()
print("Imperial Pitchs")
print("-" * 120)
print("  tpi \t ratio \t\t GearSets")
for pitch in imperial_pitches:
    ratio = starting_pitch * pitch
    gear_set = filter_best(filter_ratio(gear_sets, ratio))
    print(f"{pitch:^{PRINT_FORMAT}}\t({ratio:^{PRINT_FORMAT}}) \t->\t{gear_set}")
