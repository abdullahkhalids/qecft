#Contributor: Victor Onofre
#Licensed under GPLV3

import stac
import bidict
import networkx as nx


def vertices_physical_qubits(d):
    # Number of qubits in the bottom row
    # Note that the distance of each graph is equiavalent to the number of vertices in the bottom row.
    # We also have N total rows as well.
    N = 3

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

    #determine the number of data points and syndrome points
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

    #assign coordinates
    surface_code_circ.physical_register.elements = \
    [stac.PhysicalQubit(col*i+j, (j, i), []) for i in range(row) for j in range(col)]

    surface_code_circ.layout_map = bidict.bidict()

    d_i = 0
    s_i = 0

    for i in range(row):
        if i % 2 == 0:
            for j in range(col):
                if j % 2 == 0:
                    surface_code_circ.register[(0,0, d_i)].constituent_register = surface_code_circ.physical_register.elements[col*i+j]
                    surface_code_circ.layout_map[(0,0,d_i)] = (j, i)
                    d_i += 1
                    
                else:
                    surface_code_circ.register[(0,1,s_i)].constituent_register = surface_code_circ.physical_register.elements[col*i+j]
                    surface_code_circ.layout_map[(0,1,s_i)] = (j, i)
                    s_i += 1
        
        else:
            for j in range(col):
                if j % 2 != 0:
                    surface_code_circ.register[(0,0, d_i)].constituent_register = surface_code_circ.physical_register.elements[col*i+j]
                    surface_code_circ.layout_map[(0,0,d_i)] = (j, i)
                    d_i += 1

                else:
                    surface_code_circ.register[(0,1,s_i)].constituent_register = surface_code_circ.physical_register.elements[col*i+j]
                    surface_code_circ.layout_map[(0,1,s_i)] = (j, i)
                    s_i += 1

    #create circuit
    surface_code_circ.clear()

    for qubit in surface_code_circ.register[(0,1)].qubits():

        s_coordinate = qubit.constituent_register.coordinates

        d_1 = (qubit.constituent_register.coordinates[0], qubit.constituent_register.coordinates[1]+1)
        d_2 = (qubit.constituent_register.coordinates[0]-1, qubit.constituent_register.coordinates[1])
        d_3 = (qubit.constituent_register.coordinates[0]+1, qubit.constituent_register.coordinates[1])
        d_4 = (qubit.constituent_register.coordinates[0], qubit.constituent_register.coordinates[1]-1)

        if s_coordinate[1] % 2 == 0: #Z

            for i in [d_1, d_2, d_3, d_4]:
                if -1 < i[0] < col and -1 < i[1] < row:
                    surface_code_circ.geo_append('CX', i, s_coordinate)

            surface_code_circ.geo_append('TICK')
        
        else: #X
            surface_code_circ.geo_append('H', s_coordinate)

            for i in [d_1, d_2, d_3, d_4]:
                if -1 < i[0] < col and -1 < i[1] < row:
                    surface_code_circ.geo_append('CX', s_coordinate, i)

            surface_code_circ.geo_append('H', s_coordinate)
            surface_code_circ.geo_append('TICK')
    
    return surface_code_circ

