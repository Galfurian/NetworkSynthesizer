/// @file   test_case_02.cpp
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

#include "test_case_02.hpp"

double Normalize(double value, double LbFrom, double UbFrom,
                 double LbTo, double UbTo)
{
    return (((UbTo - LbTo) * (value - LbFrom)) / ((UbFrom - LbFrom))) + LbTo;
}

double GetDistance(std::shared_ptr<Zone> z1, std::shared_ptr<Zone> z2)
{
    return std::sqrt(pow(z1->x - z2->x, 2) +
                     pow(z1->y - z2->y, 2) +
                     pow(z1->z - z2->z, 2));
}

ProblemInstance init_test_case_02()
{
    ProblemInstance inst;

    // ------------------------------------------------------------------------
    auto numArea = 16;
    auto minNodesPerZone = 2;
    auto maxNodesPerZone = 6;

    // ------------------------------------------------------------------------
    // Add the channels.
    inst.addChannel(1, "Bluetooth-4.0", 9, 24, 1, 1, 12, 10, 1);
    inst.addChannel(2, "Wi-Fi-AC", 34, 7000, 3, 2, 8, 7, 1);
    inst.addChannel(3, "Wi-Fi-AD", 79, 7400, 7, 4, 3, 4, 1);
    inst.addChannel(4, "fiber-Type-1", 256,  232000, 24, 3, 2, 4, 0);
    inst.addChannel(5, "fiber-Type-2", 367, 268000, 8, 2, 3, 3, 0);

    int local_min_index = 1;
    int local_max_index = 3;
    int extra_area_min_index = 4;
    int extra_area_max_index = 5;

    // ------------------------------------------------------------------------
    // Add the nodes.
    inst.addNode(1, "pic", 5, 21, 5, 1, 0);
    inst.addNode(2, "board", 22, 29, 8, 2, 1);
    inst.addNode(3, "net_board", 98, 70, 12, 5, 1);
    inst.addNode(4, "laptop", 128, 256, 15, 6, 0);

    int personal_min_index = 1;
    int personal_max_index = 3;
    int router_min_index = 3;
    int router_max_index = 4;

    // ------------------------------------------------------------------------
    double minDistance = +INT64_MAX;
    double maxDistance = 0.0;
    double normMinDistance = +INT64_MAX;
    double normMaxDistance = 0.0;

    // ------------------------------------------------------------------------
    // Add the zones.
    {
        int x = 0;
        int y = 0;
        int cont = 0;
        while (cont < numArea)
        {
            inst.addZone(cont, x, y, 0);
            if (x == 2)
            {
                x = 0;
                ++y;
            }
            else
            {
                ++x;
            }
            ++cont;
        }
    }

    // ------------------------------------------------------------------------
    for (auto z1 = inst.zones.begin(); z1 != inst.zones.end(); ++z1)
    {
        for (auto z2 = z1; z2 != inst.zones.end(); ++z2)
        {
            if (z1 == z2)
            {
                continue;
            }
            auto distance = GetDistance(z1->second, z2->second);
            if (distance > maxDistance)
            {
                maxDistance = distance;
            }
            if (distance < minDistance)
            {
                minDistance = distance;
            }
        }
    }

    // ------------------------------------------------------------------------
    for (auto z1 = inst.zones.begin(); z1 != inst.zones.end(); ++z1)
    {
        for (auto z2 = z1; z2 != inst.zones.end(); ++z2)
        {
            if (z1 == z2) continue;
            auto normDistance = Normalize(GetDistance(z1->second, z2->second),
                                          minDistance, maxDistance, 0.0, 1.0);
            if (normDistance > normMaxDistance)
            {
                normMaxDistance = normDistance;
            }
            if (normDistance < normMinDistance)
            {
                normMinDistance = normDistance;
            }
        }
    }

    // ------------------------------------------------------------------------
    // Add the continuities.
    for (auto z1 = inst.zones.begin(); z1 != inst.zones.end(); ++z1)
    {
        for (auto z2 = z1; z2 != inst.zones.end(); ++z2)
        {
            for (auto channelIt : inst.channels)
            {
                auto channel = channelIt.second;
                if (z1->first == z2->first)
                {
                    if (!channel->wireless)
                    {
                        inst.addContiguity(z1->first,
                                           z2->first,
                                           channel->id,
                                           0.0,
                                           1e12);
                    }
                    continue;
                }
                else
                {
                    if (channel->wireless)
                    {
                        inst.addContiguity(z1->first,
                                           z2->first,
                                           channel->id,
                                           0.0,
                                           0.0);
                        continue;
                    }
                }

                double conductance, deploymentCost;
                auto distance = GetDistance(z1->second, z2->second);
                auto normDist = Normalize(distance,
                                          minDistance,
                                          maxDistance,
                                          0.0,
                                          1.0);
                auto chImpact = Normalize(channel->size,
                                          inst.channelMinSize,
                                          inst.channelMaxSize,
                                          0.0,
                                          normMaxDistance);
                if (channel->wireless)
                {
                    conductance = normDist + chImpact;
                    deploymentCost = 0.0;
                }
                else
                {
                    conductance = 1.0;
                    deploymentCost = distance;
                }
                if (conductance > 1.0)
                {
                    conductance = 1.0;
                }
                inst.addContiguity(z1->first,
                                   z2->first,
                                   channel->id,
                                   conductance,
                                   deploymentCost);
            }
        }
    }

    // ------------------------------------------------------------------------
    std::vector<std::shared_ptr<Task>> routers;
    for (auto z = inst.zones.begin(); z != inst.zones.end(); ++z)
    {
        for (auto it = 0; it < TRandInteger<int>(minNodesPerZone,
                                                 maxNodesPerZone); ++it)
        {
            auto routerName = "RtZn" + ToString(z->first);
            if (it == 0)
            {
                int node_index = TRandInteger<int>(router_min_index,
                                                   router_max_index);
                int node_size = inst.nodes[node_index]->size;

                routers.emplace_back(
                    inst.addTask(routerName,
                                 TRandInteger<int>(
                                     (node_size / 2),
                                     node_size - (node_size / 4)),
                                 z->first,
                                 false));
            }
            else
            {
                auto taskName = "Ts" + ToString(it) +
                                "Zn" + ToString(z->first);
                int node_index = TRandInteger<int>(personal_min_index,
                                                   personal_max_index);
                int node_size = inst.nodes[node_index]->size;

                inst.addTask(taskName,
                             TRandInteger<int>(
                                 (node_size / 2),
                                 node_size - (node_size / 4)),
                             z->first,
                             true);
                auto dataFlowName = "DfZn" + ToString(z->first) +
                                    "Tk" + ToString(it);

                int index = TRandInteger<int>(local_min_index, local_max_index);

                int size = inst.channels[index]->size;
                int delay = inst.channels[index]->transmissionDelay;
                int error = inst.channels[index]->errorRate;

                inst.addDataFlow(
                    dataFlowName,
                    taskName,
                    routerName,
                    TRandInteger<int>(size / 2, size - (size / 8)),
                    TRandInteger<int>(delay, static_cast<int>(delay * 1.25)),
                    TRandInteger<int>(error, static_cast<int>(error * 1.25)));
            }
        }
    }

    // ------------------------------------------------------------------------
    {
        std::shared_ptr<Task> previousRouter = nullptr;
        for (auto router : routers)
        {
            if (previousRouter != nullptr)
            {
                auto dataFlowName = "Df" + previousRouter->label +
                                    "To" + router->label;

                int index = TRandInteger<int>(extra_area_min_index,
                                              extra_area_max_index);

                int size = inst.channels[index]->size;
                int delay = inst.channels[index]->transmissionDelay;
                int error = inst.channels[index]->errorRate;

                inst.addDataFlow(
                    dataFlowName,
                    previousRouter->label,
                    router->label,
                    TRandInteger<int>(size / 32, size / 16),
                    TRandInteger<int>(delay, static_cast<int>(delay * 1.5)),
                    TRandInteger<int>(error, static_cast<int>(error * 1.5)));
            }
            previousRouter = router;
        }
    }
    return inst;
}