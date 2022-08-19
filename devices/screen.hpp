#include <SFML/Graphics.hpp>
#include <iostream>
#include <bitset>

class Screen
{
private:
    std::pair <int, int> pixelSize = {10, 10};
    sf::RectangleShape pixelRectangle = sf::RectangleShape(sf::Vector2f(pixelSize.first, pixelSize.second));
    std::pair <int, int> size = {60, 60};
    std::pair <int, int> cursor = {0, 0};
    bool lastFlag = false;

    sf::RenderWindow window = sf::RenderWindow(sf::VideoMode(pixelSize.first * size.first, pixelSize.second * size.second), "15");

    sf::Color getColor(std::bitset<16> input)
    {
        return sf::Color((input[0] + (input[1] << 1) + (input[2] << 2) + (input[3] << 3) + (input[4] << 4)) << 3,
                         (input[5] + (input[6] << 1) + (input[7] << 2) + (input[8] << 3) + (input[9] << 4)) << 3,
                         (input[10] + (input[11] << 1) + (input[12] << 2) + (input[13] << 3) + (input[14] << 4)) << 3
                         );
    }

    void draw(sf::Color color)
    {
        pixelRectangle.setFillColor(color);
        pixelRectangle.setPosition(cursor.first * pixelSize.first, cursor.second * pixelSize.second);
        window.draw(pixelRectangle);
        cursor.first++;
        if (cursor.first == size.first)
            cursor = {0, cursor.second + 1};
        if (cursor.second == size.second)
            cursor.second = 0;
    }

public:
    Screen()
    {
        window.setFramerateLimit(30);
    }

    void handle(std::bitset<16> input)
    {
        char flag = input[15];
        if (flag && !lastFlag)
        {
            draw(getColor(input));
        }
        lastFlag = flag;
    }

    void render()
    {
        window.display();
    }
};
