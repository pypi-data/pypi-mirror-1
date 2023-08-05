cdef extern from "stdlib.h":
    ctypedef unsigned int size_t
    cdef void *malloc(size_t size)
    cdef void free(void *ptr)
    cdef void *realloc(void *ptr, size_t size)

    ctypedef int(*compar_func)(void *, void *)
    cdef void qsort(void *base, size_t nmemb, size_t size, compar_func compar)


def collide(objects):
    """
    collide(objects) -> list of collisions

    Collides objects, first using rdc and then using brute_force.

    Each object should have the attributes x, y, bounding_radius, and
    bounding_radius_squared.
    """
    collisions = []
    for group in rdc(objects, min_split=10):
        if len(group) > 1:
            collisions.extend(brute_force(group))
    return collisions


cdef enum _Side:
    LEFT=1
    RIGHT=2

cdef enum _Axis:
    X=1
    Y=2

cdef struct side_s:
    float x,y
    _Side side
    int index

cdef int _compar_sides_x(void *p1, void *p2):
    cdef float x1, x2
    x1 = (<side_s**>p1)[0][0].x
    x2 = (<side_s**>p2)[0][0].x
    if x1 < x2:
        return -1
    elif x1 > x2:
        return 1
    else:
        return 0

cdef int _compar_sides_y(void *p1, void *p2):
    cdef float y1, y2
    y1 = (<side_s**>p1)[0][0].y
    y2 = (<side_s**>p2)[0][0].y
    if y1 < y2:
        return -1
    elif y1 > y2:
        return 1
    else:
        return 0

def rdc(objects, int min_split=1, int max_depth=0):
    """
    rdc(objects, [max_depth,] [min_split]) -> list of collision groups

    Uses the Recursive Dimensional Clustering algorithm to find groups of
    colliding objects.

    objects should be a list of objects.  Each object should have the attributes
    x, y, and bounding_radius.

    If the number of objects in a collision group is less than min_split,
    recursion will stop.  This defaults to 1, but in practice, it is usually
    faster to just use a brute force method once a group gets down to 10
    objects.

    max_depth is the maximum number of recursions to make.  It defaults to 0,
    which is infinite.

    Instead of returning individual collisions, rdc returns groups (lists) of
    colliding objects.  For example, if A collides with B and B collides with C,
    one of the groups will be [A, B, C], even though A and C don't directly
    collide.

    Also, each object is returned at most once.  If it is in one group, it won't
    be in any other.  An object without any collisions isn't returned at all.
    """

    cdef side_s * side_list
    cdef side_s ** side_p_list
    cdef int length, i, d, group_start
    cdef float r, x, y
    length = len(objects)*2

    side_list = <side_s*>malloc(sizeof(side_s)*length)
    side_p_list = <side_s**>malloc(sizeof(side_s*)*length)
    try:
        for i from 0 <= i < length/2:
            o = objects[i]
            r = o.bounding_radius
            x = o.x
            y = o.y
            side_list[i*2].x = x-r
            side_list[i*2].y = y-r
            side_list[i*2].side = LEFT
            side_list[i*2].index = i
            side_list[i*2+1].x = x+r
            side_list[i*2+1].y = y+r
            side_list[i*2+1].side = RIGHT
            side_list[i*2+1].index = i

            side_p_list[i*2] = &side_list[i*2]
            side_p_list[i*2+1] = &side_list[i*2+1]

        _rdc(side_p_list, length, X, 0, min_split, max_depth)

        groups = []
        current_group = []
        d = 0
        for i from 0 <= i < length:
            if side_p_list[i][0].side == LEFT:
                if d == 0:
                    # Check to see if we are a single object without any
                    # collisions.  If so, we shouldn't be added as a group.
                    # (Doing this can cut running time in half.)
                    if side_p_list[i][0].index == side_p_list[i+1][0].index:
                        # The next item will be the right side of the same
                        # object; we can safely skip it.
                        i = i + 1
                        continue
                d = d + 1
                current_group.append(objects[side_p_list[i][0].index])
            else:
                d = d - 1
                if d == 0:
                    groups.append(current_group)
                    current_group = []
        return groups
    finally:
        free(side_list)
        free(side_p_list)

cdef void _rdc(side_s ** side_p_list, int length, _Axis axis, int depth,
        int min_split, int max_depth):
    cdef int i
    if length <= min_split*2:
        return
    if max_depth > 0 and depth >= max_depth:
        return

    cdef _Axis next_axis

    if axis == X:
        qsort(side_p_list, length, sizeof(side_s*), _compar_sides_x)
        next_axis = Y
    else:
        qsort(side_p_list, length, sizeof(side_s*), _compar_sides_y)
        next_axis = X

    cdef int group_start, d

    group_start = 0
    d = 0
    for i from 0 <= i < length:
        if group_start == 0 and i == length-1:
            # We only have one group. If we are the first call, go ahead and try
            # the Y access.  Otherwise, let's just bail out now.
            if depth == 0:
                _rdc(side_p_list, length, Y, 1, min_split, max_depth)
            return

        if side_p_list[i][0].side == LEFT:
            d = d + 1
        else:
            d = d - 1
            if d == 0:
                _rdc(&side_p_list[group_start], i-group_start+1, next_axis,
                        depth+1, min_split, max_depth)
                group_start = i + 1



cdef struct collision_object_s:
    float x, y, brs

cdef _brute_force(collision_object_s * objs, int length, objects):
    cdef float dx, dy
    cdef int i, j
    collisions = []
    for i from 0 <= i < length-1:
        for j from i < j < length:
            dx = objs[i].x - objs[j].x
            dy = objs[i].y - objs[j].y
            if dx*dx + dy*dy < objs[i].brs + objs[j].brs:
                collisions.append((objects[i],
                        objects[j]))
    return collisions

def brute_force(objects):
    """
    brute_force(objects) -> list of collisions

    Finds collisions between objects using a brute force algorithm.

    objects should be a list of objects, each of which have the attributes x, y,
    and bounding_radius_squared.  Each object is checked against every other
    object.

    For example, if A collides with B, B collides with C, and D doesn't collide
    with anything, the result will be: [(A, B), (B, C)]
    """
    cdef collision_object_s * objs
    cdef int i, length

    length = len(objects)
    objs = <collision_object_s*>malloc(sizeof(collision_object_s)*length)
    try:
        # First we move the data from the python objects into c structures.
        # This is especially important as most of the objects will be sprites,
        # and accessing their positions could set off a long chain of
        # calculations.  We only want to do that once.
        for i from 0 <= i < length:
            o = objects[i]
            objs[i].x = o.x
            objs[i].y = o.y
            objs[i].brs = o.bounding_radius_squared
        # Do the actual work:
        return _brute_force(objs, length, objects)
    finally:
        free(objs)
