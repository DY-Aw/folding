#include "camera.h"

Camera::Camera(float yaw, float pitch, float zoom) 
    : yaw(yaw), pitch(pitch), zoom(zoom) {}

glm::vec3 Camera::getFacing() {
    glm::vec3 facing;
    facing.x = cos(glm::radians(yaw)) * cos(glm::radians(pitch));
    facing.y = sin(glm::radians(pitch));
    facing.z = sin(glm::radians(yaw)) * cos(glm::radians(pitch));
    return glm::normalize(facing);
}

glm::mat4 Camera::getViewMatrix() {
    return viewMatrix;
}

void Camera::updateViewMatrix(Shader &shader) {
    position = -zoom * getFacing();
    viewMatrix = glm::lookAt(position, glm::vec3(0.0f, 0.0f, 0.0f), glm::vec3(0.0f, 1.0f, 0.0f));
    shader.setMat4("view", viewMatrix);
}

void Camera::orbit(float xoffset, float yoffset) {
    yaw += xoffset;
    pitch += yoffset;

    if (pitch > 89.0f)  pitch = 89.0f;
    if (pitch < -89.0f) pitch = -89.0f;
}

void Camera::changeZoom(float yoffset) {
    zoom -= yoffset;
    if (zoom < 1.0f) zoom = 1.0f;
}