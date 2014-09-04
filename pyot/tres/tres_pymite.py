import importlib
import os
import pickle
import sys
import traceback

from pyot.models.tres import TResT


def getTaskObject():
    return TResT.objects.get(id=sys.argv[0])


def setOutput(out):
    task = getTaskObject()
    task.emu.output = str(out)
    task.emu.save()
    task.save()
    if task.output is None:
        return
    r = task.output.asyncPUT(payload=str(out))
    return r


def getInput():
    task = getTaskObject()
    return str(task.emu.inp)

# def getInputTag():
#     task = getTaskObject()


def getIntInput():
    task = getTaskObject()
    return int(task.emu.inp)


def getFloatInput():
    task = getTaskObject()
    return float(task.emu.inp)


def getState(cl):
    task = getTaskObject()
    base = os.path.dirname(str(task.pf.sourcefile))
    module = os.path.splitext(os.path.basename(str(task.pf.sourcefile)))[0]
    sys.path.append(base)
    importlib.import_module(module)
    c = cl()
    try:
        return pickle.loads(task.emu._status)
    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        print ''.join('!! ' + line for line in lines)
        task.emu.status = c
        task.emu.save()
        return c


def saveState(cli):
    task = getTaskObject()
    task.emu.status = cli
    task.emu.save()


def pop(def_val):
    task = getTaskObject()
    try:
        return task.emu.pop()
    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        print ''.join('!! ' + line for line in lines)
        return def_val


def push(val):
    task = getTaskObject()
    task.emu.push(val)
    task.emu.save()
    task.save()
