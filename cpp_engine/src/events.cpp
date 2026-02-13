#include "events.h"

void EventHandler::static_cursor_callback(GLFWwindow* window, double xpos, double ypos) {
    auto* handler = static_cast<EventHandler*>(glfwGetWindowUserPointer(window));
    if (handler) {
        handler->handle_cursor(static_cast<float>(xpos), static_cast<float>(ypos));
    }
}

void EventHandler::static_mouse_callback(GLFWwindow* window, int button, int action, int mods) {
    auto* handler = static_cast<EventHandler*>(glfwGetWindowUserPointer(window));
    if (handler) {
        handler->handle_mouse(button, action, mods);
    }
}

void EventHandler::static_scroll_callback(GLFWwindow* window, double xoffset, double yoffset) {
    auto* handler = static_cast<EventHandler*>(glfwGetWindowUserPointer(window));
    if (handler) {
        handler->handle_scroll(static_cast<float>(xoffset), static_cast<float>(yoffset));
    }
}

void EventHandler::handle_cursor(float xpos, float ypos) {
    if (mouse.firstMouse) mouse.firstMouse = false;
    else {
        mouse.deltaX = xpos - mouse.x;
        mouse.deltaY = mouse.y - ypos;
    }
    mouse.x = xpos; 
    mouse.y = ypos;
}

void EventHandler::handle_mouse(int button, int action, int mods) {
    if (button == GLFW_MOUSE_BUTTON_MIDDLE) {
            if (action == GLFW_PRESS) {
                mouse.middleDown = true;
            } 
            else if (action == GLFW_RELEASE) {
                mouse.middleDown = false;
            }
        }
}

void EventHandler::handle_scroll(float xoffset, float yoffset) {
    camera->changeZoom(yoffset);
}

void EventHandler::handle_camera_movement() {
    if (mouse.middleDown) {
        camera->orbit(mouse.deltaX, mouse.deltaY);
    }
}