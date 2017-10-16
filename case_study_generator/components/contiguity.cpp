/// @file   contiguity.cpp
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

#include "contiguity.hpp"
#include "channel.hpp"
#include "utils.hpp"
#include "zone.hpp"

Contiguity::Contiguity() :
    zone1(),
    zone2(),
    channel(),
    conductivity(),
    deploymentCost()
{
}

Contiguity::Contiguity(std::shared_ptr<Zone> _zone1,
                       std::shared_ptr<Zone> _zone2,
                       std::shared_ptr<Channel> _channel,
                       double _conductivity,
                       double _deploymentCost) :
    zone1(_zone1),
    zone2(_zone2),
    channel(_channel),
    conductivity(_conductivity),
    deploymentCost(_deploymentCost)
{
}

Contiguity::~Contiguity()
{
}

std::string Contiguity::getHeader()
{
    std::string output;
    output += "#";
    output += AlignString("Zone1", StringAlign::Right, 8);
    output += AlignString("Zone2", StringAlign::Right, 8);
    output += AlignString("Channel", StringAlign::Right, 8);
    output += AlignString("Conductivity", StringAlign::Right, 15);
    output += AlignString("DeploymentCost", StringAlign::Right, 15);
    return output;
}

std::string Contiguity::toString() const
{
    std::string output;
    output += AlignString(ToString(zone1->label), StringAlign::Right, 8);
    output += AlignString(ToString(zone2->label), StringAlign::Right, 8);
    output += AlignString(ToString(channel->id), StringAlign::Right, 8);
    output += AlignString(ToString(conductivity), StringAlign::Right, 15);
    output += AlignString(ToString(deploymentCost), StringAlign::Right, 15);
    return output;
}
