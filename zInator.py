#!/usr/bin/env python
"""
zInator - comenta/copia los cambios en Z al mover el cabezal a la primera capa, para asegurar que se
          hace despues del movimiento en los ejes XY
          se comprueba la altura de Z antes de realizar cualquier cambio, y solamente se hace si
          el valor detectado para la altura de Z en ese momento es de al menos 1mm.

"""

import os
import re
import argparse


def comment(strline):
    return '; zInator commented ;' + strline

def rewrite(infile, outfile, verbose=False):
    done = False # marca de que hemos acabado, el resto se copia tal cual
    in_loop = False # marca si hemos pasado del primer LAYER_CHANGE
    z_up = False # si True, se ha detectado que Z esta alta (mas de z_up_distance en mm)
    z_up_distance = 1 # min. distancia en mm para considerar que Z esta alta
    z_down = '' # almacenamos el primer comando para llevar Z a la 1era capa
    pre_z = 0


    for line in infile:

        if done:
            outfile.write(line)
            continue

        line_out = line # linea a escribir al final, si llega

        if line.startswith(';LAYER_CHANGE'):
            in_loop = True
            if pre_z > z_up_distance:
                z_up =True
            outfile.write(';--- zInator script BEGIN - current Z='+str(pre_z)+' (minimum='+str(z_up_distance)+') \n')

        if in_loop and line.startswith('G1 X'):
            done = True
            if z_up and z_down != '':
                outfile.write(line)
                outfile.write(';next line added by zInator'+'\n')
                outfile.write(z_down)
                line_out = ';--- zInator script END'+'\n'
            else:
                outfile.write(line)
                line_out = ';--- zInator script END - NO LUCK!'+'\n'

        if line.startswith('G1 Z'):
            zpos = get_z_height(line)

            if in_loop:
                if z_up:
                    if z_down == '': # es la primera bajada, se guarda
                        z_down = line
                    line_out = comment(line) # se comentan todas las subidas/bajadas tras la primera
            else:
                pre_z = zpos
                #print('pre_z['+str(zpos)+']')
                #print(line)

        outfile.write(line_out)


def get_z_height(line):
    m = re.search(r'Z(\d+\.\d*|\.\d*|\d*)',line)
    pos =''
    zpos = 0
    if m is not None:
        pos = line[m.start()+1:m.end()]
        pos = '0'+pos
        zpos = float(pos)
    #print('pos['+pos+']zpos['+str(zpos)+']')
    return zpos

### -------- parte estandar, copiada de otro script de limpieza

def parse_args():
    parser = argparse.ArgumentParser(
        description='Gcode cleaner to work around some Z height issues in PrusaSlicer.'
    )
    parser.set_defaults(
        verbose=False,
        overwrite=False,
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help="Enable additional debug output",
    )
    parser.add_argument(
        '--overwrite',
        action='store_true',
        help="Overwrite the input file",
    )
    parser.add_argument(
        'filename',
        type=argparse.FileType('r'),
        nargs='+',
        help="One or more paths to .gcode files to clean",
    )
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    for infile in args.filename:
        infilename = infile.name
        tmpfilename = '{}.tmp{}'.format(*os.path.splitext(infilename))
        with open(tmpfilename, 'w') as tmpfile:
            rewrite(infile, tmpfile, args.verbose)
        infile.close()
        if args.overwrite:
            outfilename = infilename
        else:
            outfilename = '{}{}'.format(*os.path.splitext(infilename))
        if infilename == outfilename:
            os.unlink(infilename)
        os.rename(tmpfilename, outfilename)
        print("{}\n  => {}".format(infilename, outfilename))
        
