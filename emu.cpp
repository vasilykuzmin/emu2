#include <iostream>
#include <bitset>
#include <ctime>
#include <chrono>
#include "translation.hpp"

using namespace std::literals;

int main()
{
#ifdef AUTOMATIC
    for (int i = 0; i < (1 << ISIZE); ++i)
    {
        std::bitset<ISIZE> ibs = i;
        std::bitset<OSIZE> obs = solve(ibs);

        #ifdef ISHAPE
        int ii = 0;
        for (int i : ISHAPE)
        {
            for (int j = 0; j < i; ++j)
            {
                std::cout << ibs[ii++];
            }
            std::cout << ' ';
        }
        #endif

        std::cout << "| ";
        
        #ifdef OSHAPE
        int oo = 0;
        for (int i : OSHAPE)
        {
            for (int j = 0; j < i; ++j)
            {
                std::cout << obs[oo++];
            }
            std::cout << ' ';
        }
        std::cout << '\n';
        #endif
    }
#endif
#ifdef MANUAL
    while (true)
    {
        std::bitset<ISIZE> ipins;
        int ii = 0;
        for (int i : ISHAPE)
        {
            std::string s;
            std::cin >> s;
            for (char j : s)
            {
                ipins[ii++] = (j == '0' ? 0 : 1);
            }
        }
        std::bitset<OSIZE> opins = solve(ipins);

        #ifdef OSHAPE
            int oo = 0;
            for (int i : OSHAPE)
            {
                for (int j = 0; j < i; ++j)
                {
                    std::cout << opins[oo++];
                }
                std::cout << ' ';
            }
            std::cout << '\n';
        #endif
    }
#endif
#ifdef REPEAT
    std::bitset<ISIZE> ipins;
    auto last = std::chrono::steady_clock::now();
    int iterations = 0;
    while (true)
    {
        ipins = solve(ipins);
        iterations++;
        auto nlast = std::chrono::steady_clock::now();
        auto fps = 500ms;
        if (nlast - last > fps)
        {
            system("clear");
            std::cout << iterations * (1s / fps) << " Hz" << '\n';
            std::cout << ipins << '\n';
            last = nlast;
            iterations = 0;
        }
    }
#endif
    return 0;
}
