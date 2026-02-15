#ifndef CONSTANTS_H
#define CONSTANTS_H

#include <glm/gtc/constants.hpp>

namespace Origami {
    // Math
    static constexpr double PI = glm::pi<double>();
    static constexpr double TWO_PI = PI * 2.0;
    static constexpr double HALF_PI = PI * 0.5;

    // Folding Engine
    static constexpr double MIN_ANGLE_GAP = 1e-4;
    static constexpr double ANGLE_MAX = TWO_PI - MIN_ANGLE_GAP;
    static constexpr double ANGLE_MIN = MIN_ANGLE_GAP;
}

#endif