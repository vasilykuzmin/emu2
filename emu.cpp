#include <iostream>
#include <bitset>
#include "translation.hpp"

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
    return 0;
}
