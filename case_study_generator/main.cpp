#include <test_case_03.hpp>
#include <test_case_01.hpp>
#include <test_case_02.hpp>
#include <stress_test_generator.hpp>
#include <stress_test_generator_2.hpp>

int main() {
  //ProblemInstance tc1 = init_test_case_01();
  //tc1.printToFile();
  //ProblemInstance tc2 = init_test_case_02();
  //tc2.printToFile();
  //ProblemInstance tc3 = init_test_case_03();
  //tc3.printToFile();
  generate_stress_test_2();
  return 0;
}