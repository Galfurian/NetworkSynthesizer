/// @file   problemInstance.cpp
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

#include "problemInstance.hpp"
#include <cassert>
#include <fstream>

ProblemInstance::ProblemInstance(std::string _name) :
    name(std::move(_name)),
    zones(),
    channels(),
    nodes(),
    contiguities(),
    tasks(),
    dataFlows(),
    channelMaxSize(0),
    channelMinSize(INT32_MAX),
    channelMaxDelay(0),
    channelMinDelay(INT32_MAX),
    channelMaxErrorRate(0),
    channelMinErrorRate(INT32_MAX),
    nodeMaxSize(0),
    nodeMinSize(INT32_MAX) {
}

std::shared_ptr<Zone> ProblemInstance::addZone(int _label,
                                               int _x, int _y, int _z) {
  auto zone = std::make_shared<Zone>(_label, _x, _y, _z);
  zones[_label] = zone;
  return zone;
}

std::shared_ptr<Channel> ProblemInstance::addChannel(int _id,
                                                     std::string _label,
                                                     int _cost,
                                                     int _size,
                                                     int _energyConsumption,
                                                     int _energyPerDataFlow,
                                                     double _energyCost,
                                                     int _transmissionDelay,
                                                     int _errorRate,
                                                     bool _wireless,
                                                     bool _point_to_point) {
  auto channel = std::make_shared<Channel>(_id,
                                           _label,
                                           _cost,
                                           _size,
                                           _energyConsumption,
                                           _energyPerDataFlow,
                                           _energyCost,
                                           _transmissionDelay,
                                           _errorRate,
                                           _wireless,
                                           _point_to_point);
  channels[_id] = channel;

  if (channelMaxSize < _size) {
    channelMaxSize = _size;
  }
  if (channelMinSize > _size) {
    channelMinSize = _size;
  }
  if (channelMaxDelay < _transmissionDelay) {
    channelMaxDelay = _transmissionDelay;
  }
  if (channelMinDelay > _transmissionDelay) {
    channelMinDelay = _transmissionDelay;
  }
  if (channelMaxErrorRate < _errorRate) {
    channelMaxErrorRate = _errorRate;
  }
  if (channelMinErrorRate > _errorRate) {
    channelMinErrorRate = _errorRate;
  }
  return channel;
}

std::shared_ptr<Node> ProblemInstance::addNode(int _id,
                                               std::string _label,
                                               int _cost,
                                               int _size,
                                               int _powerConsumption,
                                               int _taskPowerConsumption,
                                               double _energyCost,
                                               bool _mobile) {
  auto node = std::make_shared<Node>(_id,
                                     _label,
                                     _cost,
                                     _size,
                                     _powerConsumption,
                                     _taskPowerConsumption,
                                     _energyCost,
                                     _mobile);
  nodes[_id] = node;
  if (nodeMinSize > _size) {
    nodeMinSize = _size;
  }
  if (nodeMaxSize < _size) {
    nodeMaxSize = _size;
  }
  return node;
}

std::shared_ptr<Contiguity> ProblemInstance::addContiguity(int _zone1,
                                                           int _zone2,
                                                           int _channel,
                                                           double _conductivity,
                                                           double _deploymentCost) {
  auto zone1 = this->getZone(_zone1);
  auto zone2 = this->getZone(_zone2);
  auto channel = this->getChannel(_channel);
  assert(zone1 != nullptr);
  assert(zone2 != nullptr);
  assert(channel != nullptr);
  auto contiguity = std::make_shared<Contiguity>(zone1,
                                                 zone2,
                                                 channel,
                                                 _conductivity,
                                                 _deploymentCost);
  contiguities.emplace_back(contiguity);
  return contiguity;
}

std::shared_ptr<Task> ProblemInstance::addTask(std::string _label,
                                               int _size,
                                               int _zone,
                                               bool _mobile) {
  auto zone = this->getZone(_zone);
  assert(zone != nullptr);
  auto task = std::make_shared<Task>(_label, _size, zone, _mobile);
  tasks.emplace_back(task);
  return task;
}

std::shared_ptr<DataFlow> ProblemInstance::addDataFlow(std::string _label,
                                                       std::string _source,
                                                       std::string _target,
                                                       int _bandwidth,
                                                       int _maximumDelay,
                                                       int _maximumError) {
  auto source = this->getTask(_source);
  auto target = this->getTask(_target);
  assert(source != nullptr);
  assert(target != nullptr);
  auto dataFlow = std::make_shared<DataFlow>(_label,
                                             source,
                                             target,
                                             _bandwidth,
                                             _maximumDelay,
                                             _maximumError);
  dataFlows.emplace_back(dataFlow);
  return dataFlow;
}

std::shared_ptr<Zone> ProblemInstance::getZone(int _label) {
  return zones[_label];
}

std::shared_ptr<Channel> ProblemInstance::getChannel(int _id) {
  return channels[_id];
}

std::shared_ptr<Node> ProblemInstance::getNode(int _id) {
  return nodes[_id];
}

std::shared_ptr<Contiguity> ProblemInstance::getContiguity(int _zone1,
                                                           int _zone2,
                                                           int _channel) {
  for (auto contiguity :contiguities) {
    if ((contiguity->zone1->label == _zone1) &&
        (contiguity->zone2->label == _zone2) &&
        (contiguity->channel->id == _channel)) {
      return contiguity;
    }
  }
  return nullptr;
}

std::shared_ptr<Task> ProblemInstance::getTask(std::string label) {
  for (auto task : tasks) {
    if (task->label == label) {
      return task;
    }
  }
  return nullptr;
}

std::string ProblemInstance::toString() {
  std::stringstream ss;
  ss << "\n# NODES\n";
  ss << this->printNodesCatalog() + "\n";
  ss << "\n# CHANNELS\n";
  ss << this->printChannelsCatalog() + "\n";
  ss << "\n# INPUT INSTANCE\n";
  ss << this->printInputInstance() + "\n";
  return ss.str();
}

void ProblemInstance::printToFile() const {
  const int dir_err = system(("mkdir -p " + name).c_str());
  if (dir_err < 0) {
    printf("Error creating directory!n");
    exit(1);
  }
  std::ofstream output;
  // ------------------------------------------------------------------------
  output.open(name + "/nodes.txt");
  output << this->printNodesCatalog(true) + "\n";
  output.close();

  // ------------------------------------------------------------------------
  output.open(name + "/channels.txt");
  output << this->printChannelsCatalog(true) + "\n";
  output.close();

  // ------------------------------------------------------------------------
  output.open(name + "/input.txt");
  output << this->printInputInstance(true) + "\n";
  output.close();
}

std::string ProblemInstance::printNodesCatalog(bool for_milp) const {
  std::stringstream ss;
  ss << Node::getHeader() + "\n";
  for (auto node : nodes) {
    ss << node.second->toString(for_milp) + "\n";
  }
  return ss.str();
}

std::string ProblemInstance::printChannelsCatalog(bool for_milp) const {
  std::stringstream ss;
  ss << Channel::getHeader() + "\n";
  for (auto channel : channels) {
    ss << channel.second->toString(for_milp) + "\n";
  }
  return ss.str();
}

std::string ProblemInstance::printInputInstance(bool for_milp) const {
  std::stringstream ss;

  // ------------------------------------------------------------------------
  ss << "# Zones\n";
  ss << Zone::getHeader() + "\n";
  if (for_milp) ss << "<ZONE>\n";
  for (const auto &zone : zones) {
    ss << zone.second->toString(for_milp) + "\n";
  }
  if (for_milp) ss << "</ZONE>\n";
  ss << "\n";

  // ------------------------------------------------------------------------
  ss << "# Continuities\n";
  ss << Contiguity::getHeader() + "\n";
  if (for_milp) ss << "<CONTIGUITY>\n";
  for (const auto &contiguity : contiguities) {
    ss << contiguity->toString(for_milp) + "\n";
  }
  if (for_milp) ss << "</CONTIGUITY>\n";
  ss << "\n";

  // ------------------------------------------------------------------------
  ss << "# Tasks\n";
  ss << Task::getHeader() + "\n";
  if (for_milp) ss << "<TASK>\n";
  for (const auto &task : tasks) {
    ss << task->toString(for_milp) + "\n";
  }
  if (for_milp) ss << "</TASK>\n";
  ss << "\n";

  // ------------------------------------------------------------------------
  ss << "# Data Flows\n";
  ss << DataFlow::getHeader() + "\n";
  if (for_milp) ss << "<DATAFLOW>\n";
  for (const auto &dataFlow : dataFlows) {
    ss << dataFlow->toString(for_milp) + "\n";
  }
  if (for_milp) ss << "</DATAFLOW>\n";
  ss << "\n";

  return ss.str();
}