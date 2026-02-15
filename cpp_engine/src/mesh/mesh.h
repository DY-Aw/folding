#ifndef MESH_H
#define MESH_H

#include "shader.h"
#include <glad/glad.h>
#include <glm/glm.hpp>
#include <glm/gtc/constants.hpp>
#include <nlohmann/json.hpp>
#include <vector>
#include <string>
#include <fstream>

using json = nlohmann::json;

enum class MeshState {
    CLEAN = 0,
    POSITIONS_DIRTY = 1,
    TOPOLOGY_DIRTY = 2
};

struct Vertex {
    glm::vec3 position;
    glm::vec3 normal;
    unsigned int pID;
    unsigned int fID;

    Vertex(glm::vec3 pos, glm::vec3 norm, unsigned int _pID, unsigned int _fID) : position(pos), normal(norm), pID(_pID), fID(_fID) {}
};

struct Point {
    glm::vec3 position;
    unsigned int id;

    Point(glm::vec3 pos, unsigned int _id) : position(pos), id(_id) {}
};

struct Face {
    std::vector<unsigned int> points;
    glm::vec3 normal;
    unsigned int id;
    bool dirty = false;

    Face(std::vector<unsigned int> _points, unsigned int _id) : points(_points), id(_id) {}
};

class Mesh {
public:
    std::vector<Vertex> vertices;
    std::vector<unsigned int> indices;
    std::vector<Point> points;
    std::vector<Face> faces;

    //----------Mesh-----------
    Mesh(std::string model);
    void updateBuffers();
    const void draw();
    void updateModelMatrix(Shader &shader);
    glm::mat4 getModelMatrix();

    //---------Geometry---------
    void fold(Face* f1, Face* f2, Point p1, Point p2, double theta);

private:
    MeshState meshState = MeshState::TOPOLOGY_DIRTY;
    unsigned int VAO, VBO, EBO;
    glm::mat4 modelMatrix;
    glm::vec3 position = glm::vec3(0.0f);
    glm::vec3 rotation = glm::vec3(0.0f);

    //---------Geometry---------
    void syncVertexData();
    void triangulateMesh();
    void calculateFaceNormal(Face* f);

    //-----------GPU------------
    void setupMesh();
    void updatePositions();
    void updateTopology();

    //-----------IO-------------
    bool loadFromJSON(const std::string& model);

};

#endif