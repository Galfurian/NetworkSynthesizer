#include "test_case_01.hpp"
#include "test_case_02.hpp"

int main()
{
//    std::cout << init_test_case_01().toString() << "\n";
//    init_test_case_01().printToFile("init_test_case_01");
    init_test_case_02().printToFile();
    std::cout << init_test_case_02().toString() << "\n";
//    corner_case_1().printToFile("corner_case_1");
    return 0;
}