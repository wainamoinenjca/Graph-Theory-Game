import pygame
import networkx as nx
import random
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Graph Theory Game")
nodeSize = 10

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

# Font
font = pygame.font.Font(None, 36)

# Initialize the graph
G = nx.Graph()

# Node and edge data
nodes = {}
edges = []

currentSig = []
goalSigs = [[0,3,2], [0,4,2], [0,0,6], [3,0,3], [0,0,4,4]]
currentGoalSig = ""

# Delete mode variables
deleteMode = False
nearestElement = None  # Can be ('node', node_id) or ('edge', edge_tuple)

def find_nearest_element(pos):
    """Find the nearest node or edge to the given position"""
    min_dist = float('inf')
    nearest = None
    
    # Check nodes
    for node, npos in nodes.items():
        dist = math.sqrt((npos[0] - pos[0]) ** 2 + (npos[1] - pos[1]) ** 2)
        if dist < min_dist:
            min_dist = dist
            nearest = ('node', node)
    
    # Check edges (distance to line segment)
    for edge in edges:
        p1 = nodes[edge[0]]
        p2 = nodes[edge[1]]
        
        # Calculate distance from point to line segment
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        if dx == 0 and dy == 0:
            dist = math.sqrt((p1[0] - pos[0]) ** 2 + (p1[1] - pos[1]) ** 2)
        else:
            t = max(0, min(1, ((pos[0] - p1[0]) * dx + (pos[1] - p1[1]) * dy) / (dx * dx + dy * dy)))
            proj_x = p1[0] + t * dx
            proj_y = p1[1] + t * dy
            dist = math.sqrt((proj_x - pos[0]) ** 2 + (proj_y - pos[1]) ** 2)
        
        if dist < min_dist:
            min_dist = dist
            nearest = ('edge', edge)
    
    return nearest

def draw_graph(anotherMessage):
    screen.fill(WHITE)
    
    # Draw edges
    for edge in edges:
        color = BLACK
        width = 2
        # Highlight edge if it's the nearest in delete mode
        if deleteMode and nearestElement and nearestElement[0] == 'edge' and nearestElement[1] == edge:
            color = RED
            width = 4
        pygame.draw.line(screen, color, nodes[edge[0]], nodes[edge[1]], width)
    
    # Draw nodes
    for node, pos in nodes.items():
        color = BLUE
        size = nodeSize
        # Highlight node if it's the nearest in delete mode
        if deleteMode and nearestElement and nearestElement[0] == 'node' and nearestElement[1] == node:
            color = RED
            size = nodeSize + 3
        pygame.draw.circle(screen, color, pos, size)
        #text = font.render(str(node), True, BLACK)
        #screen.blit(text, (pos[0] - 2 * nodeSize, pos[1] - 2 * nodeSize))
    
    # Display signatures
    sigDisplayText = font.render("Current Signature:" + str(currentSig), True, BLACK)    
    screen.blit(sigDisplayText, (400, 30))
    goalDisplayText = font.render("Goal Signature: " + str(currentGoalSig), True, BLACK)
    screen.blit(goalDisplayText, (75, 30))
    
    # Display delete mode indicator
    if deleteMode:
        modeText = font.render("DELETE MODE (press 'd' to exit)", True, RED)
        screen.blit(modeText, (200, 560))
    
    if anotherMessage == True:
        sigDisplayText = font.render("Solution found! Play again? y/n", True, BLACK)            
        screen.blit(sigDisplayText, (375, 50))
        
    pygame.display.flip()

def eval_graph():
    global currentSig
    if len(nodes) == 0 or len(nodes) == 1 or len(edges) == 0:
        currentSig = [0]
        return
        
    bucket = [0] * len(nodes)
    #bucket holds edge counts
    for edge in edges:
        bucket[edge[0]] += 1
        bucket[edge[1]] += 1
    sig = [0] * (len(nodes) - 1)
    #group for sig
    for i in bucket:
        if i == 0:
            continue
        sig[i - 1] += 1
    #remove trailing zeroes
    while len(sig) > 0 and sig[-1] == 0:
        sig = sig[:-1]
    
    if len(sig) == 0:
        sig = [0]
    
    print(bucket)
    print("sig = ", sig)
    currentSig = sig

def pickNewGoalSigRndm():
    global currentGoalSig
    currentGoalSig = random.choice(goalSigs)
    
def solutionCheck():
    print("solCheck called, currentSig = ", currentSig, "Goal = ", currentGoalSig)
    if len(nodes) < sum(currentGoalSig):
        return False
    elif str(currentGoalSig) == str(currentSig):
        return True

def delete_element(element):
    """Delete a node or edge from the graph"""
    if element[0] == 'node':
        node_id = element[1]
        # Remove all edges connected to this node
        edges_to_remove = [e for e in edges if node_id in e]
        for edge in edges_to_remove:
            edges.remove(edge)
            G.remove_edge(edge[0], edge[1])
        # Remove the node
        del nodes[node_id]
        G.remove_node(node_id)
    elif element[0] == 'edge':
        edge = element[1]
        edges.remove(edge)
        G.remove_edge(edge[0], edge[1])

def main():
    global deleteMode, nearestElement, currentSig
    
    running = True
    node_id = 0
    selected_node = None
    graphChanged = False
    pickNewGoalSigRndm()
    anotherMessage = False
    solutionCheckRes = False

    while running:
        # Update nearest element in delete mode
        if deleteMode:
            mouse_pos = pygame.mouse.get_pos()
            nearestElement = find_nearest_element(mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if event.button == 1:  # Left click
                    if deleteMode and nearestElement:
                        # Delete the nearest element
                        delete_element(nearestElement)
                        nearestElement = None
                        eval_graph()
                        solutionCheckRes = solutionCheck()
                    else:
                        # Add/select nodes (original behavior)
                        for node, npos in nodes.items():
                            if (npos[0] - pos[0]) ** 2 + (npos[1] - pos[1]) ** 2 <= 100:
                                selected_node = node
                                graphChanged = True
                                break
                        else:
                            nodes[node_id] = pos
                            G.add_node(node_id)
                            node_id += 1
                elif event.button == 3 and selected_node is not None and not deleteMode:  # Right click to connect nodes
                    for node, npos in nodes.items():
                        if (npos[0] - pos[0]) ** 2 + (npos[1] - pos[1]) ** 2 <= 100 and node != selected_node:
                            G.add_edge(selected_node, node)
                            if not (selected_node, node) in edges and not (node, selected_node) in edges:
                                edges.append((selected_node, node))
                                graphChanged = True
                                eval_graph()
                                solutionCheckRes = solutionCheck()
                            selected_node = None
                            break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:  # Press 'd' to toggle delete mode
                    deleteMode = not deleteMode
                    if not deleteMode:
                        nearestElement = None
                if event.key == pygame.K_r:  # Press 'r' to reset the graph
                    G.clear()
                    nodes.clear()
                    edges.clear()
                    node_id = 0
                    currentSig = []
                    deleteMode = False
                    nearestElement = None
                if event.key == pygame.K_y and anotherMessage == True:
                    G.clear()
                    nodes.clear()
                    edges.clear()
                    node_id = 0
                    pickNewGoalSigRndm()
                    anotherMessage = False
                    solutionCheckRes = False
                    currentSig = []
                    deleteMode = False
                    nearestElement = None
                    draw_graph(anotherMessage)
            if graphChanged == True:
                eval_graph()
                graphChanged = False
            if solutionCheckRes == True:
                anotherMessage = True

        draw_graph(anotherMessage)

    pygame.quit()

if __name__ == "__main__":
    main()
