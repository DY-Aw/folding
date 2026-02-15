#ifndef EVENTS_H
#define EVENTS_H

#include "camera.h"
#include <GLFW/glfw3.h>

struct MouseState {
    float x = 0, y = 0;
    float deltaX = 0, deltaY = 0;
    bool middleDown = false;
    bool leftDown = false;
    bool rightDown = false;
    float scrollOffset = 0;
    bool firstMouse = true;
};

class EventHandler {
public:
    MouseState mouse;
    Camera* camera;

    EventHandler(GLFWwindow* window, Camera* cam) : camera(cam) {
        glfwSetWindowUserPointer(window, this);
        glfwSetCursorPosCallback(window, static_cursor_callback);
        glfwSetMouseButtonCallback(window, static_mouse_callback);
        glfwSetScrollCallback(window, static_scroll_callback);
    }

    void poll() {
        mouse.deltaX = 0;
        mouse.deltaY = 0;
        glfwPollEvents();
        handle_camera_movement();
    }
private:
    static void static_cursor_callback(GLFWwindow* window, double xpos, double ypos);
    static void static_mouse_callback(GLFWwindow* window, int button, int action, int mods);
    static void static_scroll_callback(GLFWwindow* window, double xoffset, double yoffset);
    void handle_cursor(float xpos, float ypos);
    void handle_mouse(int button, int action, int mods);
    void handle_scroll(float xoffset, float yoffset);
    void handle_camera_movement();
};

#endif