from panda3d.bullet import BulletBoxShape, BulletRigidBodyNode
from panda3d.core import (Geom, GeomNode, GeomTriangles, GeomVertexData,
                          GeomVertexFormat, GeomVertexReader, GeomVertexWriter,
                          LVector3, NodePath, TransformState, Vec3)


def normalized(*args):
    myVec = LVector3(*args)
    myVec.normalize()
    return myVec


def printGeom(model):
    geomNodeCollection = model.findAllMatches("**/+GeomNode")
    for nodePath in geomNodeCollection:
        geomNode = nodePath.node()
        processGeomNode(geomNode)


def processGeomNode(geomNode):
    for i in range(geomNode.getNumGeoms()):
        geom = geomNode.getGeom(i)
        state = geomNode.getGeomState(i)
        print(geom)
        print(state)
        processGeom(geom)


def processGeom(geom):
    vdata = geom.getVertexData()
    print(vdata)
    processVertexData(vdata)


def processVertexData(vdata):
    vertex = GeomVertexReader(vdata, "vertex")
    # texcoord = GeomVertexReader(vdata, 'texcoord')
    while not vertex.isAtEnd():
        v = vertex.getData3()
        # t = texcoord.getData2()
        print("v = %s" % (repr(v)))


# helper function to make a square given the Lower-Left-Hand and
# Upper-Right-Hand corners


def makeSquare(x1, y1, z1, x2, y2, z2, _color=(1.0, 0.0, 0.0, 1.0)):
    format = GeomVertexFormat.getV3n3c4t2()
    vdata = GeomVertexData("square", format, Geom.UHStatic)

    vertex = GeomVertexWriter(vdata, "vertex")
    normal = GeomVertexWriter(vdata, "normal")
    color = GeomVertexWriter(vdata, "color")
    texcoord = GeomVertexWriter(vdata, "texcoord")

    # make sure we draw the sqaure in the right plane
    if x1 != x2:
        vertex.addData3(x1, y1, z1)
        vertex.addData3(x2, y1, z1)
        vertex.addData3(x2, y2, z2)
        vertex.addData3(x1, y2, z2)

        normal.addData3(normalized(2 * x1 - 1, 2 * y1 - 1, 2 * z1 - 1))
        normal.addData3(normalized(2 * x2 - 1, 2 * y1 - 1, 2 * z1 - 1))
        normal.addData3(normalized(2 * x2 - 1, 2 * y2 - 1, 2 * z2 - 1))
        normal.addData3(normalized(2 * x1 - 1, 2 * y2 - 1, 2 * z2 - 1))

    else:
        vertex.addData3(x1, y1, z1)
        vertex.addData3(x2, y2, z1)
        vertex.addData3(x2, y2, z2)
        vertex.addData3(x1, y1, z2)

        normal.addData3(normalized(2 * x1 - 1, 2 * y1 - 1, 2 * z1 - 1))
        normal.addData3(normalized(2 * x2 - 1, 2 * y2 - 1, 2 * z1 - 1))
        normal.addData3(normalized(2 * x2 - 1, 2 * y2 - 1, 2 * z2 - 1))
        normal.addData3(normalized(2 * x1 - 1, 2 * y1 - 1, 2 * z2 - 1))

    # adding different colors to the vertex for visibility
    color.addData4f(*_color)
    color.addData4f(*_color)
    color.addData4f(*_color)
    color.addData4f(*_color)

    texcoord.addData2f(0.0, 1.0)
    texcoord.addData2f(0.0, 0.0)
    texcoord.addData2f(1.0, 0.0)
    texcoord.addData2f(1.0, 1.0)

    tris = GeomTriangles(Geom.UHStatic)
    tris.addVertices(0, 1, 3)
    tris.addVertices(1, 2, 3)

    square = Geom(vdata)
    square.addPrimitive(tris)
    return square


def make_cube(hsize, color, front_color):
    square0 = makeSquare(-hsize, -hsize, -hsize, hsize, -hsize, hsize, front_color)
    square1 = makeSquare(-hsize, hsize, -hsize, hsize, hsize, hsize, color)
    square2 = makeSquare(-hsize, hsize, hsize, hsize, -hsize, hsize, color)
    square3 = makeSquare(-hsize, hsize, -hsize, hsize, -hsize, -hsize, color)
    square4 = makeSquare(-hsize, -hsize, -hsize, -hsize, hsize, hsize, color)
    square5 = makeSquare(hsize, -hsize, -hsize, hsize, hsize, hsize, color)
    snode = GeomNode("square")
    snode.addGeom(square0)
    snode.addGeom(square1)
    snode.addGeom(square2)
    snode.addGeom(square3)
    snode.addGeom(square4)
    snode.addGeom(square5)
    return snode


def make_rectangle(hsizex, hsizey, hsizez, color, front_color):
    square0 = makeSquare(
        -hsizex, -hsizey, -hsizez, hsizex, -hsizey, hsizez, front_color
    )
    square1 = makeSquare(-hsizex, hsizey, -hsizez, hsizex, hsizey, hsizez, color)
    square2 = makeSquare(-hsizex, hsizey, hsizez, hsizex, -hsizey, hsizez, color)
    square3 = makeSquare(-hsizex, hsizey, -hsizez, hsizex, -hsizey, -hsizez, color)
    square4 = makeSquare(-hsizex, -hsizey, -hsizez, -hsizex, hsizey, hsizez, color)
    square5 = makeSquare(hsizex, -hsizey, -hsizez, hsizex, hsizey, hsizez, color)
    snode = GeomNode("square")
    snode.addGeom(square0)
    snode.addGeom(square1)
    snode.addGeom(square2)
    snode.addGeom(square3)
    snode.addGeom(square4)
    snode.addGeom(square5)
    return snode
