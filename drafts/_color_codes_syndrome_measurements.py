#Contributor: Victor Onofre
#Licensed under GPLV3

import stac
import bidict
import networkx as nx


def vertices_physical_qubits(N):
    # Number of qubits in the bottom row
    # Note that the distance of each graph is equiavalent to the number of vertices in the bottom row.
    # We also have N total rows as well.
    #N = 3

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
    # this only correct for N=3, 7, 11... It is incorrect for N=5,9,... Correct it.
    heights = [i for i in range(1, N + 1, 2)] + [i for i in range(N, 2, -2)]
    # print(heights)
    # print([i for i in range(1,N+1,2)])
    # print( [i for i in range(N, 2, -2)])
    # For N = 5, we we would have this
    # heights = [3, 5, 5, 3, 1]

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
        # left diagonal edges
        if y % 4 == 0:
            H.add_edge(row_wise[y][0], row_wise[y + 2][0])

        # right diagonl edges
        elif y % 2 == 0 and y < N - 1:
            H.add_edge(row_wise[y][-1], row_wise[y + 2][-1])
    # now draw it, giving networkx the positions of each vertex as well
    #nx.draw(H, pos=pl)
    # print([i for i in range(1,N+1,2)])
    # print( [i for i in range(N, 2, -2)])
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
        if len(f) <= 5:
            # before adding we are going to sort the edges and then turn the list into
            # a tuple so it can be added to the set.
            F.add(tuple(sorted(f)))
    # turn the faces set to a list and sort it.
    # not really necessary but nice.
    faces = sorted(list(F))

    return faces, H


def _color_codes_syndrome_measurements(d):
    '''
    This function creates syndrome measurement circuit with 4.8.8 color code family

    Parameter
    -----------
    d :
        distance

    Return
    --------
    stac.Circuit with appended gates
    '''
    faces, H = vertices_physical_qubits(d)

    circ = stac.Circuit()
    circ.append_register(stac.QubitRegister('d', 0, len(H.nodes)))
    circ.append_register(stac.RegisterRegister('s', 0))
    circ.register[0, 1].append(stac.RegisterRegister('t', 0))
    circ.register[0, 1].append(stac.RegisterRegister('t', 1))

    for i in range(len(faces)):
        if len(faces[i]) == 4:
            circ.register[0, 1][0].append(stac.QubitRegister('s', i, 1))
            circ.register[0, 1][1].append(stac.QubitRegister('s', i, 1))
        else:
            circ.register[0, 1][0].append(stac.QubitRegister('s', i, 5))
            circ.register[0, 1][1].append(stac.QubitRegister('s', i, 5))

    qubit_number = list(H.nodes)

    # 4 qubit Z stabilizer
    for i in range(len(faces)):
        if len(faces[i]) == 4:
            for j in range(len(faces[i])):
                # print(qubit_number.index(faces[i][j]), faces[i][j])
                number = qubit_number.index(faces[i][j])
                circ.append('CX', (0, 0, number), (0, 1, 0, i, 0))
            circ.append('MR', (0, 1, 0, i, 0))
            circ.append('TICK')

    # 4 qubit X stabilizer
    for i in range(len(faces)):
        # print(i)
        if len(faces[i]) == 4:
            circ.append('H', (0, 1, 1, i, 0))
            for j in range(len(faces[i])):
                # print(qubit_number.index(faces[i][j]), faces[i][j])
                number = qubit_number.index(faces[i][j])
                circ.append('CX', (0, 1, 1, i, 0), (0, 0, number))
            circ.append('H', (0, 1, 1, i, 0))
            circ.append('MR', (0, 1, 1, i, 0))
            circ.append('TICK')

    # Preparation of a 4 qubit cat state for the 8 qubit X stabibilizer
    for i in range(len(faces)):
        if len(faces[i]) == 8:
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
                # (level, syndrome, type, face, i) = (0, 1, t, f, i)
                # print(qubit_number.index(faces[i][j]), faces[i][j])
                number1 = qubit_number.index(faces[i][qubits])
                number2 = qubit_number.index(faces[i][qubits + 1])
                circ.append('CX', (0, 1, 1, i, counter_x), (0, 0, number1))
                circ.append('CX', (0, 1, 1, i, counter_x), (0, 0, number2))
                print(number1, counter_x)
                print(number2, counter_x)
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
                # (level, syndrome, type, face, i) = (0, 1, t, f, i)
                # print(qubit_number.index(faces[i][j]), faces[i][j])
                number1 = qubit_number.index(faces[i][qubits])
                number2 = qubit_number.index(faces[i][qubits + 1])
                circ.append('CX', (0, 0, number1), (0, 1, 0, i, counter_z))
                circ.append('CX', (0, 0, number2), (0, 1, 0, i, counter_z))
                print(number1, counter_z)
                print(number2, counter_z)
                counter_z = counter_z + 1

            for k in range(1, 5):
                circ.append('MR', (0, 1, 0, i, k))
            circ.append('TICK')

    return circ

print(_color_codes_syndrome_measurements(7))


