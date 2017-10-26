/// @file   task.cpp
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
#include "task.hpp"
#include "utils.hpp"
#include "zone.hpp"

Task::Task() :
    label(),
    size(),
    zone(),
    mobile()
{
    // Nothing to do.
}

Task::Task(std::string _label,
           int _size,
           std::shared_ptr<Zone> _zone,
           bool _mobile) :
    label(std::move(_label)),
    size(_size),
    zone(std::move(_zone)),
    mobile(_mobile)
{
    // Nothing to do.
}

Task::~Task()
{
    // Nothing to do.
}

std::string Task::getHeader()
{
    std::stringstream ss;
    ss << "# " << std::left << std::setw(12) << "LABEL";
    ss << " |" << std::right << std::setw(12) << "SIZE";
    ss << " |" << std::right << std::setw(12) << "ZONE";
    ss << " |" << std::right << std::setw(12) << "MOBILE";
    return ss.str();
}

std::string Task::toString(bool for_milp) const
{
    std::stringstream ss;
    ss << "  " << std::left << std::setw(12) << label;
    ss << ((for_milp) ? "  " : " |")
       <<  std::right << std::setw(12) << ToString(size);
    ss << ((for_milp) ? "  " : " |")
       <<  std::right << std::setw(12) << ToString(zone->label);
    ss << ((for_milp) ? "  " : " |")
       <<  std::right << std::setw(12) << ToString(mobile);
    return ss.str();
}