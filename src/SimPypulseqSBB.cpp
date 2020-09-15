//!  Sim_seq_sbb.cpp
/*!
PYTHON interface for Bloch-McConnell pulseq SBB simulation
adapted from MATLAB version: https://github.com/kherz/pulseq-cest
*/

#include "SimulationParameters.h"
#include "SimPulseqSBBTemplate.h"
#include <matrix.h>

#define MAX_CEST_POOLS 100

void SimPypulseq
	/* For a small number of pools the matrix size can be set at compile time. This ensures allocation on the stack and therefore a faster simulation. 
	   This speed advantade vanishes for more pools and can even result in a stack overflow for very large matrices
	   In this case more than 3 pools are simulated with dynamic matrices, but this could be expanded eventually
	*/
	SimulationParameters sp;
	sp
	switch (sp.GetNumberOfCESTPools())
	{
	case 0:
		sp.IsMTActive() ? SimPulseqSBBTemplate<4>(sp) : SimPulseqSBBTemplate<3>(sp); // only water
		break;
	case 1:
		sp.IsMTActive() ? SimPulseqSBBTemplate<7>(sp) : SimPulseqSBBTemplate<6>(sp); // one cest pool
		break;
	case 2:
		sp.IsMTActive() ? SimPulseqSBBTemplate<10>(sp) : SimPulseqSBBTemplate<9>(sp); // two cest pools
		break;
	case 3:
		sp.IsMTActive() ? SimPulseqSBBTemplate<13>(sp) : SimPulseqSBBTemplate<12>(sp); // three cest pools
		break;
	default:
		SimPulseqSBBTemplate<Dynamic>(sp); // > three pools
		break;
	}

	ReturnResultToMATLAB(plhs, sp.GetMagnetizationVectors()); // return results after simulation
}
