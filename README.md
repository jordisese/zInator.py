# zInator.py
post-processing script for PrusaSlicer. checks initial Z height and moves Z lowering to first layer after XY movement

          comenta/copia los cambios en Z al mover el cabezal a la primera capa, para asegurar que se
          hace despues del movimiento en los ejes XY
          se comprueba la altura de Z antes de realizar cualquier cambio, y solamente se hace si
          el valor detectado para la altura de Z en ese momento es de al menos 1mm.

