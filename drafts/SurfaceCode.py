#d is the distance of the surface code. This function supports symmetrical surface code with an odd value of d
def _surface_codes_syndrome_measurements(d):
    import stac
    surface_code_circ = stac.Circuit()

    row = d
    col = row
    num = row * col

    s_no = num-1
    d_no = num

    surface_code_circ.append_register(stac.QubitRegister('d', 0, d_no))
    surface_code_circ.append_register(stac.QubitRegister('s', 0, s_no))

    surface_code_circ.register.structure()

    #Manually create circ.layout_map and map the virtual qubits to these physical qubits 

    import bidict
    surface_code_circ.physical_register.elements = [stac.PhysicalQubit(i, i, []) for i in range(surface_code_circ.num_qubits)]

    surface_code_circ.layout_map = bidict.bidict()

    for i in range(d_no):
        surface_code_circ.register[(0,0,i)].constituent_register = surface_code_circ.physical_register.elements[i]
        surface_code_circ.layout_map[(0,0,i)] = i

    for j in range(s_no):
        surface_code_circ.register[(0,1,j)].constituent_register = surface_code_circ.physical_register.elements[j+d_no]
        surface_code_circ.layout_map[(0,1,j)] = j+d_no
    
    #Create a data point map
    num_coordinate = {}

    for i in range(row):
        for j in range(col):
            #print(i*col+j , end=' ')
            num_coordinate[i*col+j] = (i, j)
        #print()

    #print(num_coordinate)

    #To obatain the coordinates of the two data point X
    two_cnot_X_coordinate = {}

    m = 1
    for i in range(0, col, 2):
        if num_coordinate[i][0] == num_coordinate[i+1][0]:
            two_cnot_X_coordinate[m] = (i, i+1)
            m += 1
        
    for i in range(num-1, num-col-1, -2):
        if num_coordinate[i][0] == num_coordinate[i-1][0]:
            two_cnot_X_coordinate[m] = (i-1, i)
            m += 1
    #print(two_cnot_X_coordinate)

    four_cnot_X_upper_coordinate = {}
    four_cnot_X_lower_coordinate = {}

    n = len(two_cnot_X_coordinate) + 1
    for i in range(1, num, 2):
        if i+d in num_coordinate:
            if (i, i+1) not in four_cnot_X_lower_coordinate.values():
                if num_coordinate[i][0] == num_coordinate[i+1][0]:
                    four_cnot_X_upper_coordinate[n] = (i, i+1)
                    four_cnot_X_lower_coordinate[n] = (i+d, i+1+d)
                    n += 1

    #print(four_cnot_X_upper_coordinate)
    #print(four_cnot_X_lower_coordinate)


    #Do the same to Z
    two_cnot_Z_coordinate = {}

    m = 1 + len(two_cnot_X_coordinate) + len(four_cnot_X_upper_coordinate)
    for i in range(1, num-col):
        if num_coordinate[i][0] != num_coordinate[i+1][0] or num_coordinate[i][0] != num_coordinate[i-1][0]:
            if (i-col, i) not in two_cnot_Z_coordinate.values():
                two_cnot_Z_coordinate[m] = (i, i+col)
                m += 1

    #print(two_cnot_Z_coordinate)

    four_cnot_Z_upper_coordinate = {}
    four_cnot_Z_lower_coordinate = {}

    n = len(two_cnot_Z_coordinate) + 1 + len(two_cnot_X_coordinate) + len(four_cnot_X_upper_coordinate)
    for i in range(0, num, 2):
        if i+d in num_coordinate:
            if (i, i+1) not in four_cnot_Z_lower_coordinate.values():
                if num_coordinate[i][0] == num_coordinate[i+1][0]:
                    four_cnot_Z_upper_coordinate[n] = (i, i+1)
                    four_cnot_Z_lower_coordinate[n] = (i+d, i+1+d)
                    n += 1

    #print(four_cnot_Z_upper_coordinate)
    #print(four_cnot_Z_lower_coordinate)

    #Create the syndrome circuit
    #X
    two_cnot_X = d-1
    four_cnot_X = s_no//2 - two_cnot_X
    surface_code_circ.clear()
    s_start = d_no - 1

    for i in two_cnot_X_coordinate:
        s_qubit = i + s_start
        d_qubit1 = two_cnot_X_coordinate[i][0]
        d_qubit2 = two_cnot_X_coordinate[i][1]
        surface_code_circ.geo_append('H', s_qubit)
        surface_code_circ.geo_append('CX', s_qubit,  d_qubit1)
        surface_code_circ.geo_append('CX', s_qubit, d_qubit2)
        surface_code_circ.geo_append('H', s_qubit)
        surface_code_circ.geo_append('TICK')

    for i in four_cnot_X_upper_coordinate:
        s_qubit = i + s_start
        d_qubit1 = four_cnot_X_upper_coordinate[i][0]
        d_qubit2 = four_cnot_X_upper_coordinate[i][1]
        d_qubit3 = four_cnot_X_lower_coordinate[i][0]
        d_qubit4 = four_cnot_X_lower_coordinate[i][1]
        surface_code_circ.geo_append('H', s_qubit)
        surface_code_circ.geo_append('CX', s_qubit, d_qubit1)
        surface_code_circ.geo_append('CX', s_qubit, d_qubit2)
        surface_code_circ.geo_append('CX', s_qubit, d_qubit3)
        surface_code_circ.geo_append('CX', s_qubit, d_qubit4)
        surface_code_circ.geo_append('H', s_qubit)
        surface_code_circ.geo_append('TICK')

    #Z
    for i in two_cnot_Z_coordinate:
        s_qubit = i + s_start
        d_qubit1 = two_cnot_Z_coordinate[i][0]
        d_qubit2 = two_cnot_Z_coordinate[i][1]
        surface_code_circ.geo_append('CX', d_qubit1,  s_qubit)
        surface_code_circ.geo_append('CX', d_qubit2, s_qubit)
        surface_code_circ.geo_append('TICK')

    for i in four_cnot_Z_upper_coordinate:
        s_qubit = i + s_start
        d_qubit1 = four_cnot_Z_upper_coordinate[i][0]
        d_qubit2 = four_cnot_Z_upper_coordinate[i][1]
        d_qubit3 = four_cnot_Z_lower_coordinate[i][0]
        d_qubit4 = four_cnot_Z_lower_coordinate[i][1]
        surface_code_circ.geo_append('CX', d_qubit1, s_qubit)
        surface_code_circ.geo_append('CX', d_qubit2, s_qubit)
        surface_code_circ.geo_append('CX', d_qubit3, s_qubit)
        surface_code_circ.geo_append('CX', d_qubit4, s_qubit)
        surface_code_circ.geo_append('TICK')

    for i in range(s_start, s_no+d_no):
        surface_code_circ.geo_append('MR', i)
        #print(i)

    surface_code_circ.draw()
    surface_code_circ._draw_text()

#run the function, you can change the parameter. However, the parameter must be an odd number
_surface_codes_syndrome_measurements(3)