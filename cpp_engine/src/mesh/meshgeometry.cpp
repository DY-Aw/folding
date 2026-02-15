#include "mesh.h"
#include "constants.h"
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>
#include <vector>
#include <cmath>

using namespace Origami;

void Mesh::syncVertexData() {
    for (auto& v : vertices) {
        v.position = points[v.pID].position;
        v.normal = faces[v.fID].normal; 
    }
}

void Mesh::triangulateMesh() {
    indices.clear();
    vertices.clear();
    for (auto f: faces) {
        unsigned int offset = (unsigned int)vertices.size();
        size_t numPoints = f.points.size();
        vertices.push_back(Vertex(points[f.points[0]].position, f.normal, f.points[0], f.id));
        vertices.push_back(Vertex(points[f.points[1]].position, f.normal, f.points[1], f.id));
        for (int i = 2; i < numPoints; i++) {
            vertices.push_back(Vertex(points[f.points[i]].position, f.normal, f.points[i], f.id));
            indices.push_back(offset + 0);
            indices.push_back(offset + (unsigned int)i-1);
            indices.push_back(offset + (unsigned int)i);
        }
    }
}

void Mesh::calculateFaceNormal(Face* f) {
    if (!f || f->points.size() < 3) return;
    glm::vec3 v0 = points[f->points[0]].position;
    glm::vec3 v1 = points[f->points[1]].position;
    for (size_t j = 2; j < f->points.size(); ++j) {
        glm::vec3 v2 = points[f->points[j]].position;
        glm::vec3 edge1 = v1 - v0;
        glm::vec3 edge2 = v2 - v0;
        glm::vec3 cross = glm::cross(edge1, edge2);

        if (glm::length(cross) > 0.0001f) {
            f->normal = glm::normalize(cross);
            return;
        }
    }
}

void Mesh::fold(Face* f1, Face* f2, Point p1, Point p2, double theta) {
    glm::dvec3 axis = glm::normalize(p1.position - p2.position);
    glm::dvec3 pivot = p1.position;

    double theta0 = std::acos(-glm::dot(f1->normal, f2->normal));
    glm::dvec3 cross = glm::cross(f1->normal, f2->normal);
    if (glm::dot(axis, cross) < 0) {
        theta0 = TWO_PI - theta0;
    }

    if (theta > 0) theta = std::min(theta, ANGLE_MAX - theta0);
    else theta = std::max(theta, ANGLE_MIN - theta0);

    glm::dmat4 toOrigin = glm::translate(glm::dmat4(1.0), -pivot);
    glm::dmat4 rotation = glm::rotate(glm::dmat4(1.0), theta, axis);
    glm::dmat4 fromOrigin = glm::translate(glm::dmat4(1.0), pivot);
    glm::dmat4 fullTransform = fromOrigin * rotation * toOrigin;

    for (auto p_id : f1->points) {
        glm::dvec4 transformed = fullTransform * glm::dvec4(points[p_id].position, 1.0);
        points[p_id].position = glm::vec3(transformed);
    }
    calculateFaceNormal(f1);
    meshState = MeshState::POSITIONS_DIRTY;
}