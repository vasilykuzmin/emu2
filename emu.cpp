#include <iostream>
#include <bitset>
#include "translation.hpp"

int main()
{
    for (int i = 0; i < (1 << ISIZE); ++i)
    {
        std::bitset<ISIZE> ibs = i;
        std::bitset<OSIZE> obs = solve(ibs);
        std::cout << ibs << " | " << obs << '\n';
    }

    return 0;
}
