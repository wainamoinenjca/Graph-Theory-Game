import pygame
import networkx as nx
import random

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

def draw_graph(anotherMessage):
    screen.fill(WHITE)
    for edge in edges:
        pygame.draw.line(screen, BLACK, nodes[edge[0]], nodes[edge[1]], 2)
    for node, pos in nodes.items():
        pygame.draw.circle(screen, BLUE, pos, nodeSize)
        text = font.render(str(node), True, BLACK)
        screen.blit(text, (pos[0] - 2 * nodeSize, pos[1] - 2 * nodeSize))
    sigDisplayText = font.render("Current Signature:" + str(currentSig), True, BLACK)    
    screen.blit(sigDisplayText, (400, 30))
    goalDisplayText = font.render("Goal Signature: " + str(currentGoalSig), True, BLACK)
    screen.blit(goalDisplayText, (75, 30))
    
    if anotherMessage == True:
        sigDisplayText = font.render("Solution found! Play again? y/n", True, BLACK)            
        screen.blit(sigDisplayText, (375, 50))
        
    pygame.display.flip()

def eval_graph():
    global currentSig
    if len(nodes) == 0 or len(nodes) == 1 or len(edges) == 0:
        return [0]
        
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
    while sig[-1] == 0:
        sig = sig[:-1]
    
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

def main():
    running = True
    node_id = 0
    selected_node = None
    #graphChanged bool
    graphChanged = False
    pickNewGoalSigRndm()
    anotherMessage = False
    solutionCheckRes = False
    global currentSig

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if event.button == 1:  # Left click to add/select nodes
                    for node, npos in nodes.items():
                        if (npos[0] - pos[0]) ** 2 + (npos[1] - pos[1]) ** 2 <= 100:
                            selected_node = node
                            graphChanged = True
                            break
                    else:
                        nodes[node_id] = pos
                        G.add_node(node_id)
                        node_id += 1
                elif event.button == 3 and selected_node is not None:  # Right click to connect nodes
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
                if event.key == pygame.K_r:  # Press 'r' to reset the graph
                    G.clear()
                    nodes.clear()
                    edges.clear()
                    node_id = 0
                    currentSig = []
                if event.key == pygame.K_y and anotherMessage == True:
                    G.clear()
                    nodes.clear()
                    edges.clear()
                    node_id = 0
                    pickNewGoalSigRndm()
                    anotherMessage = False
                    solutionCheckRes = False
                    currentSig = []
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
