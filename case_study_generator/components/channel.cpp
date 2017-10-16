/// @file   channel.cpp
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

#include "channel.hpp"
#include "utils.hpp"

Channel::Channel() :
    id(),
    label(),
    cost(),
    size(),
    energyConsumption(),
    energyPerDataFlow(),
    transmissionDelay(),
    errorRate(),
    wireless()
{
}

Channel::Channel(int _id,
        std::string _label,
        int _cost,
        int _size,
        int _energyConsumption,
        int _energyPerDataFlow,
        int _transmissionDelay,
        int _errorRate,
        bool _wireless) :
    id(_id),
    label(_label),
    cost(_cost),
    size(_size),
    energyConsumption(_energyConsumption),
    energyPerDataFlow(_energyPerDataFlow),
    transmissionDelay(_transmissionDelay),
    errorRate(_errorRate),
    wireless(_wireless)
{
}

Channel::~Channel()
{
}

std::string Channel::getHeader()
{
    std::string output;
    output += "#";
    output += AlignString("Label", StringAlign::Left, 15);
    output += AlignString("Id", StringAlign::Left, 5);
    output += AlignString("Cost", StringAlign::Right, 5);
    output += AlignString("Size", StringAlign::Right, 10);
    output += AlignString("EnCons", StringAlign::Right, 10);
    output += AlignString("EcPerDF", StringAlign::Right, 10);
    output += AlignString("TD", StringAlign::Right, 5);
    output += AlignString("ER", StringAlign::Right, 5);
    output += AlignString("W", StringAlign::Right, 5);
    return output;
}

std::string Channel::toString() const
{
    std::string output;
    output += " ";
    output += AlignString(label, StringAlign::Left, 15);
    output += AlignString(ToString(id), StringAlign::Left, 5);
    output += AlignString(ToString(cost), StringAlign::Right, 5);
    output += AlignString(ToString(size), StringAlign::Right, 10);
    output += AlignString(ToString(energyConsumption), StringAlign::Right, 10);
    output += AlignString(ToString(energyPerDataFlow), StringAlign::Right, 10);
    output += AlignString(ToString(transmissionDelay), StringAlign::Right, 5);
    output += AlignString(ToString(errorRate), StringAlign::Right, 5);
    output += AlignString(ToString(wireless), StringAlign::Right, 5);
    return output;
}
