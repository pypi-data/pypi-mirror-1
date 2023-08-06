def is_cyclic(step, steps_map, visited=None):

    if visited is None:
        visited = []

    if step in visited:
        # we want to say True only if the node is involved in the cycle,
        # not if the cycle is in one of its dependencies
        return visited.index(step) == 0

    visited.append(step)
    deps = steps_map.get(step, ())

    for d in deps:
        tmp_visited = list(visited)
        if is_cyclic(d, steps_map, tmp_visited):
            return True
    return False

def _computeTopologicalSort( steps ):
    result = []
    graph = [ ( x[ 'id' ], x[ 'dependencies' ] ) for x in steps]

    unresolved = []
    cyclics_inserted = False
    existing_edges = frozenset((x['id'] for x in steps))

    while True:
        for node, edges in graph:

            after = -1
            resolved = 0

            for edge in edges:

                if edge not in existing_edges:
                    # missing edged, don't bother
                    resolved += 1

                elif edge in result:
                    resolved += 1
                    after = max( after, result.index( edge ) )

            if len(edges) > resolved:
                unresolved.append((node, edges))
            else:
                result.insert( after + 1, node )

        if not unresolved:
            break
        if len(unresolved) == len(graph):
            # Nothing was resolved in this loop. There must be circular or
            # missing dependencies. Just add them to the end. We can't
            # raise an error, because checkComplete relies on this method.

            # 1st pass: insert cyclics in result before others, and let others
            # have a chance to be inserted with dependencies better resolved
            if not cyclics_inserted:
                cyclics_inserted = True
                node_map = dict(graph)
                graph = []
                unresolved = []
                for step in node_map:
                    if is_cyclic(step, node_map):
                        result.append(step)
                    else:
                        graph.append((step, node_map[step]))
                continue

            # 2nd pass: cyclics have been inserted, add remaining nodes
            for node, edges in unresolved:
                print repr((node, edges))
                result.append(node)
            break
        graph = unresolved
        unresolved = []

    return result
