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

#include <cassert>
#include <iomanip>
#include "test_case_02.hpp"

static double Normalize(double value, double LbFrom, double UbFrom,
                        double LbTo, double UbTo) {
  return (((UbTo - LbTo) * (value - LbFrom)) / ((UbFrom - LbFrom))) + LbTo;
}

static double GetDistance(std::shared_ptr<Zone> z1, std::shared_ptr<Zone> z2) {
  return std::sqrt(pow(z1->x - z2->x, 2) +
      pow(z1->y - z2->y, 2) +
      pow(z1->z - z2->z, 2));
}

static void add_channels(ProblemInstance &inst) {
  inst.addChannel(1, "Bluetooth-4.0",  9,     24,  1, 1, 0.16, 12, 10,  true,  true);
  inst.addChannel(2, "Wi-Fi-AC",      34,   7000,  3, 2, 0.30,  8,  7,  true, false);
  inst.addChannel(3, "Wi-Fi-AD",      79,   7400,  7, 4, 0.28,  3,  4,  true, false);
  inst.addChannel(4, "fiber-Type-1", 320, 200000, 18, 2, 0.21,  2,  1, false,  true);
  inst.addChannel(5, "fiber-Type-2", 367, 273000, 14, 1, 0.12,  1,  3, false,  true);
//# LABEL           | ID |  COST |       SIZE | ENERGY | DF_ENERGY | ENERGY COST |  DELAY |  ERROR | WIRELESS | POINT TO POINT |
//  Bluetooth-4.0      1       9           24        1           1        0.16         12       10          1               1
//  Wi-Fi-AC           2      34         7000        3           2        0.30          8        7          1               0
//  Wi-Fi-AD           3      79         7400        7           4        0.28          3        4          1               0
//  Fiber-Type-1       4     320       200000       18           2        0.21          2        1          0               1
//  Fiber-Type-2       5     367       273000       14           1        0.12          1        3          0               1
}

static void add_nodes(ProblemInstance &inst) {
  inst.addNode(1, "db_board_1",  10,  64,  2,  1, 0.05, false);
  inst.addNode(2, "db_board_2",  24,  98,  4,  2, 0.15, true);
  inst.addNode(3, "db_board_3",  64, 128,  8,  4, 0.40, true);
  inst.addNode(4, "db_board_4", 128, 256, 14,  7, 0.32, true);
  inst.addNode(5, "db_board_5", 514, 512, 20, 10, 0.60, false);
  //# LABEL           | ID |  COST |       SIZE | ENERGY |  TASK ENERGY | ENERGY COST | MOBILE |
  //  db_board_1         1      10           64        2              1          0.05       0
  //  db_board_2         2      24           98        4              2          0.15       1
  //  db_board_3         3      64          128        8              4          0.40       1
  //  db_board_4         4     128          256       14              7          0.32       1
  //  db_board_5         5     378          512       20             10          0.60       0
}


static void add_zones(ProblemInstance &inst, unsigned int num) {
  int x = 0;
  int y = 0;
  int cont = 0;
  while (cont < num) {
    inst.addZone(cont, x, y, 0);
    if (x == 2) {
      x = 0;
      ++y;
    } else {
      ++x;
    }
    ++cont;
  }
}

static void add_contiguities(ProblemInstance &inst) {
	static double conductance_channels[5];
	conductance_channels[0] = 0.75;
	conductance_channels[1] = 0.80;
	conductance_channels[2] = 0.85;
	conductance_channels[3] = 0.90;
	conductance_channels[4] = 0.95;
  for (auto z1 = inst.zones.begin(); z1 != inst.zones.end(); ++z1) {
    for (auto z2 = z1; z2 != inst.zones.end(); ++z2) {
      for (auto channelIt : inst.channels) {
        auto channel = channelIt.second;
        if (z1->first == z2->first) {
          if (channel->wireless) {
            inst.addContiguity(z1->first,
                               z2->first,
                               channel->id,
                               conductance_channels[channelIt.first],
                               0.0);
          } else {
            inst.addContiguity(z1->first,
                               z2->first,
                               channel->id,
                               0.0,
                               1e12);
          }
        } else {
          if (channel->wireless) {
            inst.addContiguity(z1->first,
                               z2->first,
                               channel->id,
                               0.0,
                               1e12);
          } else {
            inst.addContiguity(z1->first,
                               z2->first,
                               channel->id,
                               1.00,
                               0.02);
          }
        }
      }
    }
  }
}

static void add_zone_instance(ProblemInstance &inst,
                              std::vector<std::shared_ptr<Task>> &routers,
                              const std::shared_ptr<Zone> &zone,
                              const unsigned int &tasks_per_zone) {
  assert((tasks_per_zone >= 2) && "Too few tasks.");
  for (auto it = 0; it < tasks_per_zone; ++it) {
    auto routerName = "RtZn" + ToString(zone->label);
    if (it == 0) {
      routers.emplace_back(
          inst.addTask(routerName,
                       256,
                       zone->label,
                       false));
    } else {
      auto taskName = "Ts" + ToString(it) + "Zn" + ToString(zone->label);
      inst.addTask(taskName,
                   64,
                   zone->label,
                   true);
      auto dataFlowName = "DfZn" + ToString(zone->label) + "Tsk" + ToString(it);
      inst.addDataFlow(
          dataFlowName,
          taskName,
          routerName,
          12,
          12,
          12);
    }
  }
}

static void connect_routers(ProblemInstance &inst,
                            std::vector<std::shared_ptr<Task>> &routers) {
  std::shared_ptr<Task> previousRouter = nullptr;
  for (const auto &router : routers) {
    if (previousRouter != nullptr) {
      auto dataFlowName = "Df" + previousRouter->label + "To" + router->label;
      inst.addDataFlow(
          dataFlowName,
          previousRouter->label,
          router->label,
          128,
          4,
          4);
    }
    previousRouter = router;
  }
}

void generate_stress_test() {
  for (unsigned int id = 1; id <= 40; ++id) {
    ProblemInstance inst(std::string("stress_test_") + ((id < 10) ? "0" : "") + ToString(id));

    auto num_zones = 5 * id;
    auto num_tasks = 5;
    std::cout << "["<<std::right << std::setw(4) << id <<"]";
    std::cout << "Generating instnace with ";
    std::cout << std::right << std::setw(4) << num_zones << " zones and ";
    std::cout << std::right << std::setw(4) << num_tasks << " tasks, total " << (num_zones*num_tasks)<< ".\n";

    add_channels(inst);
    add_nodes(inst);
    add_zones(inst, num_zones);
    add_contiguities(inst);
    std::vector<std::shared_ptr<Task>> routers;
    for (auto it = inst.zones.begin(); it != inst.zones.end(); ++it) {
      add_zone_instance(inst, routers, it->second, num_tasks);
    }
    connect_routers(inst, routers);
    inst.printToFile();
  }
}