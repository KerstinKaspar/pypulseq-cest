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

%include <typemaps.i>
%include <std_vector.i>
%include <std_string.i>

%include <eigen.i>

%template(vectorMatrixXd) std::vector<Eigen::MatrixXd>;
%template(vectorVectorXd) std::vector<Eigen::VectorXd>;

// Since Eigen uses templates, we have to declare exactly which types we'd
// like to generate mappings for.
%eigen_typemaps(Eigen::VectorXd)
%eigen_typemaps(Eigen::MatrixXd)
//%eigen_typemaps(Eigen::Matrix<double, Eigen::Dynamic, Eigen::Dynamic>)

%rename(NoLineshape) None;
%include "SimulationParameters.h"
//%include "SimPulseqSBBTemplate.h"
%include "SimPulseqSBB.h"
//%template(SimPulseqSBB) SimPulseqSBBTemplate<int>;


