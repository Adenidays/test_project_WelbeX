from itertools import permutations


def calculate_optimal_route(points):
    all_permutations = permutations(points[1:])
    optimal_route = []
    min_distance = float('inf')

    for perm in all_permutations:
        total_distance = 0
        current_point = points[0]
        for point in perm:
            total_distance += ((current_point.lat - point.lat) ** 2 + (current_point.lng - point.lng) ** 2) ** 0.5
            current_point = point
        total_distance += ((current_point.lat - points[0].lat) ** 2 + (current_point.lng - points[0].lng) ** 2) ** 0.5

        if total_distance < min_distance:
            min_distance = total_distance
            optimal_route = [points[0]] + list(perm) + [points[0]]

    return optimal_route