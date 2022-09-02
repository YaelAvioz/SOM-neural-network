import sys
import math
import pygame
from hexalattice.hexalattice import *

som_size = 61


# parsing the input csv file
def parse_file(filepath):
    # getting the lines from the file
    file1 = open(filepath, 'r')
    lines = file1.readlines()

    input_examples = {}

    # for every line - getting only the relevant values(every column beside Municipality,Economic Cluster,Total Votes)
    # and adding a 'others' value - (the 'Total Votes' value - the sum of the voted)
    # the key will be the name, and the value is a pair of the Economic Cluster with the list of the votes
    for i in range(1, len(lines)):
        splitted_line = lines[i].split(',')

        # removing '\n'
        splitted_line[-1] = splitted_line[-1][:-1]

        values_sum = 0
        current_values = []

        # skipping on the first three values and creating a list with the votes
        for numeric_string in splitted_line[3:]:
            values_sum += int(numeric_string)
            current_values.append((int(numeric_string)/int(splitted_line[2])))
        input_examples[splitted_line[0]] = [splitted_line[1], current_values]

        # calculating the 'others' field value
        others_value = ((int(splitted_line[2]) - values_sum)/int(splitted_line[2]))
        input_examples[splitted_line[0]][1].append(others_value)

    return input_examples


# calculating the distance between two vectors
def calculate_distance(first_vec, second_vec):
    distance = 0
    for i in range(len(first_vec)):
        first_value = first_vec[i]
        second_value = second_vec[i]
        distance += pow((first_value - second_value), 2)
    return pow(distance, 0.5)


# getting the closest som vector to the input example vector by the distance function
def get_closest_som_vector(example_vec, som):
    best = [-1, 0]

    # checking for every som cell - who is the closest to the input example
    for i in range(len(som)):
        for j in range(len(som[i])):
            # calculating the distance between the input example and the current som cell
            current_distance = calculate_distance(example_vec, som[i][j])

            # initializing the best with the values for the first som vector
            if i == 0 and j == 0:
                best = [[i,j], current_distance]

            # checking if the current cell is closer than the current best
            else:
                if current_distance < best[1]:
                    best = [[i,j], current_distance]

    # returning a pair with the closest som cell position and the distance
    return best


# updating the som cells by the closest som cell(updating the first and second circle)
# getting the som, the first and second circle neighborhood percentage,
# the difference between the example vector and the closest som cell, the position of the closest som cell(i,j)
# updating the values of the first and second neighbors circle of the som cell position
def update_som(som, first_neighborhood, second_neighborhood, differ, i, j):
    update = [k * (first_neighborhood) for k in differ]
    second_update = [k * (second_neighborhood) for k in differ]

    # if the closest som cell is at the upper half of the som
    if i < 4:
        if (i-1) >= 0:
            if (j-1) >= 0:
                som[i-1][j-1] = [sum(x) for x in zip(*[[k * (1-first_neighborhood) for k in som[i-1][j-1]], update])]

                if (j-2) >= 0:
                    som[i - 1][j - 2] = [sum(x) for x in zip(*[[k * (1-second_neighborhood) for k in som[i - 1][j - 2]], second_update])]
                    if (i-2) >= 0:
                        som[i - 2][j - 2] = [sum(x) for x in zip(*[[k * (1-second_neighborhood) for k in som[i - 2][j - 2]], second_update])]

            if j <= (len(som[i-1]) - 1):
                som[i-1][j] = [sum(x) for x in zip(*[[k * (1-first_neighborhood) for k in som[i-1][j]], update])]
                if (j+1) <= (len(som[i-1]) - 1):
                    som[i - 1][j + 1] = [sum(x) for x in zip(*[[k * (1-second_neighborhood) for k in som[i - 1][j + 1]], second_update])]
                    if (i-2) >= 0:
                        if j <= (len(som[i - 2]) - 1):
                            som[i - 2][j] = [sum(x) for x in zip(*[[k * (1-second_neighborhood) for k in som[i - 2][j]], second_update])]

            if (i-2) >= 0:
                if (j-1) >= 0 and (j-1) <= (len(som[i - 2]) - 1):
                    som[i - 2][j - 1] = [sum(x) for x in zip(*[[k * (1-second_neighborhood) for k in som[i - 2][j - 1]], second_update])]

        if (j-1) >= 0:
            som[i][j-1] = [sum(x) for x in zip(*[[k * (1-first_neighborhood) for k in som[i][j-1]], update])]
            if (j-2) >= 0:
                som[i][j - 2] = [sum(x) for x in zip(*[[k * (1-second_neighborhood) for k in som[i][j - 2]], second_update])]

        if (j+1) <= (len(som[i]) - 1):
            som[i][j+1] = [sum(x) for x in zip(*[[k * (1-first_neighborhood) for k in som[i][j+1]], update])]
            if (j+2) <= (len(som[i]) - 1):
                som[i][j + 2] = [sum(x) for x in zip(*[[k * (1-second_neighborhood) for k in som[i][j + 2]], second_update])]

        if (i+1) <= 8:
            if j <= (len(som[i+1]) - 1):
                som[i+1][j] = [sum(x) for x in zip(*[[k * (1-first_neighborhood) for k in som[i+1][j]], update])]
                if j - 1 >= 0:
                    som[i + 1][j - 1] = [sum(x) for x in zip(*[[k * (1-second_neighborhood) for k in som[i + 1][j - 1]], second_update])]

                if (i+2) <= 8:
                    if (i+2) > 4:
                        if j - 1 >= 0:
                            som[i + 2][j - 1] = [sum(x) for x in zip(*[[k * (1-second_neighborhood) for k in som[i + 2][j - 1]], second_update])]
                    else:
                        som[i + 2][j] = [sum(x) for x in zip(*[[k * (1-second_neighborhood) for k in som[i + 2][j]], second_update])]

            if (j+1) <= (len(som[i+1]) - 1):
                som[i+1][j+1] = [sum(x) for x in zip(*[[k * (1-first_neighborhood) for k in som[i+1][j+1]], update])]
                if j + 2 <= (len(som[i + 1]) - 1):
                    som[i + 1][j + 2] = [sum(x) for x in zip(*[[k * (1-second_neighborhood) for k in som[i + 1][j + 2]], second_update])]

                if (i+2) <= 8:
                    if (i+2) > 4:
                        if j+1 <= (len(som[i + 2]) - 1):
                            som[i + 2][j + 1] = [sum(x) for x in zip(*[[k * (1-second_neighborhood) for k in som[i + 2][j + 1]], second_update])]
                    else:
                        if j + 2 <= (len(som[i + 2]) - 1):
                            som[i + 2][j + 2] = [sum(x) for x in zip(*[[k * (1-second_neighborhood) for k in som[i + 2][j + 2]], second_update])]

            if (i+2) <= 8:
                if (i + 2) > 4:
                    som[i + 2][j] = [sum(x) for x in zip(*[[k * (1-second_neighborhood) for k in som[i + 2][j]], second_update])]
                else:
                    if j + 1 <= (len(som[i + 2]) - 1):
                        som[i + 2][j + 1] = [sum(x) for x in zip(*[[k * (1-second_neighborhood) for k in som[i + 2][j + 1]], second_update])]

    # if the closest som cell is in the middle of the som
    elif i == 4:
        if (i-1) >= 0:
            if j <= (len(som[i-1]) - 1):
                som[i-1][j] = [sum(x) for x in zip(*[[k * (1-first_neighborhood) for k in som[i-1][j]], update])]
                if j+1 <= (len(som[i-1]) - 1):
                    som[i - 1][j + 1] = [sum(x) for x in zip(*[[k * (1-second_neighborhood) for k in som[i - 1][j + 1]], second_update])]

            if (j-1) >= 0:
                som[i-1][j-1] = [sum(x) for x in zip(*[[k * (1-first_neighborhood) for k in som[i-1][j-1]], update])]
                if j-2 >= 0:
                    som[i - 1][j - 2] = [sum(x) for x in zip(*[[k * (1-second_neighborhood) for k in som[i - 1][j - 2]], second_update])]

            if i-2 >= 0:
                if j-2 >= 0 and j-2 <= (len(som[i-2]) - 1):
                    som[i - 2][j - 2] = [sum(x) for x in zip(*[[k * (1-second_neighborhood) for k in som[i - 2][j - 2]], second_update])]

                if j-1 >= 0 and j-1 <= (len(som[i-2]) - 1):
                    som[i - 2][j - 1] = [sum(x) for x in zip(*[[k * (1-second_neighborhood) for k in som[i - 2][j - 1]], second_update])]

                if j >= 0 and j <= (len(som[i-2]) - 1):
                    som[i - 2][j] = [sum(x) for x in zip(*[[k * (1-second_neighborhood) for k in som[i - 2][j]], second_update])]

        if (j-1) >= 0:
            som[i][j-1] = [sum(x) for x in zip(*[[k * (1-first_neighborhood) for k in som[i][j-1]], update])]
            if (j-2) >= 0:
                som[i][j - 2] = [sum(x) for x in zip(*[[k * (1-second_neighborhood) for k in som[i][j - 2]], second_update])]

        if (j+1) <= (len(som[i]) - 1):
            som[i][j+1] = [sum(x) for x in zip(*[[k * (1-first_neighborhood) for k in som[i][j+1]], update])]
            if (j+2) <= (len(som[i]) - 1):
                som[i][j + 2] = [sum(x) for x in zip(*[[k * (1-second_neighborhood) for k in som[i][j + 2]], second_update])]

        if (i+1) <= 8:
            if j <= (len(som[i+1]) - 1):
                som[i+1][j] = [sum(x) for x in zip(*[[k * (1-first_neighborhood) for k in som[i+1][j]], update])]
                if j+1 <= (len(som[i+1]) - 1):
                    som[i + 1][j + 1] = [sum(x) for x in zip(*[[k * (1-second_neighborhood) for k in som[i + 1][j + 1]], second_update])]

            if (j-1) >= 0:
                som[i+1][j-1] = [sum(x) for x in zip(*[[k * (1-first_neighborhood) for k in som[i+1][j-1]], update])]
                if j-2 >= 0:
                    som[i + 1][j - 2] = [sum(x) for x in zip(*[[k * (1-second_neighborhood) for k in som[i + 1][j - 2]], second_update])]

            if (i+2) <= 8:
                if j - 2 >= 0 and j - 2 <= (len(som[i + 2]) - 1):
                    som[i + 2][j - 2] = [sum(x) for x in zip(*[[k * (1-second_neighborhood) for k in som[i + 2][j - 2]], second_update])]

                if j - 1 >= 0 and j - 1 <= (len(som[i + 2]) - 1):
                    som[i + 2][j - 1] = [sum(x) for x in zip(*[[k * (1-second_neighborhood) for k in som[i + 2][j - 1]], second_update])]

                if j >= 0 and j <= (len(som[i + 2]) - 1):
                    som[i + 2][j] = [sum(x) for x in zip(*[[k * (1-second_neighborhood) for k in som[i + 2][j]], second_update])]

    # if the closest som cell is at the lower half of the som
    elif i > 4:
        if (i - 1) >= 0:
            if j <= (len(som[i-1]) - 1):
                som[i - 1][j] = [sum(x) for x in zip(*[[k * (1-first_neighborhood) for k in som[i-1][j]], update])]
                if j-1 >= 0:
                    som[i - 1][j - 1] = [sum(x) for x in zip(*[[k * (1-second_neighborhood) for k in som[i - 1][j - 1]], second_update])]

            if (j + 1) <= (len(som[i - 1]) - 1):
                som[i - 1][j+1] = [sum(x) for x in zip(*[[k * (1-first_neighborhood) for k in som[i-1][j+1]], update])]
                if j+2 <= (len(som[i - 1]) - 1):
                    som[i - 1][j + 2] = [sum(x) for x in zip(*[[k * (1-second_neighborhood) for k in som[i - 1][j + 2]], second_update])]

            if i-2 >= 0:
                if i-2 < 4:
                    if j-1 >= 0 and j-1 <= (len(som[i - 2]) - 1):
                        som[i - 2][j - 1] = [sum(x) for x in zip(*[[k * (1-second_neighborhood) for k in som[i - 2][j - 1]], second_update])]
                else:
                    if j + 2 >= 0 and j + 2 <= (len(som[i - 2]) - 1):
                        som[i - 2][j + 2] = [sum(x) for x in zip(*[[k * (1-second_neighborhood) for k in som[i - 2][j + 2]], second_update])]

                if j + 1 >= 0 and j + 1 <= (len(som[i - 2]) - 1):
                    som[i - 2][j + 1] = [sum(x) for x in zip(*[[k * (1-second_neighborhood) for k in som[i - 2][j + 1]], second_update])]

                if j >= 0 and j <= (len(som[i - 2]) - 1):
                    som[i - 2][j] = [sum(x) for x in zip(*[[k * (1-second_neighborhood) for k in som[i - 2][j]], second_update])]

        if (j - 1) >= 0:
            som[i][j - 1] = [sum(x) for x in zip(*[[k * (1-first_neighborhood) for k in som[i][j-1]], update])]
            if (j - 2) >= 0:
                som[i][j - 2] = [sum(x) for x in zip(*[[k * (1-second_neighborhood) for k in som[i][j - 2]], second_update])]

        if (j + 1) <= (len(som[i]) - 1):
            som[i][j + 1] = [sum(x) for x in zip(*[[k * (1-first_neighborhood) for k in som[i][j+1]], update])]
            if (j + 2) <= (len(som[i]) - 1):
                som[i][j + 2] = [sum(x) for x in zip(*[[k * (1-second_neighborhood) for k in som[i][j + 2]], second_update])]

        if (i + 1) <= 8:
            if (j-1) >= 0:
                som[i + 1][j-1] = [sum(x) for x in zip(*[[k * (1-first_neighborhood) for k in som[i+1][j-1]], update])]
                if (j-2) >= 0:
                    som[i + 1][j - 2] = [sum(x) for x in zip(*[[k * (1-second_neighborhood) for k in som[i + 1][j - 2]], second_update])]

            if j <= (len(som[i + 1]) - 1):
                som[i + 1][j] = [sum(x) for x in zip(*[[k * (1-first_neighborhood) for k in som[i+1][j]], update])]
                if (j+1) <= (len(som[i + 1]) - 1):
                    som[i + 1][j + 1] = [sum(x) for x in zip(*[[k * (1-second_neighborhood) for k in som[i + 1][j + 1]], second_update])]

            if (i + 2) <= 8:
                if j-2 >= 0 and j-2 <= (len(som[i+2]) - 1):
                    som[i + 2][j - 2] = [sum(x) for x in zip(*[[k * (1-second_neighborhood) for k in som[i + 2][j - 2]], second_update])]

                if j-1 >= 0 and j-1 <= (len(som[i+2]) - 1):
                    som[i + 2][j - 1] = [sum(x) for x in zip(*[[k * (1-second_neighborhood) for k in som[i + 2][j - 1]], second_update])]

                if j >= 0 and j <= (len(som[i+2]) - 1):
                    som[i + 2][j] = [sum(x) for x in zip(*[[k * (1-second_neighborhood) for k in som[i + 2][j]], second_update])]


# drawing a polygon on the pygame board
def draw_regular_polygon(surface, color, position, width=0):
    radius = 25
    x, y = position

    pygame.draw.polygon(surface, color, [
        (x + radius * math.sin(2 * math.pi * i / 6),
         y + radius * math.cos(2 * math.pi * i / 6))
        for i in range(6)], width)


# calculating the average of the input list values
def average(lst):
    if lst == []:
        return 0
    return sum(lst) / len(lst)


# main function
if __name__ == '__main__':
    # parsing the file - getting a dict that the keys are the names
    # and the values are pairs of the Economic Cluster paired with the votes
    input_examples = parse_file(sys.argv[1])
    num_of_values = len(input_examples[list(input_examples.keys())[0]][1])

    # initializing the som
    som = []
    for i in range(5,10):
        som.append([ [] for _ in range(i) ])
    for i in reversed(range(5,9)):
        som.append([ [] for _ in range(i) ])

    # randomizing values for the som cells
    for i in range(num_of_values):
        for j in range(len(som)):
            for k in range(len(som[j])):
                som[j][k] = np.random.dirichlet(np.ones(num_of_values), size=1).tolist()[0]

    epochs = 10
    for ep in range(epochs):
        # for every input line - getting the closest som vector's index and the distance
        for key in input_examples.keys():
            # getting a pair of the closest som vector's position and the distance from the current input line
            closest = get_closest_som_vector(input_examples[key][1], som)

            # calculating the difference between the example vector and the closest som cell
            differ = np.subtract(input_examples[key][1], som[closest[0][0]][closest[0][1]])

            # updating the closest som cell
            som_cell_update = [i * (0.3) for i in differ]
            closest_som_cell_part = [i * (0.7) for i in som[closest[0][0]][closest[0][1]]]
            som[closest[0][0]][closest[0][1]] = [sum(x) for x in zip(*[closest_som_cell_part, som_cell_update])]

            # updating the first and second circle
            update_som(som, 0.2, 0.1, differ, closest[0][0], closest[0][1])

    # creating a list in the shape of the som that every position represents an som cell
    final_predictions_per_som_cell = {}
    for i in range(9):
        if i==0 or i==8:
            for j in range(5):
                final_predictions_per_som_cell[i,j] = []

        elif i==1 or i==7:
            for j in range(6):
                final_predictions_per_som_cell[i,j] = []

        elif i==2 or i==6:
            for j in range(7):
                final_predictions_per_som_cell[i,j] = []

        elif i==3 or i==5:
            for j in range(8):
                final_predictions_per_som_cell[i,j] = []

        elif i==4:
            for j in range(9):
                final_predictions_per_som_cell[i,j] = []

    # final predictions - adding every example to the position of it's closest som cell in the final predictions list
    for key in input_examples.keys():
        # getting a pair of the closest som vector's position and the distance from the current input line
        closest = get_closest_som_vector(input_examples[key][1], som)
        final_predictions_per_som_cell[closest[0][0], closest[0][1]].append(int(input_examples[key][0]))

        # printing the closest som cell's position for every example
        print("name:", key, ", som cell position:", closest[0])

    # returns the hex_centers
    hex_centers, _ = create_hex_grid(n=100, crop_circ=4, edge_color=(0, 0, 0), do_plot=True)

    # creates the output window
    pygame.init()
    screen = pygame.display.set_mode((600, 600))
    done = False
    screen.fill((255, 255, 255))
    for i in range(len(hex_centers)):
        # getting the color of every som cell by the avg of the Economic Clusters of the examples that matched with this som cell
        current_avg = average(final_predictions_per_som_cell[list(final_predictions_per_som_cell.keys())[i][0], list(final_predictions_per_som_cell.keys())[i][1]])

        # if no examples matched with the cell - empty cell
        if current_avg == 0:
            r, g, b = 200, 0, 0
        else:
            r, g, b = 0, 0, (1-(current_avg/10))*255

        # drawing the som cell on the board
        draw_regular_polygon(screen, (r, g, b), hex_centers[i] * 50 + 300, width=0)

        pygame.display.flip()

    # keeping the pygame form open
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True