// SimPulseqSBB.i

%module SimulationParameters

%{
#define SWIG_FILE_WITH_INIT
#include "SimPulseqSBBTemplate.h"

#include "SimulationParameters.h"

#include "SimulationParameters.cpp"

#include "BlochMcConnellSolver.h"
%}
%include "SimPulseqSBB.cpp"
%include "SimPulseqSBBTemplate.h"
%template(SimpulseqSBB) SimPulseqSBBTemplate(SimulationParameters& sp)<int>;

%include "SimulationParameters.cpp"
%include "SimulationParameters.h"



