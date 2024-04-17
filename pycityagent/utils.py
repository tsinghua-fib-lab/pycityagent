import math

def get_angle(x, y):
    return math.atan2(y, x)*180/math.pi

def point_on_line_given_distance(start_node, end_node, distance):
    """
    Given two points (start_point and end_point) defining a line, and a distance s to travel along the line,
    return the coordinates of the point reached after traveling s units along the line, starting from start_point.

    Args:
        start_point (tuple): Tuple of (x, y) representing the starting point on the line.
        end_point (tuple): Tuple of (x, y) representing the ending point on the line.
        distance (float): Distance to travel along the line, starting from start_point.

    Returns:
        tuple: Tuple of (x, y) representing the new point reached after traveling s units along the line.
    """

    x1, y1 = start_node['x'], start_node['y']
    x2, y2 = end_node['x'], end_node['y']

    # Calculate the slope m and the y-intercept b of the line
    if x1 == x2:
        # Vertical line, distance is only along the y-axis
        return (x1, y1 + distance if distance >= 0 else y1 - abs(distance))
    else:
        m = (y2 - y1) / (x2 - x1)
        b = y1 - m * x1

        # Calculate the direction vector (dx, dy) along the line
        dx = (x2 - x1) / math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        dy = (y2 - y1) / math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

        # Scale the direction vector by the given distance
        scaled_dx = dx * distance
        scaled_dy = dy * distance

        # Calculate the new point's coordinates
        x = x1 + scaled_dx
        y = y1 + scaled_dy

        return [x, y]

def get_xy_in_lane(nodes, distance, direction:str='front'):
    temp_sum = 0
    remain_s = 0
    if direction == 'front':
        # 顺道路方向前进
        if distance == 0:
            return [nodes[0]['x'], nodes[0]['y']]
        key_index = 0  # first node
        for i in range(1, len(nodes)):
            x1, y1 = nodes[i-1]['x'], nodes[i-1]['y']
            x2, y2 = nodes[i]['x'], nodes[i]['y']
            temp_sum += math.sqrt((x2 - x1)**2 + (y2-y1)**2)
            if temp_sum > distance:
                remain_s = distance - (temp_sum - math.sqrt((x2 - x1)**2 + (y2-y1)**2))
                break;
            key_index += 1
        if remain_s < 0.5:
            return [nodes[key_index]['x'], nodes[key_index]['y']]
        longlat = point_on_line_given_distance(nodes[key_index], nodes[key_index+1], remain_s)
        return longlat
    else:
        # 逆道路方向前进
        if distance == 0:
            return [nodes[-1]['x'], nodes[-1]['y']]
        key_index = len(nodes)-1  # last node
        for i in range(len(nodes)-1, 0, -1):
            x1, y1 = nodes[i]['x'], nodes[i]['y']
            x2, y2 = nodes[i-1]['x'], nodes[i-1]['y']
            temp_sum += math.sqrt((x2 - x1)**2 + (y2-y1)**2)
            if temp_sum > distance:
                remain_s = distance - (temp_sum - math.sqrt((x2 - x1)**2 + (y2-y1)**2))
                break;
            key_index -= 1
        if remain_s < 0.5:
            return [nodes[key_index]['x'], nodes[key_index]['y']]
        longlat = point_on_line_given_distance(nodes[key_index], nodes[key_index-1], remain_s)
        return longlat
    
def get_direction_by_s(nodes, distance, direction:str='front'):
    temp_sum = 0
    if direction == 'front':
        # 顺道路方向前进
        if distance == 0:
            return [nodes[0]['x'], nodes[0]['y']]
        key_index = 0  # first node
        for i in range(1, len(nodes)):
            x1, y1 = nodes[i-1]['x'], nodes[i-1]['y']
            x2, y2 = nodes[i]['x'], nodes[i]['y']
            temp_sum += math.sqrt((x2 - x1)**2 + (y2-y1)**2)
            if temp_sum > distance:
                break;
            key_index += 1
        if key_index == len(nodes)-1:
            # 端点
            x = nodes[key_index]['x']-nodes[key_index-1]['x']
            y = nodes[key_index]['y']-nodes[key_index-1]['y']
            return get_angle(x, y)
        else:
            # 中间点
            x = nodes[key_index+1]['x'] - nodes[key_index]['x']
            y = nodes[key_index+1]['y'] - nodes[key_index]['y']
            return get_angle(x, y)
    elif direction == 'back':
        # 逆道路方向前进
        if distance == 0:
            return [nodes[-1]['x'], nodes[-1]['y']]
        key_index = len(nodes)-1  # last node
        for i in range(len(nodes)-1, 0, -1):
            x1, y1 = nodes[i]['x'], nodes[i]['y']
            x2, y2 = nodes[i-1]['x'], nodes[i-1]['y']
            temp_sum += math.sqrt((x2 - x1)**2 + (y2-y1)**2)
            if temp_sum > distance:
                break;
            key_index -= 1
        if key_index == 0:
            x = nodes[key_index]['x'] - nodes[key_index+1]['x']
            y = nodes[key_index]['y'] - nodes[key_index+1]['y']
            return get_angle(x, y)
        else:
            x = nodes[key_index-1]['x'] - nodes[key_index]['x']
            y = nodes[key_index-1]['y'] - nodes[key_index]['y']
            return get_angle(x, y)
    else:
        print("Warning: wroing direction, 'front' instead")
        if distance == 0:
            return [nodes[0]['x'], nodes[0]['y']]
        key_index = 0  # first node
        for i in range(1, len(nodes)):
            x1, y1 = nodes[i-1]['x'], nodes[i-1]['y']
            x2, y2 = nodes[i]['x'], nodes[i]['y']
            temp_sum += math.sqrt((x2 - x1)**2 + (y2-y1)**2)
            if temp_sum > distance:
                break;
            key_index += 1
        if key_index == len(nodes)-1:
            # 端点
            x = nodes[key_index]['x']-nodes[key_index-1]['x']
            y = nodes[key_index]['y']-nodes[key_index-1]['y']
            return get_angle(x, y)
        else:
            # 中间点
            x = nodes[key_index+1]['x'] - nodes[key_index]['x']
            y = nodes[key_index+1]['y'] - nodes[key_index]['y']
            return get_angle(x, y)