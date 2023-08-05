"""Run Deliverance with an appropriately configured environment
"""

import os, sys

def main(args=None):
    
    lib_path = args[0]
    
    paster = args[1]
    ini_path = args[2]
        
    env = os.environ.copy()
    env['PYTHONPATH'] = os.path.pathsep.join(sys.path)
    if lib_path:
        env['DYLD_LIBRARY_PATH'] = env['LD_LIBRARY_PATH'] = lib_path

    os.execve(paster, [paster, 'serve', ini_path] + args[3:], env)