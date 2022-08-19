#include <iostream>
#include <bitset>
#include <fstream>
#include <ctime>
#include <chrono>
#include "tmp/translation.hpp"

using namespace std::literals;

int main()
{
#ifdef ramFilename
    std::ifstream ramFile;
    ramFile.open(ramFilename, std::ios::in);
    std::string s;
    ramFile >> s;
    ramFile.close();
    for (int i = 0; i < s.size(); ++i)
    {
        RAM[i] = (s[i] == '0' ? 0 : 1);
    }
#endif
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
    int logs = 0;

    std::ofstream logFile;
    logFile.open("tmp/logs.log", std::ios::out);

    while (true)
    {
        if (logs < 100)
        {
            logs++;
            for (int i = 0; i < OSIZE; ++i)
            {
                logFile << ipins[i];
            }
            logFile << '\n';
            logFile.flush();
        }
        else
        {
            logFile.close();
        }

        ipins = solve(ipins);
        
        iterations++;
        auto nlast = std::chrono::steady_clock::now();
        auto fps = 500ms;
        if (nlast - last > fps)
        {
            render();
            system("clear");
            std::cout << iterations * (1s / fps) << " Hz" << '\n';
            #ifdef OSHAPE
            int oo = 0;
            for (int i : OSHAPE)
            {
                for (int j = 0; j < i; ++j)
                {
                    std::cout << ipins[oo++];
                }
                std::cout << ' ';
            }
            std::cout << '\n';
            #endif
            last = nlast;
            iterations = 0;
        }
    }
#endif
    return 0;
}
