/// @file   zone.cpp
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

#include "zone.hpp"
#include "utils.hpp"

Zone::Zone() :
    label(),
    x(),
    y(),
    z()
{
}

Zone::Zone(int _label, int _x, int _y, int _z) :
    label(_label),
    x(_x),
    y(_y),
    z(_z)
{
}

Zone::~Zone()
{
}

std::string Zone::getHeader()
{
    std::string output;
    output += "#";
    output += AlignString("Label", StringAlign::Center, 8);
    output += AlignString("x", StringAlign::Center, 5);
    output += AlignString("y", StringAlign::Center, 5);
    output += AlignString("z", StringAlign::Center, 5);
    return output;
}

std::string Zone::toString() const
{
    std::string output;
    // Values
    output += " ";
    output += AlignString(ToString(label), StringAlign::Center, 8);
    output += AlignString(ToString(x), StringAlign::Center, 5);
    output += AlignString(ToString(y), StringAlign::Center, 5);
    output += AlignString(ToString(z), StringAlign::Center, 5);
    return output;
}