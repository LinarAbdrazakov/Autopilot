import json

with open("road_signs_info.json", "w") as file:
    names_signs = ['Stop', 'Main Road', 'One Way', 'Give Way', 'No Entry']
    color = (0, 0, 0)
    data = {}
    dirs = ['Cascades/stop_sign.xml', 'Cascades/the_main_road.xml', 'Cascades/one_way.xml', 'Cascades/give_way.xml',
            'Cascades/no_entry.xml']

    for i, name in enumerate(names_signs):
        dir = dirs[i]#input("Input directory cascades for " + name + ": ")
        #color = map(int, input("Input color for " + name + ": ").split())
        #alpha = input("Input directory cascades for ", name)
        #di = input("Input directory cascades for ", name)
        data[name] = {"dir": dir, "color": color}
    json.dump(data, file, indent=4)