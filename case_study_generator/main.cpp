#include <test_case_03.hpp>

int main()
{
    ProblemInstance instance = init_test_case_03();
    std::cout << instance.toString() << "\n";
    instance.printToFile();
    return 0;
}