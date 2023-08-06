#! /usr/bin/env python
#! -*- coding:utf-8 -*-


from mwlib.fontswitcher import FontSwitcher


ranges = [
    (11904, 12751),
    (13312, 19903),
    (19968, 40895),    
    (57340, 63555),
    (63744, 64255),
    (65104, 65135),
    (65280, 65375)
    ]

fs = FontSwitcher()

print fs.scripts.getScriptsForCodeBlocks(ranges)
