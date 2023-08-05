def visualize(insts):
    import xmlrpclib
    g = xmlrpclib.Server("http://localhost:8080/grinedit/").grinedit
    g.initGraph()

    start = g.addVertex("CircleVertex", {"color": (255,0,0), "diameter": 20})
    vs = {}
    for i in insts:
        vs[i] = g.addVertex("MultiLineBoxVertex",
                            {"label": "%s(%s)" % (i.opname, i.argstr),
                             "fontResize": False})

    g.addEdge("LinearEdge", {"v1": start, "v2": vs[insts[0]]})

    # next
    for i in insts:
        if i.next and i not in i.next.relyOn:
            g.addEdge("ArrowEdge",
                      {"v1": vs[i], "v2": vs[i.next],
                       "color": (127, 127, 255), "scale": 1.5})
    
    # relyOn
    for i in insts:
        for j in i.relyOn:
            g.addEdge("ArrowEdge",
                      {"v1": vs[j], "v2": vs[i],
                       "color": (0,0,255), "scale": 3.0})
    
    # jumpTo
    for i in insts:
        if i.jumpTo != None:
            g.addEdge("ArrowEdge",
                      {"v1": vs[i], "v2": vs[i.jumpTo],
                       "color": (255,0,0), "scale": 3.0,
                       "strength": 0.001})

    
    g.modLaw("PL_Repulsion", {"RepulsionRadius": 30.0})
