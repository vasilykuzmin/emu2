#include <iostream>
#include <bitset>
#include "translation.hpp"

int main()
{
    for (int i = 0; i < (1 << ISIZE); ++i)
    {
        std::bitset<ISIZE> ibs = i;
        std::bitset<OSIZE> obs = solve(ibs);
        int ii = 0;
        for (int i : ISHAPE)
        {
            for (int j = 0; j < i; ++j)
            {
                std::cout << ibs[ii++];
            }
            std::cout << ' ';
        }
        std::cout << "| ";
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
    }

    return 0;
}
