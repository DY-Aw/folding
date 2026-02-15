#include "mesh.h"
#include "shader.h"
#include <glad/glad.h>
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>
#include <string>

Mesh::Mesh(const std::string model) : VAO(0), VBO(0), EBO(0) {
    if (model.empty() || !loadFromJSON(model)) {
        this->points = {
            {glm::vec3(-0.5f,  0.0f, 0.5f), 0},
            {glm::vec3( 0.5f,  0.0f, 0.5f), 1},
            {glm::vec3( 0.5f,  0.0f,-0.5f), 2},
            {glm::vec3(-0.5f,  0.0f,-0.5f), 3}
        };
        this->faces = {Face({0, 1, 2, 3}, 0)};
        this->faces[0].normal = glm::vec3(0.0f, 1.0f, 0.0f);
    }
    setupMesh();
}

void Mesh::updateBuffers() {
    switch (meshState) {
        case MeshState::CLEAN:
            return;
        case MeshState::POSITIONS_DIRTY:
            updatePositions();
            break;
        case MeshState::TOPOLOGY_DIRTY:
            updateTopology();
            break;
    }
    meshState = MeshState::CLEAN;
}

const void Mesh::draw() {
    glBindVertexArray(VAO);
    glDrawElements(GL_TRIANGLES, indices.size(), GL_UNSIGNED_INT, 0);
    glBindVertexArray(0);
}

void Mesh::updateModelMatrix(Shader &shader) {
    modelMatrix = glm::translate(glm::mat4(1.0f), position);
    modelMatrix = glm::rotate(modelMatrix, glm::radians(rotation.z), glm::vec3(0, 0, 1));
    modelMatrix = glm::rotate(modelMatrix, glm::radians(rotation.y), glm::vec3(0, 1, 0));
    modelMatrix = glm::rotate(modelMatrix, glm::radians(rotation.x), glm::vec3(1, 0, 0));
    shader.setMat4("model", modelMatrix);
}

glm::mat4 Mesh::getModelMatrix() { return modelMatrix; }