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

#include "task.hpp"
#include "utils.hpp"
#include "zone.hpp"

Task::Task() :
    label(),
    size(),
    zone(),
    mobile()
{

}

Task::Task(std::string _label,
           int _size,
           std::shared_ptr<Zone> _zone,
           bool _mobile) :
    label(_label),
    size(_size),
    zone(_zone),
    mobile(_mobile)
{

}

Task::~Task()
{

}

std::string Task::getHeader()
{
    std::string output;
    output += "#";
    output += AlignString("Label", StringAlign::Center, 15);
    output += AlignString("Size", StringAlign::Right, 5);
    output += AlignString("Zone", StringAlign::Right, 5);
    output += AlignString("Mobile", StringAlign::Right, 5);
    return output;
}

std::string Task::toString() const
{
    std::string output;
    output += AlignString(label, StringAlign::Center, 15);
    output += AlignString(ToString(size), StringAlign::Right, 5);
    output += AlignString(ToString(zone->label), StringAlign::Right, 5);
    output += AlignString(ToString(mobile), StringAlign::Right, 5);
    return output;
}