import re
from pathlib import Path

propspattern = re.compile(r'defineProps<{[^{}]*}>')
propspersepattern = re.compile(r'(\w+):\s*([\w\[\]]+)')
emitspattern = re.compile(r'defineEmits<{[^{}]*}>')
emitspersepattern = re.compile(r"\(event:\s*'(\w+)',\s*([^)]+)\):\s*void")
emitsargspattern = re.compile(r"(\w+):\s*([^),]+)")
componentnamepattern = re.compile(r'<[^\s]*')

def getFiles():
    rootdir = input("Enter the root directory: ")
    files = list(Path(rootdir).rglob("*.vue"))
    
    return files

def getProps(file):
    ret = []

    with open(file, "r", encoding='utf-8') as f:
        content = f.read()
        props = propspattern.search(content)
        if props is not None:
            for prop in propspersepattern.finditer(props.group()):
                name = prop.group(1)
                type = prop.group(2)
                ret.append({"name": name, "type": type})

    return ret

def getEmits(file):
    ret = []

    with open(file, "r", encoding='utf-8') as f:
        content = f.read()
        emits = emitspattern.search(content)
        if emits is not None:            
            for emit in emitspersepattern.finditer(emits.group()):
                name = emit.group(1)
                argsmatch = emit.group(2)
                args = []

                for arg in emitsargspattern.finditer(argsmatch):
                    argname = arg.group(1)
                    argtype = arg.group(2)
                    args.append({"name": argname, "type": argtype})

                ret.append({"name": name, "args": args})

    return ret

def findChildrenComponents(file, componentnames):
    ret = []

    with open(file, "r", encoding='utf-8') as f:
        content = f.read()
        for name in componentnames:
            res = componentnamepattern.findall(content)
            for r in res:
                if r[1:] == name:
                    ret.append(name)
                    break

    return ret

def generateUML(data, components):
    ret = ""
    ret += "@startuml output.png\n"

    for component in data.keys():
        ret += f"class {component} {{\n"

        for prop in data[component]["props"]:
            ret += f"  + {prop['name']}: {prop['type']}\n"

        for emit in data[component]["emits"]:
            ret += f"  + {emit['name']}("
            for arg in emit['args']:
                ret += f"{arg['name']}: {arg['type']}, "
            ret = ret[:-2] + ")\n"

        ret += "}\n"

    for component in components.keys():
        for child in components[component]:
            if len(data[child]['props']) > 0:
                ret += f"{component} -down-> {child} : {', '.join(map(lambda p : p['name'], data[child]['props']))}\n"
            if len(data[child]['emits']) > 0:
                ret += f"{child} -up-> {component} : {', '.join(map(lambda p : f"{p['name']}({','.join(map(lambda a : a['name'], p['args']))})", data[child]['emits']))}\n"
            if len(data[child]['props']) == 0 and len(data[child]['emits']) == 0:
                ret += f"{component} -- {child}\n"
    ret += "@enduml"
    return ret

if __name__ == "__main__":
    data = {}
    components = {}

    files = getFiles()
    for file in files:
        #print(file)
        props = getProps(file)
        emits = getEmits(file)
        data[file.name[:-4]] = {"props": props, "emits": emits}
    
    componentnames = data.keys()

    for file in files:
        children = findChildrenComponents(file, componentnames)
        components[file.name[:-4]] = children

    #print(data)
    #print(components)

    uml = generateUML(data, components)

    output = "output.pu"
    with open(output, "w", encoding='utf-8') as f:
        f.write(uml)