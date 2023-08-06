mono_overview = [((1, 2), (3, 4), (5, 6))]
mono_zapped = [((1, 2),), ((3,  4),), ((5, 6),)]

assert zip(*mono_overview) == mono_zapped
assert zip(*mono_zapped) == mono_overview


stereo_overview = [((1,2), (3, 4), (5, 6)), ((-1, -2), (-3, -4), (-5, -6))]
stereo_zapped = [((1, 2), (-1, -2)), ((3,  4), (-3,  -4)), ((5, 6), (-5, -6))]

assert zip(*stereo_overview) == stereo_zapped 
assert zip(*stereo_zapped) == stereo_overview
