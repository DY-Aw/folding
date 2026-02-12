#ifndef CAMERA_H
#define CAMERA_H

#include "shader.h"
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>
#include <vector>

class Camera {
public:
    float yaw;
    float pitch;
    float zoom;
    glm::vec3 position;

    Camera(float yaw = -60.0f, float pitch = -30.0f, float zoom = 3.0f);

    glm::mat4 getViewMatrix();
    void updateViewMatrix(Shader &shader);
    void orbit(float xoffset, float yoffset);
    void changeZoom(float yoffset);

private:
    glm::mat4 viewMatrix;

    glm::vec3 getFacing();
};

#endif