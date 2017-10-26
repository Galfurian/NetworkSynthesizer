/// @file   problemInstance.hpp
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

#include <map>
#include <vector>
#include <memory>

#include "utils.hpp"
#include "zone.hpp"
#include "node.hpp"
#include "task.hpp"
#include "channel.hpp"
#include "contiguity.hpp"
#include "dataFlow.hpp"

class ProblemInstance
{
public:
    std::map<int, std::shared_ptr<Zone>> zones;
    std::map<int, std::shared_ptr<Channel>> channels;
    std::map<int, std::shared_ptr<Node>> nodes;
    std::vector<std::shared_ptr<Contiguity>> contiguities;
    std::vector<std::shared_ptr<Task>> tasks;
    std::vector<std::shared_ptr<DataFlow>> dataFlows;

    int channelMaxSize;
    int channelMinSize;
    int channelMaxDelay;
    int channelMinDelay;
    int channelMaxErrorRate;
    int channelMinErrorRate;

    int nodeMaxSize;
    int nodeMinSize;

    ProblemInstance();

    std::shared_ptr<Zone> addZone(int _label, int _x, int _y, int _z);

    std::shared_ptr<Channel> addChannel(int _id,
                                        std::string _label,
                                        int _cost,
                                        int _size,
                                        int _energyConsumption,
                                        int _energyPerDataFlow,
                                        int _transmissionDelay,
                                        int _errorRate,
                                        bool _wireless,
                                        int _maxConnection);

    std::shared_ptr<Node> addNode(int _id,
                                  std::string _label,
                                  int _cost,
                                  int _size,
                                  int _powerConsumption,
                                  int _taskPowerConsumption,
                                  bool _mobile);

    std::shared_ptr<Contiguity> addContiguity(int _zone1,
                                              int _zone2,
                                              int _channel,
                                              double _conductivity,
                                              double _deploymentCost);

    std::shared_ptr<Task>
    addTask(std::string _label, int _size, int _zone, bool _mobile);

    std::shared_ptr<DataFlow> addDataFlow(std::string _label,
                                          std::string _source,
                                          std::string _target,
                                          int _bandwidth,
                                          int _maximumDelay,
                                          int _maximumError);

    std::shared_ptr<Zone> getZone(int _label);

    std::shared_ptr<Channel> getChannel(int _id);

    std::shared_ptr<Node> getNode(int _id);

    std::shared_ptr<Contiguity> getContiguity(int _zone1,
                                              int _zone2,
                                              int _channel);

    std::shared_ptr<Task> getTask(std::string label);

    std::string toString();

    void printToFile() const;

    std::string printNodesCatalog() const;

    std::string printChannelsCatalog() const;

    std::string printInputInstance(bool withDelimiters = false) const;
};