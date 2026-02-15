#include "shader.h"
#include "mesh/mesh.h"
#include "camera.h"
#include "events.h"
#include <string>
#include <glad/glad.h>
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>
#include <GLFW/glfw3.h>

Mesh* paper;
const unsigned int sw = 1500;
const unsigned int sh = 900;
const float yfov = glm::radians(45.0f);

//  Debug: ----------------------------------
const std::string model = "";
//  -----------------------------------------

int main() {
    glfwInit();
    GLFWwindow* window = glfwCreateWindow(sw, sh, "Origami Engine", NULL, NULL);
    glfwMakeContextCurrent(window);
    gladLoadGLLoader((GLADloadproc)glfwGetProcAddress);

    Shader shader("shaders/vertex.vert", "shaders/fragment.frag");
    Camera camera;

    glfwSetWindowUserPointer(window, &camera);

    glm::mat4 projection = glm::perspective(yfov, (float)sw / (float)sh, 0.1f, 100.0f);

    shader.use();
    shader.setMat4("projection", projection);

    paper = new Mesh(model);
    EventHandler eventhandler{window, &camera};
    glClearColor(0.1f, 0.1f, 0.1f, 1.0f);
    glEnable(GL_DEPTH_TEST);
    while (!glfwWindowShouldClose(window)) {
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
        shader.use();
        eventhandler.poll();
        camera.updateViewMatrix(shader);
        paper->updateModelMatrix(shader);

        paper->updateBuffers();

        paper->draw();
        glfwSwapBuffers(window);
    }
    glDeleteProgram(shader.ID);
    glfwTerminate();
    return 0;
}