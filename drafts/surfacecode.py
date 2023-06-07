# Contributor: Haochen Li
# Licensed under GPLV3

import stac
import bidict


def _surface_codes_syndrome_measurements(row, col):
    '''
    This function creates syndrome measurement circuit with surface code of any dimension. 

    Parameter
    -----------
    col : int > 0
        The number of qubits in a horizontal line. 

    row : int > 0
        The number of qubits in a vertical line.


    Return
    --------
    stac.Circuit with appended gates
    '''

    surface_code_circ = stac.Circuit()
    num = row * col

    # determine the number of data points and syndrome points
    if row % 2 == 0:
        d_num = s_num = num // 2
    else:
        if col % 2 == 0:
            d_num = s_num = num // 2
        else:
            d_num = (num + 1) // 2
            s_num = d_num - 1

    surface_code_circ.append_register(stac.QubitRegister('d', 0, d_num))
    surface_code_circ.append_register(stac.QubitRegister('s', 0, s_num))

    # assign coordinates
    surface_code_circ.physical_register.elements = \
        [stac.PhysicalQubit(col*i+j, (j, i), [])
         for i in range(row) for j in range(col)]

    surface_code_circ.layout_map = bidict.bidict()

    d_i = 0
    s_i = 0

    for i in range(row):
        if i % 2 == 0:
            for j in range(col):
                if j % 2 == 0:
                    surface_code_circ.register[(
                        0, 0, d_i)].constituent_register = surface_code_circ.physical_register.elements[col*i+j]
                    surface_code_circ.layout_map[(0, 0, d_i)] = (j, i)
                    d_i += 1

                else:
                    surface_code_circ.register[(
                        0, 1, s_i)].constituent_register = surface_code_circ.physical_register.elements[col*i+j]
                    surface_code_circ.layout_map[(0, 1, s_i)] = (j, i)
                    s_i += 1

        else:
            for j in range(col):
                if j % 2 != 0:
                    surface_code_circ.register[(
                        0, 0, d_i)].constituent_register = surface_code_circ.physical_register.elements[col*i+j]
                    surface_code_circ.layout_map[(0, 0, d_i)] = (j, i)
                    d_i += 1

                else:
                    surface_code_circ.register[(
                        0, 1, s_i)].constituent_register = surface_code_circ.physical_register.elements[col*i+j]
                    surface_code_circ.layout_map[(0, 1, s_i)] = (j, i)
                    s_i += 1

    # create circuit
    surface_code_circ.clear()

    for qubit in surface_code_circ.register[(0, 1)].qubits():

        s_coordinate = qubit.constituent_register.coordinates

        d_1 = (
            qubit.constituent_register.coordinates[0], qubit.constituent_register.coordinates[1]+1)
        d_2 = (
            qubit.constituent_register.coordinates[0]-1, qubit.constituent_register.coordinates[1])
        d_3 = (
            qubit.constituent_register.coordinates[0]+1, qubit.constituent_register.coordinates[1])
        d_4 = (
            qubit.constituent_register.coordinates[0], qubit.constituent_register.coordinates[1]-1)

        if s_coordinate[1] % 2 == 0:  # Z

            for i in [d_1, d_2, d_3, d_4]:
                if -1 < i[0] < col and -1 < i[1] < row:
                    surface_code_circ.geo_append('CX', i, s_coordinate)

            surface_code_circ.geo_append('TICK')

        else:  # X
            surface_code_circ.geo_append('H', s_coordinate)

            for i in [d_1, d_2, d_3, d_4]:
                if -1 < i[0] < col and -1 < i[1] < row:
                    surface_code_circ.geo_append('CX', s_coordinate, i)

            surface_code_circ.geo_append('H', s_coordinate)
            surface_code_circ.geo_append('TICK')

    return surface_code_circ
