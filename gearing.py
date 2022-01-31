import itertools
import sortedcontainers

INCH_TO_MM = 25.4
PRECISON = 6 # round to one nanometer per cycle pitch error


class GearSet:
    def __init__(self, gears):
        self.gears = sorted(gears)
        self.ratio = 1
        for pair in list(gears):
            self.ratio *= pair[1] / pair[0]

    def __eq__(self, other: object) -> bool:
        return self.ratio == other.ratio

    def __lt__(self, other: object) -> bool:
        return self.ratio < other.ratio

    def __hash__(self) -> int:
        return hash(tuple(self.gears))

    def __repr__(self) -> str:
        return f'{self.ratio:0.6f} -> [{list(self.gears)}]'


def closest_ratio(ratio, ratio_groups) -> list:
    values = ratio_groups.values()
    x = list(values)
    idx = ratio_groups.bisect_left(ratio)
    if idx == 0:
        return values[0]
    if idx == len(ratio_groups):
        return values[-1]
    lower, upper = ratio_groups.keys()[idx - 1:idx + 1]
    if abs(ratio - lower) < abs(ratio - upper):
        return values[idx - 1]
    return values[idx]


def pick_best(gear_set, preferred_drive_gear, preferred_driven_gear) -> list:
    shortest_train_length = min([len(gs.gears) for gs in gear_set])
    shortest_trains = [gs for gs in gear_set if len(gs.gears) == shortest_train_length]

    preffered_smallest = {st for st in shortest_trains if any(True for s in st.gears if s[0] == preferred_drive_gear)}
    preffered_largest = {st for st in shortest_trains if any(True for s in st.gears if s[1] == preferred_driven_gear)}
    if preffered_smallest & preffered_largest:
        return preffered_smallest & preffered_largest
    elif preffered_smallest:
        return preffered_smallest
    elif preffered_largest:
        return preffered_largest
    return shortest_trains


gears = sorted([20, 20, 22, 26, 28, 30, 32, 38, 45, 50, 50, 55, 73])

metric_pitches = [  # mm
    0.10,
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
    24,
    20,
    18,
    16,
    14,
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


permutations = list(itertools.permutations(gears, 4)) + list(itertools.permutations(gears, 6))
gearsets = sorted({GearSet(x) for x in {tuple(zip(p[::2], p[1::2])) for p in permutations}})

ratio_groups = sortedcontainers.SortedDict()
for gs in gearsets:
    ratio_groups.setdefault(gs.ratio, []).append(gs)

starting_pitch = 1 / 8  # 8 tpi leadscrew in inches per thread

print()
print('Metric Pitches')
print('-' * 120)
print('  mm \t actual \t\t Gearsets')
for pitch in metric_pitches:
    ratio = INCH_TO_MM * starting_pitch / pitch
    best = pick_best(closest_ratio(ratio, ratio_groups), gears[1], gears[-1])
    print(f'{pitch:0.3f}\t({INCH_TO_MM * starting_pitch / next(iter(best)).ratio:0.3f}) \t->\t{[b.gears for b in best]}')

print()
print('Imperial Pitchs')
print('-' * 120)
print('  tpi \t actual \t\t GearSets')
for pitch in imperial_pitches:
    ratio = starting_pitch * pitch
    best = pick_best(closest_ratio(ratio, ratio_groups), gears[1], gears[-1])
    print(f'{pitch:0.3f}\t({next(iter(best)).ratio / starting_pitch:0.3f}) \t->\t{[b.gears for b in best]}')
