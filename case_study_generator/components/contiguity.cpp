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

#include <iomanip>
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
    // Nothing to do.
}

Contiguity::Contiguity(std::shared_ptr<Zone> _zone1,
                       std::shared_ptr<Zone> _zone2,
                       std::shared_ptr<Channel> _channel,
                       double _conductivity,
                       double _deploymentCost) :
    zone1(std::move(_zone1)),
    zone2(std::move(_zone2)),
    channel(std::move(_channel)),
    conductivity(_conductivity),
    deploymentCost(_deploymentCost)
{
    // Nothing to do.
}

Contiguity::~Contiguity()
{
    // Nothing to do.
}

std::string Contiguity::getHeader()
{
    std::stringstream ss;
    ss << "# " << std::right << std::setw(8) << "ZONE1";
    ss << " |" << std::right << std::setw(8) << "ZONE2";
    ss << " |" << std::right << std::setw(8) << "CHANNEL";
    ss << " |" << std::right << std::setw(16) << "CONDUCTIVITY";
    ss << " |" << std::right << std::setw(16) << "DEPLOYMENT COST";
    return ss.str();
}

std::string Contiguity::toString(bool for_milp) const
{
    std::stringstream ss;
    ss << "  " << std::right << std::setw(8) << zone1->label;
    ss << ((for_milp) ? "  " : " |")
       <<  std::right << std::setw(8) << ToString(zone2->label);
    ss << ((for_milp) ? "  " : " |")
       <<  std::right << std::setw(8) << ToString(channel->id);
    ss << ((for_milp) ? "  " : " |")
       <<  std::right << std::setw(16) << ToString(conductivity);
    ss << ((for_milp) ? "  " : " |")
       <<  std::right << std::setw(16) << ToString(deploymentCost);
    return ss.str();
}
