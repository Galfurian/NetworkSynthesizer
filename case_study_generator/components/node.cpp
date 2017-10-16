/// @file   node.cpp
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

#include "node.hpp"
#include "utils.hpp"


Node::Node() :
    id(),
    label(),
    cost(),
    size(),
    powerConsumption(),
    taskPowerConsumption(),
    mobile()
{

}

Node::Node(int _id,
           std::string _label,
           int _cost,
           int _size,
           int _powerConsumption,
           int _taskPowerConsumption,
           bool _mobile) :
    id(_id),
    label(_label),
    cost(_cost),
    size(_size),
    powerConsumption(_powerConsumption),
    taskPowerConsumption(_taskPowerConsumption),
    mobile(_mobile)
{

}

Node::~Node()
{

}

std::string Node::getHeader()
{
    std::string output;
    output += "#";
    output += AlignString("Label", StringAlign::Left, 15);
    output += AlignString("Id", StringAlign::Left, 5);
    output += AlignString("Cost", StringAlign::Right, 5);
    output += AlignString("Size", StringAlign::Right, 5);
    output += AlignString("PC", StringAlign::Right, 5);
    output += AlignString("TPC", StringAlign::Right, 5);
    output += AlignString("Mobile", StringAlign::Right, 7);
    return output;
}

std::string Node::toString() const
{
    std::string output;
    // Values
    output += " ";
    output += AlignString(label, StringAlign::Left, 15);
    output += AlignString(ToString(id), StringAlign::Left, 5);
    output += AlignString(ToString(cost), StringAlign::Right, 5);
    output += AlignString(ToString(size), StringAlign::Right, 5);
    output += AlignString(ToString(powerConsumption), StringAlign::Right, 5);
    output += AlignString(ToString(taskPowerConsumption), StringAlign::Right,
                          5);
    output += AlignString(ToString(mobile), StringAlign::Center, 7);
    return output;
}