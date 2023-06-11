#Contributor: Victor Onofre
#Licensed under GPLV3

import stac
import networkx as nx


def vertices_physical_qubits(N):
    '''
    Creates graph for coordinates of the vertices/physical qubits with 4.8.8 color code family

    Parameter
    -----------
    N : distance

    Return
    --------
    H : Graph for coordinates of the vertices/physical qubits
    faces: Faces of the graph
    '''
    # Number of qubits in the bottom row
    # Note that the distance of each graph is equiavalent to the number of vertices in the bottom row.
    # We also have N total rows as well.

    # create a graph
    H = nx.Graph()

    # This stores the vertices in each row.
    row_wise = [[] for _ in range(N)]
    # print(row_wise)

    # planar layout (pl) is used to store the coordinates of each vertex
    # keys are vertices and values are the coordinates.
    # This is later used by networkx to draw the graph
    pl = dict()

    # heights of each column
    first_twenty_odd = list(range(1, 20, 2))
    new_odd = [first_twenty_odd[i] for i in range(0, len(first_twenty_odd), 2)]
    # heights of each column
    if N not in new_odd:
        # Case for N=3, 7, 11...
        heights = [i for i in range(1, N + 1, 2)] + [i for i in range(N, 2, -2)]
    else:
        # Case for N=5,9,...
        heights = [i for i in range(3, N + 1, 2)] + [i for i in range(N, 0, -2)]

    # So lets go column by column
    # [x, y] is the coordinate of the vertex
    for x, j in enumerate(heights):
        # print(x,j)
        for y in range(j):
            # add node to graph
            H.add_node((x, y))
            row_wise[y].append((x, y))
            # print(row_wise)
            # we are labelling the vertex at [x,y] by (x,y)
            pl[(x, y)] = [x, y]
            # print(pl)
            # We can add all the vertical edges right here
            if y != 0:
                H.add_edge((x, y), (x, y - 1))
    # print(row_wise[0])
    # add all the edges in the bottom row
    for i in range(len(row_wise[0]) - 1):
        H.add_edge(row_wise[0][i], row_wise[0][i + 1])
    # add the edges in the other rows. Remember these alternate.
    for y in range(1, N):
        for i in range(len(row_wise[y]) - 1):
            if i % 2 == 1:
                continue
            H.add_edge(row_wise[y][i], row_wise[y][i + 1])

    # add diagonal edges
    # Again, I wrote this for N=3,7,11.. It fails for N=5,9.. Correct it.
    for y in range(N):
        # Case for N=3, 7, 11...
        if N not in new_odd:
            # left diagonal edges
            if y % 4 == 0:
                H.add_edge(row_wise[y][0], row_wise[y+2][0])
            # right diagonl edges
            elif y % 2 == 0 and y < N-1:
                H.add_edge(row_wise[y][-1], row_wise[y+2][-1])
        else:
            # Case for N=5,9,...
            # left diagonal edges
            if y % 2 == 0 and y < N-1:
                H.add_edge(row_wise[y][0], row_wise[y+2][0])
            # right diagonal edges
            elif y % 3 == 0:
                print(y)
                H.add_edge(row_wise[y-1][-1], row_wise[y-3][-1])
    # now draw it, giving networkx the positions of each vertex as well
    #nx.draw(H, pos=pl)

    # First networkx has to check that the graph is indeed planar.
    # the planar embedding (pe) is its record of this.
    _, pe = nx.check_planarity(H)

    # Lets create a set to store all the faces
    F = set()

    # This the brute forcing.
    for edge in pe.edges:
        # find a face
        f = pe.traverse_face(*edge)
        # if the face is length 4 and 8 we process more
        # sometimes traverse_face returns big cycles eg. the whole outside of the graph
        # lets throw those away.
        if N > 3:
            if len(f) <= 8 and len(f) > 3:
                # before adding we are going to sort the edges and then turn the list into
                # a tuple so it can be added to the set.
                F.add(tuple(sorted(f)))
        else:
            if len(f) <= 4:
                F.add(tuple(sorted(f)))
    # turn the faces set to a list and sort it.
    # not really necessary but nice.
    faces = sorted(list(F))

    return faces, H


def _color_codes_syndrome_measurements(d):
    '''
    Creates syndrome measurement circuit with 4.8.8 color code family

    Parameter
    -----------
    d : distance

    Return
    --------
    stac.Circuit with appended gates
    '''

    # Retrieve graph for coordinates of the vertices/physical qubits and
    # the respective faces of the graph given the distance d
    faces, H = vertices_physical_qubits(d)

    # Define circuit for syndrome measurement
    circ = stac.Circuit()
    # Data qubits
    circ.append_register(stac.QubitRegister('d', 0, len(H.nodes)))
    # Subregister for ancilla qubits
    circ.append_register(stac.RegisterRegister('s', 0))
    # Subregister for Z stabilizers ancilla qubits
    circ.register[0, 1].append(stac.RegisterRegister('t', 0))
    # Subregister for X stabilizers ancilla qubits
    circ.register[0, 1].append(stac.RegisterRegister('t', 1))

    # Define number of ancilla qubits in each subregister depending on the face 4 or 8
    for i in range(len(faces)):
        if len(faces[i]) == 4:
            circ.register[0, 1][0].append(stac.QubitRegister('f', i, 1))
            circ.register[0, 1][1].append(stac.QubitRegister('f', i, 1))
        else:
            circ.register[0, 1][0].append(stac.QubitRegister('f', i, 5))
            circ.register[0, 1][1].append(stac.QubitRegister('f', i, 5))

    # Total number of data qubits
    qubit_number = list(H.nodes)

    # 4 qubit Z stabilizer
    for i in range(len(faces)):
        if len(faces[i]) == 4:
            for j in range(len(faces[i])):
                number = qubit_number.index(faces[i][j])
                # (level, syndrome, type, face, i) = (0, 1, t, f, i)
                circ.append('CX', (0, 0, number), (0, 1, 0, i, 0))
            circ.append('MR', (0, 1, 0, i, 0))
            circ.append('TICK')

    # 4 qubit X stabilizer
    for i in range(len(faces)):
        if len(faces[i]) == 4:
            circ.append('H', (0, 1, 1, i, 0))
            for j in range(len(faces[i])):
                number = qubit_number.index(faces[i][j])
                # (level, syndrome, type, face, i) = (0, 1, t, f, i)
                circ.append('CX', (0, 1, 1, i, 0), (0, 0, number))
            circ.append('H', (0, 1, 1, i, 0))
            circ.append('MR', (0, 1, 1, i, 0))
            circ.append('TICK')

    # Preparation of a 4 qubit cat state for the 8 qubit X stabibilizer
    for i in range(len(faces)):
        if len(faces[i]) == 8:
            # (level, syndrome, type, face, i) = (0, 1, t, f, i)
            circ.append('H', (0, 1, 0, i, 0))
            circ.append('CX', (0, 1, 0, i, 0), (0, 1, 0, i, 1))
            circ.append('CX', (0, 1, 0, i, 0), (0, 1, 0, i, 2))
            circ.append('CX', (0, 1, 0, i, 0), (0, 1, 0, i, 3))
            circ.append('CX', (0, 1, 0, i, 0), (0, 1, 0, i, 4))
            circ.append('CX', (0, 1, 0, i, 1), (0, 1, 0, i, 0))
            circ.append('H', (0, 1, 0, i, 0))
            circ.append('MR', (0, 1, 0, i, 0))
            circ.append('TICK')

    # Preparation of a 4 qubit cat state for the 8 qubit Z stabibilizer
    for i in range(len(faces)):
        if len(faces[i]) == 8:
            # (level, syndrome, type, face, i) = (0, 1, t, f, i)
            circ.append('H', (0, 1, 1, i, 0))
            circ.append('CX', (0, 1, 1, i, 0), (0, 1, 1, i, 1))
            circ.append('CX', (0, 1, 1, i, 0), (0, 1, 1, i, 2))
            circ.append('CX', (0, 1, 1, i, 0), (0, 1, 1, i, 3))
            circ.append('CX', (0, 1, 1, i, 0), (0, 1, 1, i, 4))
            circ.append('CX', (0, 1, 1, i, 1), (0, 1, 1, i, 0))
            circ.append('H', (0, 1, 1, i, 0))
            circ.append('MR', (0, 1, 1, i, 0))
            circ.append('TICK')

    # 8 qubit X stabibilizer
    for i in range(len(faces)):
        if len(faces[i]) == 8:
            counter_x = 1
            for qubits in range(0, len(faces[i]), 2):
                number1 = qubit_number.index(faces[i][qubits])
                number2 = qubit_number.index(faces[i][qubits + 1])
                # (level, syndrome, type, face, i) = (0, 1, t, f, i)
                circ.append('CX', (0, 1, 1, i, counter_x), (0, 0, number1))
                circ.append('CX', (0, 1, 1, i, counter_x), (0, 0, number2))
                counter_x = counter_x + 1
            for k in range(1, 5):
                circ.append('H', (0, 1, 1, i, k))
                circ.append('MR', (0, 1, 1, i, k))
            circ.append('TICK')

    # 8 qubit Z stabibilizer
    for i in range(len(faces)):
        if len(faces[i]) == 8:
            counter_z = 1
            for k in range(1, 5):
                circ.append('H', (0, 1, 0, i, k))
            for qubits in range(0, len(faces[i]), 2):
                number1 = qubit_number.index(faces[i][qubits])
                number2 = qubit_number.index(faces[i][qubits + 1])
                # (level, syndrome, type, face, i) = (0, 1, t, f, i)
                circ.append('CX', (0, 0, number1), (0, 1, 0, i, counter_z))
                circ.append('CX', (0, 0, number2), (0, 1, 0, i, counter_z))
                counter_z = counter_z + 1

            for k in range(1, 5):
                circ.append('MR', (0, 1, 0, i, k))
            circ.append('TICK')

    return circ

print(_color_codes_syndrome_measurements(5))
