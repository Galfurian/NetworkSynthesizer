/// @file   node.hpp
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

#pragma once

#include <string>

class Node
{
public:
    /// a unique id from 1 to N associated to each node tipology
    int id;
    /// is just a name assigned to a node tipology
    std::string label;
    /// is the cost of buying a device of type node_label
    int cost;
    /// the processing capacity of the device
    int size;
    /// is the intrinsic power consumption of the node.
    int powerConsumption;
    /// is the power consumed by a task placed inside the node.
    int taskPowerConsumption;
    /// is the cost of energy for this device.
    double energyCost;
    /// boolean attribute. Is the device mobile?
    bool mobile;

    Node();

    Node(int _id,
        std::string _label,
        int _cost,
        int _size,
        int _powerConsumption,
        int _taskPowerConsumption,
        double _energyCost,
        bool _mobile);

    ~Node();

    static std::string getHeader();

    std::string toString(bool for_milp = false) const;
};
