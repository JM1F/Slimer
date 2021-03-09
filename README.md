# Slimer
![Slimer](https://user-images.githubusercontent.com/71614127/110403148-815f4c00-8074-11eb-9414-8c2f4c8df673.png)

Simple rogue-like game made using [python-pygame](https://www.pygame.org/news).
## How to play the game
The game consists of 5 procedurally generated rooms where you have to fight a random amount of enemies where they chase you around and deal damage if they hit you. The procedurally generated rooms also can spawn health packs that allow the player to regenerate health back.

![Room](https://user-images.githubusercontent.com/71614127/110403496-13675480-8075-11eb-951f-fbd3d76df423.png)

Once all the rooms have successfully been beaten you will move onto the final room. This room contains the boss, in order to beat the game you will need to defeat the boss.

![Boss](https://user-images.githubusercontent.com/71614127/110404676-3135b900-8077-11eb-9070-e5a55d9f6e3d.png)

## Controls
<ins>Movement</ins> - W,A,S,D to move in all directions.

<ins>Aim/Fire</ins> - Use mouse to aim and MOUSE1 to shoot.

## Algorithms Used

***A * Searching Algorithm***

The blue enemies use the A* Search Algorithm to locate the player's sprite.

```python
def aStar(graph, start, end):
    # Initialize a priority queue
    Pqueue = PriorityQueue()
    Pqueue.put((start), 0)
    # Initialzing path and cost dictionary
    path = {}
    cost = {}
    # Setting the starting node None and cost to 0 
    path[(start)] = None
    cost[(start)] = 0
    # Iterate while the priority queue is not empty 
    while not Pqueue.empty():
        current = Pqueue.get()
        if current == end:
            # Break used to stop the astar search when the
            # current node and goal node are the same
            break
        # Check the next neighbouring nodes of the
        # current node
        for next in graph.node_neighbours(vector(current)):
            next = vector_to_integer(next)
            # Get the next node cost 
            next_cost = cost[current] + graph.cost(current, next)
            if next not in cost or next_cost < cost[next]:
                # Get the priority by adding the next cost and
                # the hueristic value
                priority = next_cost + heuristicValue(vector(end), vector(next))
                cost[next] = next_cost
                # Puts the node into the priority queue
                Pqueue.put(next, priority)
                path[next] = vector(current) - vector(next)
    return path

```

***Breadth-First Searching Algorithm***

Beacon items also have a chance to spawn in. This makes all the enemies attracted to the beacon's position.

<ins>Beacon Looks Like This:</ins>

![orb_green](https://user-images.githubusercontent.com/71614127/110407509-da7eae00-807b-11eb-9763-a6e533d2208e.png)

```python
def breadthfirst_search(graph, start, end):
        queue = deque()
        queue.append(start)
        path = {}
        path[start] = None
        while len(queue) > 0:
            current = queue.popleft()
            if current == end:
                break
            if graph.node_neighbours(current) != None:
                for next in graph.node_neighbours(current):
                    if vector_to_integer(next) not in path:
                        queue.append(next)
                        path[vector_to_integer(next)] = current - next
        return path
```

## Download
* You can download the game ***<ins>[HERE](https://github.com/JM1F/Slimer/files/6105404/Slimer.zip)</ins>***

## Further Reading

* This project was part of an assignment with school.

* For more information on how the project is made and the thought process behind it: <ins>[Project Write-Up](https://github.com/JM1F/Slimer/files/6105495/Project.Write.Up.pdf)</ins>
