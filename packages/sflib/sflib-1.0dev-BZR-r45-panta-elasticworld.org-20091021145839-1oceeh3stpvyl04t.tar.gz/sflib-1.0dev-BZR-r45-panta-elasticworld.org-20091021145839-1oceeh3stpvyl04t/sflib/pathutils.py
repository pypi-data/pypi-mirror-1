import os

def splitpath(pathname, normalize=True):
    """
    Split the ``pathname`` into all its components.

    NOTE: This is DIFFERENT from os.path.split()!.

    >>> splitpath('aaa/bbb/ccc/ddd.txt')
    ['aaa', 'bbb', 'ccc', 'ddd.txt']

    >>> splitpath('/aaa/bbb/ccc/ddd.txt')
    ['/', 'aaa', 'bbb', 'ccc', 'ddd.txt']

    >>> splitpath('/aaa/bbb/ccc/')
    ['/', 'aaa', 'bbb', 'ccc']

    >>> splitpath('/')
    ['/']
    """

    assert isinstance(pathname, basestring)

    pathsep = os.path.sep

    if normalize:
        pathname = os.path.normcase(os.path.normpath(pathname))
        pathsep  = os.path.normcase(os.path.normpath(pathsep))

    if pathname == pathsep:
        return [pathsep,]

    comps = pathname.split(pathsep)
    if (len(comps) == 2) and (comps == ['', '']):
        return [pathsep,]

    if (len(comps) > 0) and (comps[0] == ''):
        comps[0] = pathsep
    return comps

def joinpath(components, normalize=True):
    """
    Inverse of splitpath

    >>> joinpath(['aaa', 'bbb', 'ccc', 'ddd.txt'])
    'aaa/bbb/ccc/ddd.txt'

    >>> joinpath(['/', 'aaa', 'bbb', 'ccc', 'ddd.txt'])
    '/aaa/bbb/ccc/ddd.txt'

    >>> joinpath(['/', 'aaa', 'bbb', 'ccc'])
    '/aaa/bbb/ccc'

    >>> joinpath(['/'])
    '/'
    """

    components = list(components)
    pathsep = os.path.sep

    if normalize:
        components = [os.path.normcase(os.path.normpath(c)) for c in components]
        pathsep  = os.path.normcase(os.path.normpath(pathsep))

    if (len(components) == 1) and (components[0] == pathsep):
        return pathsep
    elif (len(components) > 1) and (components[0] == pathsep):
        components[0] = ''

    return pathsep.join(components)

def commonpath(pathname1, pathname2, normalize=True):
    """
    Similar to os.path.commonprefix(), but this version doesn't work
    character-by-character, but by logical path components.

    Return a *list* of the common path components.

    >>> commonpath('/abc/def/ghi', '/abc/def')
    ['/', 'abc', 'def']

    >>> commonpath('/abc/def/ghi/', '/abc/def')
    ['/', 'abc', 'def']

    >>> commonpath('/abc/def/ghi', '/abc/def/')
    ['/', 'abc', 'def']

    >>> commonpath('/abc/def/ghi/', '/abc/def/')
    ['/', 'abc', 'def']

    >>> commonpath('/abc/def/ghi', '/abc/def/gh')
    ['/', 'abc', 'def']

    >>> commonpath('/abc/def/ghi/jkl', '/abc/def/mmm/nnn')
    ['/', 'abc', 'def']
    """

    if normalize:
        pathname1 = os.path.normcase(os.path.normpath(pathname1))
        pathname2 = os.path.normcase(os.path.normpath(pathname2))

    p1_components = splitpath(pathname1)
    p2_components = splitpath(pathname2)

    l1 = len(p1_components)
    l2 = len(p2_components)
    min_l = l1
    if l2 < l1:
        min_l = l2

    common = []
    i = 0
    while i < min_l:
        c1 = p1_components[i]
        c2 = p2_components[i]

        if c1 == c2:
            common.append(c1)
        else:
            break
        i += 1
    return common

def is_common_path(base, pathname, normalize=True):
    """
    Return True if ``base`` is common to ``pathname``,
    False otherwise.

    >>> is_common_path('/aaa/bbb', '/aaa/bbb/ccc/ddd.txt')
    True

    >>> is_common_path('aaa/bbb', 'aaa/bbb/ccc/ddd.txt')
    True

    >>> is_common_path('/aaa/bbb/', '/aaa/bbb/ccc/ddd.txt')
    True

    >>> is_common_path('aaa/bbb/', 'aaa/bbb/ccc/ddd.txt')
    True

    >>> is_common_path('/aaa/bbb', 'aaa/bbb/ccc/ddd.txt')
    False

    >>> is_common_path('/aaa/bbb/', 'aaa/bbb/ccc/ddd.txt')
    False

    >>> is_common_path('aaa/bbb', '/aaa/bbb/ccc/ddd.txt')
    False

    >>> is_common_path('aaa/bbb/', '/aaa/bbb/ccc/ddd.txt')
    False

    >>> is_common_path('aaa/bbb', 'aaa/bbb')
    True

    >>> is_common_path('aaa/bbb', 'aaa/bbb/')
    True

    >>> is_common_path('aaa/bbb/', 'aaa/bbb')
    True
    """

    if normalize:
        pathname = os.path.normcase(os.path.normpath(pathname))
        base     = os.path.normcase(os.path.normpath(base))

    common = commonpath(pathname, base, normalize=normalize)

    base_components = splitpath(base)

    if ((len(base_components) == len(common)) and
        (base_components == common)):
        return True
    return False

def relativepath(pathname, base, normalize=True):
    """
    Return the part of ``pathname`` relative to ``base``.

    Similar to os.path.relpath(), but not only for Python 2.6, and this version
    doesn't work char-by-char, but by logical path components.

    >>> relativepath('/aaa/bbb/ccc/ddd.txt', '/sss/fff')
    '/aaa/bbb/ccc/ddd.txt'

    >>> relativepath('/aaa/bbb/ccc/ddd.txt', '/aaa/bbb')
    'ccc/ddd.txt'

    >>> relativepath('/aaa/bbb/ccc/ddd.txt', '/aaa/bbb/')
    'ccc/ddd.txt'

    >>> relativepath('/aaa/bbb/ccc/ddd.txt', '/aaa/bb')
    '/aaa/bbb/ccc/ddd.txt'

    >>> relativepath('/aaa/bbb/ccc/ddd.txt', '/aaa/bbb/ccc')
    'ddd.txt'

    >>> relativepath('/aaa/bbb/ccc/ddd.txt', '/aaa/bbb/ccc/ddd')
    '/aaa/bbb/ccc/ddd.txt'

    >>> relativepath('/aaa/bbb/ccc/ddd.txt', '/aaa/bbb/ccc/ddd.txt')
    ''

    >>> relativepath('aaa/bbb/ccc/ddd.txt', 'sss/fff')
    'aaa/bbb/ccc/ddd.txt'

    >>> relativepath('aaa/bbb/ccc/ddd.txt', 'aaa/bbb')
    'ccc/ddd.txt'

    >>> relativepath('aaa/bbb/ccc/ddd.txt', 'aaa/bbb/')
    'ccc/ddd.txt'

    >>> relativepath('aaa/bbb/ccc/ddd.txt', 'aaa/bb')
    'aaa/bbb/ccc/ddd.txt'

    >>> relativepath('aaa/bbb/ccc/ddd.txt', 'aaa/bbb/ccc')
    'ddd.txt'

    >>> relativepath('aaa/bbb/ccc/ddd.txt', 'aaa/bbb/ccc/ddd')
    'aaa/bbb/ccc/ddd.txt'

    >>> relativepath('aaa/bbb/ccc/ddd.txt', 'aaa/bbb/ccc/ddd.txt')
    ''

    >>> relativepath('aaa/bbb/ccc/ddd.txt', '/aaa/bbb')
    'aaa/bbb/ccc/ddd.txt'

    >>> relativepath('/aaa/bbb/ccc/ddd.txt', 'aaa/bbb')
    '/aaa/bbb/ccc/ddd.txt'

    >>> relativepath('/aaa/bbb/ccc', '/')
    'aaa/bbb/ccc'

    >>> relativepath('aaa/bbb/ccc', '/')
    'aaa/bbb/ccc'

    >>> relativepath('/', '')
    '/'

    >>> relativepath('/', '/')
    '/'
    """

    pathsep = os.path.sep

    if normalize:
        pathname = os.path.normcase(os.path.normpath(pathname))
        base     = os.path.normcase(os.path.normpath(base))
        pathsep  = os.path.normcase(os.path.normpath(pathsep))

    if ((pathname == pathsep) and (base == pathsep)):
        return pathname

    pathname_components = splitpath(pathname)
    base_components     = splitpath(base)

    if len(base_components) > len(pathname_components):
        return pathname

    assert len(base_components) <= len(pathname_components)

    min_l = len(base_components)

    if base_components != pathname_components[:min_l]:
        return pathname

    assert base_components == pathname_components[:min_l]

    return joinpath(pathname_components[min_l:])

if __name__ == '__main__':
    import doctest
    doctest.testmod()
