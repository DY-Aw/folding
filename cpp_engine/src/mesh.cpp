#include "mesh.h"

Mesh::Mesh(const std::string model) : VAO(0), VBO(0), EBO(0) {
    if (model.empty() || !loadFromJSON(model)) {
        this->points = {
            { glm::vec3(-0.5f,  0.0f, 0.5f), 0 },
            { glm::vec3( 0.5f,  0.0f, 0.5f), 1 },
            { glm::vec3( 0.5f,  0.0f,-0.5f), 2 },
            { glm::vec3(-0.5f,  0.0f,-0.5f), 3 }
        };
        this->faces = {
            Face({0, 1, 2, 3})
        };
        this->faces[0].normal = glm::vec3(0.0f, 1.0f, 0.0f);
    }
    setupMesh();
}

bool Mesh::loadFromJSON(const std::string& model) {
    this->points.clear();
    this->faces.clear();
    std::ifstream file("models/" + model);
    if (!file.is_open()) {
        std::cerr << "Could not open file: models/" << model << std::endl;
        return false;
    }
    try {
        json data = json::parse(file);
        unsigned int p_id = 0;
        for (const auto& p : data["points"]) {
            glm::vec3 point(p[0], p[1], p[2]);
            this->points.push_back(Point(point, p_id));
            p_id++;
        }
        for (const auto& f : data["faces"]) {
            std::vector<unsigned int> faceIndices = f.get<std::vector<unsigned int>>();
            this->faces.push_back(Face(faceIndices));
        }
        for (auto& face : this->faces) {
            if (face.points.size() < 3) continue;
            glm::vec3 v0 = this->points[face.points[0]].position;
            glm::vec3 v1 = this->points[face.points[1]].position;
            glm::vec3 v2 = this->points[face.points[2]].position;
            glm::vec3 edge1 = v1 - v0;
            glm::vec3 edge2 = v2 - v0;
            face.normal = glm::normalize(glm::cross(edge1, edge2));
        }
        return true;
    } catch (json::parse_error& e) {
        std::cerr << "JSON Parse Error: " << e.what() << std::endl;
        return false;
    }
}

void Mesh::setupMesh() {
    glGenVertexArrays(1, &VAO);
    glGenBuffers(1, &VBO);
    glGenBuffers(1, &EBO);

    glBindVertexArray(VAO);
    updateBuffers();

    glEnableVertexAttribArray(0);
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, sizeof(Vertex), (void*)0);

    glEnableVertexAttribArray(1);
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, sizeof(Vertex), (void*)offsetof(Vertex, normal));

    glBindVertexArray(0);
}

void Mesh::updateBuffers() {
    triangulateMesh();
    glBindVertexArray(VAO);
    glBindBuffer(GL_ARRAY_BUFFER, VBO);
    glBufferData(GL_ARRAY_BUFFER, vertices.size() * sizeof(Vertex), &vertices[0], GL_DYNAMIC_DRAW);

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO);
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.size() * sizeof(unsigned int), &indices[0], GL_STATIC_DRAW);
}

void Mesh::triangulateMesh() {
    indices.clear();
    vertices.clear();
    for (auto f: faces) {
        unsigned int offset = (unsigned int)vertices.size();
        size_t numPoints = f.points.size();
        vertices.push_back({points[f.points[0]].position, f.normal});
        vertices.push_back({points[f.points[1]].position, f.normal});
        for (int i = 2; i < numPoints; i++) {
            vertices.push_back({points[f.points[i]].position, f.normal});
            indices.push_back(offset + 0);
            indices.push_back(offset + (unsigned int)i-1);
            indices.push_back(offset + (unsigned int)i);
        }
    }
}

glm::mat4 Mesh::getModelMatrix() { return modelMatrix; }

void Mesh::updateModelMatrix(Shader &shader) {
    modelMatrix = glm::translate(glm::mat4(1.0f), position);
    modelMatrix = glm::rotate(modelMatrix, glm::radians(rotation.z), glm::vec3(0, 0, 1));
    modelMatrix = glm::rotate(modelMatrix, glm::radians(rotation.y), glm::vec3(0, 1, 0));
    modelMatrix = glm::rotate(modelMatrix, glm::radians(rotation.x), glm::vec3(1, 0, 0));
    shader.setMat4("model", modelMatrix);
}

void Mesh::draw() {
    glBindVertexArray(VAO);
    glDrawElements(GL_TRIANGLES, indices.size(), GL_UNSIGNED_INT, 0);
    glBindVertexArray(0);
}