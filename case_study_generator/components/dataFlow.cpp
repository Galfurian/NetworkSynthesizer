/// @file   dataFlow.cpp
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
#include "dataFlow.hpp"
#include "utils.hpp"
#include "task.hpp"

DataFlow::DataFlow() :
    label(),
    source(),
    target(),
    bandwidth(),
    maximumDelay(),
    maximumError()
{

}

DataFlow::DataFlow(std::string _label,
                   std::shared_ptr<Task> _source,
                   std::shared_ptr<Task> _target,
                   int _bandwidth,
                   int _maximumDelay,
                   int _maximumError) :
    label(_label),
    source(_source),
    target(_target),
    bandwidth(_bandwidth),
    maximumDelay(_maximumDelay),
    maximumError(_maximumError)
{

}

DataFlow::~DataFlow()
{

}

std::string DataFlow::getHeader()
{
    std::stringstream ss;
    ss << "# " << std::left << std::setw(24) << "LABEL";
    ss << " | " << std::left << std::setw(16) << "SOURCE";
    ss << " | " << std::left << std::setw(16) << "TARGET";
    ss << " | " << std::right << std::setw(16) << "BANDWIDTH";
    ss << " | " << std::right << std::setw(16) << "MAX DELAY";
    ss << " | " << std::right << std::setw(16) << "MAX ERROR";
    return ss.str();
}

std::string DataFlow::toString(bool for_milp) const
{
    std::stringstream ss;
    ss << "  " << std::left << std::setw(24) << label;
    ss << ((for_milp) ? "   " : " | ")
       << std::left << std::setw(16) << source->label;
    ss << ((for_milp) ? "   " : " | ")
       << std::left << std::setw(16) << target->label;
    ss << ((for_milp) ? "   " : " | ")
       << std::right << std::setw(16) << ToString(bandwidth);
    ss << ((for_milp) ? "   " : " | ")
       << std::right << std::setw(16) << ToString(maximumDelay);
    ss << ((for_milp) ? "   " : " | ")
       << std::right << std::setw(16) << ToString(maximumError);
    return ss.str();
}
