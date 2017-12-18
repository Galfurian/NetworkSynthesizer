/// @file   test_case_01.cpp
/// @author Enrico Fraccaroli
/// @date   Jan 09 2017
/// @copyright
/// Copyright (c) 2017 Enrico Fraccaroli <enrico.fraccaroli@gmail.com>
/// Permission is hereby granted, free of charge, to any person obtaining a
/// copy of this software and associated documentation files (the "Software"),
/// to deal in the Software without restriction, including without limitation
/// the rights to use, copy, modify, merge, publish, distribute, sublicense,
/// and/or sell copies of the Software, and to permit persons to whom the
/// Software is furnished to do so, subject to the following conditions:
///     The above copyright notice and this permission notice shall be included
///     in all copies or substantial portions of the Software.
/// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
/// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
/// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
/// THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
/// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
/// FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
/// DEALINGS IN THE SOFTWARE.

#include <climits>
#include "test_case_01.hpp"

ProblemInstance init_test_case_01()
{
    ProblemInstance inst("test_case_01");
    inst.addZone(1, 0, 5, 0);
    inst.addZone(2, 1, 5, 0);
    inst.addZone(3, 2, 5, 0);
    inst.addZone(4, 3, 5, 0);
    inst.addZone(5, 6, 5, 0);
    inst.addZone(6, 7, 5, 0);
    inst.addZone(7, 8, 5, 0);
    inst.addZone(8, 9, 5, 0);
    inst.addZone(9, 0, 1, 0);
    inst.addZone(10, 1, 1, 0);
    inst.addZone(11, 2, 1, 0);
    inst.addZone(16, 7, 1, 0);
    inst.addZone(17, 8, 1, 0);
    inst.addZone(18, 9, 1, 0);
    inst.addZone(20, 2, 4, 0);
    inst.addZone(21, 7, 4, 0);
    inst.addZone(22, 2, 2, 0);
    inst.addZone(23, 7, 2, 0);
    inst.addZone(30, 4, 5, 0);
    inst.addZone(31, 5, 5, 0);
    inst.addChannel(1, "Bluetooth-4.0", 9, 24, 1, 1, 0.75, 12, 10, true, true);
    inst.addChannel(2, "Wi-Fi-AC", 34, 7000, 3, 2, 1.10, 8, 7, true, false);
    inst.addChannel(3, "Wi-Fi-AD", 79, 7400, 7, 4, 1.15, 3, 4, true, false);
    inst.addChannel(4, "fiber-Type-1", 256, 232000, 24, 3, 0.75, 2, 4, false, true);
    inst.addChannel(5, "fiber-Type-2", 367, 268000, 8, 2, 1.00, 3, 3, false, true);
    inst.addNode(1, "db_board_1", 5, 32, 5, 1, 0.15, false);
    inst.addNode(2, "db_board_2", 22, 64, 8, 2, 0.30, true);
    inst.addNode(3, "db_board_3", 98, 128, 12, 5, 0.41, true);
    inst.addNode(4, "db_board_4", 128, 256, 15, 6, 0.33, false);
    inst.addNode(4, "db_board_4", 514, 512, 25, 8, 0.25, false);
    inst.addContiguity(1, 20, 1, 0.45, 0.0);
    inst.addContiguity(1, 20, 2, 0.58, 0.0);
    inst.addContiguity(1, 20, 3, 0.97, 0.0);
    inst.addContiguity(2, 20, 1, 0.76, 0.0);
    inst.addContiguity(2, 20, 2, 0.34, 0.0);
    inst.addContiguity(2, 20, 3, 0.93, 0.0);
    inst.addContiguity(3, 20, 1, 0.56, 0.0);
    inst.addContiguity(3, 20, 2, 0.97, 0.0);
    inst.addContiguity(3, 20, 3, 0.67, 0.0);
    inst.addContiguity(4, 20, 1, 0.66, 0.0);
    inst.addContiguity(4, 20, 2, 0.45, 0.0);
    inst.addContiguity(4, 20, 3, 0.89, 0.0);
    inst.addContiguity(5, 21, 1, 0.87, 0.0);
    inst.addContiguity(5, 21, 2, 0.74, 0.0);
    inst.addContiguity(5, 21, 3, 0.31, 0.0);
    inst.addContiguity(6, 21, 1, 0.83, 0.0);
    inst.addContiguity(6, 21, 2, 0.59, 0.0);
    inst.addContiguity(6, 21, 3, 0.23, 0.0);
    inst.addContiguity(7, 21, 1, 0.70, 0.0);
    inst.addContiguity(7, 21, 2, 0.67, 0.0);
    inst.addContiguity(7, 21, 3, 0.50, 0.0);
    inst.addContiguity(8, 21, 1, 0.58, 0.0);
    inst.addContiguity(8, 21, 2, 0.56, 0.0);
    inst.addContiguity(8, 21, 3, 0.49, 0.0);
    inst.addContiguity(9, 22, 1, 0.23, 0.0);
    inst.addContiguity(9, 22, 2, 0.87, 0.0);
    inst.addContiguity(9, 22, 3, 0.56, 0.0);
    inst.addContiguity(10, 22, 1, 0.56, 0.0);
    inst.addContiguity(10, 22, 2, 0.45, 0.0);
    inst.addContiguity(10, 22, 3, 0.36, 0.0);
    inst.addContiguity(11, 22, 1, 0.45, 0.0);
    inst.addContiguity(11, 22, 2, 0.57, 0.0);
    inst.addContiguity(11, 22, 3, 0.73, 0.0);
    inst.addContiguity(16, 23, 1, 0.85, 0.0);
    inst.addContiguity(16, 23, 2, 0.46, 0.0);
    inst.addContiguity(16, 23, 3, 0.53, 0.0);
    inst.addContiguity(17, 23, 1, 0.85, 0.0);
    inst.addContiguity(17, 23, 2, 0.57, 0.0);
    inst.addContiguity(17, 23, 3, 0.33, 0.0);
    inst.addContiguity(18, 23, 1, 0.85, 0.0);
    inst.addContiguity(18, 23, 2, 0.57, 0.0);
    inst.addContiguity(18, 23, 3, 0.33, 0.0);
    inst.addContiguity(20, 30, 1, 0.64, 0.0);
    inst.addContiguity(20, 30, 2, 0.12, 0.0);
    inst.addContiguity(20, 30, 3, 0.84, 0.0);
    inst.addContiguity(20, 30, 4, 0.69, 645);
    inst.addContiguity(20, 30, 5, 0.95, 1252);
    inst.addContiguity(21, 31, 1, 0.85, 0.0);
    inst.addContiguity(21, 31, 2, 0.47, 0.0);
    inst.addContiguity(21, 31, 3, 0.79, 0.0);
    inst.addContiguity(21, 31, 4, 0.37, 687);
    inst.addContiguity(21, 31, 5, 0.77, 1235);
    inst.addContiguity(22, 30, 1, 0.29, 0.0);
    inst.addContiguity(22, 30, 2, 0.57, 0.0);
    inst.addContiguity(22, 30, 3, 0.76, 0.0);
    inst.addContiguity(22, 30, 4, 0.40, 675);
    inst.addContiguity(22, 30, 5, 0.94, 1024);
    inst.addContiguity(23, 31, 1, 0.97, 0.0);
    inst.addContiguity(23, 31, 2, 0.54, 0.0);
    inst.addContiguity(23, 31, 3, 0.34, 0.0);
    inst.addContiguity(23, 31, 4, 0.23, 789);
    inst.addContiguity(23, 31, 5, 0.78, 1083);
    inst.addContiguity(30, 31, 1, 0.07, 0.0);
    inst.addContiguity(30, 31, 2, 0.12, 0.0);
    inst.addContiguity(30, 31, 3, 0.21, 0.0);
    inst.addContiguity(30, 31, 4, 0.78, 824);
    inst.addContiguity(30, 31, 5, 1.00, 1486);
    inst.addTask("O1T1", 45, 1, 0);
    inst.addTask("O1T2", 88, 1, 0);
    inst.addTask("O1T3", 39, 1, 0);
    inst.addTask("O2T1", 28, 2, 0);
    inst.addTask("O2T2", 59, 2, 0);
    inst.addTask("O2T3", 25, 2, 0);
    inst.addTask("O3T1", 43, 3, 0);
    inst.addTask("O3T2", 43, 3, 0);
    inst.addTask("O3T3", 31, 3, 0);
    inst.addTask("O4T1", 66, 4, 1);
    inst.addTask("O4T2", 58, 4, 1);
    inst.addTask("O4T3", 44, 4, 0);
    inst.addTask("O5T1", 35, 5, 1);
    inst.addTask("O5T2", 46, 5, 1);
    inst.addTask("O5T3", 33, 5, 0);
    inst.addTask("O6T1", 31, 6, 1);
    inst.addTask("O6T2", 26, 6, 1);
    inst.addTask("O6T3", 59, 6, 0);
    inst.addTask("O7T1", 28, 7, 1);
    inst.addTask("O7T2", 65, 7, 1);
    inst.addTask("O7T3", 22, 7, 0);
    inst.addTask("O8T1", 35, 8, 1);
    inst.addTask("O8T2", 32, 8, 1);
    inst.addTask("O8T3", 16, 8, 0);
    inst.addTask("O9T1", 53, 9, 1);
    inst.addTask("O9T2", 41, 9, 1);
    inst.addTask("O9T3", 28, 9, 0);
    inst.addTask("O10T1", 33, 10, 1);
    inst.addTask("O10T2", 31, 10, 1);
    inst.addTask("O10T3", 38, 10, 0);
    inst.addTask("O11T1", 23, 11, 1);
    inst.addTask("O11T2", 41, 11, 1);
    inst.addTask("O11T3", 38, 11, 0);
    inst.addTask("O16T1", 23, 16, 1);
    inst.addTask("O16T2", 21, 16, 1);
    inst.addTask("O16T3", 18, 16, 0);
    inst.addTask("O17T1", 43, 17, 1);
    inst.addTask("O17T2", 36, 17, 1);
    inst.addTask("O17T3", 48, 17, 0);
    inst.addTask("O18T1", 23, 18, 1);
    inst.addTask("O18T2", 32, 18, 1);
    inst.addTask("O18T3", 28, 18, 0);
    inst.addTask("TRout1", 98, 20, 0);
    inst.addTask("TRout2", 87, 21, 0);
    inst.addTask("TRout3", 121, 22, 0);
    inst.addTask("TRout4", 102, 23, 0);
    inst.addTask("Srv1", 175, 30, 0);
    inst.addTask("Srv2", 197, 31, 0);
    inst.addDataFlow("SR1SR2", "Srv1", "Srv2", TRandInteger<int>(256, 512), 1,
                     1);
    inst.addDataFlow("DO1T1", "O1T1", "TRout1", TRandInteger<int>(32, 256), 10,
                     31);
    inst.addDataFlow("DO1T2", "O1T2", "TRout1", TRandInteger<int>(32, 256), 17,
                     75);
    inst.addDataFlow("DO1T3", "O1T3", "TRout1", TRandInteger<int>(32, 256), 13,
                     52);
    inst.addDataFlow("DO2T1", "O2T1", "TRout1", TRandInteger<int>(32, 256), 23,
                     16);
    inst.addDataFlow("DO2T2", "O2T2", "TRout1", TRandInteger<int>(32, 256), 26,
                     38);
    inst.addDataFlow("DO2T3", "O2T3", "TRout1", TRandInteger<int>(32, 256), 21,
                     23);
    inst.addDataFlow("DO3T1", "O3T1", "TRout1", TRandInteger<int>(32, 256), 18,
                     65);
    inst.addDataFlow("DO3T2", "O3T2", "TRout1", TRandInteger<int>(32, 256), 21,
                     53);
    inst.addDataFlow("DO3T3", "O3T3", "TRout1", TRandInteger<int>(32, 256), 23,
                     27);
    inst.addDataFlow("DO4T1", "O4T1", "TRout1", TRandInteger<int>(32, 256), 18,
                     52);
    inst.addDataFlow("DO4T2", "O4T2", "TRout1", TRandInteger<int>(32, 256), 18,
                     67);
    inst.addDataFlow("DO4T3", "O4T3", "TRout1", TRandInteger<int>(32, 256), 18,
                     35);
    inst.addDataFlow("DO5T1", "O5T1", "TRout2", TRandInteger<int>(32, 256), 18,
                     32);
    inst.addDataFlow("DO5T2", "O5T2", "TRout2", TRandInteger<int>(32, 256), 11,
                     63);
    inst.addDataFlow("DO5T3", "O5T3", "TRout2", TRandInteger<int>(32, 256), 12,
                     28);
    inst.addDataFlow("DO6T1", "O6T1", "TRout2", TRandInteger<int>(32, 256), 15,
                     56);
    inst.addDataFlow("DO6T2", "O6T2", "TRout2", TRandInteger<int>(32, 256), 17,
                     15);
    inst.addDataFlow("DO6T3", "O6T3", "TRout2", TRandInteger<int>(32, 256), 18,
                     26);
    inst.addDataFlow("DO7T1", "O7T1", "TRout2", TRandInteger<int>(32, 256), 12,
                     53);
    inst.addDataFlow("DO7T2", "O7T2", "TRout2", TRandInteger<int>(32, 256), 18,
                     41);
    inst.addDataFlow("DO7T3", "O7T3", "TRout2", TRandInteger<int>(32, 256), 16,
                     28);
    inst.addDataFlow("DO8T1", "O8T1", "TRout2", TRandInteger<int>(32, 256), 19,
                     34);
    inst.addDataFlow("DO8T2", "O8T2", "TRout2", TRandInteger<int>(32, 256), 12,
                     36);
    inst.addDataFlow("DO8T3", "O8T3", "TRout2", TRandInteger<int>(32, 256), 14,
                     24);
    inst.addDataFlow("DO9T1", "O9T1", "TRout3", TRandInteger<int>(32, 256), 29,
                     21);
    inst.addDataFlow("DO9T2", "O9T2", "TRout3", TRandInteger<int>(32, 256), 21,
                     24);
    inst.addDataFlow("DO9T3", "O9T3", "TRout3", TRandInteger<int>(32, 256), 24,
                     18);
    inst.addDataFlow("DO10T1", "O10T1", "TRout3", TRandInteger<int>(32, 256),
                     29, 21);
    inst.addDataFlow("DO10T2", "O10T2", "TRout3", TRandInteger<int>(32, 256),
                     31, 24);
    inst.addDataFlow("DO10T3", "O10T3", "TRout3", TRandInteger<int>(32, 256),
                     45, 18);
    inst.addDataFlow("DO11T1", "O11T1", "TRout3", TRandInteger<int>(32, 256),
                     29, 21);
    inst.addDataFlow("DO11T2", "O11T2", "TRout3", TRandInteger<int>(32, 256),
                     21, 24);
    inst.addDataFlow("DO11T3", "O11T3", "TRout3", TRandInteger<int>(32, 256),
                     35, 18);
    inst.addDataFlow("DO16T1", "O16T1", "TRout4", TRandInteger<int>(32, 256),
                     29, 61);
    inst.addDataFlow("DO16T2", "O16T2", "TRout4", TRandInteger<int>(32, 256),
                     33, 34);
    inst.addDataFlow("DO16T3", "O16T3", "TRout4", TRandInteger<int>(32, 256),
                     25, 48);
    inst.addDataFlow("DO17T1", "O17T1", "TRout4", TRandInteger<int>(32, 256),
                     29, 21);
    inst.addDataFlow("DO17T2", "O17T2", "TRout4", TRandInteger<int>(32, 256),
                     22, 54);
    inst.addDataFlow("DO17T3", "O17T3", "TRout4", TRandInteger<int>(32, 256),
                     55, 78);
    inst.addDataFlow("DO18T1", "O18T1", "TRout4", TRandInteger<int>(32, 256),
                     49, 41);
    inst.addDataFlow("DO18T2", "O18T2", "TRout4", TRandInteger<int>(32, 256),
                     26, 74);
    inst.addDataFlow("DO18T3", "O18T3", "TRout4", TRandInteger<int>(32, 256),
                     15, 28);
    inst.addDataFlow("DTRout1", "TRout1", "Srv1", TRandInteger<int>(512, 768),
                     7, 12);
    inst.addDataFlow("DTRout2", "TRout2", "Srv2", TRandInteger<int>(512, 768),
                     20, 21);
    inst.addDataFlow("DTRout3", "TRout3", "Srv1", TRandInteger<int>(512, 768),
                     7, 12);
    inst.addDataFlow("DTRout4", "TRout4", "Srv2", TRandInteger<int>(512, 768),
                     20, 21);
    return inst;
}