# Copyright (C) 2008, Charles Wang <charlesw1234@163.com>
# Author: Charles Wang <charlesw1234@163.com>

import filecmp
import os
import os.path

def ensure_dir(dir):
    if not os.path.isdir(dir): os.makedirs(dir)

def smart_write(fpath, content):
    if os.path.isfile(fpath) or os.path.islink(fpath):
        f = file(fpath)
        orig_content = f.read()
        f.close()
        if orig_content == content: return False
    f = file(fpath, 'w')
    f.write(content)
    f.close()
    return True

def smart_symlink(src, dst):
    if os.path.islink(dst):
        if os.readlink(dst) == src: return False
        os.remove(dst)
    elif os.path.isfile(dst):
        if filecmp.cmp(dst, src): return False
        os.remove(dst)
    os.symlink(src, dst)
    return True

def uniq_extend(result, added):
    for a in added:
        if a not in result: result.append(a)
    return result
