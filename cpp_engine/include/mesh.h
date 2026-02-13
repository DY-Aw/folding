#ifndef MESH_H
#define MESH_H

#include "shader.h"
#include <glad/glad.h>
#include <glm/glm.hpp>
#include <nlohmann/json.hpp>
#include <vector>
#include <string>
#include <fstream>

using json = nlohmann::json;

struct Vertex {
    glm::vec3 position;
    glm::vec3 normal;
};

struct Point {
    glm::vec3 position;
    unsigned int id;

    Point(glm::vec3 pos, unsigned int _id) : position(pos), id(_id) {}
};

struct Face {
    std::vector<unsigned int> points;
    glm::vec3 normal;

    Face(std::vector<unsigned int> _points) : points(_points) {}
};

class Mesh {
public:
    std::vector<Vertex> vertices;
    std::vector<unsigned int> indices;

    Mesh(std::string model);
    glm::mat4 getModelMatrix();
    void updateModelMatrix(Shader &shader);
    void updateBuffers();
    void draw();
private:
    std::vector<Point> points;
    std::vector<Face> faces;
    unsigned int VAO, VBO, EBO;
    glm::mat4 modelMatrix;
    glm::vec3 position = glm::vec3(0.0f);
    glm::vec3 rotation = glm::vec3(0.0f);

    bool loadFromJSON(const std::string& model);
    void setupMesh();
    void triangulateMesh();
};

#endif