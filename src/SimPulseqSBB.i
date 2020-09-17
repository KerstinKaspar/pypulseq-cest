// SimPulseqSBB.i

%module SimulationParameters

%{
#define SWIG_FILE_WITH_INIT
#include "SimPulseqSBBTemplate.h"
#include "BlochMcConnellSolver.h"
#include <functional>
#include <numeric>
#include <vector>
#include "3rdParty/Eigen/Eigen"
using namespace Eigen;
#include "SimulationParameters.h"
#include "3rdParty/src_ext_seq/ExternalSequence.h"
#define _USE_MATH_DEFINES
#include <cmath>
#include "SimulationParameters.cpp"

%}

%include "SimPulseqSBB.cpp"
%include "SimPulseqSBBTemplate.h"
%template(SimPulseqSBBT) SimPulseqSBBTemplate<int>;
%include "3rdParty/Eigen/Eigen"
using namespace Eigen;
%include "SimulationParameters.cpp"
%include "SimulationParameters.h"



