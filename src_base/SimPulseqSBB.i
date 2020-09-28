// SimPulseqSBB.i

%module SimPulseqSBB

%{
#define SWIG_FILE_WITH_INIT
#include <vector>
#include <iostream>
#include <string>
#include <sstream>
#include <fstream>
#include <set>
#include <map>
#include <functional>
#define _USE_MATH_DEFINES
#include <cmath>
#include "ExternalSequence.h"
#include "SimulationParameters.h"
#include "SimPulseqSBB.h"
#include "SimPulseqSBBTemplate.h"
#include "BlochMcConnellSolver.h"
%}

%include "eigen.i"
%include "SimulationParameters.h"
//%include "SimPulseqSBBTemplate.h"
%include "SimPulseqSBB.h"
//%template(SimPulseqSBB) SimPulseqSBBTemplate<int>;




/*
%module SimPulseqSBB

%{
#define SWIG_FILE_WITH_INIT
#include "SimPulseqSBBTemplate.h"
//#include "BlochMcConnellSolver.h"
#include <functional>
#include <numeric>
#include <vector>
#include "3rdParty/Eigen/Eigen"
//using namespace Eigen;
#include "ExternalSequence.h"
#include "SimulationParameters.h"
#include "SimPulseqSBB.h"
//typedef  SimulationParameters
#define _USE_MATH_DEFINES
#include <cmath>

%}

%include "eigen.i"
//%include "SimulationParameters.cpp"
%include "SimulationParameters.h"
%include "SimPulseqSBB.cpp"
//%include "SimPulseqSBBTemplate.h"
//%template(SimPulseqSBBT) SimPulseqSBBTemplate<int>;
// using namespace Eigen;
*/



