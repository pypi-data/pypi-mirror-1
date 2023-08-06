"""
some helpers for the test suite
"""
import os
import shutil
import os.path as osp
import ovcs

DATAPATH = osp.join(osp.split(ovcs.__file__)[0], 'tests', 'data')


def fullpath(basepath):
    path = osp.join(DATAPATH, basepath)
    return path

def cleanup(fset, global_cleanset):
    for path in fset:
        try:
            if osp.isdir(path):
                shutil.rmtree(path)
            else:
                os.unlink(path)
        except:
            global_cleanset.add(path)

def shutdown(cleanset):
    emptyset = set()
    cleanup(cleanset, emptyset)
    assert len(emptyset) == 0, '%s' % emptyset
