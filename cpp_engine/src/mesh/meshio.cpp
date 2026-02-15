#include "mesh.h"

bool Mesh::loadFromJSON(const std::string& model) {
    points.clear();
    faces.clear();
    std::ifstream file("models/" + model);
    if (!file.is_open()) {
        std::cerr << "Could not open file: models/" << model << std::endl;
        return false;
    }
    try {
        json data = json::parse(file);
        unsigned int p_id = 0, f_id = 0;
        for (const auto& p : data["points"]) {
            glm::vec3 point(p[0], p[1], p[2]);
            points.push_back(Point(point, p_id));
            p_id++;
        }
        for (const auto& f : data["faces"]) {
            std::vector<unsigned int> faceIndices = f.get<std::vector<unsigned int>>();
            faces.push_back(Face(faceIndices, f_id));
            calculateFaceNormal(&faces.back());
            f_id++;
        }
        return true;
    } catch (json::parse_error& e) {
        std::cerr << "JSON Parse Error: " << e.what() << std::endl;
        return false;
    }
}
