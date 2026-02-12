#ifndef MESH_H
#define MESH_H

#include "shader.h"
#include <glad/glad.h>
#include <glm/glm.hpp>
#include <vector>

struct Vertex {
    glm::vec3 position;
    glm::vec3 normal;
};

struct Point {
    glm::vec3 position;
    unsigned int id;
};

struct Face {
    std::vector<unsigned int> points;
    glm::vec3 normal;
};

class Mesh {
public:
    std::vector<Vertex> vertices;
    std::vector<unsigned int> indices;

    Mesh();
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

    void setupMesh();
    void triangulateMesh();
};

#endif