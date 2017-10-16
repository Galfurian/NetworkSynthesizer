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

#include "corner_case_1.hpp"

ProblemInstance corner_case_1()
{
    ProblemInstance inst;
    // Add the channels.
    inst.addChannel(1, "Bluetooth-4.0", 9, 24, 1, 1, 12, 10, 1);
    inst.addChannel(2, "Wi-Fi-AC", 34, 256, 3, 2, 8, 7, 1);
//    inst.addChannel(3, "Wi-Fi-AD", 79, 7400, 7, 4, 3, 2, 1);
//    inst.addChannel(3, "ethernet", 27, 100000, 20, 2, 5, 2, 0);
//    inst.addChannel(5, "fiber", 367, 273000, 14, 1, 1, 1, 0);
    // Add the nodes.
    inst.addNode(1, "pic", 5, 21, 5, 1, 0);
    inst.addNode(2, "board", 22, 29, 8, 2, 1);
    inst.addNode(3, "net_board", 98, 70, 12, 5, 1);
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