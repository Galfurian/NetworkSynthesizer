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

#include <iomanip>
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
    wireless(),
    point_to_point()
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
                 bool _wireless,
                 bool _point_to_point) :
    id(_id),
    label(_label),
    cost(_cost),
    size(_size),
    energyConsumption(_energyConsumption),
    energyPerDataFlow(_energyPerDataFlow),
    transmissionDelay(_transmissionDelay),
    errorRate(_errorRate),
    wireless(_wireless),
    point_to_point(_point_to_point)
{
}

Channel::~Channel()
{
}

std::string Channel::getHeader()
{
    std::stringstream ss;
    ss << "# " << std::left << std::setw(15) << "LABEL";
    ss << "| " << std::left << std::setw(4) << "ID";
    ss << "| " << std::right << std::setw(6) << "COST";
    ss << " |" << std::right << std::setw(12) << "SIZE";
    ss << " |" << std::right << std::setw(8) << "ENERGY";
    ss << " |" << std::right << std::setw(16) << "DATAFLOW ENERGY";
    ss << " |" << std::right << std::setw(12) << "DELAY";
    ss << " |" << std::right << std::setw(12) << "ERROR";
    ss << " |" << std::right << std::setw(12) << "WIRELESS";
    ss << " |" << std::right << std::setw(18) << "POIN TO POINT";
    return ss.str();
}

std::string Channel::toString(bool for_milp) const
{
    std::stringstream ss;
    ss << "  " << std::left << std::setw(15) << label;
    ss << ((for_milp) ? "  " : "| ")
       << std::left << std::setw(4) << ToString(id);
    ss << ((for_milp) ? "  " : "| ")
       << std::right << std::setw(6) << ToString(cost);
    ss << ((for_milp) ? "  " : " |")
       << std::right << std::setw(12) << ToString(size);
    ss << ((for_milp) ? "  " : " |")
       << std::right << std::setw(8) << ToString(energyConsumption);
    ss << ((for_milp) ? "  " : " |")
       << std::right << std::setw(16) << ToString(energyPerDataFlow);
    ss << ((for_milp) ? "  " : " |")
       << std::right << std::setw(12) << ToString(transmissionDelay);
    ss << ((for_milp) ? "  " : " |")
       << std::right << std::setw(12) << ToString(errorRate);
    ss << ((for_milp) ? "  " : " |")
       << std::right << std::setw(12) << ToString(wireless);
    ss << ((for_milp) ? "  " : " |")
       << std::right << std::setw(18) << ToString(point_to_point);
    return ss.str();
}
