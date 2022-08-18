from plover.steno import Stroke

from typing import List, Tuple

KEYS = [
    ("#", "num", "num_n"),
    ("S-", "ls", "ls_n"),
    ("T-", "lt", "lt_n"),
    ("K-", "lk", "lk_n"),
    ("P-", "lp", "lp_n"),
    ("W-", "lw", "lw_n"),
    ("H-", "lh", "lh_n"),
    ("R-", "lr", "lr_n"),
    ("A-", "la", "la_n"),
    ("O-", "lo", "lo_n"),
    ("*", "star", "star_n"),
    ("-E", "re", "re_n"),
    ("-U", "ru", "ru_n"),
    ("-F", "rf", "rf_n"),
    ("-R", "rr", "rr_n"),
    ("-P", "rp", "rp_n"),
    ("-B", "rb", "rb_n"),
    ("-L", "rl", "rl_n"),
    ("-G", "rg", "rg_n"),
    ("-T", "rt", "rt_n"),
    ("-S", "rs", "rs_n"),
    ("-D", "rd", "rd_n"),
    ("-Z", "rz", "rz_n")
]


def convert_stroke(stroke: Tuple[str, ...], _: str) -> List[str]:
    return [pos if key in stroke else neg for (key, pos, neg) in KEYS]
