import os, sys
from subprocess import Popen, PIPE
import zipfile, shutil, tempfile


def systemCommand(command, justRun=False):
    error = None
    output = None
    try:
        if not justRun:
            p = Popen(command, shell=True, stderr=PIPE, stdin=PIPE, stdout=PIPE)
            error = p.stderr.read()
            output = p.stdout.read()
            del(p)
        else:
            os.system(command)
    except Exception, e:
        if error:
            error += str(e)
        else:
            error = str(e)
    return(output, error)


def makeZip(base_path, output_path, archive_file, work_dir=None, skip_dirs=[], skip_files=[]):
    """zip a directory"""
    if not work_dir:
        work_dir = os.getcwd()
    if not os.path.isdir(base_path):
        os.chdir(work_dir)
        return False
    os.chdir(base_path)
    output_file = "%s%s%s" % (output_path, os.sep, archive_file)
    z = zipfile.ZipFile(output_file, mode="w", compression=zipfile.ZIP_DEFLATED)
    try:
        local = '.'
        if os.name == 'nt':
            local = ''
        for dirpath, dirs, files in os.walk(local):
            skip = False
            for sd in skip_dirs:
                if dirpath.startswith(sd):
                    skip = True
            if skip:
                continue
            for a_file in files:
                if a_file in skip_files:
                    continue
                a_path = os.path.join(dirpath, a_file)
                z.write(a_path, a_path)
        z.close()
    finally:
        z.close()
        os.chdir(work_dir)
    if os.path.isfile(output_file):
        return True
    return False


def _check_dirs(out_dir):
    if not os.path.isdir(out_dir):
        root, new_dir = os.path.split(out_dir)
        if not os.path.isdir(root):
            _check_dirs(root)
        os.mkdir(out_dir)   
    

   
def unzip(data, dir=None):
    if not dir:
        dir = os.getcwd()
    fname = tempfile.mktemp(dir=dir)
    fh = open("%s.zip" % fname, 'w')
    fh.write(data)
    fh.close()
    z = zipfile.ZipFile("%s.zip" % fname)
    for name in z.namelist():
        if name.endswith('/'):
            os.mkdir(os.path.join(dir, name))
        else:
            outfile = os.path.join(dir, name)
            out_dir, f = os.path.split(outfile)
            _check_dirs(out_dir)
            outfh = open(outfile, 'w')
            outfh.write(z.read(name))
            outfh.close()
    os.unlink("%s.zip" % fname)


def clean(base_path, target, work_dir=None, ignoreErrors=False):
    if not work_dir:
        work_dir = os.getcwd()
    if not os.path.isdir(base_path):
        os.chdir(work_dir)
        return False
    os.chdir(base_path)
    if os.path.isdir(target):
        shutil.rmtree(target, ignore_errors=ignoreErrors)
        for root, dirs, files in os.walk(target, topdown=False):
            try:
                [os.unlink(os.path.join(root, file)) for file in files]
                for d in dirs:
                    for file in os.listdir(d):
                        os.unlink(os.path.join(os.path.join(root, d), file))
                        os.rmdir(os.path.join(root, d))
                os.rmdir(root)
            except OSError, e:
                if ignoreErrors:
                    pass
                else:
                    os.chdir(work_dir)
                    return False
        os.chdir(work_dir)
        return True
    else:
        os.chdir(work_dir)
        return False
