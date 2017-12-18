/// @file   corner_case_1.cpp
/// @author Enrico Fraccaroli
/// @date   Jan 17 2017
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
#include "corner_case_1.hpp"

ProblemInstance corner_case_1()
{
    ProblemInstance inst("corner_case_1");
    // Add the channels.
    inst.addChannel(1, "Bluetooth-4.0", 9, 24, 1, 1, 0.75, 12, 10, true, true);
    inst.addChannel(2, "Wi-Fi-AC", 34, 7000, 3, 2, 1.10, 8, 7, true, false);
    inst.addChannel(3, "Wi-Fi-AD", 79, 7400, 7, 4, 1.15, 3, 4, true, false);
    inst.addChannel(4, "fiber-Type-1", 256, 232000, 24, 3, 0.75, 2, 4, false, true);
    inst.addChannel(5, "fiber-Type-2", 367, 268000, 8, 2, 1.00, 3, 3, false, true);
    // Add the nodes.
    inst.addNode(1, "db_board_1", 5, 32, 5, 1, 0.15, false);
    inst.addNode(2, "db_board_2", 22, 64, 8, 2, 0.30, true);
    inst.addNode(3, "db_board_3", 98, 128, 12, 5, 0.41, true);
    inst.addNode(4, "db_board_4", 128, 256, 15, 6, 0.33, false);
    inst.addNode(4, "db_board_4", 514, 512, 25, 8, 0.25, false);
    // Add the zones.
    inst.addZone(0, 0, 0, 0);
    inst.addZone(1, 0, 1, 0);
    inst.addZone(2, 1, 0, 0);
    inst.addZone(3, 1, 1, 0);
    // Add the continuities.
    inst.addContiguity(0, 1, 1, 1.0, 0.0);
    inst.addContiguity(0, 1, 2, 1.0, 0.0);
    inst.addContiguity(2, 3, 1, 1.0, 0.0);
    inst.addContiguity(2, 3, 2, 1.0, 0.0);
    // Add the tasks.
    inst.addTask("Task0", TRandInteger<int>(10, 30), 0, false);
    inst.addTask("Task1", TRandInteger<int>(10, 30), 1, false);
    inst.addTask("Task2", TRandInteger<int>(10, 30), 2, false);
    inst.addTask("Task3", TRandInteger<int>(10, 30), 3, false);
    // Add the data-flows.
    inst.addDataFlow("DataFlow1", "Task0", "Task1",
                     TRandInteger<int>(32, 64),
                     TRandInteger<int>(inst.channelMaxDelay,
                                       inst.channelMaxDelay * 2),
                     TRandInteger<int>(inst.channelMaxErrorRate,
                                       inst.channelMaxErrorRate * 2));
    inst.addDataFlow("DataFlow2", "Task2", "Task3",
                     TRandInteger<int>(32, 64),
                     TRandInteger<int>(inst.channelMaxDelay,
                                       inst.channelMaxDelay * 2),
                     TRandInteger<int>(inst.channelMaxErrorRate,
                                       inst.channelMaxErrorRate * 2));
    return inst;
}