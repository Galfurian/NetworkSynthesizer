#include <test_case_03.hpp>
#include <test_case_01.hpp>
#include <test_case_02.hpp>
#include <test_case_04.hpp>

int main()
{
    ProblemInstance tc1 = init_test_case_01();
    tc1.printToFile();
    ProblemInstance tc2 = init_test_case_02();
    tc2.printToFile();
    ProblemInstance tc3 = init_test_case_03();
    tc3.printToFile();
    ProblemInstance tc4 = init_test_case_04();
    tc4.printToFile();
    return 0;
}